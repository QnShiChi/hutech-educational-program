"""
Workflow URL routing.
"""

from django.urls import path

from . import views

# These are included under /api/v1/programs/{program_pk}/ via program urls
workflow_nested = [
    path(
        "submit/",
        views.WorkflowActionViewSet.as_view({"post": "submit"}),
    ),
    path(
        "approve/",
        views.WorkflowActionViewSet.as_view({"post": "approve"}),
    ),
    path(
        "reject/",
        views.WorkflowActionViewSet.as_view({"post": "reject"}),
    ),
    path(
        "workflow/",
        views.WorkflowActionViewSet.as_view({"get": "workflow_status"}),
    ),
    path(
        "workflow-history/",
        views.WorkflowActionViewSet.as_view({"get": "workflow_history"}),
    ),
    path(
        "versions/",
        views.EntityVersionViewSet.as_view({"get": "list"}),
    ),
    path(
        "versions/compare/",
        views.EntityVersionViewSet.as_view({"get": "compare"}),
    ),
    path(
        "versions/<uuid:pk>/",
        views.EntityVersionViewSet.as_view({"get": "retrieve"}),
    ),
    path(
        "versions/<uuid:pk>/rollback/",
        views.EntityVersionViewSet.as_view({"post": "rollback"}),
    ),
]

# Workflow comment URLs
comment_urls = [
    path(
        "workflows/<uuid:workflow_id>/steps/<uuid:step_id>/comments/",
        views.ApprovalCommentViewSet.as_view({"get": "list", "post": "create"}),
    ),
]

# Notification URLs
notification_urls = [
    path(
        "notifications/",
        views.NotificationViewSet.as_view({"get": "list"}),
    ),
    path(
        "notifications/unread-count/",
        views.NotificationViewSet.as_view({"get": "unread_count"}),
    ),
    path(
        "notifications/<uuid:pk>/",
        views.NotificationViewSet.as_view({"patch": "partial_update"}),
    ),
    path(
        "notifications/mark-all-read/",
        views.NotificationViewSet.as_view({"post": "mark_all_read"}),
    ),
]

# Top-level workflow URLs
urlpatterns = [
    path(
        "pending/",
        views.PendingApprovalsViewSet.as_view({"get": "list"}),
    ),
] + comment_urls + notification_urls
