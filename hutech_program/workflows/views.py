"""
Workflow & Version views.
"""

from django.db import models as db_models
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from hutech_program.programs.models import TrainingProgram
from hutech_program.rbac.permissions import HasModulePermission

from .models import ApprovalWorkflow, ProgramVersion, WorkflowStatus
from .serializers import (
    ApprovalWorkflowSerializer,
    ProgramVersionDetailSerializer,
    ProgramVersionListSerializer,
    WorkflowActionSerializer,
)
from .services import VersionService, WorkflowService


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
    }

    def _get_program(self):
        program_pk = self.kwargs.get("program_pk")
        return get_object_or_404(TrainingProgram, pk=program_pk)

    @action(detail=False, methods=["post"], url_path="submit")
    def submit(self, request, program_pk=None):
        program = self._get_program()
        workflow = WorkflowService.submit(program, request.user)
        serializer = ApprovalWorkflowSerializer(workflow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="approve")
    def approve(self, request, program_pk=None):
        program = self._get_program()
        ser = WorkflowActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        workflow = WorkflowService.approve(
            program, request.user, comment=ser.validated_data.get("comment", "")
        )
        serializer = ApprovalWorkflowSerializer(workflow)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="reject")
    def reject(self, request, program_pk=None):
        program = self._get_program()
        ser = WorkflowActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        workflow = WorkflowService.reject(
            program, request.user, comment=ser.validated_data.get("comment", "")
        )
        serializer = ApprovalWorkflowSerializer(workflow)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="workflow")
    def workflow_status(self, request, program_pk=None):
        program = self._get_program()
        workflow = ApprovalWorkflow.objects.filter(
            entity_type="TrainingProgram",
            entity_id=program.id,
        ).prefetch_related("steps__approver_role", "steps__approver").order_by("-created_at").first()

        if not workflow:
            return Response({"detail": "Chưa có quy trình phê duyệt."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ApprovalWorkflowSerializer(workflow)
        return Response(serializer.data)


class ProgramVersionViewSet(
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
        return ProgramVersion.objects.filter(
            program_id=program_pk
        ).select_related("approved_by")

    def get_serializer_class(self):
        if self.action == "list":
            return ProgramVersionListSerializer
        return ProgramVersionDetailSerializer

    @action(detail=False, methods=["get"])
    def compare(self, request, program_pk=None):
        v1_num = request.query_params.get("v1")
        v2_num = request.query_params.get("v2")
        if not v1_num or not v2_num:
            return Response(
                {"detail": "Cần cung cấp v1 và v2."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = self.get_queryset()
        version1 = get_object_or_404(qs, version_number=v1_num)
        version2 = get_object_or_404(qs, version_number=v2_num)

        diff = VersionService.compare(version1, version2)
        return Response({
            "v1": int(v1_num),
            "v2": int(v2_num),
            "diff": diff,
        })

    @action(detail=True, methods=["post"])
    def rollback(self, request, program_pk=None, pk=None):
        program = get_object_or_404(TrainingProgram, pk=program_pk)
        version = get_object_or_404(self.get_queryset(), pk=pk)

        VersionService.rollback(program, version, request.user)
        return Response({"detail": f"Đã rollback về phiên bản v{version.version_number}."})


class PendingApprovalsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    List pending approvals for the current user (based on role).
    """

    serializer_class = ApprovalWorkflowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Find all role IDs of the user
        user_role_ids = user.user_roles.values_list("role_id", flat=True)

        return ApprovalWorkflow.objects.filter(
            status=WorkflowStatus.IN_PROGRESS,
            steps__step_number=db_models.F("current_step"),
            steps__approver_role_id__in=user_role_ids,
            steps__status="PENDING",
        ).prefetch_related("steps__approver_role", "steps__approver").distinct()
