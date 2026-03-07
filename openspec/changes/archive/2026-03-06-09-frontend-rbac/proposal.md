# Proposal: Frontend RBAC Pages

## Pages

### 1. User Management (/rbac/users)
- Table: Họ tên, Email, Mã NV, Đơn vị, Vai trò (tags), Trạng thái
- Search by name/email/employee_id
- Filter by department, role, status
- Actions: Tạo mới, Sửa, Gán vai trò, Vô hiệu hóa

### 2. User Detail/Edit (/rbac/users/:id)
- Form: Thông tin cá nhân + Danh sách vai trò (table with department scope)
- Gán vai trò: Modal chọn role + department

### 3. Role Management (/rbac/roles)
- Table: Tên vai trò, Code, Level, Số users, Số permissions
- Detail: Permissions matrix (checkboxes grouped by module)

### 4. Department Management (/rbac/departments)
- Tree view (Ant Design Tree component)
- CRUD form in drawer/modal
- Show user count per department

## Tasks
- [ ] 1.1 User list page with DataTable
- [ ] 1.2 User create/edit form (Modal or page)
- [ ] 1.3 Role assignment modal (select role + department)
- [ ] 1.4 Role list page
- [ ] 1.5 Role detail: permission matrix (checkbox grid)
- [ ] 1.6 Department tree view with CRUD
- [ ] 1.7 Custom hooks: useUsers, useRoles, useDepartments, usePermissions
- [ ] 1.8 Wire up all API calls
- [ ] 1.9 Permission guards on all actions
