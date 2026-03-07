# Tasks: Frontend RBAC Pages

## Foundation

- [x] 1.1 Add types to `types/api.ts` — UserRole, DepartmentTree, AuditLog, PermissionItem interfaces
- [x] 1.2 Create `services/rbacService.ts` — typed Axios functions for all RBAC endpoints
- [x] 1.3 Create `hooks/useUsers.ts` — react-query hooks: useUsers, useUser, useCreateUser, useUpdateUser, useAssignRole, useRemoveRole
- [x] 1.4 Create `hooks/useRoles.ts` — react-query hooks: useRoles, useRole, useCreateRole, useUpdateRole
- [x] 1.5 Create `hooks/useDepartments.ts` — react-query hooks: useDepartments, useDepartmentTree, useCreateDepartment, useUpdateDepartment, useDeleteDepartment
- [x] 1.6 Create `hooks/usePermissions.ts` — react-query hooks: usePermissions (with module filter)

## User Management

- [x] 2.1 Rewrite `UsersPage.tsx` — DataTable with server-side search, department filter, status filter, pagination; row actions (edit, deactivate)
- [x] 2.2 Create `UserDetailPage.tsx` — user edit form + role assignment table with assign/remove modals
- [x] 2.3 Update `App.tsx` routes — add `/rbac/users/new`, update `/rbac/users/:id` to UserDetailPage

## Role Management

- [x] 3.1 Rewrite `RolesPage.tsx` — DataTable with search, permission count column, system role badge; row click navigates to detail
- [x] 3.2 Create `RoleDetailPage.tsx` — role form + permission matrix (Checkbox.Group grouped by module in Collapse panels)
- [x] 3.3 Update `App.tsx` routes — add `/rbac/roles/new` and `/rbac/roles/:id`

## Department Management

- [x] 4.1 Rewrite `DepartmentsPage.tsx` — Ant Design Tree from `/departments/tree/`; Drawer for create/edit form with code, name, type, parent (TreeSelect)
- [x] 4.2 Wire up create/edit/delete actions with PermissionGuard on `rbac.manage_departments`

## Audit Logs (optional)

- [x] 5.1 Create `AuditLogsPage.tsx` — read-only paginated table with filters (action, entity_type, user), expandable row for JSON diff
- [x] 5.2 Create `hooks/useAuditLogs.ts` — react-query hook
- [x] 5.3 Update `App.tsx` route — add `/rbac/audit-logs`

## Integration & Polish

- [x] 6.1 Wrap all write actions with `<PermissionGuard>` — buttons hidden when user lacks permission
- [x] 6.2 Add sidebar menu items for Audit Logs in `AppLayout.tsx` (if not present) guarded by `rbac.view_audit_logs`
- [x] 6.3 Verify build — `npm run build` must pass with zero errors
