"""
Notification model for system-wide notifications.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from hutech_program.common import BaseModel


class Notification(BaseModel):
    """
    Thông báo cho người dùng.
    Được tạo tự động khi submit, approve, reject CTĐT.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Người nhận"),
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Tiêu đề"),
    )
    message = models.TextField(
        verbose_name=_("Nội dung"),
    )
    link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Liên kết"),
    )
    category = models.CharField(
        max_length=30,
        default="WORKFLOW",
        verbose_name=_("Loại thông báo"),
        help_text=_("WORKFLOW, COURSE_CHANGE, SYSTEM, REMINDER"),
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_("Đã đọc"),
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Thời gian đọc"),
    )

    class Meta:
        verbose_name = _("Thông báo")
        verbose_name_plural = _("Thông báo")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"[{'✓' if self.is_read else '○'}] {self.title}"
