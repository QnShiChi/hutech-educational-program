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
        "versions/",
        views.ProgramVersionViewSet.as_view({"get": "list"}),
    ),
    path(
        "versions/compare/",
        views.ProgramVersionViewSet.as_view({"get": "compare"}),
    ),
    path(
        "versions/<uuid:pk>/",
        views.ProgramVersionViewSet.as_view({"get": "retrieve"}),
    ),
    path(
        "versions/<uuid:pk>/rollback/",
        views.ProgramVersionViewSet.as_view({"post": "rollback"}),
    ),
]

# Top-level workflow URLs
urlpatterns = [
    path(
        "pending/",
        views.PendingApprovalsViewSet.as_view({"get": "list"}),
    ),
]
