import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import * as programService from '@/services/programService';

export function usePrograms(filters?: programService.ProgramFilters) {
  return useQuery({
    queryKey: ['programs', filters],
    queryFn: () => programService.getPrograms(filters).then((r) => r.data),
  });
}

export function useProgram(id?: string) {
  return useQuery({
    queryKey: ['program', id],
    queryFn: () => programService.getProgram(id!).then((r) => r.data),
    enabled: !!id,
  });
}

export function useCreateProgram() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof programService.createProgram>[0]) =>
      programService.createProgram(data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['programs'] });
      message.success('Tạo chương trình đào tạo thành công');
    },
    onError: () => message.error('Không thể tạo chương trình đào tạo'),
  });
}

export function useUpdateProgram() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof programService.updateProgram>[1] }) =>
      programService.updateProgram(id, data).then((r) => r.data),
    onSuccess: (_d, vars) => {
      qc.invalidateQueries({ queryKey: ['programs'] });
      qc.invalidateQueries({ queryKey: ['program', vars.id] });
      message.success('Cập nhật chương trình đào tạo thành công');
    },
    onError: () => message.error('Không thể cập nhật chương trình đào tạo'),
  });
}

export function useDeleteProgram() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => programService.deleteProgram(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['programs'] });
      message.success('Xóa chương trình đào tạo thành công');
    },
    onError: () => message.error('Không thể xóa chương trình đào tạo'),
  });
}
