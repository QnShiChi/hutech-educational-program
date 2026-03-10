"""
Approval Workflow models: ApprovalWorkflow, ApprovalStep, ApprovalComment,
EntityVersion, plus enums.
Implements multi-level approval: Khoa → Phòng ĐT → BGH.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from hutech_program.common import BaseModel, UUIDModel


# ────────────────────────── Choices ──────────────────────────


class WorkflowStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", _("Đang xử lý")
    COMPLETED = "COMPLETED", _("Hoàn thành")
    REJECTED = "REJECTED", _("Bị từ chối")
    CANCELLED = "CANCELLED", _("Đã hủy")


class StepStatus(models.TextChoices):
    PENDING = "PENDING", _("Chờ đến lượt")
    IN_REVIEW = "IN_REVIEW", _("Đang xét duyệt")
    APPROVED = "APPROVED", _("Đã duyệt")
    REJECTED = "REJECTED", _("Từ chối")
    SKIPPED = "SKIPPED", _("Bỏ qua")


class EntityType(models.TextChoices):
    TRAINING_PROGRAM = "TrainingProgram", _("Chương trình đào tạo")
    PLO = "ProgramLearningOutcome", _("Chuẩn đầu ra")
    SYLLABUS = "Syllabus", _("Đề cương chi tiết")


# ────────────────────────── Models ──────────────────────────


class ApprovalWorkflow(BaseModel):
    """
    Quy trình phê duyệt gắn với 1 entity (CTĐT, PLO, hoặc Đề cương).
    Mỗi entity có thể có nhiều workflows (nếu bị reject rồi submit lại).
    Chỉ 1 workflow active tại 1 thời điểm.
    """

    entity_type = models.CharField(
        max_length=50,
        choices=EntityType.choices,
        verbose_name=_("Loại đối tượng"),
    )
    entity_id = models.UUIDField(
        db_index=True,
        verbose_name=_("ID đối tượng"),
    )
    status = models.CharField(
        max_length=20,
        choices=WorkflowStatus.choices,
        default=WorkflowStatus.IN_PROGRESS,
        verbose_name=_("Trạng thái"),
    )
    current_step_number = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Bước hiện tại"),
    )
    total_steps = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Tổng số bước"),
    )
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="initiated_workflows",
        verbose_name=_("Người khởi tạo"),
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Thời gian hoàn thành"),
    )

    class Meta:
        verbose_name = _("Quy trình phê duyệt")
        verbose_name_plural = _("Quy trình phê duyệt")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["initiated_by", "-created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["entity_type", "entity_id"],
                condition=models.Q(status="IN_PROGRESS"),
                name="unique_active_workflow_per_entity",
            )
        ]

    @property
    def current_step(self):
        return self.steps.filter(step_number=self.current_step_number).first()

    @property
    def is_final_step(self):
        return self.current_step_number == self.total_steps

    def get_entity(self):
        """Resolve the actual entity object."""
        from hutech_program.programs.models import TrainingProgram

        model_map = {
            EntityType.TRAINING_PROGRAM: TrainingProgram,
        }
        model_class = model_map.get(self.entity_type)
        if model_class:
            return model_class.objects.filter(id=self.entity_id).first()
        return None

    def __str__(self) -> str:
        return f"Workflow {self.entity_type}:{self.entity_id} ({self.status})"


class ApprovalStep(BaseModel):
    """
    Một bước trong quy trình phê duyệt.
    Mỗi workflow có N steps (3 cho CTĐT/PLO, 4 cho Đề cương).
    """

    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name="steps",
        verbose_name=_("Quy trình"),
    )
    step_number = models.PositiveIntegerField(
        verbose_name=_("Số bước"),
    )
    step_name = models.CharField(
        max_length=100,
        verbose_name=_("Tên bước"),
    )
    required_role = models.ForeignKey(
        "rbac.Role",
        on_delete=models.PROTECT,
        verbose_name=_("Vai trò cần có"),
        help_text=_("Vai trò cần có để duyệt bước này"),
    )
    required_department_scope = models.BooleanField(
        default=True,
        verbose_name=_("Phạm vi đơn vị"),
        help_text=_(
            "True = phải cùng department với entity. "
            "False = cross-department (PDT, BGH)"
        ),
    )
    status = models.CharField(
        max_length=20,
        choices=StepStatus.choices,
        default=StepStatus.PENDING,
        verbose_name=_("Trạng thái"),
    )
    acted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_actions",
        verbose_name=_("Người thực hiện"),
    )
    acted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Thời gian xử lý"),
    )
    action_comment = models.TextField(
        blank=True,
        verbose_name=_("Nhận xét"),
    )
    # Optimistic locking
    version = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Phiên bản (locking)"),
    )

    class Meta:
        verbose_name = _("Bước phê duyệt")
        verbose_name_plural = _("Bước phê duyệt")
        ordering = ["step_number"]
        unique_together = ["workflow", "step_number"]
        indexes = [
            models.Index(fields=["status", "required_role"]),
        ]

    def __str__(self) -> str:
        return f"Step {self.step_number}: {self.step_name} ({self.status})"


class ApprovalComment(BaseModel):
    """
    Comment thread trên từng bước duyệt.
    Cho phép trao đổi giữa người duyệt và người nộp mà không cần reject.
    """

    step = models.ForeignKey(
        ApprovalStep,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("Bước"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Tác giả"),
    )
    content = models.TextField(verbose_name=_("Nội dung"))
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name=_("Phản hồi cho"),
    )

    class Meta:
        verbose_name = _("Bình luận phê duyệt")
        verbose_name_plural = _("Bình luận phê duyệt")
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.author} on step {self.step.step_number}"


class EntityVersion(BaseModel):
    """
    Snapshot toàn bộ dữ liệu entity tại thời điểm phê duyệt cuối.
    Sử dụng JSONB cho PostgreSQL.
    """

    entity_type = models.CharField(
        max_length=50,
        choices=EntityType.choices,
        verbose_name=_("Loại đối tượng"),
    )
    entity_id = models.UUIDField(verbose_name=_("ID đối tượng"))
    version_number = models.PositiveIntegerField(
        verbose_name=_("Số phiên bản"),
    )
    snapshot_data = models.JSONField(
        default=dict,
        verbose_name=_("Dữ liệu snapshot"),
        help_text=_("Full serialized entity data at approval time"),
    )
    change_summary = models.TextField(
        blank=True,
        verbose_name=_("Tóm tắt thay đổi"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Người tạo"),
    )
    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resulting_versions",
        verbose_name=_("Quy trình tạo phiên bản"),
    )

    class Meta:
        verbose_name = _("Phiên bản tài liệu")
        verbose_name_plural = _("Phiên bản tài liệu")
        ordering = ["-version_number"]
        unique_together = ["entity_type", "entity_id", "version_number"]
        indexes = [
            models.Index(
                fields=["entity_type", "entity_id", "-version_number"]
            ),
        ]

    def __str__(self) -> str:
        return f"{self.entity_type}:{self.entity_id} v{self.version_number}"


# ────────────────────── Legacy alias ──────────────────────
# Keep backward compatibility for existing code referencing ProgramVersion
ProgramVersion = EntityVersion
