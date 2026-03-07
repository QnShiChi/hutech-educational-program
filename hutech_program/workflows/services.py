"""
Business services for approval workflow, versioning, and notifications.
"""

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from hutech_program.notifications.models import Notification
from hutech_program.programs.models import ProgramStatus, TrainingProgram
from hutech_program.rbac.models import UserRole

from .models import (
    ApprovalStep,
    ApprovalWorkflow,
    ProgramVersion,
    StepStatus,
    TRAINING_PROGRAM_STEPS,
    WorkflowStatus,
)


# ────────────────────────── Workflow Service ──────────────────────────


class WorkflowService:
    """State machine logic for multi-level approval."""

    # Valid transitions: from_status → [to_statuses]
    STATUS_MAP = {
        1: {
            "reviewing": ProgramStatus.KHOA_REVIEWING,
            "approved": ProgramStatus.KHOA_APPROVED,
        },
        2: {
            "reviewing": ProgramStatus.PDT_REVIEWING,
            "approved": ProgramStatus.PDT_APPROVED,
        },
        3: {
            "reviewing": ProgramStatus.BGH_REVIEWING,
            "approved": ProgramStatus.PUBLISHED,
        },
    }

    @classmethod
    @transaction.atomic
    def submit(cls, program, user):
        """Submit program for approval. Creates workflow + 3 steps."""
        if program.status not in (ProgramStatus.DRAFT, ProgramStatus.REVISION_REQUIRED):
            raise ValidationError(
                {"status": f"Không thể nộp duyệt khi trạng thái là {program.get_status_display()}."}
            )

        # Prevent concurrent submissions
        existing = ApprovalWorkflow.objects.filter(
            entity_type="TrainingProgram",
            entity_id=program.id,
            status__in=[WorkflowStatus.PENDING, WorkflowStatus.IN_PROGRESS],
        ).exists()
        if existing:
            raise ValidationError(
                {"workflow": "CTĐT này đang trong quy trình phê duyệt."}
            )

        # Create workflow
        workflow = ApprovalWorkflow.objects.create(
            entity_type="TrainingProgram",
            entity_id=program.id,
            current_step=1,
            status=WorkflowStatus.IN_PROGRESS,
            initiated_by=user,
        )

        # Create 3 approval steps
        from hutech_program.rbac.models import Role

        for step_def in TRAINING_PROGRAM_STEPS:
            role = Role.objects.filter(code=step_def["approver_role_code"]).first()
            if not role:
                raise ValidationError(
                    {"role": f"Không tìm thấy vai trò {step_def['approver_role_code']}."}
                )
            ApprovalStep.objects.create(
                workflow=workflow,
                step_number=step_def["step_number"],
                step_name=step_def["step_name"],
                approver_role=role,
            )

        # Update program status
        program.status = ProgramStatus.SUBMITTED
        program.save(update_fields=["status", "updated_at"])

        # Auto-advance to KHOA_REVIEWING
        program.status = ProgramStatus.KHOA_REVIEWING
        program.save(update_fields=["status", "updated_at"])

        # Notify approvers for step 1
        NotificationService.notify_approvers(
            workflow=workflow,
            step_number=1,
            program=program,
        )

        return workflow

    @classmethod
    @transaction.atomic
    def approve(cls, program, user, comment=""):
        """Approve current step and advance workflow."""
        workflow = cls._get_active_workflow(program)
        step = cls._get_current_step(workflow)

        cls._validate_approver_role(user, step)

        # Mark step as approved
        step.status = StepStatus.APPROVED
        step.approver = user
        step.comment = comment
        step.acted_at = timezone.now()
        step.save()

        # Advance to next step or complete
        next_step_number = step.step_number + 1
        status_map = cls.STATUS_MAP.get(step.step_number, {})

        if next_step_number <= len(TRAINING_PROGRAM_STEPS):
            # Advance — update program to approved status for this level, then reviewing for next
            workflow.current_step = next_step_number
            workflow.save(update_fields=["current_step", "updated_at"])

            program.status = status_map.get("approved", program.status)
            program.save(update_fields=["status", "updated_at"])

            # Auto-advance to next reviewing status
            next_status_map = cls.STATUS_MAP.get(next_step_number, {})
            reviewing_status = next_status_map.get("reviewing")
            if reviewing_status:
                program.status = reviewing_status
                program.save(update_fields=["status", "updated_at"])

            # Notify next approvers + creator
            NotificationService.notify_approvers(
                workflow=workflow,
                step_number=next_step_number,
                program=program,
            )
            NotificationService.notify_creator(
                workflow=workflow,
                program=program,
                action="approved",
                step=step,
            )
        else:
            # Final approval — PUBLISHED
            workflow.status = WorkflowStatus.APPROVED
            workflow.save(update_fields=["status", "updated_at"])

            program.status = ProgramStatus.PUBLISHED
            program.save(update_fields=["status", "updated_at"])

            # Create version snapshot
            VersionService.create_snapshot(program, user)

            # Notify creator
            NotificationService.notify_creator(
                workflow=workflow,
                program=program,
                action="published",
                step=step,
            )

        return workflow

    @classmethod
    @transaction.atomic
    def reject(cls, program, user, comment):
        """Reject at current step. Comment is required."""
        if not comment.strip():
            raise ValidationError({"comment": "Phải có nhận xét khi từ chối."})

        workflow = cls._get_active_workflow(program)
        step = cls._get_current_step(workflow)

        cls._validate_approver_role(user, step)

        # Mark step as rejected
        step.status = StepStatus.REJECTED
        step.approver = user
        step.comment = comment
        step.acted_at = timezone.now()
        step.save()

        # Reset workflow
        workflow.status = WorkflowStatus.REJECTED
        workflow.save(update_fields=["status", "updated_at"])

        # Reset program status
        program.status = ProgramStatus.REVISION_REQUIRED
        program.save(update_fields=["status", "updated_at"])

        # Notify creator
        NotificationService.notify_creator(
            workflow=workflow,
            program=program,
            action="rejected",
            step=step,
        )

        return workflow

    @classmethod
    def _get_active_workflow(cls, program):
        workflow = ApprovalWorkflow.objects.filter(
            entity_type="TrainingProgram",
            entity_id=program.id,
            status=WorkflowStatus.IN_PROGRESS,
        ).first()
        if not workflow:
            raise ValidationError(
                {"workflow": "Không tìm thấy quy trình phê duyệt đang hoạt động."}
            )
        return workflow

    @classmethod
    def _get_current_step(cls, workflow):
        step = workflow.steps.filter(step_number=workflow.current_step).first()
        if not step:
            raise ValidationError({"step": "Không tìm thấy bước phê duyệt hiện tại."})
        return step

    @classmethod
    def _validate_approver_role(cls, user, step):
        """Check that user has the required role for this step."""
        has_role = UserRole.objects.filter(
            user=user,
            role=step.approver_role,
        ).exists()
        if not has_role and not user.is_superuser:
            raise ValidationError(
                {"permission": f"Bạn không có quyền {step.step_name}."}
            )


