import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import * as rbac from '@/services/rbacService';

export function useUsers(filters?: rbac.UserFilters) {
  return useQuery({
    queryKey: ['users', filters],
    queryFn: () => rbac.getUsers(filters).then((r) => r.data),
  });
}

export function useUser(id?: string) {
  return useQuery({
    queryKey: ['users', id],
    queryFn: () => rbac.getUser(id!).then((r) => r.data),
    enabled: !!id,
  });
}

export function useCreateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof rbac.createUser>[0]) =>
      rbac.createUser(data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users'] });
      message.success('Tạo người dùng thành công');
    },
    onError: () => message.error('Không thể tạo người dùng'),
  });
}

export function useUpdateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof rbac.updateUser>[1] }) =>
      rbac.updateUser(id, data).then((r) => r.data),
    onSuccess: (_d, vars) => {
      qc.invalidateQueries({ queryKey: ['users'] });
      qc.invalidateQueries({ queryKey: ['users', vars.id] });
      message.success('Cập nhật người dùng thành công');
    },
    onError: () => message.error('Không thể cập nhật người dùng'),
  });
}

export function useDeactivateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => rbac.deactivateUser(id).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users'] });
      message.success('Đã vô hiệu hóa người dùng');
    },
    onError: () => message.error('Không thể vô hiệu hóa người dùng'),
  });
}

export function useAssignRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, data }: { userId: string; data: Parameters<typeof rbac.assignRole>[1] }) =>
      rbac.assignRole(userId, data).then((r) => r.data),
    onSuccess: (_d, vars) => {
      qc.invalidateQueries({ queryKey: ['users', vars.userId] });
      message.success('Gán vai trò thành công');
    },
    onError: () => message.error('Không thể gán vai trò'),
  });
}

export function useRemoveRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, roleId }: { userId: string; roleId: string }) =>
      rbac.removeRole(userId, roleId),
    onSuccess: (_d, vars) => {
      qc.invalidateQueries({ queryKey: ['users', vars.userId] });
      message.success('Đã xóa vai trò');
    },
    onError: () => message.error('Không thể xóa vai trò'),
  });
}
