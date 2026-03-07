from django.contrib import admin

from .models import (
    AuditLog,
    Department,
    Permission,
    Role,
    RolePermission,
    UserRole,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "type", "parent", "is_active", "created_at"]
    list_filter = ["type", "is_active"]
    search_fields = ["name", "code", "name_en"]
    list_editable = ["is_active"]
    raw_id_fields = ["parent"]


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1
    raw_id_fields = ["permission"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "level", "is_system", "created_at"]
    list_filter = ["is_system", "level"]
    search_fields = ["code", "name"]
    inlines = [RolePermissionInline]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "module"]
    list_filter = ["module"]
    search_fields = ["code", "name"]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "department", "assigned_by", "created_at"]
    list_filter = ["role", "department"]
    search_fields = ["user__username", "user__name", "role__code", "department__code"]
    raw_id_fields = ["user", "assigned_by"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "user", "action", "entity_type", "entity_id"]
    list_filter = ["action", "entity_type", "created_at"]
    search_fields = ["entity_type", "user__username"]
    readonly_fields = [
        "user",
        "action",
        "entity_type",
        "entity_id",
        "old_data",
        "new_data",
        "ip_address",
        "user_agent",
        "created_at",
    ]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