# ────────────────────────── Version Service ──────────────────────────


class VersionService:
    """Manages program version snapshots."""

    @classmethod
    def create_snapshot(cls, program, approved_by):
        """Create a full JSONB snapshot of the program and all nested data."""
        # Determine next version number
        last_version = ProgramVersion.objects.filter(
            program=program
        ).order_by("-version_number").first()
        next_number = (last_version.version_number + 1) if last_version else 1

        snapshot = cls._serialize_program(program)

        return ProgramVersion.objects.create(
            program=program,
            version_number=next_number,
            snapshot_data=snapshot,
            approved_by=approved_by,
        )

    @classmethod
    def compare(cls, version1, version2):
        """Compare two version snapshots and return diff."""
        diff = {}
        data1 = version1.snapshot_data
        data2 = version2.snapshot_data

        all_keys = set(list(data1.keys()) + list(data2.keys()))
        for key in sorted(all_keys):
            v1 = data1.get(key)
            v2 = data2.get(key)
            if v1 != v2:
                diff[key] = {"old": v1, "new": v2}

        return diff

    @classmethod
    @transaction.atomic
    def rollback(cls, program, version, user):
        """Restore program from a version snapshot."""
        data = version.snapshot_data

        # Restore basic fields
        basic_fields = [
            "program_name_vi", "program_name_en", "degree_name",
            "education_level", "total_credits", "training_duration",
            "decision_number", "decision_date", "issuing_institution",
            "general_objective", "admission_requirements",
            "graduation_requirements", "career_opportunities",
            "further_education", "teaching_methodology",
            "assessment_methodology", "implementation_guide",
        ]
        for field in basic_fields:
            if field in data:
                setattr(program, field, data[field])

        program.status = ProgramStatus.DRAFT
        program.last_modified_by = user
        program.save()

        return program

    @classmethod
    def _serialize_program(cls, program):
        """Serialize entire program with all related data."""
        data = {
            "program_code": program.program_code,
            "program_name_vi": program.program_name_vi,
            "program_name_en": program.program_name_en,
            "degree_name": program.degree_name,
            "education_level": program.education_level,
            "total_credits": program.total_credits,
            "training_duration": program.training_duration,
            "decision_number": program.decision_number,
            "decision_date": str(program.decision_date) if program.decision_date else None,
            "issuing_institution": program.issuing_institution,
            "general_objective": program.general_objective,
            "admission_requirements": program.admission_requirements,
            "graduation_requirements": program.graduation_requirements,
            "career_opportunities": program.career_opportunities,
            "further_education": program.further_education,
            "teaching_methodology": program.teaching_methodology,
            "assessment_methodology": program.assessment_methodology,
            "implementation_guide": program.implementation_guide,
        }

        # Objectives (POs)
        data["objectives"] = list(
            program.objectives.values("code", "description", "order_index")
        )

        # PLOs
        plos = []
        for plo in program.plos.prefetch_related("performance_indicators", "objectives"):
            plo_data = {
                "code": plo.code,
                "description": plo.description,
                "competency_level": str(plo.competency_level),
                "competency_label": plo.competency_label,
                "order_index": plo.order_index,
                "po_codes": list(plo.objectives.values_list("code", flat=True)),
                "performance_indicators": list(
                    plo.performance_indicators.values("code", "description", "order_index")
                ),
            }
            plos.append(plo_data)
        data["plos"] = plos

        # Knowledge blocks
        data["knowledge_blocks"] = list(
            program.knowledge_blocks.values(
                "name", "total_credits", "required_credits",
                "elective_credits", "percentage", "order_index",
            )
        )

        # Program courses
        courses = []
        for pc in program.program_courses.select_related("course", "knowledge_block"):
            course_data = {
                "course_code": pc.course.code,
                "course_name": pc.course.name_vi,
                "order_number": pc.order_number,
                "is_required": pc.is_required,
                "semester": pc.semester,
                "total_credits": pc.course.total_credits,
            }
            courses.append(course_data)
        data["program_courses"] = courses

        # Semester plans
        data["semester_plans"] = list(
            program.semester_plans.select_related("program_course__course").values(
                "semester_number",
                "program_course__course__code",
                "order_index",
            )
        )

        # Assessment plans
        data["assessment_plans"] = list(
            program.assessment_plans.select_related("pi").values(
                "pi__code",
                "contributing_courses_text",
                "direct_evidence",
                "assessment_tool",
                "expected_standard",
                "assessment_schedule",
            )
        )

        return data


