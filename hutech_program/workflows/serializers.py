"""
Workflow & Version serializers.
"""

from rest_framework import serializers

from .models import ApprovalStep, ApprovalWorkflow, ProgramVersion


class ApprovalStepSerializer(serializers.ModelSerializer):
    approver_role_code = serializers.CharField(
        source="approver_role.code", read_only=True
    )
    approver_name = serializers.CharField(
        source="approver.name", read_only=True, default=None
    )

    class Meta:
        model = ApprovalStep
        fields = [
            "id", "step_number", "step_name",
            "approver_role", "approver_role_code",
            "approver", "approver_name",
            "status", "comment", "acted_at",
        ]
        read_only_fields = fields


class ApprovalWorkflowSerializer(serializers.ModelSerializer):
    steps = ApprovalStepSerializer(many=True, read_only=True)
    initiated_by_name = serializers.CharField(
        source="initiated_by.name", read_only=True
    )

    class Meta:
        model = ApprovalWorkflow
        fields = [
            "id", "entity_type", "entity_id",
            "current_step", "status",
            "initiated_by", "initiated_by_name",
            "steps", "created_at", "updated_at",
        ]
        read_only_fields = fields


class WorkflowActionSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True, default="")


class ProgramVersionListSerializer(serializers.ModelSerializer):
    approved_by_name = serializers.CharField(
        source="approved_by.name", read_only=True, default=None
    )

    class Meta:
        model = ProgramVersion
        fields = [
            "id", "version_number", "change_summary",
            "approved_by", "approved_by_name",
            "created_at",
        ]
        read_only_fields = fields


class ProgramVersionDetailSerializer(serializers.ModelSerializer):
    approved_by_name = serializers.CharField(
        source="approved_by.name", read_only=True, default=None
    )

    class Meta:
        model = ProgramVersion
        fields = [
            "id", "version_number", "snapshot_data",
            "change_summary", "approved_by", "approved_by_name",
            "created_at",
        ]
        read_only_fields = fields
