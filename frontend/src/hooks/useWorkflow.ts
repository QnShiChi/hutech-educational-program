import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import * as ws from '@/services/workflowService';

export function useWorkflowStatus(programId?: string) {
  return useQuery({
    queryKey: ['program', programId, 'workflow'],
    queryFn: () => ws.getWorkflowStatus(programId!).then((r) => r.data),
    enabled: !!programId,
  });
}

export function useSubmitProgram(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => ws.submitProgram(programId).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId] });
      qc.invalidateQueries({ queryKey: ['program', programId, 'workflow'] });
      message.success('Đã gửi chương trình để phê duyệt');
    },
    onError: () => message.error('Không thể gửi yêu cầu phê duyệt'),
  });
}

export function useApproveProgram(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data?: { comment?: string }) =>
      ws.approveProgram(programId, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId] });
      qc.invalidateQueries({ queryKey: ['program', programId, 'workflow'] });
      message.success('Đã phê duyệt chương trình');
    },
    onError: () => message.error('Không thể phê duyệt'),
  });
}

export function useRejectProgram(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { comment: string }) =>
      ws.rejectProgram(programId, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId] });
      qc.invalidateQueries({ queryKey: ['program', programId, 'workflow'] });
      message.success('Đã từ chối chương trình');
    },
    onError: () => message.error('Không thể từ chối'),
  });
}

export function useVersions(programId?: string) {
  return useQuery({
    queryKey: ['program', programId, 'versions'],
    queryFn: () => ws.getVersions(programId!).then((r) => r.data),
    enabled: !!programId,
  });
}

export function useCompareVersions(programId?: string, v1?: string, v2?: string) {
  return useQuery({
    queryKey: ['program', programId, 'versions', 'compare', v1, v2],
    queryFn: () => ws.compareVersions(programId!, v1!, v2!).then((r) => r.data),
    enabled: !!programId && !!v1 && !!v2,
  });
}

export function useRollbackVersion(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (versionId: string) => ws.rollbackVersion(programId, versionId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId] });
      qc.invalidateQueries({ queryKey: ['program', programId, 'versions'] });
      message.success('Đã khôi phục phiên bản');
    },
    onError: () => message.error('Không thể khôi phục phiên bản'),
  });
}
