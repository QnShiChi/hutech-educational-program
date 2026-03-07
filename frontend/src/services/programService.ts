import apiClient from '@/services/apiClient';
import type {
  PaginatedResponse,
  TrainingProgram,
  ProgramObjective,
  ProgramLearningOutcome,
  PerformanceIndicator,
  KnowledgeBlock,
  ProgramCourse,
  CoursePrerequisite,
  SemesterPlanEntry,
  CoursePLOContribution,
  PLOAssessmentPlan,
  PLOCoverage,
} from '@/types/api';

/* ─── Query params ─── */
export interface ProgramFilters {
  search?: string;
  status?: string;
  department?: string;
  degree_level?: string;
  page?: number;
  page_size?: number;
}

/* ─── Programs ─── */
export const getPrograms = (params?: ProgramFilters) =>
  apiClient.get<PaginatedResponse<TrainingProgram>>('/programs/', { params });

export const getProgram = (id: string) =>
  apiClient.get<TrainingProgram>(`/programs/${id}/`);

export const createProgram = (data: Partial<TrainingProgram>) =>
  apiClient.post<TrainingProgram>('/programs/', data);

export const updateProgram = (id: string, data: Partial<TrainingProgram>) =>
  apiClient.put<TrainingProgram>(`/programs/${id}/`, data);

export const deleteProgram = (id: string) =>
  apiClient.delete(`/programs/${id}/`);

/* ─── Objectives (PO) ─── */
export const getObjectives = (programId: string) =>
  apiClient.get<ProgramObjective[]>(`/programs/${programId}/objectives/`);

export const createObjective = (programId: string, data: Partial<ProgramObjective>) =>
  apiClient.post<ProgramObjective>(`/programs/${programId}/objectives/`, data);

export const updateObjective = (programId: string, id: string, data: Partial<ProgramObjective>) =>
  apiClient.put<ProgramObjective>(`/programs/${programId}/objectives/${id}/`, data);

export const deleteObjective = (programId: string, id: string) =>
  apiClient.delete(`/programs/${programId}/objectives/${id}/`);

export const reorderObjectives = (programId: string, ids: string[]) =>
  apiClient.post(`/programs/${programId}/objectives/reorder/`, { order: ids });

/* ─── PLOs ─── */
export const getPLOs = (programId: string) =>
  apiClient.get<ProgramLearningOutcome[]>(`/programs/${programId}/plos/`);

export const createPLO = (programId: string, data: Partial<ProgramLearningOutcome>) =>
  apiClient.post<ProgramLearningOutcome>(`/programs/${programId}/plos/`, data);

export const updatePLO = (programId: string, id: string, data: Partial<ProgramLearningOutcome>) =>
  apiClient.put<ProgramLearningOutcome>(`/programs/${programId}/plos/${id}/`, data);

export const deletePLO = (programId: string, id: string) =>
  apiClient.delete(`/programs/${programId}/plos/${id}/`);

export const reorderPLOs = (programId: string, ids: string[]) =>
  apiClient.post(`/programs/${programId}/plos/reorder/`, { order: ids });

/* ─── PIs ─── */
export const getPIs = (programId: string, ploId: string) =>
  apiClient.get<PerformanceIndicator[]>(`/programs/${programId}/plos/${ploId}/pis/`);

export const createPI = (programId: string, ploId: string, data: Partial<PerformanceIndicator>) =>
  apiClient.post<PerformanceIndicator>(`/programs/${programId}/plos/${ploId}/pis/`, data);

export const updatePI = (programId: string, ploId: string, id: string, data: Partial<PerformanceIndicator>) =>
  apiClient.put<PerformanceIndicator>(`/programs/${programId}/plos/${ploId}/pis/${id}/`, data);

export const deletePI = (programId: string, ploId: string, id: string) =>
  apiClient.delete(`/programs/${programId}/plos/${ploId}/pis/${id}/`);

/* ─── PO-PLO Matrix ─── */
export const getPOPLOMatrix = (programId: string) =>
  apiClient.get<{ mappings: { po_id: string; plo_id: string }[] }>(`/programs/${programId}/po-plo-matrix/`);

