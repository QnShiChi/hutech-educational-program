"""
Notification admin registration.
"""

from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "is_read", "created_at"]
    list_filter = ["is_read"]
    search_fields = ["title", "message"]
    readonly_fields = ["user", "title", "message", "link", "created_at"]
