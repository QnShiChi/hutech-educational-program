"""
Notification serializers.
"""

from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "title", "message", "link",
            "is_read", "created_at",
        ]
        read_only_fields = ["id", "title", "message", "link", "created_at"]


class UnreadCountSerializer(serializers.Serializer):
    count = serializers.IntegerField()
