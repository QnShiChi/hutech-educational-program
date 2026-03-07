"""
Import serializers.
"""

from rest_framework import serializers

from .models import ImportTask


class ImportTaskUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    department_id = serializers.UUIDField()

    def validate_file(self, value):
        if not value.name.endswith(".docx"):
            raise serializers.ValidationError("Chỉ chấp nhận file .docx")
        return value


class ImportTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportTask
        fields = [
            "id", "file_name", "status", "progress",
            "result", "error_message", "program",
            "uploaded_by", "created_at",
        ]
        read_only_fields = fields


class ImportTaskPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportTask
        fields = [
            "id", "file_name", "status", "parsed_data", "result",
        ]
        read_only_fields = fields
