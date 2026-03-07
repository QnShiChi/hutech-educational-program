# Tasks: 02 - RBAC Module

## 1. Models

- [x] 1.1 Create `hutech_program/common/models.py` with UUIDModel, TimeStampedModel base classes
- [x] 1.2 Create Department model with self-referencing parent FK
- [x] 1.3 Create Role model
- [x] 1.4 Create Permission model
- [x] 1.5 Create RolePermission M2M through model
- [x] 1.6 Create UserRole model (user + role + department scope)
- [x] 1.7 Create AuditLog model with JSON diff fields
- [x] 1.8 Run makemigrations + migrate
- [x] 1.9 Register all models in Django Admin with search/filter

## 2. Permission System

- [x] 2.1 Create `HasModulePermission` DRF permission class
- [x] 2.2 Create `DepartmentScopedPermission` for object-level checks
- [x] 2.3 Create `AuditLogMixin` for automatic audit logging on model changes
- [x] 2.4 Add `get_user_permissions(user)` utility → returns set of permission codes
- [x] 2.5 Add `user.has_perm_code(code)` method to User model

## 3. Seed Data

- [x] 3.1 Create management command `seed_rbac`
- [x] 3.2 Define all permissions (programs._, plo._, syllabus._, courses._, rbac.\*)
- [x] 3.3 Create 6 system roles with correct permission mappings
- [x] 3.4 Create sample departments (BGH, PDT, 3 sample Khoa)
- [x] 3.5 Create test users for each role
- [x] 3.6 Run command and verify in admin

## 4. API Endpoints

- [x] 4.1 DepartmentViewSet (CRUD + tree endpoint)
- [x] 4.2 RoleViewSet (CRUD + permissions sub-resource)
- [x] 4.3 PermissionViewSet (list only, filtered by module)
- [x] 4.4 UserViewSet (CRUD with role management)
  - [x] 4.4.1 POST /users/{id}/assign-role/
  - [x] 4.4.2 DELETE /users/{id}/roles/{role_id}/
  - [x] 4.4.3 GET /users/me/ (current user profile + all permissions)
- [x] 4.5 AuditLogViewSet (read-only, filtered by entity/user/date)
- [x] 4.6 Register all ViewSets in api_router.py under /api/v1/rbac/

## 5. Serializers

- [x] 5.1 DepartmentSerializer (flat) + DepartmentTreeSerializer (nested children)
- [x] 5.2 RoleSerializer with inline permissions
- [x] 5.3 PermissionSerializer
- [x] 5.4 UserRoleSerializer (for assignment)
- [x] 5.5 UserListSerializer (summary) + UserDetailSerializer (with roles/departments)
- [x] 5.6 AuditLogSerializer (read-only, with user name)

## 6. Tests

- [x] 6.1 Test Department CRUD + hierarchy
- [x] 6.2 Test Role CRUD + permission assignment
- [x] 6.3 Test User role assignment + removal
- [x] 6.4 Test permission checking: access granted/denied per role
- [x] 6.5 Test department-scoped access (Khoa A can't edit Khoa B's data)
- [x] 6.6 Test audit log creation on model changes
- [x] 6.7 Test seed_rbac command
- [x] 6.8 Create factories (factory_boy) for all RBAC models

## 7. Verification

- [x] 7.1 All endpoints documented in Swagger (drf-spectacular)
- [x] 7.2 Admin UI shows all RBAC data with filters
- [x] 7.3 Permission check works: GV can't access admin endpoints
- [x] 7.4 Department tree API returns correct hierarchy
- [x] 7.5 pytest passes with >80% coverage on rbac app
