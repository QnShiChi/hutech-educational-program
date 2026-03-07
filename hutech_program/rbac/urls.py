"""
RBAC URL routing.
"""

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("departments", views.DepartmentViewSet, basename="department")
router.register("roles", views.RoleViewSet, basename="role")
router.register("permissions", views.PermissionViewSet, basename="permission")
router.register("users", views.RBACUserViewSet, basename="rbac-user")
router.register("audit-logs", views.AuditLogViewSet, basename="auditlog")

urlpatterns = router.urls
