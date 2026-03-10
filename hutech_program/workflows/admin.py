"""
Workflow admin registration.

All workflow admin classes are readonly — workflows must be created
and transitioned via the service layer (WorkflowService).
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import ApprovalComment, ApprovalStep, ApprovalWorkflow, EntityVersion


# ────────────────────── Inlines ──────────────────────


class ApprovalStepInline(admin.TabularInline):
    model = ApprovalStep
    extra = 0
    can_delete = False
    readonly_fields = [
        "step_number",
        "step_name",
        "required_role",
        "status",
        "acted_by",
        "acted_at",
        "action_comment",
        "version",
    ]

    def has_add_permission(self, request, obj=None):
        return False


class ApprovalCommentInline(admin.TabularInline):
    model = ApprovalComment
    extra = 0
    can_delete = False
    readonly_fields = ["author", "content", "parent", "created_at"]

    def has_add_permission(self, request, obj=None):
        return False


# ────────────────────── Main Admins ──────────────────────


@admin.register(ApprovalWorkflow)
class ApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = [
        "entity_type",
        "entity_display",
        "status",
        "step_progress",
        "initiated_by",
        "created_at",
        "completed_at",
    ]
    list_filter = [
        "status",
        "entity_type",
        ("created_at", admin.DateFieldListFilter),
    ]
    search_fields = [
        "entity_id",
        "initiated_by__name",
        "initiated_by__email",
    ]
    readonly_fields = [
        "entity_type",
        "entity_id",
        "status",
        "current_step_number",
        "total_steps",
        "initiated_by",
        "completed_at",
        "created_at",
        "updated_at",
    ]
    inlines = [ApprovalStepInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description=_("Đối tượng"))
    def entity_display(self, obj):
        """Resolve entity name from get_entity(), fallback to UUID."""
        entity = obj.get_entity()
        if entity:
            return str(entity)
        return str(obj.entity_id)

    @admin.display(description=_("Tiến độ"))
    def step_progress(self, obj):
        """Display step progress as 'current/total'."""
        return f"{obj.current_step_number}/{obj.total_steps}"


@admin.register(EntityVersion)
class EntityVersionAdmin(admin.ModelAdmin):
    list_display = [
        "entity_type",
        "entity_id",
        "version_number",
        "change_summary",
        "created_by",
        "created_at",
    ]
    list_filter = ["entity_type"]
    search_fields = ["entity_id"]
    readonly_fields = [
        "entity_type",
        "entity_id",
        "version_number",
        "snapshot_data",
        "change_summary",
        "created_by",
        "workflow",
        "created_at",
        "updated_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ApprovalComment)
class ApprovalCommentAdmin(admin.ModelAdmin):
    list_display = ["step", "author", "content_preview", "created_at"]
    list_filter = ["step__workflow__entity_type"]
    search_fields = ["content", "author__name", "author__email"]
    readonly_fields = [
        "step",
        "author",
        "content",
        "parent",
        "created_at",
        "updated_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description=_("Nội dung"))
    def content_preview(self, obj):
        """Show first 100 chars of comment content."""
        if len(obj.content) > 100:
            return obj.content[:100] + "…"
        return obj.content
