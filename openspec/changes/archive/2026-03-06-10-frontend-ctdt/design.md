# Design: Frontend CTĐT Module

## Architecture

### Tech Stack

- **React 18** + **TypeScript** + **Vite**
- **Ant Design 5** (vi_VN locale) — Tabs, Table, Form, Modal, Tree, Upload, Tag, Select
- **@tanstack/react-query** for server-state (caching, pagination, mutations)
- **Zustand** (`authStore`) for auth state & permission checks
- **Axios** (`apiClient`) with JWT interceptors
- **@dnd-kit/core** + **@dnd-kit/sortable** for drag-drop (PO/PLO reorder, semester plan)
- **xlsx** (SheetJS) for Excel export

### Directory Layout

```
frontend/src/
├── pages/
│   ├── ProgramsPage.tsx        # rewrite stub → full DataTable with filters
│   ├── ProgramNewPage.tsx      # rewrite stub → create form
│   ├── ProgramDetailPage.tsx   # rewrite stub → 7-tab layout
│   ├── ProgramImportPage.tsx   # rewrite stub → upload + preview + confirm
│   ├── CoursesPage.tsx         # rewrite stub → master course list
│   └── CourseDetailPage.tsx    # rewrite stub → course edit form
├── components/
│   ├── programs/
│   │   ├── GeneralInfoTab.tsx       # Tab 1: program info form
│   │   ├── ObjectivesOutcomesTab.tsx # Tab 2: PO/PLO/matrix
│   │   ├── EditableList.tsx         # Reusable editable+sortable list (PO, PLO)
│   │   ├── CheckboxMatrix.tsx       # PO-PLO checkbox matrix
│   │   ├── CoursesTab.tsx           # Tab 3: knowledge blocks + courses
│   │   ├── CourseSearchModal.tsx    # Modal to search & add courses
│   │   ├── CoursePLOMatrix.tsx      # Tab 4: HP-PLO-PI pivot table
│   │   ├── SemesterPlanTab.tsx      # Tab 5: 8-column drag-drop
│   │   ├── AssessmentPlanTab.tsx    # Tab 6: PLO assessment plan
│   │   └── WorkflowTab.tsx          # Tab 7: approval workflow + versions
│   └── ...existing
├── services/
│   ├── programService.ts      # NEW: programs API calls
│   ├── courseService.ts       # NEW: courses API calls
│   ├── importService.ts       # NEW: import API calls
│   └── workflowService.ts    # NEW: workflow/version API calls
├── hooks/
│   ├── usePrograms.ts         # NEW: react-query hooks for programs
│   ├── useProgramDetail.ts   # NEW: hooks for PO, PLO, PI, matrix, etc.
│   ├── useCourses.ts         # NEW: hooks for master courses + program courses
│   ├── useImport.ts          # NEW: hooks for import flow
│   └── useWorkflow.ts        # NEW: hooks for workflow actions + versions
└── types/
    └── api.ts                 # extend with ImportTask, WorkflowStep, Version, etc.
```

## Component Design

### 1. ProgramsPage (`/programs`)

- **PageHeader** with "Tạo mới" button + "Import Word" button
- **DataTable** with server-side pagination via react-query
- Columns: Mã ngành, Tên ngành, Trình độ (Tag), Hình thức, Tín chỉ, Trạng thái (StatusTag), Phiên bản
- Search by name/code (server-side `?search=`)
- Filter by status (Select), department (Select), degree_level (Select)
- Row click → navigate to ProgramDetailPage

### 2. ProgramNewPage (`/programs/new`)

- **Ant Design Form** with required fields: code, name, name_en, department_id, degree_level, training_mode, total_credits, duration_years
- On success → navigate to `/programs/:id`

### 3. ProgramDetailPage (`/programs/:id`) — 7-Tab Layout

Uses `<Tabs>` with the following tabs:

#### Tab 1: GeneralInfoTab — Thông tin chung

- View/edit toggle (Ant Form with `disabled` prop)
- Fields: code, name, name_en, department, degree_level, training_mode, total_credits, duration_years, effective_year, version
- Status badge (StatusTag) + workflow action buttons inline
- Edit button guarded by `programs.manage_programs`

#### Tab 2: ObjectivesOutcomesTab — Mục tiêu & CĐR

