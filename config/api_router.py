from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from hutech_program.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)

app_name = "api"
urlpatterns = [
    *router.urls,
    path("rbac/", include("hutech_program.rbac.urls")),
    path("programs/", include("hutech_program.programs.urls")),
    path("workflows/", include("hutech_program.workflows.urls")),
    path("notifications/", include("hutech_program.notifications.urls")),
    path("imports/", include("hutech_program.imports.urls")),
]

