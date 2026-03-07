"""
RBAC models: Department, Role, Permission, UserRole, AuditLog.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from hutech_program.common import BaseModel, UUIDModel


# ────────────────────────── Choices ──────────────────────────


class DepartmentType(models.TextChoices):
    KHOA = "KHOA", _("Khoa")
    VIEN = "VIEN", _("Viện")
    PHONG = "PHONG", _("Phòng")
    TRUNG_TAM = "TRUNG_TAM", _("Trung tâm")
    BAN_GIAM_HIEU = "BAN_GIAM_HIEU", _("Ban Giám Hiệu")


class PermissionModule(models.TextChoices):
    PROGRAMS = "programs", _("Chương trình đào tạo")
    PLO = "plo", _("Chuẩn đầu ra")
    SYLLABUS = "syllabus", _("Đề cương chi tiết")
    COURSES = "courses", _("Học phần")
    RBAC = "rbac", _("Quản trị hệ thống")


class AuditAction(models.TextChoices):
    CREATE = "CREATE", _("Tạo mới")
    UPDATE = "UPDATE", _("Cập nhật")
    DELETE = "DELETE", _("Xóa")
    SUBMIT = "SUBMIT", _("Nộp duyệt")
    APPROVE = "APPROVE", _("Phê duyệt")
    REJECT = "REJECT", _("Từ chối")
    ROLLBACK = "ROLLBACK", _("Quay lại phiên bản")


# ────────────────────────── Models ──────────────────────────


class Department(BaseModel):
    """
    Đơn vị / Khoa / Viện.
    Hỗ trợ cấu trúc phân cấp (self-referencing parent).
    """

    code = models.CharField(
        max_length=20, unique=True, verbose_name=_("Mã đơn vị")
    )
    name = models.CharField(max_length=200, verbose_name=_("Tên đơn vị"))
    name_en = models.CharField(
        max_length=200, blank=True, verbose_name=_("Tên tiếng Anh")
    )
    type = models.CharField(
        max_length=20,
        choices=DepartmentType.choices,
        default=DepartmentType.KHOA,
        verbose_name=_("Loại đơn vị"),
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Đơn vị cha"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Hoạt động"))

    class Meta:
        verbose_name = _("Đơn vị")
        verbose_name_plural = _("Đơn vị")
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["type"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Permission(UUIDModel):
    """
    Quyền hạn trong hệ thống, theo format {module}.{action}.
    """

    code = models.CharField(
        max_length=50, unique=True, verbose_name=_("Mã quyền")
    )
    name = models.CharField(max_length=100, verbose_name=_("Tên quyền"))
    module = models.CharField(
        max_length=20,
        choices=PermissionModule.choices,
        verbose_name=_("Module"),
    )
    description = models.TextField(blank=True, verbose_name=_("Mô tả"))

    class Meta:
        verbose_name = _("Quyền")
        verbose_name_plural = _("Quyền")
        ordering = ["module", "code"]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Role(BaseModel):
    """
    Vai trò trong hệ thống (GIANG_VIEN, TRUONG_NGANH, ...).
    """

    code = models.CharField(
        max_length=30, unique=True, verbose_name=_("Mã vai trò")
    )
    name = models.CharField(max_length=100, verbose_name=_("Tên vai trò"))
    description = models.TextField(blank=True, verbose_name=_("Mô tả"))
    level = models.IntegerField(
        default=0,
        verbose_name=_("Cấp bậc"),
        help_text=_("Thứ tự trong hệ thống phê duyệt"),
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name=_("Vai trò hệ thống"),
        help_text=_("Vai trò hệ thống không thể xóa"),
    )
    permissions = models.ManyToManyField(
        Permission,
        through="RolePermission",
        blank=True,
        related_name="roles",
        verbose_name=_("Quyền hạn"),
    )

    class Meta:
        verbose_name = _("Vai trò")
        verbose_name_plural = _("Vai trò")
        ordering = ["level"]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class RolePermission(models.Model):
    """
    Bảng trung gian Role ↔ Permission.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, verbose_name=_("Vai trò")
    )
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, verbose_name=_("Quyền")
    )

    class Meta:
        verbose_name = _("Quyền của vai trò")
        verbose_name_plural = _("Quyền của vai trò")
        unique_together = ["role", "permission"]

    def __str__(self) -> str:
        return f"{self.role.code} → {self.permission.code}"


class UserRole(BaseModel):
    """
    Gán vai trò cho người dùng, scoped theo đơn vị.
    Một user có thể có nhiều role trong nhiều đơn vị khác nhau.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name=_("Người dùng"),
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name=_("Vai trò"),
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name=_("Đơn vị"),
        help_text=_("Vai trò này có hiệu lực trong đơn vị nào"),
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_roles",
        verbose_name=_("Người gán"),
    )

    class Meta:
        verbose_name = _("Vai trò người dùng")
        verbose_name_plural = _("Vai trò người dùng")
        unique_together = ["user", "role", "department"]
        indexes = [
            models.Index(fields=["user", "role"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.role.code} @ {self.department.code}"


class AuditLog(UUIDModel):
    """
    Ghi lại mọi thay đổi trạng thái trong hệ thống.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Người thực hiện"),
    )
    action = models.CharField(
        max_length=20,
        choices=AuditAction.choices,
        verbose_name=_("Hành động"),
    )
    entity_type = models.CharField(
        max_length=50, verbose_name=_("Loại đối tượng")
    )
    entity_id = models.UUIDField(verbose_name=_("ID đối tượng"))
    old_data = models.JSONField(
        null=True, blank=True, verbose_name=_("Dữ liệu cũ")
    )
    new_data = models.JSONField(
        null=True, blank=True, verbose_name=_("Dữ liệu mới")
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name=_("Địa chỉ IP")
    )
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Thời gian")
    )

    class Meta:
        verbose_name = _("Nhật ký")
        verbose_name_plural = _("Nhật ký")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.entity_type}:{self.entity_id}"
