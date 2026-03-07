# Tasks: Frontend CTĐT Module

## Phase 1: Foundation — Services, Hooks & Types

- [x] 1.1 Extend `types/api.ts` — add KnowledgeBlock, CoursePrerequisite, SemesterPlanEntry, CoursePLOContribution, PLOAssessmentPlan, ImportTask, WorkflowStep, WorkflowDetail, ProgramVersion interfaces
- [x] 1.2 Create `services/programService.ts` — typed Axios functions for programs, objectives, PLOs, PIs, PO-PLO matrix, knowledge blocks, program courses, prerequisites, semester plan, course-PLO matrix, assessment plans, PLO coverage
- [x] 1.3 Create `services/courseService.ts` — typed Axios for master courses and course groups
- [x] 1.4 Create `services/importService.ts` — upload, status, preview, confirm
- [x] 1.5 Create `services/workflowService.ts` — submit, approve, reject, workflow status, versions, compare, rollback, pending approvals
- [x] 1.6 Create `hooks/usePrograms.ts` — usePrograms, useProgram, useCreateProgram, useUpdateProgram, useDeleteProgram
- [x] 1.7 Create `hooks/useProgramDetail.ts` — useObjectives, usePLOs, usePIs, usePOPLOMatrix, useKnowledgeBlocks, useProgramCourses, useSemesterPlan, useCoursePLOMatrix, useAssessmentPlans + all corresponding mutations
- [x] 1.8 Create `hooks/useCourses.ts` — useCourses, useCourse, useCreateCourse, useUpdateCourse
- [x] 1.9 Create `hooks/useImport.ts` — useUploadImport, useImportStatus (with polling), useImportPreview, useConfirmImport
- [x] 1.10 Create `hooks/useWorkflow.ts` — useWorkflowStatus, useSubmitProgram, useApproveProgram, useRejectProgram, useVersions, useCompareVersions, useRollbackVersion

## Phase 2: Program List & Create

- [x] 2.1 Rewrite `ProgramsPage.tsx` — DataTable with server-side search, filter by status/department/degree_level, pagination; row click navigates to detail
- [x] 2.2 Rewrite `ProgramNewPage.tsx` — Ant Form for program creation with all required fields; on success navigate to `/programs/:id`

## Phase 3: Program Detail — Tabs 1 & 2

- [x] 3.1 Rewrite `ProgramDetailPage.tsx` — 7-tab layout with Ant Tabs; fetches program data, renders tab components
- [x] 3.2 Create `components/programs/GeneralInfoTab.tsx` — view/edit toggle form with StatusTag + workflow action buttons
- [x] 3.3 Create `components/programs/EditableList.tsx` — reusable sortable editable list (used for both PO and PLO)
- [x] 3.4 Create `components/programs/CheckboxMatrix.tsx` — PO-PLO checkbox matrix table
- [x] 3.5 Create `components/programs/ObjectivesOutcomesTab.tsx` — combines EditableList for PO, EditableList for PLO, CheckboxMatrix
- [x] 3.6 Install `@dnd-kit/core` and `@dnd-kit/sortable` dependencies

## Phase 4: Program Detail — Tab 3 (Courses)

- [x] 4.1 Create `components/programs/CourseSearchModal.tsx` — search master courses, select, add to program
- [x] 4.2 Create `components/programs/CoursesTab.tsx` — knowledge blocks expandable sections, courses table per block, credit summary, add/remove course

## Phase 5: Program Detail — Tab 4 (HP-PLO-PI Matrix)

- [x] 5.1 Create `components/programs/CoursePLOMatrix.tsx` — 2-level header (PLO → PI), editable dropdown cells, color coding, sticky headers
- [x] 5.2 Add bulk save logic with debounce for CoursePLOMatrix
- [x] 5.3 Add Excel export button (SheetJS `xlsx`)
- [x] 5.4 Install `xlsx` dependency

## Phase 6: Program Detail — Tab 5 (Semester Plan)

- [x] 6.1 Create `components/programs/SemesterPlanTab.tsx` — 8-column card layout, drag-drop courses between semesters with @dnd-kit
- [x] 6.2 Add prerequisite validation indicators (warning icon if course placed before prerequisite)
- [x] 6.3 Add per-semester credit summary + save button

## Phase 7: Program Detail — Tab 6 & 7 (Assessment & Workflow)

- [x] 7.1 Create `components/programs/AssessmentPlanTab.tsx` — editable table grouped by PLO with inline editing + bulk save
- [x] 7.2 Create `components/programs/WorkflowTab.tsx` — Ant Steps vertical timeline + action buttons (Submit/Approve/Reject) + reject modal
- [x] 7.3 Add version history table with compare button to WorkflowTab

## Phase 8: Master Courses & Import

- [x] 8.1 Rewrite `CoursesPage.tsx` — DataTable for master courses with search, create modal
- [x] 8.2 Rewrite `CourseDetailPage.tsx` — Ant Form for course view/edit
- [x] 8.3 Rewrite `ProgramImportPage.tsx` — Upload.Dragger + progress polling + preview with collapsible sections + confirm/cancel

## Phase 9: Integration & Polish

- [x] 9.1 Wrap all write actions with `<PermissionGuard>` across all new pages/tabs
- [x] 9.2 Verify routing in `App.tsx` — ensure all program/course/import routes work correctly
- [x] 9.3 Verify build — `npm run build` must pass with zero errors
