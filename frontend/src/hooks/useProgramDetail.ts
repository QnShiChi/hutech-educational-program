import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import * as ps from '@/services/programService';

/* ─── Objectives (PO) ─── */
export function useObjectives(programId?: string) {
  return useQuery({
    queryKey: ['program', programId, 'objectives'],
    queryFn: () => ps.getObjectives(programId!).then((r) => r.data),
    enabled: !!programId,
  });
}

export function useCreateObjective(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof ps.createObjective>[1]) =>
      ps.createObjective(programId, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'objectives'] });
      message.success('Thêm mục tiêu thành công');
    },
    onError: () => message.error('Không thể thêm mục tiêu'),
  });
}

export function useUpdateObjective(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof ps.updateObjective>[2] }) =>
      ps.updateObjective(programId, id, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'objectives'] });
      message.success('Cập nhật mục tiêu thành công');
    },
    onError: () => message.error('Không thể cập nhật mục tiêu'),
  });
}

export function useDeleteObjective(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => ps.deleteObjective(programId, id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'objectives'] });
      message.success('Xóa mục tiêu thành công');
    },
    onError: () => message.error('Không thể xóa mục tiêu'),
  });
}

export function useReorderObjectives(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (ids: string[]) => ps.reorderObjectives(programId, ids),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['program', programId, 'objectives'] }),
  });
}

/* ─── PLOs ─── */
export function usePLOs(programId?: string) {
  return useQuery({
    queryKey: ['program', programId, 'plos'],
    queryFn: () => ps.getPLOs(programId!).then((r) => r.data),
    enabled: !!programId,
  });
}

export function useCreatePLO(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof ps.createPLO>[1]) =>
      ps.createPLO(programId, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'plos'] });
      message.success('Thêm CĐR thành công');
    },
    onError: () => message.error('Không thể thêm CĐR'),
  });
}

export function useUpdatePLO(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof ps.updatePLO>[2] }) =>
      ps.updatePLO(programId, id, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'plos'] });
      message.success('Cập nhật CĐR thành công');
    },
    onError: () => message.error('Không thể cập nhật CĐR'),
  });
}

export function useDeletePLO(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => ps.deletePLO(programId, id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'plos'] });
      message.success('Xóa CĐR thành công');
    },
    onError: () => message.error('Không thể xóa CĐR'),
  });
}

export function useReorderPLOs(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (ids: string[]) => ps.reorderPLOs(programId, ids),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['program', programId, 'plos'] }),
  });
}

/* ─── PIs ─── */
export function usePIs(programId?: string, ploId?: string) {
  return useQuery({
    queryKey: ['program', programId, 'plo', ploId, 'pis'],
    queryFn: () => ps.getPIs(programId!, ploId!).then((r) => r.data),
    enabled: !!programId && !!ploId,
  });
}

export function useCreatePI(programId: string, ploId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof ps.createPI>[2]) =>
      ps.createPI(programId, ploId, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'plo', ploId, 'pis'] });
      message.success('Thêm chỉ số thành công');
    },
    onError: () => message.error('Không thể thêm chỉ số'),
  });
}

/* ─── PO-PLO Matrix ─── */
export function usePOPLOMatrix(programId?: string) {
  return useQuery({
    queryKey: ['program', programId, 'po-plo-matrix'],
    queryFn: () => ps.getPOPLOMatrix(programId!).then((r) => r.data),
    enabled: !!programId,
  });
}

export function useUpdatePOPLOMatrix(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof ps.updatePOPLOMatrix>[1]) =>
      ps.updatePOPLOMatrix(programId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'po-plo-matrix'] });
      message.success('Cập nhật ma trận PO-PLO thành công');
    },
    onError: () => message.error('Không thể cập nhật ma trận'),
  });
}

/* ─── Knowledge Blocks ─── */
export function useKnowledgeBlocks(programId?: string) {
  return useQuery({
    queryKey: ['program', programId, 'knowledge-blocks'],
    queryFn: () => ps.getKnowledgeBlocks(programId!).then((r) => r.data),
    enabled: !!programId,
  });
}

