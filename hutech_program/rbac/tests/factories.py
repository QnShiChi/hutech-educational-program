"""
Factory Boy factories for RBAC models.
"""

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from hutech_program.rbac.models import (
    AuditAction,
    AuditLog,
    Department,
    DepartmentType,
    Permission,
    PermissionModule,
    Role,
    RolePermission,
    UserRole,
)

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ["username"]

    username = factory.Sequence(lambda n: f"user_{n}")
    name = factory.Faker("name")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department
        django_get_or_create = ["code"]

    code = factory.Sequence(lambda n: f"DEPT_{n}")
    name = factory.LazyAttribute(lambda obj: f"Department {obj.code}")
    type = DepartmentType.KHOA
    is_active = True


class PermissionFactory(DjangoModelFactory):
    class Meta:
        model = Permission
        django_get_or_create = ["code"]

    code = factory.Sequence(lambda n: f"test.perm_{n}")
    name = factory.LazyAttribute(lambda obj: f"Permission {obj.code}")
    module = PermissionModule.PROGRAMS


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = Role
        django_get_or_create = ["code"]

    code = factory.Sequence(lambda n: f"ROLE_{n}")
    name = factory.LazyAttribute(lambda obj: f"Role {obj.code}")
    level = factory.Sequence(lambda n: n)
    is_system = False


class RolePermissionFactory(DjangoModelFactory):
    class Meta:
        model = RolePermission

    role = factory.SubFactory(RoleFactory)
    permission = factory.SubFactory(PermissionFactory)


class UserRoleFactory(DjangoModelFactory):
    class Meta:
        model = UserRole

    user = factory.SubFactory(UserFactory)
    role = factory.SubFactory(RoleFactory)
    department = factory.SubFactory(DepartmentFactory)


class AuditLogFactory(DjangoModelFactory):
    class Meta:
        model = AuditLog

    user = factory.SubFactory(UserFactory)
    action = AuditAction.CREATE
    entity_type = "TestEntity"
    entity_id = factory.Faker("uuid4")
