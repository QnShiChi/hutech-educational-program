"""
Workflow admin registration.
"""

from django.contrib import admin

from .models import ApprovalStep, ApprovalWorkflow, ProgramVersion


class ApprovalStepInline(admin.TabularInline):
    model = ApprovalStep
    extra = 0
    readonly_fields = ["acted_at"]


@admin.register(ApprovalWorkflow)
class ApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ["entity_type", "entity_id", "status", "current_step", "initiated_by", "created_at"]
    list_filter = ["status", "entity_type"]
    search_fields = ["entity_id"]
    inlines = [ApprovalStepInline]


@admin.register(ProgramVersion)
class ProgramVersionAdmin(admin.ModelAdmin):
    list_display = ["program", "version_number", "approved_by", "created_at"]
    list_filter = ["program"]
    readonly_fields = ["snapshot_data"]