- **Section PO**: `<EditableList>` with code + description, drag-to-reorder
  - API: `GET/POST /programs/:id/objectives/`, `POST .../reorder/`
- **Section PLO**: `<EditableList>` with code + description + bloom_level, drag-to-reorder
  - API: `GET/POST /programs/:id/plos/`, `POST .../reorder/`
- **Divider**
- **PO-PLO Matrix**: `<CheckboxMatrix>`
  - Rows = PO, Columns = PLO; click cell to toggle
  - API: `GET/PUT /programs/:id/po-plo-matrix/`
  - Payload: `{ mappings: [{ po_id, plo_id }] }`

#### Tab 3: CoursesTab — Khối kiến thức & Học phần

- **Knowledge Block list** (expandable sections, each showing courses)
  - API: `GET /programs/:id/knowledge-blocks/`
- **Add Knowledge Block** button + inline form
- **Courses table** per block (Ant Table nested)
  - Columns: Mã HP, Tên HP, Tín chỉ, Loại, BB/TC, HK
  - Add course: opens `<CourseSearchModal>` → `POST /programs/:id/courses/`
  - Remove: `DELETE /programs/:id/courses/:courseId/`
- **Credit summary** at bottom (total BB, TC, grand total vs program total_credits)
- **Course search modal**: searches from master course list `GET /courses/?search=`

#### Tab 4: CoursePLOMatrix — Ma trận HP-PLO-PI

- **2-level column header**: PLO → PI beneath each PLO
  - Build from `GET /programs/:id/plos/` and each PLO's PIs
- **Rows**: program courses from `GET /programs/:id/courses/`
- **Cells**: Ant Select with options: —, I, T, R (or 1, 2, 3)
- **Color coding**: I=green, T=yellow, R=orange, empty=white
- Sticky header + first 2 columns (CSS `position: sticky`)
- Virtual scrolling: not needed initially (Ant Table can handle ~100 rows)
- **Bulk save**: collect dirty cells, debounce 500ms, `PUT /programs/:id/course-plo-matrix/`
- **Export to Excel**: SheetJS `xlsx.writeFile()` button

#### Tab 5: SemesterPlanTab — Kế hoạch giảng dạy

- **8 columns** = HK 1–8 rendered as Ant Card columns
- Each column lists courses assigned to that semester
- **Drag-drop** between columns using @dnd-kit
- Per-semester credit total displayed
- Prerequisite check: visual warning if a course is placed before its prerequisite
- **Save**: `PUT /programs/:id/semester-plan/` with `{ plan: [{ course_id, semester }] }`

#### Tab 6: AssessmentPlanTab — Kế hoạch đánh giá PLO

- **Editable table** grouped by PLO
- Columns: PLO, PI, HP lấy mẫu (Select), Minh chứng (text), Công cụ (text), Tiêu chuẩn (text), Lịch (text)
- API: `GET/POST /programs/:id/assessment-plans/`, `POST .../bulk/`
- Inline editing with save row / save all

#### Tab 7: WorkflowTab — Phê duyệt & Lịch sử

- **Workflow timeline** (Ant Steps vertical)
  - API: `GET /programs/:id/workflow/`
  - Each step shows: step name, status, approver, date, comment
- **Action buttons**: Submit / Approve / Reject (role-based via permissions)
  - Submit: `POST /programs/:id/submit/`
  - Approve: `POST /programs/:id/approve/`
  - Reject: `POST /programs/:id/reject/` (modal with required comment)
- **Version history** table below timeline
  - API: `GET /programs/:id/versions/`
  - Columns: Version, Snapshot date, Created by
  - Compare button: `GET /programs/:id/versions/compare/?v1=...&v2=...`

### 4. ProgramImportPage (`/programs/import`)

- **Upload zone** using Ant Upload.Dragger (accepts `.docx`)
- Upload: `POST /imports/training-program/` with FormData
- **Progress polling**: `GET /imports/:id/status/` every 2s until complete
- **Preview**: `GET /imports/:id/preview/` → collapsible sections showing parsed data
- **Confirm**: `POST /imports/:id/confirm/` → navigate to new program

### 5. CoursesPage (`/courses`)

- **DataTable** with master course list `GET /courses/`
- Columns: Mã HP, Tên HP, Tín chỉ, LT, TH, Tự học, Loại (Tag)
- Search by code/name
- Create course modal (admin only)
- Row click → CourseDetailPage

