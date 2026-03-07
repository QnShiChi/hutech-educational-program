"""
RBAC ViewSets.
"""

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .mixins import AuditLogMixin
from .models import AuditLog, Department, Permission, Role, UserRole
from .permissions import HasModulePermission
from .serializers import (
    AssignRoleSerializer,
    AuditLogSerializer,
    DepartmentSerializer,
    DepartmentTreeSerializer,
    PermissionSerializer,
    RoleSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserRoleSerializer,
)

User = get_user_model()


class DepartmentViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """CRUD + tree endpoint for departments."""

    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "list": None,
        "retrieve": None,
        "tree": None,
        "create": "rbac.manage_departments",
        "update": "rbac.manage_departments",
        "partial_update": "rbac.manage_departments",
        "destroy": "rbac.manage_departments",
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["type", "is_active", "parent"]
    search_fields = ["name", "code", "name_en"]
    ordering_fields = ["code", "name", "created_at"]

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """Return departments as a nested tree (only root nodes)."""
        roots = Department.objects.filter(parent__isnull=True, is_active=True)
        serializer = DepartmentTreeSerializer(roots, many=True)
        return Response(serializer.data)


class RoleViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """CRUD for roles + permissions sub-resource."""

    queryset = Role.objects.prefetch_related("permissions")
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "list": None,
        "retrieve": None,
        "create": "rbac.manage_roles",
        "update": "rbac.manage_roles",
        "partial_update": "rbac.manage_roles",
        "destroy": "rbac.manage_roles",
    }
    filter_backends = [filters.SearchFilter]
    search_fields = ["code", "name"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_system:
            return Response(
                {"detail": "Không thể xóa vai trò hệ thống."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    def permissions(self, request, pk=None):
        """Get permissions for a specific role."""
        role = self.get_object()
        serializer = PermissionSerializer(role.permissions.all(), many=True)
        return Response(serializer.data)


class PermissionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """List-only view for permissions (filterable by module)."""

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["module"]
    search_fields = ["code", "name"]


class RBACUserViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """User management with role assignment."""

    queryset = User.objects.select_related("department").prefetch_related(
        "user_roles__role", "user_roles__department"
    )
    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "list": "rbac.manage_users",
        "retrieve": "rbac.manage_users",
        "create": "rbac.manage_users",
        "update": "rbac.manage_users",
        "partial_update": "rbac.manage_users",
        "destroy": "rbac.manage_users",
        "me": None,
        "assign_role": "rbac.manage_users",
        "remove_role": "rbac.manage_users",
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active", "department"]
    search_fields = ["username", "name", "email", "employee_id"]
    ordering_fields = ["username", "name", "date_joined"]

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserDetailSerializer

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Current user profile with roles and permissions."""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="assign-role")
    def assign_role(self, request, pk=None):
        """Assign a role to a user in a specific department."""
        user = self.get_object()
        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = Role.objects.get(pk=serializer.validated_data["role_id"])
        department = Department.objects.get(pk=serializer.validated_data["department_id"])

        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            department=department,
            defaults={"assigned_by": request.user},
        )

        if not created:
            return Response(
                {"detail": "Người dùng đã có vai trò này trong đơn vị này."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            UserRoleSerializer(user_role).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["delete"],
        url_path="roles/(?P<role_pk>[^/.]+)",
    )
    def remove_role(self, request, pk=None, role_pk=None):
        """Remove a role from a user."""
        user = self.get_object()
        deleted, _ = UserRole.objects.filter(user=user, role_id=role_pk).delete()
        if not deleted:
            return Response(
                {"detail": "Không tìm thấy vai trò này cho người dùng."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuditLogViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Read-only audit logs with filtering."""

    queryset = AuditLog.objects.select_related("user")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    required_permission = "rbac.view_audit_logs"
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["action", "entity_type", "user"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
