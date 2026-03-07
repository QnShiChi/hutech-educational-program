# Spec: RBAC Module

## Requirements

### REQ-RBAC-01: Department Management
WHEN an admin creates a Department,
the system SHALL store: code (unique), name, type (KHOA/VIEN/PHONG/TRUNG_TAM/BAN_GIAM_HIEU), parent_id (self-referencing for hierarchy), is_active.

#### Scenario: Create Department
GIVEN an admin user
WHEN they POST /api/v1/rbac/departments/ with valid data
THEN the system creates the department and returns 201

#### Scenario: Department Hierarchy
GIVEN departments: "HUTECH" → "Khoa CNTT" → "BM Kỹ thuật phần mềm"
WHEN fetching /api/v1/rbac/departments/?tree=true
THEN return nested tree structure

### REQ-RBAC-02: Role Management
The system SHALL have 6 predefined roles seeded on first deploy.
Each role has a `level` field indicating approval hierarchy order.
Custom roles MAY be created by admin.

| Role | Level | Scope |
|------|-------|-------|
| GIANG_VIEN | 1 | Own syllabus only |
| TRUONG_NGANH | 2 | Department syllabus |
| LANH_DAO_KHOA | 3 | Department CTDT + PLO + syllabus |
| PHONG_DAO_TAO | 4 | All departments |
| BAN_GIAM_HIEU | 5 | Final approve only |
| ADMIN | 99 | System-wide |

### REQ-RBAC-03: Permission System
Permissions are module-scoped strings: `{module}.{action}`

#### Permission Matrix:
```
Module: programs (CTDT)
  programs.view          - Xem CTDT (published)
  programs.view_draft    - Xem CTDT draft (own department)
  programs.create        - Tạo CTDT
  programs.edit          - Sửa CTDT (own department)
  programs.delete        - Xóa CTDT draft
  programs.submit        - Nộp CTDT để duyệt
  programs.approve_khoa  - Duyệt cấp Khoa
  programs.approve_pdt   - Duyệt cấp Phòng ĐT
  programs.approve_bgh   - Duyệt cấp BGH
  programs.export        - Xuất báo cáo
  programs.manage_all    - Quản lý toàn bộ (cross-department)

Module: plo (Chuẩn đầu ra)
  plo.view, plo.create, plo.edit, plo.delete
  plo.approve_khoa, plo.approve_pdt, plo.approve_bgh

Module: syllabus (Đề cương chi tiết)
  syllabus.view, syllabus.create, syllabus.edit, syllabus.delete
  syllabus.submit
  syllabus.approve_truong_nganh, syllabus.approve_khoa
  syllabus.approve_pdt, syllabus.approve_bgh

Module: courses (Học phần)
  courses.view, courses.create, courses.edit, courses.delete

Module: rbac (Quản trị)
  rbac.manage_users, rbac.manage_roles, rbac.manage_departments
  rbac.view_audit_logs
```

#### Default Role-Permission Mapping:
```
GIANG_VIEN:
  programs.view, plo.view, syllabus.view
  syllabus.create, syllabus.edit, syllabus.submit
  courses.view

TRUONG_NGANH:
  (all of GIANG_VIEN) +
  syllabus.approve_truong_nganh, syllabus.view_draft(department)

LANH_DAO_KHOA:
  (all of TRUONG_NGANH) +
  programs.create, programs.edit, programs.submit, programs.view_draft
  plo.create, plo.edit, plo.submit
  syllabus.approve_khoa
  programs.approve_khoa, plo.approve_khoa

PHONG_DAO_TAO:
  (all of LANH_DAO_KHOA) +
  programs.manage_all, programs.export
  programs.approve_pdt, plo.approve_pdt, syllabus.approve_pdt
  courses.create, courses.edit

BAN_GIAM_HIEU:
  programs.view, programs.view_draft
  programs.approve_bgh, plo.approve_bgh, syllabus.approve_bgh

ADMIN:
  rbac.manage_users, rbac.manage_roles, rbac.manage_departments
  rbac.view_audit_logs
  (+ all permissions)
```

### REQ-RBAC-04: User-Role Assignment
- A user CAN have multiple roles (e.g., GIANG_VIEN + TRUONG_NGANH)
- Each UserRole is scoped to a Department
- Role assignment is ADMIN-only action

#### Scenario: Assign Role
GIVEN admin user
WHEN POST /api/v1/rbac/users/{user_id}/assign-role/ with {role_id, department_id}
THEN user gets the role in that department scope

#### Scenario: Check Permission
GIVEN user with role LANH_DAO_KHOA in "Khoa CNTT"
WHEN they try to edit a CTDT of "Khoa CNTT"
THEN access is GRANTED

GIVEN user with role LANH_DAO_KHOA in "Khoa CNTT"  
WHEN they try to edit a CTDT of "Khoa Ngoại ngữ"
THEN access is DENIED (403)

### REQ-RBAC-05: Audit Logging
Every state-changing action SHALL be logged:
- Who (user_id)
- What (action: CREATE/UPDATE/DELETE/APPROVE/REJECT/SUBMIT)
- Which entity (entity_type + entity_id)
- When (timestamp)
- Old/new data (JSONB diff)
- IP address

## API Endpoints

```
GET    /api/v1/rbac/departments/                    # List (filterable, searchable)
POST   /api/v1/rbac/departments/                    # Create (admin only)
GET    /api/v1/rbac/departments/{id}/               # Detail
PUT    /api/v1/rbac/departments/{id}/               # Update (admin only)
DELETE /api/v1/rbac/departments/{id}/               # Soft delete (admin only)
GET    /api/v1/rbac/departments/tree/               # Tree structure

GET    /api/v1/rbac/roles/                          # List
POST   /api/v1/rbac/roles/                          # Create (admin only)
GET    /api/v1/rbac/roles/{id}/                     # Detail with permissions
PUT    /api/v1/rbac/roles/{id}/                     # Update (admin only)
GET    /api/v1/rbac/roles/{id}/permissions/         # Permissions of role

GET    /api/v1/rbac/permissions/                    # List all permissions
GET    /api/v1/rbac/permissions/?module=programs     # Filter by module

GET    /api/v1/rbac/users/                          # List users (admin/pdt)
POST   /api/v1/rbac/users/                          # Create user (admin only)
GET    /api/v1/rbac/users/{id}/                     # User detail with roles
PUT    /api/v1/rbac/users/{id}/                     # Update user
POST   /api/v1/rbac/users/{id}/assign-role/         # Assign role (admin)
DELETE /api/v1/rbac/users/{id}/roles/{role_id}/     # Remove role (admin)
GET    /api/v1/rbac/users/me/                       # Current user profile + permissions

GET    /api/v1/rbac/audit-logs/                     # List logs (admin/pdt)
GET    /api/v1/rbac/audit-logs/?user={id}&entity_type=TrainingProgram
```
