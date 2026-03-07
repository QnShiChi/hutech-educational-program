import apiClient from '@/services/apiClient';
import type {
  PaginatedResponse,
  WorkflowDetail,
  ProgramVersion,
  ApprovalWorkflow,
} from '@/types/api';

/* ─── Workflow Actions ─── */
export const submitProgram = (programId: string) =>
  apiClient.post<WorkflowDetail>(`/programs/${programId}/submit/`);

export const approveProgram = (programId: string, data?: { comment?: string }) =>
  apiClient.post<WorkflowDetail>(`/programs/${programId}/approve/`, data);

export const rejectProgram = (programId: string, data: { comment: string }) =>
  apiClient.post<WorkflowDetail>(`/programs/${programId}/reject/`, data);

export const getWorkflowStatus = (programId: string) =>
  apiClient.get<WorkflowDetail>(`/programs/${programId}/workflow/`);

/* ─── Versions ─── */
export const getVersions = (programId: string) =>
  apiClient.get<ProgramVersion[]>(`/programs/${programId}/versions/`);

export const getVersion = (programId: string, versionId: string) =>
  apiClient.get<ProgramVersion>(`/programs/${programId}/versions/${versionId}/`);

export const compareVersions = (programId: string, v1: string, v2: string) =>
  apiClient.get<Record<string, unknown>>(`/programs/${programId}/versions/compare/`, { params: { v1, v2 } });

export const rollbackVersion = (programId: string, versionId: string) =>
  apiClient.post(`/programs/${programId}/versions/${versionId}/rollback/`);

/* ─── Pending Approvals ─── */
export interface PendingApprovalFilters {
  page?: number;
  page_size?: number;
}

export const getPendingApprovals = (params?: PendingApprovalFilters) =>
  apiClient.get<PaginatedResponse<ApprovalWorkflow>>('/workflows/pending/', { params });