### 6. CourseDetailPage (`/courses/:id`)

- **Form** for code, name, name_en, credits, theory_hours, practice_hours, self_study_hours, course_type, description
- API: `GET/PUT /courses/:id/`

## API Service Layer

### `programService.ts`

```typescript
// Programs
getPrograms(params)         → GET /programs/
getProgram(id)              → GET /programs/{id}/
createProgram(data)         → POST /programs/
updateProgram(id, data)     → PUT /programs/{id}/
deleteProgram(id)           → DELETE /programs/{id}/

// Objectives (PO)
getObjectives(programId)    → GET /programs/{id}/objectives/
createObjective(pid, data)  → POST /programs/{id}/objectives/
updateObjective(pid, id, d) → PUT /programs/{id}/objectives/{id}/
deleteObjective(pid, id)    → DELETE /programs/{id}/objectives/{id}/
reorderObjectives(pid, ids) → POST /programs/{id}/objectives/reorder/

// PLOs
getPLOs(programId)          → GET /programs/{id}/plos/
createPLO(pid, data)        → POST /programs/{id}/plos/
updatePLO(pid, id, data)    → PUT /programs/{id}/plos/{id}/
deletePLO(pid, id)          → DELETE /programs/{id}/plos/{id}/
reorderPLOs(pid, ids)       → POST /programs/{id}/plos/reorder/

// PIs (under PLO)
getPIs(pid, ploId)          → GET /programs/{pid}/plos/{ploId}/pis/
createPI(pid, ploId, data)  → POST .../pis/
updatePI(pid, ploId, id, d) → PUT .../pis/{id}/
deletePI(pid, ploId, id)    → DELETE .../pis/{id}/

// PO-PLO Matrix
getPOPLOMatrix(pid)         → GET /programs/{id}/po-plo-matrix/
updatePOPLOMatrix(pid, d)   → PUT /programs/{id}/po-plo-matrix/

// Knowledge Blocks
getKnowledgeBlocks(pid)     → GET /programs/{id}/knowledge-blocks/
createKnowledgeBlock(pid,d) → POST .../knowledge-blocks/
updateKnowledgeBlock(...)   → PUT .../knowledge-blocks/{id}/
deleteKnowledgeBlock(...)   → DELETE .../knowledge-blocks/{id}/

// Program Courses
getProgramCourses(pid)      → GET /programs/{id}/courses/
addProgramCourse(pid, data) → POST /programs/{id}/courses/
bulkAddCourses(pid, data)   → POST /programs/{id}/courses/bulk/
updateProgramCourse(...)    → PUT /programs/{id}/courses/{id}/
removeProgramCourse(...)    → DELETE /programs/{id}/courses/{id}/

// Prerequisites
getPrerequisites(pid)       → GET /programs/{id}/prerequisites/
updatePrerequisites(pid, d) → PUT /programs/{id}/prerequisites/

// Semester Plan
getSemesterPlan(pid)        → GET /programs/{id}/semester-plan/
updateSemesterPlan(pid, d)  → PUT /programs/{id}/semester-plan/

// Course-PLO Matrix
getCoursePLOMatrix(pid)     → GET /programs/{id}/course-plo-matrix/
updateCoursePLOMatrix(pid,d)→ PUT /programs/{id}/course-plo-matrix/

// Assessment Plans
getAssessmentPlans(pid)     → GET /programs/{id}/assessment-plans/
createAssessmentPlan(pid,d) → POST /programs/{id}/assessment-plans/
bulkUpsertAssessmentPlans(p)→ POST /programs/{id}/assessment-plans/bulk/
updateAssessmentPlan(...)   → PUT .../assessment-plans/{id}/
deleteAssessmentPlan(...)   → DELETE .../assessment-plans/{id}/

// PLO Coverage Validation
getPLOCoverage(pid)         → GET /programs/{id}/plo-coverage-validation/
```

### `courseService.ts`

```typescript
getCourses(params)          → GET /courses/
getCourse(id)               → GET /courses/{id}/
createCourse(data)          → POST /courses/
updateCourse(id, data)      → PUT /courses/{id}/
getCourseGroups(params)     → GET /course-groups/
```

### `importService.ts`

