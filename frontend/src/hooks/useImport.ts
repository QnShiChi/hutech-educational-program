import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import * as importService from '@/services/importService';

export function useUploadImport() {
  return useMutation({
    mutationFn: (file: File) => importService.uploadImport(file).then((r) => r.data),
    onSuccess: () => {
      message.success('Tải lên file thành công, đang xử lý...');
    },
    onError: () => message.error('Không thể tải lên file'),
  });
}

export function useImportStatus(id?: string) {
  return useQuery({
    queryKey: ['import', id],
    queryFn: () => importService.getImportStatus(id!).then((r) => r.data),
    enabled: !!id,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === 'completed' || status === 'failed') return false;
      return 2000;
    },
  });
}

export function useImportPreview(id?: string) {
  return useQuery({
    queryKey: ['import-preview', id],
    queryFn: () => importService.getImportPreview(id!).then((r) => r.data),
    enabled: !!id,
  });
}

export function useConfirmImport() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => importService.confirmImport(id).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['programs'] });
      message.success('Import chương trình đào tạo thành công');
    },
    onError: () => message.error('Không thể xác nhận import'),
  });
}
