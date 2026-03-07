"""
Programs URL routing with nested resources.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from hutech_program.workflows.urls import workflow_nested

router = DefaultRouter()
router.register("", views.TrainingProgramViewSet, basename="program")

# Course management (top-level)
course_router = DefaultRouter()
course_router.register("courses", views.CourseViewSet, basename="course")
course_router.register("course-groups", views.CourseGroupViewSet, basename="course-group")

# Nested routes under program
program_nested = [
    path(
        "objectives/",
        views.ProgramObjectiveViewSet.as_view(
            {"get": "list", "post": "create"}
        ),
    ),
    path(
        "objectives/reorder/",
        views.ProgramObjectiveViewSet.as_view({"post": "reorder"}),
    ),
    path(
        "objectives/<uuid:pk>/",
        views.ProgramObjectiveViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
    ),
    path(
        "plos/",
        views.PLOViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "plos/reorder/",
        views.PLOViewSet.as_view({"post": "reorder"}),
    ),
    path(
        "plos/<uuid:plo_pk>/",
        views.PLOViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
    ),
    path(
        "plos/<uuid:plo_pk>/pis/",
        views.PerformanceIndicatorViewSet.as_view(
            {"get": "list", "post": "create"}
        ),
    ),
    path(
        "plos/<uuid:plo_pk>/pis/<uuid:pk>/",
        views.PerformanceIndicatorViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
    ),
    path(
        "po-plo-matrix/",
        views.POPLOMatrixView.as_view({"get": "retrieve", "put": "update"}),
    ),
    path(
        "knowledge-blocks/",
        views.KnowledgeBlockViewSet.as_view(
            {"get": "list", "post": "create"}
        ),
    ),
    path(
        "knowledge-blocks/<uuid:pk>/",
        views.KnowledgeBlockViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
    ),
    # Course management (nested under program)
    path(
        "courses/",
        views.ProgramCourseViewSet.as_view(
            {"get": "list", "post": "create"}
        ),
    ),
    path(
        "courses/bulk/",
        views.ProgramCourseViewSet.as_view({"post": "bulk_add"}),
    ),
    path(
        "courses/<uuid:pk>/",
        views.ProgramCourseViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
    ),
    path(
        "prerequisites/",
        views.PrerequisiteView.as_view({"get": "retrieve", "put": "update"}),
    ),
    path(
        "semester-plan/",
        views.SemesterPlanView.as_view({"get": "retrieve", "put": "update"}),
    ),
    # HP-PLO-PI Matrix
    path(
        "course-plo-matrix/",
        views.CoursePLOMatrixView.as_view({"get": "retrieve", "put": "update"}),
    ),
    # PLO Assessment Plan
    path(
        "assessment-plans/",
        views.PLOAssessmentPlanViewSet.as_view(
            {"get": "list", "post": "create"}
        ),
    ),
    path(
        "assessment-plans/bulk/",
        views.PLOAssessmentPlanViewSet.as_view({"post": "bulk_upsert"}),
    ),
    path(
        "assessment-plans/<uuid:pk>/",
        views.PLOAssessmentPlanViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
    ),
    # PLO Coverage Validation
    path(
        "plo-coverage-validation/",
        views.PLOCoverageValidationView.as_view({"get": "retrieve"}),
    ),
]

urlpatterns = [
    *course_router.urls,
    *router.urls,
    path("<uuid:program_pk>/", include(program_nested + workflow_nested)),
]

