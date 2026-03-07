"""
Import models: ImportTask for tracking async import jobs.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from hutech_program.common import BaseModel


class ImportStatus(models.TextChoices):
    PENDING = "PENDING", _("Chờ xử lý")
    PROCESSING = "PROCESSING", _("Đang xử lý")
    PREVIEW = "PREVIEW", _("Xem trước")
    COMPLETED = "COMPLETED", _("Hoàn thành")
    FAILED = "FAILED", _("Thất bại")


class ImportTask(BaseModel):
    """
    Track an async import job.
    Stores parsed data, progress, and results.
    """

    file_name = models.CharField(
        max_length=200,
        verbose_name=_("Tên file"),
    )
    file = models.FileField(
        upload_to="imports/%Y/%m/",
        verbose_name=_("File upload"),
    )
    department = models.ForeignKey(
        "rbac.Department",
        on_delete=models.CASCADE,
        verbose_name=_("Khoa"),
    )
    status = models.CharField(
        max_length=20,
        choices=ImportStatus.choices,
        default=ImportStatus.PENDING,
        verbose_name=_("Trạng thái"),
    )
    progress = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Tiến độ (%)"),
    )
    parsed_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("Dữ liệu đã phân tích"),
    )
    result = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("Kết quả"),
        help_text=_("{program_id, warnings, errors}"),
    )
    program = models.ForeignKey(
        "programs.TrainingProgram",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="import_tasks",
        verbose_name=_("CTĐT đã tạo"),
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="import_tasks",
        verbose_name=_("Người upload"),
    )
    error_message = models.TextField(
        blank=True,
        verbose_name=_("Thông báo lỗi"),
    )

    class Meta:
        verbose_name = _("Tác vụ import")
        verbose_name_plural = _("Tác vụ import")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.file_name} ({self.status})"
