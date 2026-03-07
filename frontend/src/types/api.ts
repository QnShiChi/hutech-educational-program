/* ─── Pagination ─── */
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/* ─── Auth ─── */
export interface TokenPair {
  access: string;
  refresh: string;
}

/* ─── RBAC ─── */
export interface Permission {
  id: number;
  codename: string;
  name: string;
}

export interface Role {
  id: string;
  code: string;
  name: string;
  description: string;
  level: number;
  permissions: Permission[];
  permission_ids?: number[];
  is_system_role: boolean;
  user_count?: number;
  created_at: string;
}

export interface Department {
  id: string;
  name: string;
  name_en?: string;
  code: string;
  type?: string;
  parent: string | null;
  head: string | null;
  is_active: boolean;
  user_count?: number;
}

export interface UserRole {
  id: string;
  user: string;
  role: string;
  role_name: string;
  department: string;
  department_name: string;
  assigned_by: string | null;
  created_at: string;
}

export interface DepartmentTree extends Omit<Department, 'parent' | 'head'> {
  children: DepartmentTree[];
}

export interface AuditLog {
  id: string;
  user: string | null;
  user_name: string | null;
  user_username: string | null;
  action: string;
  entity_type: string;
  entity_id: string;
  old_data: Record<string, unknown> | null;
  new_data: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface PermissionItem {
  id: number;
  code: string;
  name: string;
  module: string;
  description: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  name: string;
  first_name: string;
  last_name: string;
  employee_id: string | null;
  phone: string;
  department: Department | null;
  department_id: string | null;
  roles: Role[];
  permissions: string[];
  is_active: boolean;
  date_joined: string;
}

/* ─── Programs / CTĐT ─── */
export type ProgramStatus =
  | 'draft'
  | 'review'
  | 'approved'
  | 'active'
  | 'archived';

export type DegreeLevel =
  | 'cu_nhan'
  | 'thac_si'
  | 'tien_si'
  | 'cao_dang';

export type TrainingMode = 'chinh_quy' | 'lien_thong' | 'tu_xa';

export interface TrainingProgram {
  id: string;
  code: string;
  name: string;
  name_en: string;
  department: Department | null;
  department_id: string | null;
  degree_level: DegreeLevel;
  training_mode: TrainingMode;
  total_credits: number;
  duration_years: number;
  status: ProgramStatus;
  version: string;
  effective_year: number | null;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProgramObjective {
  id: string;
  program: string;
  code: string;
  description: string;
  order: number;
}

export interface ProgramLearningOutcome {
  id: string;
  program: string;
  code: string;
  description: string;
  bloom_level: string;
  order: number;
}

export interface PerformanceIndicator {
  id: string;
  plo: string;
  code: string;
  description: string;
  order: number;
}

/* ─── Courses ─── */
export type CourseType =
  | 'dai_cuong'
  | 'co_so_nganh'
  | 'chuyen_nganh'
  | 'tu_chon'
  | 'thuc_tap'
  | 'tot_nghiep';

export interface CourseGroup {
  id: string;
  program: string;
  name: string;
  min_credits: number;
  max_credits: number | null;
  order: number;
}

export interface Course {
  id: string;
  code: string;
  name: string;
  name_en: string;
  credits: number;
  theory_hours: number;
  practice_hours: number;
  self_study_hours: number;
  course_type: CourseType;
  description: string;
}

export interface ProgramCourse {
  id: string;
  program: string;
  course: Course;
  group: CourseGroup | null;
  semester: number;
  is_required: boolean;
}

/* ─── Workflows ─── */
export type ApprovalStatus =
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'returned';

export interface ApprovalWorkflow {
  id: string;
  program: string;
  current_step: number;
  status: ApprovalStatus;
  created_by: string;
  created_at: string;
}

/* ─── Notifications ─── */
export interface Notification {
  id: string;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  created_at: string;
  link: string | null;
}

/* ─── Enums (matching backend choices) ─── */
export const PROGRAM_STATUS_LABELS: Record<ProgramStatus, string> = {
  draft: 'Bản nháp',
  review: 'Đang duyệt',
  approved: 'Đã duyệt',
  active: 'Đang áp dụng',
  archived: 'Lưu trữ',
};

export const DEGREE_LEVEL_LABELS: Record<DegreeLevel, string> = {
  cu_nhan: 'Cử nhân',
  thac_si: 'Thạc sĩ',
  tien_si: 'Tiến sĩ',
  cao_dang: 'Cao đẳng',
};

export const TRAINING_MODE_LABELS: Record<TrainingMode, string> = {
  chinh_quy: 'Chính quy',
  lien_thong: 'Liên thông',
  tu_xa: 'Từ xa',
};

export const COURSE_TYPE_LABELS: Record<CourseType, string> = {
  dai_cuong: 'Đại cương',
  co_so_nganh: 'Cơ sở ngành',
  chuyen_nganh: 'Chuyên ngành',
  tu_chon: 'Tự chọn',
  thuc_tap: 'Thực tập',
  tot_nghiep: 'Tốt nghiệp',
};

export const APPROVAL_STATUS_LABELS: Record<ApprovalStatus, string> = {
  pending: 'Đang chờ',
  approved: 'Đã duyệt',
  rejected: 'Từ chối',
  returned: 'Trả lại',
};

/* ─── Knowledge Blocks ─── */
export interface KnowledgeBlock {
  id: string;
  program: string;
  name: string;
  min_credits: number;
  max_credits: number | null;
  order: number;
}

/* ─── Prerequisites ─── */
export interface CoursePrerequisite {
  id: string;
  course: string;
  prerequisite: string;
}

/* ─── Semester Plan ─── */
export interface SemesterPlanEntry {
  course_id: string;
  semester: number;
}

/* ─── Course-PLO Contribution ─── */
export type ContributionLevel = 'I' | 'T' | 'R' | '';
export interface CoursePLOContribution {
  id: string;
  program_course: string;
  pi: string;
  level: ContributionLevel;
}

/* ─── Assessment Plans ─── */
export interface PLOAssessmentPlan {
  id: string;
  program: string;
  plo: string;
  pi: string | null;
  sample_course: string | null;
  evidence: string;
  tool: string;
  standard: string;
  schedule: string;
}

/* ─── Import ─── */
export type ImportStatus = 'pending' | 'processing' | 'completed' | 'failed';
export interface ImportTask {
  id: string;
  file_name: string;
  status: ImportStatus;
  progress: number;
  error_message: string | null;
  result_program: string | null;
  created_at: string;
  completed_at: string | null;
}

/* ─── Workflow Detail ─── */
export interface WorkflowStep {
  step: number;
  name: string;
  status: ApprovalStatus;
  approver: string | null;
  approver_name: string | null;
  decided_at: string | null;
  comment: string | null;
}

export interface WorkflowDetail {
  id: string;
  program: string;
  current_step: number;
  status: ApprovalStatus;
  steps: WorkflowStep[];
  created_by: string;
  created_at: string;
}

/* ─── Program Version ─── */
export interface ProgramVersion {
  id: string;
  program: string;
  version_number: number;
  snapshot: Record<string, unknown>;
  created_by: string | null;
  created_at: string;
  comment: string;
}

/* ─── PLO Coverage Validation ─── */
export interface PLOCoverage {
  plo_id: string;
  plo_code: string;
  covered: boolean;
  course_count: number;
}
