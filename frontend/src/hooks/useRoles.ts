import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import * as rbac from '@/services/rbacService';

export function useRoles(filters?: rbac.RoleFilters) {
  return useQuery({
    queryKey: ['roles', filters],
    queryFn: () => rbac.getRoles(filters).then((r) => r.data),
  });
}

export function useRole(id?: string) {
  return useQuery({
    queryKey: ['roles', id],
    queryFn: () => rbac.getRole(id!).then((r) => r.data),
    enabled: !!id,
  });
}

export function useCreateRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof rbac.createRole>[0]) =>
      rbac.createRole(data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['roles'] });
      message.success('Tạo vai trò thành công');
    },
    onError: () => message.error('Không thể tạo vai trò'),
  });
}

export function useUpdateRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof rbac.updateRole>[1] }) =>
      rbac.updateRole(id, data).then((r) => r.data),
    onSuccess: (_d, vars) => {
      qc.invalidateQueries({ queryKey: ['roles'] });
      qc.invalidateQueries({ queryKey: ['roles', vars.id] });
      message.success('Cập nhật vai trò thành công');
    },
    onError: () => message.error('Không thể cập nhật vai trò'),
  });
}
