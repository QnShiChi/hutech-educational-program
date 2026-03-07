# Design: Frontend RBAC Pages

## Architecture

### Tech Stack

- **React 18** + **TypeScript** + **Vite**
- **Ant Design 5** (vi_VN locale) — Table, Tree, Form, Modal, Tag, Select
- **@tanstack/react-query** for server-state (caching, pagination, mutations)
- **Zustand** (`authStore`) for auth state & permission checks
- **Axios** (`apiClient`) with JWT interceptors

### Directory Layout

```
frontend/src/
├── pages/
│   ├── UsersPage.tsx          # rewrite stub → full CRUD
│   ├── UserDetailPage.tsx     # NEW: user edit + role assignment
│   ├── RolesPage.tsx          # rewrite stub → full CRUD
│   ├── RoleDetailPage.tsx     # NEW: role detail + permission matrix
│   ├── DepartmentsPage.tsx    # rewrite stub → tree + CRUD
│   └── AuditLogsPage.tsx      # NEW: read-only log viewer
├── services/
│   └── rbacService.ts         # NEW: all RBAC API calls
├── hooks/
│   ├── useUsers.ts            # NEW: react-query hooks for users
│   ├── useRoles.ts            # NEW: react-query hooks for roles
│   ├── useDepartments.ts      # NEW: react-query hooks for departments
│   └── usePermissions.ts      # NEW: react-query hooks for permissions
└── types/
    └── api.ts                 # extend with UserRole, AuditLog, DepartmentTree
```

## Component Design

### 1. UsersPage (`/rbac/users`)

- **PageHeader** with "Tạo người dùng" button (guarded by `rbac.manage_users`)
- **DataTable** with server-side pagination via react-query
- Columns: Họ tên, Email, Mã NV, Đơn vị, Vai trò (Tag list), Trạng thái (StatusTag)
- Search by name/email/employee_id (server-side `?search=`)
- Filter by department (Select), active status (Select)
- Row actions: Sửa, Vô hiệu hóa (with ConfirmModal)

### 2. UserDetailPage (`/rbac/users/:id`)

- **Ant Design Form** for user fields: name, email, employee_id, phone, department, is_active
- **Role Assignment Table** below the form:
  - Columns: Vai trò, Đơn vị, Người gán, Ngày gán, Hành động (Xóa)
  - "Gán vai trò" button → Modal with Role Select + Department Select
  - POST `/api/v1/rbac/users/{id}/assign-role/`
  - DELETE `/api/v1/rbac/users/{id}/roles/{role_id}/`
- Permission guard: entire page requires `rbac.manage_users`

### 3. RolesPage (`/rbac/roles`)

- **PageHeader** with "Tạo vai trò" button (guarded by `rbac.manage_roles`)
- **DataTable** columns: Tên, Mã, Level, Hệ thống (Tag), Số permissions
- Search by code/name
- Row click → navigate to RoleDetailPage
- Cannot delete system roles (backend protection + disable button)

### 4. RoleDetailPage (`/rbac/roles/:id`)

- **Form** for code, name, description, level
- **Permission Matrix** (checkbox grid):
  - Rows grouped by module (programs, plo, syllabus, courses, rbac)
  - Columns = individual permissions in that module
  - Ant Design Checkbox.Group within Collapse panels per module
  - On save: PUT role with `permission_ids[]`
- System roles: form fields disabled, label badge

### 5. DepartmentsPage (`/rbac/departments`)

- **Ant Design Tree** component using `/api/v1/rbac/departments/tree/`
- Right-click context menu or action buttons: Tạo con, Sửa, Xóa
- **Drawer** (Ant Design Drawer) for create/edit form:
  - Fields: code, name, name_en, type (Select from DepartmentType), parent (TreeSelect), is_active
- All write actions guarded by `rbac.manage_departments`

### 6. AuditLogsPage (`/rbac/audit-logs`) — _optional, low priority_