# ────────────────────────── Notification Service ──────────────────────────


class NotificationService:
    """Creates notifications for workflow events."""

    @classmethod
    def notify(cls, users, title, message, link=""):
        """Send notification to multiple users."""
        notifications = []
        for user in users:
            notifications.append(
                Notification(
                    user=user,
                    title=title,
                    message=message,
                    link=link,
                )
            )
        return Notification.objects.bulk_create(notifications)

    @classmethod
    def notify_approvers(cls, workflow, step_number, program):
        """Notify users with the approver role for the given step."""
        step = workflow.steps.filter(step_number=step_number).first()
        if not step:
            return

        # Find users with this role
        approver_users = UserRole.objects.filter(
            role=step.approver_role,
        ).values_list("user", flat=True)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(id__in=approver_users)

        if users.exists():
            cls.notify(
                users=users,
                title=f"Yêu cầu phê duyệt: {program.program_code}",
                message=(
                    f"CTĐT \"{program.program_name_vi}\" cần được {step.step_name}. "
                    f"Người nộp: {workflow.initiated_by.name}."
                ),
                link=f"/programs/{program.id}",
            )

    @classmethod
    def notify_creator(cls, workflow, program, action, step):
        """Notify the creator about workflow progress."""
        action_messages = {
            "approved": f"CTĐT \"{program.program_name_vi}\" đã được duyệt ở bước: {step.step_name}.",
            "rejected": (
                f"CTĐT \"{program.program_name_vi}\" bị từ chối ở bước: {step.step_name}. "
                f"Nhận xét: {step.comment}"
            ),
            "published": f"CTĐT \"{program.program_name_vi}\" đã được phê duyệt và công bố!",
        }

        action_titles = {
            "approved": f"Đã duyệt: {program.program_code}",
            "rejected": f"Bị từ chối: {program.program_code}",
            "published": f"Đã công bố: {program.program_code}",
        }

        cls.notify(
            users=[workflow.initiated_by],
            title=action_titles.get(action, f"Cập nhật: {program.program_code}"),
            message=action_messages.get(action, ""),
            link=f"/programs/{program.id}",
        )
