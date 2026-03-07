# Proposal: Frontend CTĐT Module

## Summary
Implement toàn bộ giao diện quản lý CTĐT — module phức tạp nhất với nhiều trang, tabs, và component đặc biệt (ma trận editable, kế hoạch HK).

## Pages

### 1. Danh sách CTĐT (/programs)
- Table: Tên ngành, Mã ngành, Trình độ, Khoa, Tín chỉ, Trạng thái, Phiên bản
- Filter: status, department, education_level
- Search: tên ngành, mã ngành
- Actions: Tạo mới, Import Word, Xem chi tiết

### 2. Import Word (/programs/import)
- Upload zone (drag & drop)
- Progress indicator
- Preview parsed data (collapsible sections)
- Error/warning report
- Confirm button to save

### 3. Chi tiết CTĐT (/programs/:id) — Tab Layout

#### Tab 1: Thông tin chung
- Form display/edit: tên, mã, trình độ, tín chỉ, thời gian...
- Mục tiêu chung (rich text)
- Decision info (số QĐ, ngày)
- Status badge + workflow actions (Submit, etc.)

#### Tab 2: Mục tiêu & Chuẩn đầu ra
- Section PO: Editable list (code + description), drag-to-reorder
- Section PLO: Editable list (code + description + Bloom level), drag-to-reorder
- Ma trận PO-PLO: Interactive checkbox matrix table
  - Rows = PO, Columns = PLO (or vice versa)
  - Click cell to toggle X/empty

#### Tab 3: Khối kiến thức & Học phần
- Tree view of Knowledge Blocks (with credit summary)
- Courses table within each block
- "Thêm học phần" button → search existing or create new
- Prerequisites config per course (select from dropdown)
- Bottom summary: tổng tín chỉ BB/TC, kiểm tra vs total_credits

#### Tab 4: Ma trận HP-PLO-PI
- COMPLEX COMPONENT — largest table in the system
- Columns: PI codes grouped under PLO headers (2-level header)
  PLO1          | PLO2         | ...
  PI.1.1 PI.1.2 | PI.2.1 PI.2.2 | ...
- Rows: Courses (mã HP, tên HP)
- Cells: Editable dropdown (-, 1, 2, 3)
- Color coding: 1=green-100, 2=yellow-100, 3=orange-100
- Sticky header + sticky first 2 columns
- Virtual scrolling if >50 rows (performance)
- Bulk save with debounce
- Export to Excel button

#### Tab 5: Kế hoạch giảng dạy
- 8 columns = 8 HK
- Each column shows courses assigned to that semester
- Drag-drop courses between semesters
- Per-semester credit total
- Validation: prerequisites must be in earlier semester

#### Tab 6: Kế hoạch đánh giá PLO
- Table: PLO → PI → HP lấy mẫu → Minh chứng → Công cụ → Tiêu chuẩn → Lịch
- Editable inline (text fields + dropdowns)
- Group by PLO

#### Tab 7: Phê duyệt & Lịch sử
- Workflow timeline (vertical steps)
- Each step: status, approver, date, comment
- Action buttons: Submit / Approve / Reject (based on role + current step)
- Reject: modal with required comment
- Version history table
- Version comparison: side-by-side diff

## Tasks

### Phase 1: Core Pages
- [ ] 1.1 Program list page with filters
- [ ] 1.2 Program create form (basic info)
- [ ] 1.3 Program detail page with tab layout
- [ ] 1.4 Tab 1: General info form (view/edit mode)
- [ ] 1.5 Custom hooks: useProgram, usePrograms, useProgramMutations

### Phase 2: PO/PLO/Matrix
- [ ] 2.1 Tab 2: PO list (editable, sortable)
- [ ] 2.2 Tab 2: PLO list (editable, sortable, Bloom level)
- [ ] 2.3 Tab 2: PO-PLO checkbox matrix component
- [ ] 2.4 Custom hooks: usePOs, usePLOs, usePOPLOMatrix

### Phase 3: Courses
- [ ] 3.1 Tab 3: Knowledge block tree
- [ ] 3.2 Tab 3: Courses table per block
- [ ] 3.3 Course search/add modal (from master list)
- [ ] 3.4 Prerequisites config modal
- [ ] 3.5 Credit summary component
- [ ] 3.6 Master course list page (/courses)

### Phase 4: HP-PLO-PI Matrix
- [ ] 4.1 Matrix component: 2-level header (PLO → PI)
- [ ] 4.2 Editable cells with dropdown
- [ ] 4.3 Color coding
- [ ] 4.4 Sticky headers + first columns
- [ ] 4.5 Virtual scroll for large datasets
- [ ] 4.6 Bulk save logic
- [ ] 4.7 Export to Excel (SheetJS)

### Phase 5: Semester Plan
- [ ] 5.1 8-column semester view
- [ ] 5.2 Drag-drop between semesters (dnd-kit or react-beautiful-dnd)
- [ ] 5.3 Credit sum per semester
- [ ] 5.4 Prerequisite validation indicators

### Phase 6: Assessment & Workflow
- [ ] 6.1 Tab 6: Assessment plan table (editable)
- [ ] 6.2 Tab 7: Workflow timeline component
- [ ] 6.3 Tab 7: Submit/Approve/Reject actions
- [ ] 6.4 Tab 7: Version history + comparison

### Phase 7: Import
- [ ] 7.1 Upload page with drag-drop zone
- [ ] 7.2 Progress polling
- [ ] 7.3 Preview with collapsible sections
- [ ] 7.4 Confirm/cancel flow
