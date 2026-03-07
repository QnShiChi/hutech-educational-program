import apiClient from '@/services/apiClient';
import type { ImportTask } from '@/types/api';

/* ─── Import ─── */
export const uploadImport = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post<ImportTask>('/imports/training-program/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getImportStatus = (id: string) =>
  apiClient.get<ImportTask>(`/imports/${id}/status/`);

export const getImportPreview = (id: string) =>
  apiClient.get<Record<string, unknown>>(`/imports/${id}/preview/`);

export const confirmImport = (id: string) =>
  apiClient.post<ImportTask>(`/imports/${id}/confirm/`);