export const updatePOPLOMatrix = (programId: string, data: { mappings: { po_id: string; plo_id: string }[] }) =>
  apiClient.put(`/programs/${programId}/po-plo-matrix/`, data);

/* ─── Knowledge Blocks ─── */
export const getKnowledgeBlocks = (programId: string) =>
  apiClient.get<KnowledgeBlock[]>(`/programs/${programId}/knowledge-blocks/`);

export const createKnowledgeBlock = (programId: string, data: Partial<KnowledgeBlock>) =>
  apiClient.post<KnowledgeBlock>(`/programs/${programId}/knowledge-blocks/`, data);

export const updateKnowledgeBlock = (programId: string, id: string, data: Partial<KnowledgeBlock>) =>
  apiClient.put<KnowledgeBlock>(`/programs/${programId}/knowledge-blocks/${id}/`, data);

export const deleteKnowledgeBlock = (programId: string, id: string) =>
  apiClient.delete(`/programs/${programId}/knowledge-blocks/${id}/`);

/* ─── Program Courses ─── */
export const getProgramCourses = (programId: string) =>
  apiClient.get<ProgramCourse[]>(`/programs/${programId}/courses/`);

export const addProgramCourse = (programId: string, data: { course_id: string; group_id?: string; semester?: number; is_required?: boolean }) =>
  apiClient.post<ProgramCourse>(`/programs/${programId}/courses/`, data);

export const bulkAddCourses = (programId: string, data: { courses: { course_id: string; group_id?: string }[] }) =>
  apiClient.post(`/programs/${programId}/courses/bulk/`, data);

export const updateProgramCourse = (programId: string, id: string, data: Partial<ProgramCourse>) =>
  apiClient.put<ProgramCourse>(`/programs/${programId}/courses/${id}/`, data);

export const removeProgramCourse = (programId: string, id: string) =>
  apiClient.delete(`/programs/${programId}/courses/${id}/`);

/* ─── Prerequisites ─── */
export const getPrerequisites = (programId: string) =>
  apiClient.get<CoursePrerequisite[]>(`/programs/${programId}/prerequisites/`);

export const updatePrerequisites = (programId: string, data: { prerequisites: { course: string; prerequisite: string }[] }) =>
  apiClient.put(`/programs/${programId}/prerequisites/`, data);

/* ─── Semester Plan ─── */
export const getSemesterPlan = (programId: string) =>
  apiClient.get<{ plan: SemesterPlanEntry[] }>(`/programs/${programId}/semester-plan/`);

export const updateSemesterPlan = (programId: string, data: { plan: SemesterPlanEntry[] }) =>
  apiClient.put(`/programs/${programId}/semester-plan/`, data);

/* ─── Course-PLO Matrix ─── */
export const getCoursePLOMatrix = (programId: string) =>
  apiClient.get<CoursePLOContribution[]>(`/programs/${programId}/course-plo-matrix/`);

export const updateCoursePLOMatrix = (programId: string, data: { contributions: Partial<CoursePLOContribution>[] }) =>
  apiClient.put(`/programs/${programId}/course-plo-matrix/`, data);

/* ─── Assessment Plans ─── */
export const getAssessmentPlans = (programId: string) =>
  apiClient.get<PLOAssessmentPlan[]>(`/programs/${programId}/assessment-plans/`);

export const createAssessmentPlan = (programId: string, data: Partial<PLOAssessmentPlan>) =>
  apiClient.post<PLOAssessmentPlan>(`/programs/${programId}/assessment-plans/`, data);

export const bulkUpsertAssessmentPlans = (programId: string, data: { plans: Partial<PLOAssessmentPlan>[] }) =>
  apiClient.post(`/programs/${programId}/assessment-plans/bulk/`, data);

export const updateAssessmentPlan = (programId: string, id: string, data: Partial<PLOAssessmentPlan>) =>
  apiClient.put<PLOAssessmentPlan>(`/programs/${programId}/assessment-plans/${id}/`, data);

export const deleteAssessmentPlan = (programId: string, id: string) =>
  apiClient.delete(`/programs/${programId}/assessment-plans/${id}/`);

/* ─── PLO Coverage Validation ─── */
export const getPLOCoverage = (programId: string) =>
  apiClient.get<PLOCoverage[]>(`/programs/${programId}/plo-coverage-validation/`);