export function useCreateKnowledgeBlock(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof ps.createKnowledgeBlock>[1]) =>
      ps.createKnowledgeBlock(programId, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'knowledge-blocks'] });
      message.success('Thêm khối kiến thức thành công');
    },
    onError: () => message.error('Không thể thêm khối kiến thức'),
  });
}

export function useDeleteKnowledgeBlock(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => ps.deleteKnowledgeBlock(programId, id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'knowledge-blocks'] });
      message.success('Xóa khối kiến thức thành công');
    },
    onError: () => message.error('Không thể xóa khối kiến thức'),
  });
}

/* ─── Program Courses ─── */
export function useProgramCourses(programId?: string) {
  return useQuery({
    queryKey: ['program', programId, 'courses'],
    queryFn: () => ps.getProgramCourses(programId!).then((r) => r.data),
    enabled: !!programId,
  });
}

export function useAddProgramCourse(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof ps.addProgramCourse>[1]) =>
      ps.addProgramCourse(programId, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'courses'] });
      message.success('Thêm học phần thành công');
    },
    onError: () => message.error('Không thể thêm học phần'),
  });
}

export function useRemoveProgramCourse(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => ps.removeProgramCourse(programId, id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'courses'] });
      message.success('Xóa học phần thành công');
    },
    onError: () => message.error('Không thể xóa học phần'),
  });
}

/* ─── Semester Plan ─── */
export function useSemesterPlan(programId?: string) {
  return useQuery({
    queryKey: ['program', programId, 'semester-plan'],
    queryFn: () => ps.getSemesterPlan(programId!).then((r) => r.data),
    enabled: !!programId,
  });
}

export function useUpdateSemesterPlan(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof ps.updateSemesterPlan>[1]) =>
      ps.updateSemesterPlan(programId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'semester-plan'] });
      qc.invalidateQueries({ queryKey: ['program', programId, 'courses'] });
      message.success('Cập nhật kế hoạch giảng dạy thành công');
    },
    onError: () => message.error('Không thể cập nhật kế hoạch giảng dạy'),
  });
}

/* ─── Course-PLO Matrix ─── */
export function useCoursePLOMatrix(programId?: string) {
  return useQuery({
    queryKey: ['program', programId, 'course-plo-matrix'],
    queryFn: () => ps.getCoursePLOMatrix(programId!).then((r) => r.data),
    enabled: !!programId,
  });
}

export function useUpdateCoursePLOMatrix(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof ps.updateCoursePLOMatrix>[1]) =>
      ps.updateCoursePLOMatrix(programId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'course-plo-matrix'] });
      message.success('Cập nhật ma trận HP-PLO thành công');
    },
    onError: () => message.error('Không thể cập nhật ma trận'),
  });
}

/* ─── Assessment Plans ─── */
export function useAssessmentPlans(programId?: string) {
  return useQuery({
    queryKey: ['program', programId, 'assessment-plans'],
    queryFn: () => ps.getAssessmentPlans(programId!).then((r) => r.data),
    enabled: !!programId,
  });
}

export function useCreateAssessmentPlan(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof ps.createAssessmentPlan>[1]) =>
      ps.createAssessmentPlan(programId, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'assessment-plans'] });
      message.success('Thêm kế hoạch đánh giá thành công');
    },
    onError: () => message.error('Không thể thêm kế hoạch đánh giá'),
  });
}

export function useBulkUpsertAssessmentPlans(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof ps.bulkUpsertAssessmentPlans>[1]) =>
      ps.bulkUpsertAssessmentPlans(programId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'assessment-plans'] });
      message.success('Lưu kế hoạch đánh giá thành công');
    },
    onError: () => message.error('Không thể lưu kế hoạch đánh giá'),
  });
}

export function useDeleteAssessmentPlan(programId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => ps.deleteAssessmentPlan(programId, id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['program', programId, 'assessment-plans'] });
      message.success('Xóa kế hoạch đánh giá thành công');
    },
    onError: () => message.error('Không thể xóa kế hoạch đánh giá'),
  });
}

/* ─── PLO Coverage ─── */
export function usePLOCoverage(programId?: string) {
  return useQuery({
    queryKey: ['program', programId, 'plo-coverage'],
    queryFn: () => ps.getPLOCoverage(programId!).then((r) => r.data),
    enabled: !!programId,
  });
}
