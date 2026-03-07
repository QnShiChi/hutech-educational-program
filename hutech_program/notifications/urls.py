"""
Notification URL routing.
"""

from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.NotificationViewSet.as_view({"get": "list"}),
    ),
    path(
        "read-all/",
        views.NotificationViewSet.as_view({"post": "read_all"}),
    ),
    path(
        "unread-count/",
        views.NotificationViewSet.as_view({"get": "unread_count"}),
    ),
    path(
        "<uuid:pk>/",
        views.NotificationViewSet.as_view({"get": "retrieve"}),
    ),
    path(
        "<uuid:pk>/read/",
        views.NotificationViewSet.as_view({"put": "mark_read"}),
    ),
]
