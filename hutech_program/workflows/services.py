"""
Business services for approval workflow, versioning, and notifications.
"""

from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from hutech_program.notifications.models import Notification
from hutech_program.programs.models import ProgramStatus, TrainingProgram
from hutech_program.rbac.models import AuditAction, AuditLog, UserRole

from .models import (
    ApprovalStep,
    ApprovalWorkflow,
    EntityType,
    EntityVersion,
    StepStatus,
    WorkflowStatus,
)


# ────────────────────────── Workflow Service ──────────────────────────


class WorkflowService:
    """
    Core service handling all workflow state transitions.
    All public methods are wrapped in database transactions.
    """

    # Workflow step configurations per entity type
    WORKFLOW_CONFIGS = {
        EntityType.TRAINING_PROGRAM: [
            {"step": 1, "name": "Xét duyệt cấp Khoa/Viện", "role": "LANH_DAO_KHOA", "dept_scope": True},
            {"step": 2, "name": "Xét duyệt Phòng Đào tạo", "role": "PHONG_DAO_TAO", "dept_scope": False},
            {"step": 3, "name": "Phê duyệt Ban Giám Hiệu", "role": "BAN_GIAM_HIEU", "dept_scope": False},
        ],
        EntityType.PLO: [
            {"step": 1, "name": "Xét duyệt cấp Khoa/Viện", "role": "LANH_DAO_KHOA", "dept_scope": True},
            {"step": 2, "name": "Xét duyệt Phòng Đào tạo", "role": "PHONG_DAO_TAO", "dept_scope": False},
            {"step": 3, "name": "Phê duyệt Ban Giám Hiệu", "role": "BAN_GIAM_HIEU", "dept_scope": False},
        ],
        EntityType.SYLLABUS: [
            {"step": 1, "name": "Trưởng bộ môn kiểm tra", "role": "TRUONG_NGANH", "dept_scope": True},
            {"step": 2, "name": "Trưởng Khoa/Viện xét duyệt", "role": "LANH_DAO_KHOA", "dept_scope": True},
            {"step": 3, "name": "Phòng Đào tạo xét duyệt", "role": "PHONG_DAO_TAO", "dept_scope": False},
            {"step": 4, "name": "Ban Giám Hiệu phê duyệt", "role": "BAN_GIAM_HIEU", "dept_scope": False},
        ],
    }

    # Entity status mapping: step_number → entity status while that step is IN_REVIEW
    STATUS_MAPS = {
        EntityType.TRAINING_PROGRAM: {
            1: "KHOA_REVIEWING",
            2: "PDT_REVIEWING",
            3: "BGH_REVIEWING",
        },
        EntityType.PLO: {
            1: "KHOA_REVIEWING",
            2: "PDT_REVIEWING",
            3: "BGH_REVIEWING",
        },
        EntityType.SYLLABUS: {
            1: "TBM_REVIEWING",
            2: "TK_REVIEWING",
            3: "PDT_REVIEWING",
            4: "BGH_REVIEWING",
        },
    }

    @classmethod
    @transaction.atomic
    def submit(cls, entity, entity_type: str, user) -> ApprovalWorkflow:
        """
        Submit entity for approval. Creates workflow + all steps.
        Validates: entity status, no active workflow, user permission.
        """
        # Validate entity status
        if entity.status not in (ProgramStatus.DRAFT, ProgramStatus.REVISION_REQUIRED):
            raise ValidationError(
                {"status": "Chỉ có thể nộp duyệt từ trạng thái Bản nháp hoặc Cần chỉnh sửa"}
            )

        # Validate no active workflow
        existing = ApprovalWorkflow.objects.filter(
            entity_type=entity_type,
            entity_id=entity.id,
            status=WorkflowStatus.IN_PROGRESS,
        ).exists()
        if existing:
            raise ValidationError(
                {"workflow": "Tài liệu đang trong quy trình phê duyệt"}
            )

        # Get workflow config for entity type
        steps_config = cls.WORKFLOW_CONFIGS.get(entity_type)
        if not steps_config:
            raise ValidationError(
                {"entity_type": f"Không hỗ trợ quy trình phê duyệt cho loại: {entity_type}"}
            )

        # Create workflow
        workflow = ApprovalWorkflow.objects.create(
            entity_type=entity_type,
            entity_id=entity.id,
            current_step_number=1,
            total_steps=len(steps_config),
            status=WorkflowStatus.IN_PROGRESS,
            initiated_by=user,
        )

        # Create approval steps
        from hutech_program.rbac.models import Role

        for step_def in steps_config:
            role = Role.objects.filter(code=step_def["role"]).first()
            if not role:
                raise ValidationError(
                    {"role": f"Không tìm thấy vai trò {step_def['role']}"}
                )
            ApprovalStep.objects.create(
                workflow=workflow,
                step_number=step_def["step"],
                step_name=step_def["name"],
                required_role=role,
                required_department_scope=step_def.get("dept_scope", True),
                status=StepStatus.IN_REVIEW if step_def["step"] == 1 else StepStatus.PENDING,
            )

        # Update entity status
        status_map = cls.STATUS_MAPS.get(entity_type, {})
        new_status = status_map.get(1, "KHOA_REVIEWING")
        entity.status = new_status
        entity.save(update_fields=["status", "updated_at"])

        # Notify approvers for step 1
        first_step = workflow.steps.filter(step_number=1).first()
        if first_step:
            NotificationService.notify_step_approvers(first_step, entity)

        # Audit log
        cls._create_audit_log(
            user=user,
            action=AuditAction.SUBMIT,
            entity_type=entity_type,
            entity_id=entity.id,
            new_data={"status": new_status, "workflow_id": str(workflow.id)},
        )

        return workflow

    @classmethod
    @transaction.atomic
    def approve(cls, workflow: ApprovalWorkflow, user, comment: str = "") -> ApprovalStep:
        """
        Approve current step. If final, complete workflow + create version.
        Uses optimistic locking.
        """
        step = workflow.current_step
        if not step or step.status != StepStatus.IN_REVIEW:
            raise ValidationError(
                {"step": "Không tìm thấy bước phê duyệt đang chờ xử lý"}
            )

        entity = workflow.get_entity()
        if not entity:
            raise ValidationError({"entity": "Không tìm thấy đối tượng"})

        # Validate approver
        cls._validate_approver(step, user, entity)

        # Optimistic locking: read current version and filter update
        rows_updated = ApprovalStep.objects.filter(
            id=step.id,
            version=step.version,
        ).update(
            status=StepStatus.APPROVED,
            acted_by=user,
            acted_at=timezone.now(),
            action_comment=comment,
            version=step.version + 1,
            updated_at=timezone.now(),
        )
        if rows_updated == 0:
            raise ValidationError(
                {"conflict": "Bước này đã được xử lý bởi người khác. Vui lòng tải lại trang."}
            )

        # Refresh step from DB
        step.refresh_from_db()

        if not workflow.is_final_step:
            # Advance to next step
            cls._advance_to_next_step(workflow)

            # Notify next approvers
            next_step = workflow.current_step
            if next_step:
                NotificationService.notify_step_approvers(next_step, entity)

            # Notify initiator
            NotificationService.notify_initiator(
                workflow,
                f"Đã duyệt: {entity}",
                f"{entity} đã được duyệt ở bước: {step.step_name}.",
            )
        else:
            # Final approval
            cls._complete_workflow(workflow, user)

            # Notify initiator
            NotificationService.notify_initiator(
                workflow,
                f"Đã công bố: {entity}",
                f"{entity} đã được phê duyệt và công bố!",
            )

            # Notify department users
            if hasattr(entity, "managing_department") and entity.managing_department:
                NotificationService.notify_department_users(
                    department=entity.managing_department,
                    title=f"CTĐT đã được công bố",
                    message=f"{entity} đã được công bố phiên bản {getattr(entity, 'version', 1)}.",
                    link=f"/programs/{entity.id}",
                )

        # Audit log
        cls._create_audit_log(
            user=user,
            action=AuditAction.APPROVE,
            entity_type=workflow.entity_type,
            entity_id=workflow.entity_id,
            new_data={
                "step_number": step.step_number,
                "step_name": step.step_name,
                "comment": comment,
            },
        )

        return step

    @classmethod
    @transaction.atomic
    def reject(cls, workflow: ApprovalWorkflow, user, comment: str) -> ApprovalStep:
        """Reject current step. Comment is required."""
        if not comment or not comment.strip():
            raise ValidationError(
                {"comment": "Vui lòng nhập lý do từ chối"}
            )
        if len(comment.strip()) < 10:
            raise ValidationError(
                {"comment": "Lý do từ chối phải có ít nhất 10 ký tự"}
            )

        step = workflow.current_step
        if not step or step.status != StepStatus.IN_REVIEW:
            raise ValidationError(
                {"step": "Không tìm thấy bước phê duyệt đang chờ xử lý"}
            )

        entity = workflow.get_entity()
        if not entity:
            raise ValidationError({"entity": "Không tìm thấy đối tượng"})

        # Validate approver
        cls._validate_approver(step, user, entity)

        # Mark step as rejected
        step.status = StepStatus.REJECTED
        step.acted_by = user
        step.acted_at = timezone.now()
        step.action_comment = comment
        step.save()

        # Set workflow to rejected
        workflow.status = WorkflowStatus.REJECTED
        workflow.save(update_fields=["status", "updated_at"])

        # Set entity to revision required
        entity.status = ProgramStatus.REVISION_REQUIRED
        entity.save(update_fields=["status", "updated_at"])

        # Notify initiator
        NotificationService.notify_initiator(
            workflow,
            f"Bị từ chối: {entity}",
            f"{entity} bị từ chối ở bước: {step.step_name}. Nhận xét: {comment}",
        )

        # Audit log
        cls._create_audit_log(
            user=user,
            action=AuditAction.REJECT,
            entity_type=workflow.entity_type,
            entity_id=workflow.entity_id,
            new_data={
                "step_number": step.step_number,
                "step_name": step.step_name,
                "comment": comment,
            },
        )

        return step

    @classmethod
    def _validate_approver(cls, step: ApprovalStep, user, entity) -> None:
        """Check user has correct role + department for this step."""
        if user.is_superuser:
            return

        user_roles = UserRole.objects.filter(
            user=user,
            role=step.required_role,
        )

        if step.required_department_scope:
            # Need to match entity's department
            dept = getattr(entity, "managing_department", None)
            if dept:
                user_roles = user_roles.filter(department=dept)

        if not user_roles.exists():
            raise PermissionDenied(
                "Bạn không có quyền phê duyệt ở bước này"
            )

    @classmethod
    def _advance_to_next_step(cls, workflow: ApprovalWorkflow) -> None:
        """Set next step to IN_REVIEW, update workflow and entity."""
        next_number = workflow.current_step_number + 1
        next_step = workflow.steps.filter(step_number=next_number).first()
        if next_step:
            next_step.status = StepStatus.IN_REVIEW
            next_step.save(update_fields=["status", "updated_at"])

        workflow.current_step_number = next_number
        workflow.save(update_fields=["current_step_number", "updated_at"])

        # Update entity status
        entity = workflow.get_entity()
        if entity:
            status_map = cls.STATUS_MAPS.get(workflow.entity_type, {})
            new_status = status_map.get(next_number)
            if new_status:
                entity.status = new_status
                entity.save(update_fields=["status", "updated_at"])

    @classmethod
    def _complete_workflow(cls, workflow: ApprovalWorkflow, user) -> EntityVersion:
        """Set entity PUBLISHED, create version snapshot."""
        workflow.status = WorkflowStatus.COMPLETED
        workflow.completed_at = timezone.now()
        workflow.save(update_fields=["status", "completed_at", "updated_at"])

        entity = workflow.get_entity()
        if entity:
            entity.status = ProgramStatus.PUBLISHED
            if hasattr(entity, "version"):
                entity.version = (entity.version or 0) + 1
            entity.save()

            # Create version snapshot
            return VersionService.create_snapshot(
                entity=entity,
                entity_type=workflow.entity_type,
                user=user,
                workflow=workflow,
            )
        return None

    @classmethod
    def _get_notifiable_users(cls, step: ApprovalStep, entity) -> QuerySet:
        """Find all users with the required role (+ department if scoped)."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        user_roles = UserRole.objects.filter(role=step.required_role)

        if step.required_department_scope:
            dept = getattr(entity, "managing_department", None)
            if dept:
                user_roles = user_roles.filter(department=dept)

        user_ids = user_roles.values_list("user_id", flat=True)
        return User.objects.filter(id__in=user_ids)

    @classmethod
    def _get_active_workflow_for_entity(cls, entity_type, entity_id):
        """Get the active IN_PROGRESS workflow for an entity."""
        workflow = ApprovalWorkflow.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            status=WorkflowStatus.IN_PROGRESS,
        ).first()
        if not workflow:
            raise ValidationError(
                {"workflow": "Không tìm thấy quy trình phê duyệt đang hoạt động"}
            )
        return workflow

    @classmethod
    def _create_audit_log(cls, user, action, entity_type, entity_id, old_data=None, new_data=None):
        """Create audit log entry."""
        AuditLog.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_data=old_data,
            new_data=new_data,
        )


# ────────────────────────── Version Service ──────────────────────────


class VersionService:
    """Manages entity version snapshots, comparison, and rollback."""

    @classmethod
    def create_snapshot(cls, entity, entity_type: str, user, workflow=None) -> EntityVersion:
        """Create a full JSONB snapshot of the entity and all nested data."""
        last_version = EntityVersion.objects.filter(
            entity_type=entity_type,
            entity_id=entity.id,
        ).order_by("-version_number").first()
        next_number = (last_version.version_number + 1) if last_version else 1

        snapshot = cls._serialize_training_program(entity)

        return EntityVersion.objects.create(
            entity_type=entity_type,
            entity_id=entity.id,
            version_number=next_number,
            snapshot_data=snapshot,
            created_by=user,
            workflow=workflow,
        )

    @classmethod
    def compare_versions(cls, entity_type, entity_id, v1: int, v2: int) -> dict:
        """Deep diff two version snapshots. Returns structured changes."""
        version1 = EntityVersion.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            version_number=v1,
        ).first()
        version2 = EntityVersion.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            version_number=v2,
        ).first()

        if not version1 or not version2:
            raise ValidationError({"versions": "Không tìm thấy phiên bản"})

        return cls._deep_diff(version1.snapshot_data, version2.snapshot_data)

    @classmethod
    @transaction.atomic
    def rollback(cls, entity_type, entity_id, target_version: int, user) -> EntityVersion:
        """Restore entity from snapshot. Creates new version recording rollback."""
        target = EntityVersion.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            version_number=target_version,
        ).first()
        if not target:
            raise ValidationError({"version": "Không tìm thấy phiên bản"})

        # Get entity
        if entity_type == EntityType.TRAINING_PROGRAM:
            entity = TrainingProgram.objects.filter(id=entity_id).first()
        else:
            raise ValidationError({"entity_type": "Chưa hỗ trợ rollback cho loại này"})

        if not entity:
            raise ValidationError({"entity": "Không tìm thấy đối tượng"})

        data = target.snapshot_data

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
                setattr(entity, field, data[field])

        entity.status = ProgramStatus.DRAFT
        entity.last_modified_by = user
        entity.save()

        # Cancel any active workflow
        ApprovalWorkflow.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            status=WorkflowStatus.IN_PROGRESS,
        ).update(status=WorkflowStatus.CANCELLED)

        # Get current version number
        current = EntityVersion.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
        ).order_by("-version_number").first()
        current_ver = current.version_number if current else 0

        # Create new version recording the rollback
        new_version = EntityVersion.objects.create(
            entity_type=entity_type,
            entity_id=entity_id,
            version_number=current_ver + 1,
            snapshot_data=data,
            change_summary=f"Rollback từ phiên bản {current_ver} về phiên bản {target_version}",
            created_by=user,
        )

        # Audit log
        AuditLog.objects.create(
            user=user,
            action=AuditAction.ROLLBACK,
            entity_type=entity_type,
            entity_id=entity_id,
            new_data={
                "rollback_from": current_ver,
                "rollback_to": target_version,
            },
        )

        return new_version

    @classmethod
    def _serialize_training_program(cls, program) -> dict:
        """Full serialization including POs, PLOs, PIs, courses, matrices, plans."""
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

        # PLOs with PIs and PO mappings
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

    @classmethod
    def _deep_diff(cls, old: dict, new: dict) -> dict:
        """Recursive JSON diff. Returns structured changes per section."""
        changes = {}

        # Handle list sections (PLOs, courses, etc.) separately
        list_sections = {"plos", "objectives", "knowledge_blocks", "program_courses",
                         "semester_plans", "assessment_plans"}

        all_keys = set(list(old.keys()) + list(new.keys()))

        for key in sorted(all_keys):
            v_old = old.get(key)
            v_new = new.get(key)

            if v_old == v_new:
                continue

            if key in list_sections and isinstance(v_old, list) and isinstance(v_new, list):
                # Array diff: match by 'code' or 'course_code' field
                match_key = "code" if key in {"plos", "objectives"} else "course_code"
                changes[key] = cls._diff_list(v_old, v_new, match_key)
            else:
                changes[key] = {"old": v_old, "new": v_new}

        return changes

    @classmethod
    def _diff_list(cls, old_list: list, new_list: list, match_key: str) -> dict:
        """Diff two lists of dicts, matching items by a key field."""
        old_map = {}
        for item in old_list:
            if isinstance(item, dict) and match_key in item:
                old_map[item[match_key]] = item

        new_map = {}
        for item in new_list:
            if isinstance(item, dict) and match_key in item:
                new_map[item[match_key]] = item

        added = [v for k, v in new_map.items() if k not in old_map]
        removed = [v for k, v in old_map.items() if k not in new_map]

        modified = []
        for key in old_map:
            if key in new_map and old_map[key] != new_map[key]:
                item_changes = {}
                for field in set(list(old_map[key].keys()) + list(new_map[key].keys())):
                    if old_map[key].get(field) != new_map[key].get(field):
                        item_changes[field] = {
                            "old": old_map[key].get(field),
                            "new": new_map[key].get(field),
                        }
                if item_changes:
                    item_changes[match_key] = key
                    modified.append(item_changes)

        return {"added": added, "removed": removed, "modified": modified}

    # Keep backward compatibility alias
    _serialize_program = _serialize_training_program


# ────────────────────────── Notification Service ──────────────────────────


class NotificationService:
    """Creates notifications for workflow events."""

    @classmethod
    def notify_users(cls, users, title: str, message: str,
                     link: str = "", category: str = "WORKFLOW"):
        """Bulk create Notification records."""
        notifications = []
        for user in users:
            notifications.append(
                Notification(
                    user=user,
                    title=title,
                    message=message,
                    link=link,
                    category=category,
                )
            )
        return Notification.objects.bulk_create(notifications)

    @classmethod
    def notify_step_approvers(cls, step: ApprovalStep, entity):
        """Find users with step.required_role and department, then notify."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        user_roles = UserRole.objects.filter(role=step.required_role)

        if step.required_department_scope:
            dept = getattr(entity, "managing_department", None)
            if dept:
                user_roles = user_roles.filter(department=dept)

        user_ids = user_roles.values_list("user_id", flat=True)
        users = User.objects.filter(id__in=user_ids)

        # Exclude the current workflow initiator from approver notifications
        # (they don't need to approve their own submission)

        if users.exists():
            entity_name = str(entity)
            cls.notify_users(
                users=users,
                title=f"Yêu cầu phê duyệt: {entity_name}",
                message=(
                    f"{entity_name} cần được {step.step_name}. "
                    f"Người nộp: {step.workflow.initiated_by.name}."
                ),
                link=f"/programs/{entity.id}?tab=workflow",
            )

    @classmethod
    def notify_initiator(cls, workflow: ApprovalWorkflow, title: str, message: str):
        """Notify the person who started the workflow."""
        cls.notify_users(
            users=[workflow.initiated_by],
            title=title,
            message=message,
            link=f"/programs/{workflow.entity_id}?tab=workflow",
        )

    @classmethod
    def notify_department_users(cls, department, title: str, message: str, link: str = ""):
        """Notify all users in entity's department."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        user_ids = UserRole.objects.filter(
            department=department,
        ).values_list("user_id", flat=True).distinct()

        users = User.objects.filter(id__in=user_ids)
        if users.exists():
            cls.notify_users(
                users=users,
                title=title,
                message=message,
                link=link,
            )

    # Legacy compatibility aliases
    @classmethod
    def notify(cls, users, title, message, link=""):
        return cls.notify_users(users, title, message, link)

    @classmethod
    def notify_approvers(cls, workflow, step_number, program):
        step = workflow.steps.filter(step_number=step_number).first()
        if step:
            cls.notify_step_approvers(step, program)

    @classmethod
    def notify_creator(cls, workflow, program, action, step):
        action_messages = {
            "approved": f"{program} đã được duyệt ở bước: {step.step_name}.",
            "rejected": (
                f"{program} bị từ chối ở bước: {step.step_name}. "
                f"Nhận xét: {step.action_comment}"
            ),
            "published": f"{program} đã được phê duyệt và công bố!",
        }
        action_titles = {
            "approved": f"Đã duyệt: {program}",
            "rejected": f"Bị từ chối: {program}",
            "published": f"Đã công bố: {program}",
        }
        cls.notify_initiator(
            workflow,
            action_titles.get(action, f"Cập nhật: {program}"),
            action_messages.get(action, ""),
        )
