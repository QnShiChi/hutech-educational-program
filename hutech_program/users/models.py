import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model cho HUTECH Program.
    Mở rộng từ AbstractUser với UUID primary key và thông tin nhân viên.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    # Cookiecutter default: dùng name thay cho first_name/last_name
    name = models.CharField(_("Tên người dùng"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    # Thông tin nhân viên HUTECH
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("Mã nhân viên"),
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_("Số điện thoại"),
    )
    department = models.ForeignKey(
        "rbac.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Đơn vị"),
        related_name="users",
    )

    class Meta:
        verbose_name = _("Người dùng")
        verbose_name_plural = _("Người dùng")

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view."""
        return reverse("users:detail", kwargs={"username": self.username})

    def has_perm_code(self, code: str) -> bool:
        """Check if user has a specific RBAC permission code."""
        if self.is_superuser:
            return True
        return self.user_roles.filter(role__permissions__code=code).exists()
