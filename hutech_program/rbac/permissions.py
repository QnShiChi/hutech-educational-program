"""
DRF permission classes for RBAC.
"""

from rest_framework.permissions import BasePermission


class HasModulePermission(BasePermission):
    """
    Module-level permission check.

    Usage on ViewSet:
        permission_classes = [HasModulePermission]
        required_permission = "programs.create"

    Or per-action:
        permission_map = {
            "create": "programs.create",
            "list": "programs.view",
            "update": "programs.edit",
            "destroy": "programs.delete",
        }
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # Superusers bypass all checks
        if user.is_superuser:
            return True

        # ADMIN role bypasses all checks
        if user.user_roles.filter(role__code="ADMIN").exists():
            return True

        perm_code = self._get_required_permission(view)
        if not perm_code:
            return True  # No permission required for this action

        return user.user_roles.filter(
            role__permissions__code=perm_code
        ).exists()

    def _get_required_permission(self, view):
        """Resolve the permission code for the current action."""
        # Per-action permission map
        perm_map = getattr(view, "permission_map", None)
        if perm_map:
            action = getattr(view, "action", None)
            if action and action in perm_map:
                return perm_map[action]

        # Single permission for all actions
        return getattr(view, "required_permission", None)


class DepartmentScopedPermission(HasModulePermission):
    """
    Object-level permission check scoped to department.
    Cross-department access only for PHONG_DAO_TAO and ADMIN roles.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser:
            return True

        # Get the department of the object
        obj_department = getattr(
            obj,
            "managing_department",
            getattr(obj, "department", None),
        )

        if not obj_department:
            return True

        # Phòng ĐT and Admin can access all departments
        if user.user_roles.filter(
            role__code__in=["PHONG_DAO_TAO", "ADMIN"]
        ).exists():
            return True

        # Others can only access their own department's objects
        return user.user_roles.filter(department=obj_department).exists()
