import apiClient from '@/services/apiClient';
import type {
  PaginatedResponse,
  User,
  Role,
  Department,
  DepartmentTree,
  UserRole,
  AuditLog,
  PermissionItem,
} from '@/types/api';

/* ─── Query params ─── */
export interface UserFilters {
  search?: string;
  department?: string;
  is_active?: boolean;
  page?: number;
  page_size?: number;
}

export interface RoleFilters {
  search?: string;
  page?: number;
  page_size?: number;
}

export interface DepartmentFilters {
  search?: string;
  is_active?: boolean;
  page?: number;
  page_size?: number;
}

export interface AuditLogFilters {
  action?: string;
  entity_type?: string;
  user?: string;
  page?: number;
  page_size?: number;
}

export interface PermissionFilters {
  module?: string;
}

/* ─── Users ─── */
export const getUsers = (params?: UserFilters) =>
  apiClient.get<PaginatedResponse<User>>('/rbac/users/', { params });

export const getUser = (id: string) =>
  apiClient.get<User>(`/rbac/users/${id}/`);

export const createUser = (data: Partial<User>) =>
  apiClient.post<User>('/rbac/users/', data);

export const updateUser = (id: string, data: Partial<User>) =>
  apiClient.put<User>(`/rbac/users/${id}/`, data);

export const deactivateUser = (id: string) =>
  apiClient.patch<User>(`/rbac/users/${id}/`, { is_active: false });

export const assignRole = (userId: string, data: { role: string; department?: string }) =>
  apiClient.post<UserRole>(`/rbac/users/${userId}/assign-role/`, data);

export const removeRole = (userId: string, roleId: string) =>
  apiClient.delete(`/rbac/users/${userId}/roles/${roleId}/`);

/* ─── Roles ─── */
export const getRoles = (params?: RoleFilters) =>
  apiClient.get<PaginatedResponse<Role>>('/rbac/roles/', { params });

export const getRole = (id: string) =>
  apiClient.get<Role>(`/rbac/roles/${id}/`);

export const createRole = (data: Partial<Role>) =>
  apiClient.post<Role>('/rbac/roles/', data);

export const updateRole = (id: string, data: Partial<Role>) =>
  apiClient.put<Role>(`/rbac/roles/${id}/`, data);

/* ─── Departments ─── */
export const getDepartments = (params?: DepartmentFilters) =>
  apiClient.get<PaginatedResponse<Department>>('/rbac/departments/', { params });

export const getDepartmentTree = () =>
  apiClient.get<DepartmentTree[]>('/rbac/departments/tree/');

export const createDepartment = (data: Partial<Department>) =>
  apiClient.post<Department>('/rbac/departments/', data);

export const updateDepartment = (id: string, data: Partial<Department>) =>
  apiClient.put<Department>(`/rbac/departments/${id}/`, data);

export const deleteDepartment = (id: string) =>
  apiClient.delete(`/rbac/departments/${id}/`);

/* ─── Permissions ─── */
export const getPermissions = (params?: PermissionFilters) =>
  apiClient.get<PaginatedResponse<PermissionItem>>('/rbac/permissions/', { params });

/* ─── Audit Logs ─── */
export const getAuditLogs = (params?: AuditLogFilters) =>
  apiClient.get<PaginatedResponse<AuditLog>>('/rbac/audit-logs/', { params });