- Read-only paginated table
- Columns: Thời gian, Người dùng, Hành động (Tag), Loại đối tượng, ID
- Filter by action, entity_type, user
- Expandable row → show old_data / new_data JSON diff
- Guarded by `rbac.view_audit_logs`

## API Service Layer

### `rbacService.ts`

All functions return typed Axios promises, following existing `apiClient` pattern:

```typescript
// Users
getUsers(params)      → GET /rbac/users/
getUser(id)           → GET /rbac/users/{id}/
createUser(data)      → POST /rbac/users/
updateUser(id, data)  → PUT /rbac/users/{id}/
assignRole(id, data)  → POST /rbac/users/{id}/assign-role/
removeRole(id, roleId)→ DELETE /rbac/users/{id}/roles/{roleId}/

// Roles
getRoles(params)      → GET /rbac/roles/
getRole(id)           → GET /rbac/roles/{id}/
createRole(data)      → POST /rbac/roles/
updateRole(id, data)  → PUT /rbac/roles/{id}/

// Departments
getDepartments(params)→ GET /rbac/departments/
getDepartmentTree()   → GET /rbac/departments/tree/
createDepartment(data)→ POST /rbac/departments/
updateDepartment(id, d)→ PUT /rbac/departments/{id}/
deleteDepartment(id)  → DELETE /rbac/departments/{id}/

// Permissions
getPermissions(params)→ GET /rbac/permissions/

// Audit Logs
getAuditLogs(params)  → GET /rbac/audit-logs/
```

## React-Query Hooks

Each hook wraps the service layer with proper query keys, pagination, and optimistic cache invalidation:

```typescript
// useUsers.ts
useUsers(filters)         → useQuery(['users', filters], ...)
useUser(id)               → useQuery(['users', id], ...)
useCreateUser()           → useMutation(..., onSuccess → invalidate 'users')
useUpdateUser()           → useMutation(...)
useAssignRole()           → useMutation(..., onSuccess → invalidate ['users', id])
useRemoveRole()           → useMutation(...)

// Similar for useRoles, useDepartments, usePermissions, useAuditLogs
```

## Routing Changes

Update `App.tsx`:

```diff
 <Route path="rbac/users" element={<UsersPage />} />
-<Route path="rbac/users/:id" element={<UsersPage />} />
+<Route path="rbac/users/new" element={<UserDetailPage />} />
+<Route path="rbac/users/:id" element={<UserDetailPage />} />
 <Route path="rbac/roles" element={<RolesPage />} />
+<Route path="rbac/roles/new" element={<RoleDetailPage />} />
+<Route path="rbac/roles/:id" element={<RoleDetailPage />} />
 <Route path="rbac/departments" element={<DepartmentsPage />} />
+<Route path="rbac/audit-logs" element={<AuditLogsPage />} />
```

## Type Extensions

Add to `types/api.ts`:

```typescript
export interface UserRole {
  id: string;
  user: string;
  role: string;
  role_name: string;
  department: string;
  department_name: string;
  assigned_by: string | null;
  created_at: string;
}

export interface DepartmentTree extends Omit<Department, "parent" | "head"> {
  name_en: string;
  type: string;
  children: DepartmentTree[];
}

export interface AuditLog {
  id: string;
  user: string | null;
  user_name: string | null;
  user_username: string | null;
  action: string;
  entity_type: string;
  entity_id: string;
  old_data: Record<string, unknown> | null;
  new_data: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface PermissionItem {
  id: string;
  code: string;
  name: string;
  module: string;
  description: string;
}
```

## Permission Guards

All RBAC pages use `<PermissionGuard>` for write actions:

- User CRUD: `rbac.manage_users`
- Role CRUD: `rbac.manage_roles`
- Department CRUD: `rbac.manage_departments`
- Audit Logs view: `rbac.view_audit_logs`

List/view actions are available to authenticated users with any of the above permissions.
