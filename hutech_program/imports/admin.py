"""
Import admin registration.
"""

from django.contrib import admin

from .models import ImportTask


@admin.register(ImportTask)
class ImportTaskAdmin(admin.ModelAdmin):
    list_display = ["file_name", "status", "progress", "department", "uploaded_by", "created_at"]
    list_filter = ["status"]
    search_fields = ["file_name"]
    readonly_fields = ["parsed_data", "result"]
