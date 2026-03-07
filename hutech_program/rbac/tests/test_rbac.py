"""
Tests for RBAC module: models, permissions, API endpoints, seed command.
"""

import uuid

import pytest
from django.core.management import call_command
from django.test import RequestFactory
from rest_framework.test import APIClient

from hutech_program.rbac.mixins import get_user_permissions
from hutech_program.rbac.models import (
    AuditLog,
    Department,
    DepartmentType,
    Permission,
    Role,
    RolePermission,
    UserRole,
)

from .factories import (
    AuditLogFactory,
    DepartmentFactory,
    PermissionFactory,
    RoleFactory,
    RolePermissionFactory,
    UserFactory,
    UserRoleFactory,
)

pytestmark = pytest.mark.django_db


# ────────────── Model Tests ──────────────


class TestDepartmentModel:
    def test_create_department(self):
        dept = DepartmentFactory(code="K.CNTT", name="Khoa CNTT")
        assert str(dept) == "K.CNTT - Khoa CNTT"
        assert dept.is_active is True

    def test_department_hierarchy(self):
        parent = DepartmentFactory(code="HUTECH")
        child = DepartmentFactory(code="K.CNTT", parent=parent)
        grandchild = DepartmentFactory(code="BM.KTPM", parent=child)

        assert child.parent == parent
        assert grandchild.parent == child
        assert parent.children.count() == 1
        assert child.children.count() == 1

    def test_department_types(self):
        dept = DepartmentFactory(type=DepartmentType.BAN_GIAM_HIEU)
        assert dept.type == "BAN_GIAM_HIEU"


class TestRoleModel:
    def test_create_role(self):
        role = RoleFactory(code="GIANG_VIEN", name="Giảng viên", level=1)
        assert str(role) == "GIANG_VIEN - Giảng viên"

    def test_role_permission_assignment(self):
        role = RoleFactory()
        perm1 = PermissionFactory(code="programs.view")
        perm2 = PermissionFactory(code="programs.create")
        RolePermissionFactory(role=role, permission=perm1)
        RolePermissionFactory(role=role, permission=perm2)
        assert role.permissions.count() == 2


class TestUserRoleModel:
    def test_assign_role(self):
        user = UserFactory()
        role = RoleFactory()
        dept = DepartmentFactory()
        user_role = UserRoleFactory(user=user, role=role, department=dept)
        assert str(user_role) == f"{user} → {role.code} @ {dept.code}"

    def test_unique_constraint(self):
        user = UserFactory()
        role = RoleFactory()
        dept = DepartmentFactory()
        UserRoleFactory(user=user, role=role, department=dept)
        with pytest.raises(Exception):
            UserRoleFactory(user=user, role=role, department=dept)


class TestPermissionChecking:
    def test_get_user_permissions(self):
        user = UserFactory()
        role = RoleFactory()
        dept = DepartmentFactory()
        perm = PermissionFactory(code="programs.view")
        RolePermissionFactory(role=role, permission=perm)
        UserRoleFactory(user=user, role=role, department=dept)

        perms = get_user_permissions(user)
        assert "programs.view" in perms

    def test_has_perm_code(self):
        user = UserFactory()
        role = RoleFactory()
        dept = DepartmentFactory()
        perm = PermissionFactory(code="programs.edit")
        RolePermissionFactory(role=role, permission=perm)
        UserRoleFactory(user=user, role=role, department=dept)

        assert user.has_perm_code("programs.edit") is True
        assert user.has_perm_code("programs.delete") is False

    def test_superuser_has_all_perms(self):
        user = UserFactory(is_superuser=True)
        PermissionFactory(code="any.perm")
        assert user.has_perm_code("any.perm") is True

    def test_department_scoped_access(self):
        dept_a = DepartmentFactory(code="K.A")
        dept_b = DepartmentFactory(code="K.B")
        role = RoleFactory()
        user = UserFactory()
        UserRoleFactory(user=user, role=role, department=dept_a)

        # User has role in dept_a but not dept_b
        assert user.user_roles.filter(department=dept_a).exists()
        assert not user.user_roles.filter(department=dept_b).exists()


