"""
Workflow & Version serializers.
"""

from rest_framework import serializers

from hutech_program.notifications.models import Notification

from .models import (
    ApprovalComment,
    ApprovalStep,
    ApprovalWorkflow,
    EntityVersion,
)


class ApprovalCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(
        source="author.name", read_only=True
    )

    class Meta:
        model = ApprovalComment
        fields = [
            "id", "author", "author_name",
            "content", "parent", "created_at",
        ]
        read_only_fields = ["id", "author", "author_name", "created_at"]


class ApprovalCommentCreateSerializer(serializers.Serializer):
    content = serializers.CharField()
    parent_id = serializers.UUIDField(required=False, allow_null=True)


class ApprovalStepSerializer(serializers.ModelSerializer):
    required_role_code = serializers.CharField(
        source="required_role.code", read_only=True
    )
    required_role_name = serializers.CharField(
        source="required_role.name", read_only=True
    )
    acted_by_name = serializers.CharField(
        source="acted_by.name", read_only=True, default=None
    )
    comments = ApprovalCommentSerializer(many=True, read_only=True)

    class Meta:
        model = ApprovalStep
        fields = [
            "id", "step_number", "step_name",
            "required_role", "required_role_code", "required_role_name",
            "required_department_scope",
            "status",
            "acted_by", "acted_by_name", "acted_at", "action_comment",
            "comments",
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
            "status", "current_step_number", "total_steps",
            "initiated_by", "initiated_by_name",
            "completed_at",
            "steps", "created_at", "updated_at",
        ]
        read_only_fields = fields


class WorkflowActionSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True, default="")


class SubmitSerializer(serializers.Serializer):
    """Empty serializer for submit action."""
    pass


class ApproveSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True, default="")


class RejectSerializer(serializers.Serializer):
    comment = serializers.CharField(
        required=True,
        min_length=10,
        error_messages={
            "required": "Vui lòng nhập lý do từ chối",
            "blank": "Vui lòng nhập lý do từ chối",
            "min_length": "Lý do từ chối phải có ít nhất 10 ký tự",
        },
    )


class EntityVersionListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.name", read_only=True, default=None
    )

    class Meta:
        model = EntityVersion
        fields = [
            "id", "entity_type", "entity_id",
            "version_number", "change_summary",
            "created_by", "created_by_name",
            "created_at",
        ]
        read_only_fields = fields


class EntityVersionDetailSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.name", read_only=True, default=None
    )

    class Meta:
        model = EntityVersion
        fields = [
            "id", "entity_type", "entity_id",
            "version_number", "snapshot_data",
            "change_summary",
            "created_by", "created_by_name",
            "created_at",
        ]
        read_only_fields = fields


class VersionComparisonSerializer(serializers.Serializer):
    v1 = serializers.IntegerField()
    v2 = serializers.IntegerField()
    changes = serializers.DictField()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "title", "message", "link",
            "category", "is_read", "read_at",
            "created_at",
        ]
        read_only_fields = [
            "id", "title", "message", "link",
            "category", "read_at", "created_at",
        ]


class PendingApprovalSerializer(serializers.Serializer):
    entity_type = serializers.CharField()
    entity_id = serializers.UUIDField()
    entity_name = serializers.CharField()
    submitted_by = serializers.CharField()
    submitted_at = serializers.DateTimeField()
    days_waiting = serializers.IntegerField()
    department_name = serializers.CharField(allow_null=True)
    step_name = serializers.CharField()


# Legacy backward-compat aliases
ProgramVersionListSerializer = EntityVersionListSerializer
ProgramVersionDetailSerializer = EntityVersionDetailSerializer
