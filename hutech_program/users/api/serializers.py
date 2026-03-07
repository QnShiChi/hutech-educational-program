from rest_framework import serializers

from hutech_program.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer cho User model."""

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
            "is_active",
        ]
        read_only_fields = ["id"]
