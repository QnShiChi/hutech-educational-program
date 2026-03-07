"""
RBAC serializers.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    AuditLog,
    Department,
    Permission,
    Role,
    RolePermission,
    UserRole,
)

User = get_user_model()


# ────────────────── Department ──────────────────


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            "id",
            "code",
            "name",
            "name_en",
            "type",
            "parent",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DepartmentTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            "id",
            "code",
            "name",
            "name_en",
            "type",
            "is_active",
            "children",
        ]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return DepartmentTreeSerializer(children, many=True).data


# ────────────────── Permission ──────────────────


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "code", "name", "module", "description"]
        read_only_fields = ["id"]


# ────────────────── Role ──────────────────


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="permissions",
    )

    class Meta:
        model = Role
        fields = [
            "id",
            "code",
            "name",
            "description",
            "level",
            "is_system",
            "permissions",
            "permission_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        permissions = validated_data.pop("permissions", [])
        role = Role.objects.create(**validated_data)
        if permissions:
            for perm in permissions:
                RolePermission.objects.create(role=role, permission=perm)
        return role

    def update(self, instance, validated_data):
        permissions = validated_data.pop("permissions", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if permissions is not None:
            instance.rolepermission_set.all().delete()
            for perm in permissions:
                RolePermission.objects.create(role=instance, permission=perm)
        return instance


# ────────────────── UserRole ──────────────────


class UserRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = UserRole
        fields = [
            "id",
            "user",
            "role",
            "role_name",
            "department",
            "department_name",
            "assigned_by",
            "created_at",
        ]
        read_only_fields = ["id", "assigned_by", "created_at"]


class AssignRoleSerializer(serializers.Serializer):
    """Serializer for assigning a role to a user."""

    role_id = serializers.UUIDField()
    department_id = serializers.UUIDField()

    def validate_role_id(self, value):
        try:
            Role.objects.get(pk=value)
        except Role.DoesNotExist:
            raise serializers.ValidationError("Role not found.")
        return value

    def validate_department_id(self, value):
        try:
            Department.objects.get(pk=value)
        except Department.DoesNotExist:
            raise serializers.ValidationError("Department not found.")
        return value


# ────────────────── User ──────────────────


class UserListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.name", read_only=True, default=None
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "email",
            "employee_id",
            "phone",
            "department",
            "department_name",
            "is_active",
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.name", read_only=True, default=None
    )
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "email",
            "employee_id",
            "phone",
            "department",
            "department_name",
            "is_active",
            "roles",
            "permissions",
        ]

    def get_roles(self, obj):
        return UserRoleSerializer(obj.user_roles.select_related("role", "department"), many=True).data

    def get_permissions(self, obj):
        from hutech_program.rbac.mixins import get_user_permissions
        return sorted(get_user_permissions(obj))


# ────────────────── AuditLog ──────────────────


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True, default=None)
    user_username = serializers.CharField(source="user.username", read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "user_name",
            "user_username",
            "action",
            "entity_type",
            "entity_id",
            "old_data",
            "new_data",
            "ip_address",
            "created_at",
        ]
        read_only_fields = fields
