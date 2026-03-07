import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import * as rbac from '@/services/rbacService';

export function useDepartments(filters?: rbac.DepartmentFilters) {
  return useQuery({
    queryKey: ['departments', filters],
    queryFn: () => rbac.getDepartments(filters).then((r) => r.data),
  });
}

export function useDepartmentTree() {
  return useQuery({
    queryKey: ['departments', 'tree'],
    queryFn: () => rbac.getDepartmentTree().then((r) => r.data),
  });
}

export function useCreateDepartment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof rbac.createDepartment>[0]) =>
      rbac.createDepartment(data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['departments'] });
      message.success('Tạo đơn vị thành công');
    },
    onError: () => message.error('Không thể tạo đơn vị'),
  });
}

export function useUpdateDepartment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof rbac.updateDepartment>[1] }) =>
      rbac.updateDepartment(id, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['departments'] });
      message.success('Cập nhật đơn vị thành công');
    },
    onError: () => message.error('Không thể cập nhật đơn vị'),
  });
}

export function useDeleteDepartment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => rbac.deleteDepartment(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['departments'] });
      message.success('Đã xóa đơn vị');
    },
    onError: () => message.error('Không thể xóa đơn vị'),
  });
}
