"""
Workflow, Version, Notification, and Pending Approval views.
"""

from django.db import models as db_models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from hutech_program.notifications.models import Notification
from hutech_program.programs.models import TrainingProgram
from hutech_program.rbac.models import UserRole
from hutech_program.rbac.permissions import HasModulePermission

from .models import (
    ApprovalComment,
    ApprovalStep,
    ApprovalWorkflow,
    EntityType,
    EntityVersion,
    StepStatus,
    WorkflowStatus,
)
from .serializers import (
    ApprovalCommentCreateSerializer,
    ApprovalCommentSerializer,
    ApprovalWorkflowSerializer,
    ApproveSerializer,
    EntityVersionDetailSerializer,
    EntityVersionListSerializer,
    NotificationSerializer,
    PendingApprovalSerializer,
    RejectSerializer,
    WorkflowActionSerializer,
)
from .services import VersionService, WorkflowService


# ────────────────────────── Workflow Actions ──────────────────────────


class WorkflowActionViewSet(viewsets.ViewSet):
    """
    Submit / Approve / Reject actions on a training program.
    Nested under /programs/{program_pk}/...
    """

    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "submit": "programs.edit",
        "approve": "programs.edit",
        "reject": "programs.edit",
        "workflow_status": "programs.view",
        "workflow_history": "programs.view",
    }

    def _get_program(self):
        program_pk = self.kwargs.get("program_pk")
        return get_object_or_404(TrainingProgram, pk=program_pk)

    @action(detail=False, methods=["post"], url_path="submit")
    def submit(self, request, program_pk=None):
        program = self._get_program()
        workflow = WorkflowService.submit(
            entity=program,
            entity_type=EntityType.TRAINING_PROGRAM,
            user=request.user,
        )
        serializer = ApprovalWorkflowSerializer(workflow)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="approve")
    def approve(self, request, program_pk=None):
        program = self._get_program()
        workflow = WorkflowService._get_active_workflow_for_entity(
            EntityType.TRAINING_PROGRAM, program.id
        )
        ser = ApproveSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        WorkflowService.approve(
            workflow, request.user, comment=ser.validated_data.get("comment", "")
        )
        workflow.refresh_from_db()
        serializer = ApprovalWorkflowSerializer(workflow)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="reject")
    def reject(self, request, program_pk=None):
        program = self._get_program()
        workflow = WorkflowService._get_active_workflow_for_entity(
            EntityType.TRAINING_PROGRAM, program.id
        )
        ser = RejectSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        WorkflowService.reject(
            workflow, request.user, comment=ser.validated_data["comment"]
        )
        workflow.refresh_from_db()
        serializer = ApprovalWorkflowSerializer(workflow)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="workflow")
    def workflow_status(self, request, program_pk=None):
        """Get current active workflow for this program."""
        program = self._get_program()
        workflow = ApprovalWorkflow.objects.filter(
            entity_type=EntityType.TRAINING_PROGRAM,
            entity_id=program.id,
        ).prefetch_related(
            "steps__required_role", "steps__acted_by", "steps__comments__author"
        ).order_by("-created_at").first()

        if not workflow:
            return Response(
                {"detail": "Chưa có quy trình phê duyệt."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ApprovalWorkflowSerializer(workflow)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="workflow-history")
    def workflow_history(self, request, program_pk=None):
        """Get all workflows (including rejected ones) for this program."""
        program = self._get_program()
        workflows = ApprovalWorkflow.objects.filter(
            entity_type=EntityType.TRAINING_PROGRAM,
            entity_id=program.id,
        ).prefetch_related(
            "steps__required_role", "steps__acted_by", "steps__comments__author"
        ).order_by("-created_at")

        serializer = ApprovalWorkflowSerializer(workflows, many=True)
        return Response(serializer.data)


# ────────────────────────── Comments ──────────────────────────


class ApprovalCommentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Comments on workflow steps."""

    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalCommentSerializer

    def get_queryset(self):
        step_id = self.kwargs.get("step_id")
        return ApprovalComment.objects.filter(
            step_id=step_id
        ).select_related("author").order_by("created_at")

    def create(self, request, workflow_id=None, step_id=None):
        ser = ApprovalCommentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        step = get_object_or_404(ApprovalStep, id=step_id, workflow_id=workflow_id)

        parent = None
        parent_id = ser.validated_data.get("parent_id")
        if parent_id:
            parent = get_object_or_404(ApprovalComment, id=parent_id, step=step)

        comment = ApprovalComment.objects.create(
            step=step,
            author=request.user,
            content=ser.validated_data["content"],
            parent=parent,
        )

        return Response(
            ApprovalCommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )


# ────────────────────────── Versions ──────────────────────────


class EntityVersionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    List / detail / compare / rollback versions.
    Nested under /programs/{program_pk}/versions/
    """

    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "list": "programs.view",
        "retrieve": "programs.view",
        "compare": "programs.view",
        "rollback": "programs.edit",
    }

    def get_queryset(self):
        program_pk = self.kwargs.get("program_pk")
        return EntityVersion.objects.filter(
            entity_type=EntityType.TRAINING_PROGRAM,
            entity_id=program_pk,
        ).select_related("created_by")

    def get_serializer_class(self):
        if self.action == "list":
            return EntityVersionListSerializer
        return EntityVersionDetailSerializer

    @action(detail=False, methods=["get"])
    def compare(self, request, program_pk=None):
        v1_num = request.query_params.get("v1")
        v2_num = request.query_params.get("v2")
        if not v1_num or not v2_num:
            return Response(
                {"detail": "Cần cung cấp v1 và v2."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        diff = VersionService.compare_versions(
            entity_type=EntityType.TRAINING_PROGRAM,
            entity_id=program_pk,
            v1=int(v1_num),
            v2=int(v2_num),
        )
        return Response({
            "v1": int(v1_num),
            "v2": int(v2_num),
            "changes": diff,
        })

    @action(detail=True, methods=["post"])
    def rollback(self, request, program_pk=None, pk=None):
        version = get_object_or_404(self.get_queryset(), pk=pk)
        VersionService.rollback(
            entity_type=EntityType.TRAINING_PROGRAM,
            entity_id=program_pk,
            target_version=version.version_number,
            user=request.user,
        )
        return Response(
            {"detail": f"Đã rollback về phiên bản v{version.version_number}."}
        )


# ────────────────────────── Notifications ──────────────────────────


class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """User notifications."""

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

    def perform_update(self, serializer):
        """When marking as read, set read_at timestamp."""
        instance = serializer.save()
        if instance.is_read and not instance.read_at:
            instance.read_at = timezone.now()
            instance.save(update_fields=["read_at"])

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"count": count})

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        updated = self.get_queryset().filter(is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return Response({"updated": updated})


# ────────────────────────── Pending Approvals ──────────────────────────


class PendingApprovalsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    List pending approvals for the current user (based on role).
    """

    serializer_class = PendingApprovalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Not used directly since we build custom data
        return ApprovalWorkflow.objects.none()

    def list(self, request):
        user = request.user

        # Find user's roles (with department)
        user_roles = UserRole.objects.filter(user=user).select_related("role", "department")

        # Filter by entity_type if provided
        entity_type_filter = request.query_params.get("entity_type")

        # Build pending items
        pending_items = []

        for user_role in user_roles:
            # Find steps where this user can act
            steps_qs = ApprovalStep.objects.filter(
                status=StepStatus.IN_REVIEW,
                required_role=user_role.role,
                workflow__status=WorkflowStatus.IN_PROGRESS,
            ).select_related("workflow__initiated_by")

            # If department-scoped, filter (this is handled by step config)
            # We need to check if the entity belongs to the user's department
            for step in steps_qs:
                workflow = step.workflow

                if entity_type_filter and workflow.entity_type != entity_type_filter:
                    continue

                entity = workflow.get_entity()
                if not entity:
                    continue

                # Check department scope
                if step.required_department_scope:
                    entity_dept = getattr(entity, "managing_department", None)
                    if entity_dept and entity_dept != user_role.department:
                        continue

                days_waiting = (timezone.now() - workflow.created_at).days
                dept_name = None
                if hasattr(entity, "managing_department") and entity.managing_department:
                    dept_name = entity.managing_department.name

                pending_items.append({
                    "entity_type": workflow.entity_type,
                    "entity_id": workflow.entity_id,
                    "entity_name": str(entity),
                    "submitted_by": workflow.initiated_by.name,
                    "submitted_at": workflow.created_at,
                    "days_waiting": days_waiting,
                    "department_name": dept_name,
                    "step_name": step.step_name,
                })

        # Deduplicate by entity_id
        seen = set()
        unique_items = []
        for item in pending_items:
            if item["entity_id"] not in seen:
                seen.add(item["entity_id"])
                unique_items.append(item)

        # Sort by oldest first
        unique_items.sort(key=lambda x: x["submitted_at"])

        serializer = PendingApprovalSerializer(unique_items, many=True)
        return Response(serializer.data)


# Legacy alias for backward compatibility
ProgramVersionViewSet = EntityVersionViewSet