class TestAuditLogModel:
    def test_create_audit_log(self):
        log = AuditLogFactory(
            action="CREATE",
            entity_type="TrainingProgram",
            old_data=None,
            new_data={"name": "Test"},
        )
        assert log.action == "CREATE"
        assert log.new_data == {"name": "Test"}


# ────────────── API Tests ──────────────


class TestDepartmentAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin = UserFactory(is_superuser=True)
        self.client.force_authenticate(self.admin)

    def test_list_departments(self):
        DepartmentFactory.create_batch(3)
        response = self.client.get("/api/v1/rbac/departments/")
        assert response.status_code == 200
        assert response.data["count"] == 3

    def test_create_department(self):
        response = self.client.post(
            "/api/v1/rbac/departments/",
            {"code": "K.NEW", "name": "Khoa Mới", "type": "KHOA"},
        )
        assert response.status_code == 201
        assert Department.objects.filter(code="K.NEW").exists()

    def test_department_tree(self):
        root = DepartmentFactory(code="ROOT", parent=None)
        DepartmentFactory(code="CHILD1", parent=root)
        DepartmentFactory(code="CHILD2", parent=root)
        response = self.client.get("/api/v1/rbac/departments/tree/")
        assert response.status_code == 200
        tree = response.data
        root_node = [d for d in tree if d["code"] == "ROOT"]
        assert len(root_node) == 1
        assert len(root_node[0]["children"]) == 2

    def test_update_department(self):
        dept = DepartmentFactory(code="K.OLD")
        response = self.client.patch(
            f"/api/v1/rbac/departments/{dept.id}/",
            {"name": "Updated Name"},
        )
        assert response.status_code == 200
        dept.refresh_from_db()
        assert dept.name == "Updated Name"


class TestRoleAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin = UserFactory(is_superuser=True)
        self.client.force_authenticate(self.admin)

    def test_list_roles(self):
        RoleFactory.create_batch(3)
        response = self.client.get("/api/v1/rbac/roles/")
        assert response.status_code == 200

    def test_create_role_with_permissions(self):
        p1 = PermissionFactory(code="test.view")
        p2 = PermissionFactory(code="test.edit")
        response = self.client.post(
            "/api/v1/rbac/roles/",
            {
                "code": "NEW_ROLE",
                "name": "New Role",
                "level": 5,
                "permission_ids": [str(p1.id), str(p2.id)],
            },
            format="json",
        )
        assert response.status_code == 201
        role = Role.objects.get(code="NEW_ROLE")
        assert role.permissions.count() == 2

    def test_cannot_delete_system_role(self):
        role = RoleFactory(is_system=True)
        response = self.client.delete(f"/api/v1/rbac/roles/{role.id}/")
        assert response.status_code == 400

    def test_role_permissions_endpoint(self):
        role = RoleFactory()
        perm = PermissionFactory(code="test.perm")
        RolePermissionFactory(role=role, permission=perm)
        response = self.client.get(f"/api/v1/rbac/roles/{role.id}/permissions/")
        assert response.status_code == 200
        assert len(response.data) == 1


class TestUserRoleAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin = UserFactory(is_superuser=True)
        self.client.force_authenticate(self.admin)

    def test_assign_role(self):
        user = UserFactory()
        role = RoleFactory()
        dept = DepartmentFactory()
        response = self.client.post(
            f"/api/v1/rbac/users/{user.id}/assign-role/",
            {"role_id": str(role.id), "department_id": str(dept.id)},
            format="json",
        )
        assert response.status_code == 201
        assert UserRole.objects.filter(user=user, role=role).exists()

    def test_assign_duplicate_role(self):
        user = UserFactory()
        role = RoleFactory()
        dept = DepartmentFactory()
        UserRoleFactory(user=user, role=role, department=dept)
        response = self.client.post(
            f"/api/v1/rbac/users/{user.id}/assign-role/",
            {"role_id": str(role.id), "department_id": str(dept.id)},
            format="json",
        )
        assert response.status_code == 409

    def test_remove_role(self):
        user = UserFactory()
        role = RoleFactory()
        dept = DepartmentFactory()
        UserRoleFactory(user=user, role=role, department=dept)
        response = self.client.delete(
            f"/api/v1/rbac/users/{user.id}/roles/{role.id}/"
        )
        assert response.status_code == 204
        assert not UserRole.objects.filter(user=user, role=role).exists()

    def test_me_endpoint(self):
        response = self.client.get("/api/v1/rbac/users/me/")
        assert response.status_code == 200
        assert response.data["username"] == self.admin.username
        assert "permissions" in response.data
        assert "roles" in response.data


class TestPermissionAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin = UserFactory(is_superuser=True)
        self.client.force_authenticate(self.admin)

    def test_list_permissions(self):
        PermissionFactory.create_batch(5)
        response = self.client.get("/api/v1/rbac/permissions/")
        assert response.status_code == 200

    def test_filter_by_module(self):
        PermissionFactory(code="programs.test1", module="programs")
        PermissionFactory(code="plo.test1", module="plo")
        response = self.client.get("/api/v1/rbac/permissions/?module=programs")
        assert response.status_code == 200
        for perm in response.data["results"]:
            assert perm["module"] == "programs"


class TestAuditLogAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin = UserFactory(is_superuser=True)
        # Need rbac.view_audit_logs permission
        admin_role = RoleFactory(code="ADMIN_TEST")
        perm = PermissionFactory(code="rbac.view_audit_logs", module="rbac")
        RolePermissionFactory(role=admin_role, permission=perm)
        dept = DepartmentFactory()
        UserRoleFactory(user=self.admin, role=admin_role, department=dept)
        self.client.force_authenticate(self.admin)

    def test_list_audit_logs(self):
        AuditLogFactory.create_batch(3)
        response = self.client.get("/api/v1/rbac/audit-logs/")
        assert response.status_code == 200

    def test_audit_log_created_on_model_change(self):
        # Create a department via API to trigger audit logging
        response = self.client.post(
            "/api/v1/rbac/departments/",
            {"code": "K.AUDIT", "name": "Audit Test", "type": "KHOA"},
        )
        assert response.status_code == 201
        log = AuditLog.objects.filter(entity_type="Department").first()
        assert log is not None
        assert log.action == "CREATE"


class TestPermissionDenied:
    def test_gv_cannot_manage_users(self):
        client = APIClient()
        user = UserFactory()
        role = RoleFactory(code="GV_TEST")
        perm = PermissionFactory(code="programs.view")
        RolePermissionFactory(role=role, permission=perm)
        dept = DepartmentFactory()
        UserRoleFactory(user=user, role=role, department=dept)
        client.force_authenticate(user)

        response = client.get("/api/v1/rbac/users/")
        assert response.status_code == 403

    def test_unauthenticated_denied(self):
        client = APIClient()
        response = client.get("/api/v1/rbac/departments/")
        assert response.status_code in [401, 403]


# ────────────── Seed Command Tests ──────────────


class TestSeedRBACCommand:
    def test_seed_creates_data(self):
        call_command("seed_rbac")
        assert Permission.objects.count() >= 35
        assert Role.objects.count() >= 6
        assert Department.objects.count() >= 5

    def test_seed_idempotent(self):
        call_command("seed_rbac")
        count1 = Permission.objects.count()
        call_command("seed_rbac")
        count2 = Permission.objects.count()
        assert count1 == count2

    def test_seed_with_reset(self):
        call_command("seed_rbac")
        call_command("seed_rbac", reset=True)
        assert Permission.objects.count() >= 35
