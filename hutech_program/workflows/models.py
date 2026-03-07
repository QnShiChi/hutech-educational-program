"""
Approval Workflow models: ApprovalWorkflow, ApprovalStep, ProgramVersion.
Implements multi-level approval: Khoa → Phòng ĐT → BGH.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from hutech_program.common import BaseModel, UUIDModel


# ────────────────────────── Choices ──────────────────────────


class WorkflowStatus(models.TextChoices):
    PENDING = "PENDING", _("Đang chờ")
    IN_PROGRESS = "IN_PROGRESS", _("Đang xét duyệt")
    APPROVED = "APPROVED", _("Đã duyệt")
    REJECTED = "REJECTED", _("Bị từ chối")


class StepStatus(models.TextChoices):
    PENDING = "PENDING", _("Chờ xử lý")
    APPROVED = "APPROVED", _("Đã duyệt")
    REJECTED = "REJECTED", _("Bị từ chối")
    SKIPPED = "SKIPPED", _("Bỏ qua")


# Step definitions for training program approval
TRAINING_PROGRAM_STEPS = [
    {"step_number": 1, "step_name": "Xét duyệt cấp Khoa", "approver_role_code": "LANH_DAO_KHOA"},
    {"step_number": 2, "step_name": "Xét duyệt Phòng Đào tạo", "approver_role_code": "PHONG_DAO_TAO"},
    {"step_number": 3, "step_name": "Xét duyệt Ban Giám hiệu", "approver_role_code": "BAN_GIAM_HIEU"},
]


# ────────────────────────── Models ──────────────────────────


class ApprovalWorkflow(BaseModel):
    """
    Quy trình phê duyệt.
    Tracking toàn bộ workflow từ submit → approval/rejection.
    """

    entity_type = models.CharField(
        max_length=50,
        verbose_name=_("Loại đối tượng"),
        help_text=_("VD: TrainingProgram"),
    )
    entity_id = models.UUIDField(verbose_name=_("ID đối tượng"))
    current_step = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Bước hiện tại"),
    )
    status = models.CharField(
        max_length=20,
        choices=WorkflowStatus.choices,
        default=WorkflowStatus.PENDING,
        verbose_name=_("Trạng thái"),
    )
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="initiated_workflows",
        verbose_name=_("Người khởi tạo"),
    )

    class Meta:
        verbose_name = _("Quy trình phê duyệt")
        verbose_name_plural = _("Quy trình phê duyệt")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Workflow {self.entity_type}:{self.entity_id} ({self.status})"


class ApprovalStep(BaseModel):
    """
    Từng bước phê duyệt trong workflow.
    """

    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name="steps",
        verbose_name=_("Quy trình"),
    )
    step_number = models.PositiveIntegerField(
        verbose_name=_("Số bước"),
        help_text=_("1=Khoa, 2=Phòng ĐT, 3=BGH"),
    )
    step_name = models.CharField(
        max_length=100,
        verbose_name=_("Tên bước"),
    )
    approver_role = models.ForeignKey(
        "rbac.Role",
        on_delete=models.PROTECT,
        verbose_name=_("Vai trò duyệt"),
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_steps",
        verbose_name=_("Người duyệt"),
    )
    status = models.CharField(
        max_length=20,
        choices=StepStatus.choices,
        default=StepStatus.PENDING,
        verbose_name=_("Trạng thái"),
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_("Nhận xét"),
    )
    acted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Thời gian xử lý"),
    )

    class Meta:
        verbose_name = _("Bước phê duyệt")
        verbose_name_plural = _("Bước phê duyệt")
        ordering = ["step_number"]
        unique_together = ["workflow", "step_number"]

    def __str__(self) -> str:
        return f"Step {self.step_number}: {self.step_name} ({self.status})"


class ProgramVersion(BaseModel):
    """
    Version snapshot of a TrainingProgram at approval time.
    Stores full JSONB data for comparison and rollback.
    """

    program = models.ForeignKey(
        "programs.TrainingProgram",
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name=_("Chương trình"),
    )
    version_number = models.PositiveIntegerField(
        verbose_name=_("Số phiên bản"),
    )
    snapshot_data = models.JSONField(
        default=dict,
        verbose_name=_("Dữ liệu snapshot"),
        help_text=_("Full CTĐT data at approval time"),
    )
    change_summary = models.TextField(
        blank=True,
        verbose_name=_("Tóm tắt thay đổi"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="approved_versions",
        verbose_name=_("Người duyệt"),
    )

    class Meta:
        verbose_name = _("Phiên bản CTĐT")
        verbose_name_plural = _("Phiên bản CTĐT")
        ordering = ["-version_number"]
        unique_together = ["program", "version_number"]

    def save(self, *args, **kwargs):
        # Auto-calculate version_number if not provided
        if not self.version_number:
            last = (
                ProgramVersion.objects.filter(program=self.program)
                .order_by("-version_number")
                .first()
            )
            self.version_number = (last.version_number + 1) if last else 1

        # Auto-generate snapshot_data when empty and program is assigned
        if not self.snapshot_data and self.program_id:
            from hutech_program.workflows.services import VersionService

            self.snapshot_data = VersionService._serialize_program(self.program)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.program.program_code} v{self.version_number}"