```typescript
uploadImport(file)          → POST /imports/training-program/ (FormData)
getImportStatus(id)         → GET /imports/{id}/status/
getImportPreview(id)        → GET /imports/{id}/preview/
confirmImport(id)           → POST /imports/{id}/confirm/
```

### `workflowService.ts`

```typescript
submitProgram(pid)          → POST /programs/{pid}/submit/
approveProgram(pid, data)   → POST /programs/{pid}/approve/
rejectProgram(pid, data)    → POST /programs/{pid}/reject/
getWorkflowStatus(pid)      → GET /programs/{pid}/workflow/
getVersions(pid)            → GET /programs/{pid}/versions/
getVersion(pid, vid)        → GET /programs/{pid}/versions/{vid}/
compareVersions(pid, v1, v2)→ GET /programs/{pid}/versions/compare/?v1=...&v2=...
rollbackVersion(pid, vid)   → POST /programs/{pid}/versions/{vid}/rollback/
getPendingApprovals(params) → GET /workflows/pending/
```

## React-Query Hooks

```typescript
// usePrograms.ts
usePrograms(filters)        → useQuery(['programs', filters], ...)
useProgram(id)              → useQuery(['program', id], ...)
useCreateProgram()          → useMutation(... onSuccess → invalidate 'programs')
useUpdateProgram()          → useMutation(...)
useDeleteProgram()          → useMutation(...)

// useProgramDetail.ts (nested resources)
useObjectives(pid)          → useQuery(['program', pid, 'objectives'], ...)
useCreateObjective(pid)     → useMutation(... onSuccess → invalidate objectives)
useUpdateObjective(pid)     → useMutation(...)
useDeleteObjective(pid)     → useMutation(...)
useReorderObjectives(pid)   → useMutation(...)
// ... same pattern for PLOs, PIs
usePOPLOMatrix(pid)         → useQuery(['program', pid, 'po-plo-matrix'], ...)
useUpdatePOPLOMatrix(pid)   → useMutation(...)
useKnowledgeBlocks(pid)     → useQuery(['program', pid, 'knowledge-blocks'], ...)
useProgramCourses(pid)      → useQuery(['program', pid, 'courses'], ...)
useAddProgramCourse(pid)    → useMutation(...)
useSemesterPlan(pid)        → useQuery(['program', pid, 'semester-plan'], ...)
useCoursePLOMatrix(pid)     → useQuery(['program', pid, 'course-plo-matrix'], ...)
useAssessmentPlans(pid)     → useQuery(['program', pid, 'assessment-plans'], ...)

// useCourses.ts
useCourses(filters)         → useQuery(['courses', filters], ...)
useCourse(id)               → useQuery(['course', id], ...)
useCreateCourse()           → useMutation(...)
useUpdateCourse()           → useMutation(...)

// useImport.ts
useUploadImport()           → useMutation(...)
useImportStatus(id)         → useQuery(['import', id], ..., refetchInterval: 2000)
useImportPreview(id)        → useQuery(['import-preview', id], ...)
useConfirmImport()          → useMutation(...)

// useWorkflow.ts
useWorkflowStatus(pid)      → useQuery(['program', pid, 'workflow'], ...)
useSubmitProgram(pid)       → useMutation(...)
useApproveProgram(pid)      → useMutation(...)
useRejectProgram(pid)       → useMutation(...)
useVersions(pid)            → useQuery(['program', pid, 'versions'], ...)
useCompareVersions(pid)     → useQuery(['program', pid, 'versions', 'compare'], ...)
useRollbackVersion(pid)     → useMutation(...)
```

## Type Extensions

Add to `types/api.ts`:

```typescript
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
  course: string; // ProgramCourse id
  prerequisite: string; // ProgramCourse id
}

/* ─── Semester Plan ─── */
export interface SemesterPlanEntry {
  course_id: string;
  semester: number;
}

/* ─── Course-PLO Contribution ─── */
export type ContributionLevel = "I" | "T" | "R" | "";
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
export type ImportStatus = "pending" | "processing" | "completed" | "failed";
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
```

## Permission Guards

All CTĐT pages use `<PermissionGuard>` for write actions:

- Program CRUD/edit: `programs.manage_programs`
- Course CRUD: `programs.manage_courses`
- Workflow submit: `programs.submit_program`
- Workflow approve: `programs.approve_program`
- Import: `programs.manage_programs`

List/view actions available to authenticated users with `programs.view_programs`.
