# HUTECH Program V1 — OpenSpec Package
## Hướng dẫn sử dụng với Claude Code

---

## Bước 0: Chuẩn bị

### Yêu cầu
- Node.js 20+, Python 3.12+, Docker Desktop
- Claude Code (CLI) — `npm install -g @anthropic-ai/claude-code`
- Git

### Cài đặt OpenSpec
```bash
npm install -g @fission-ai/openspec
```

---

## Bước 1: Khởi tạo Project

### 1.1 Tạo project từ Cookiecutter Django
```bash
# Install cookiecutter
pip install cookiecutter

# Generate project
cookiecutter gh:cookiecutter/cookiecutter-django
# → Trả lời theo options trong openspec/changes/01-project-setup/design.md
```

### 1.2 Copy spec files vào project
```bash
cd hutech_program/
cp -r /path/to/hutech-program-spec/openspec ./
cp /path/to/hutech-program-spec/CLAUDE.md ./
```

### 1.3 Init OpenSpec
```bash
openspec init
```

---

## Bước 2: Thực hiện từng Change với Claude Code

### Quy trình cho mỗi change:

```bash
# 1. Đọc proposal
cat openspec/changes/01-project-setup/proposal.md

# 2. Vào Claude Code
claude

# 3. Dùng prompt pattern sau:
```

### Prompt Template cho Claude Code:

```
Đọc file CLAUDE.md để hiểu project conventions.
Đọc openspec/changes/{XX-change-name}/proposal.md để hiểu yêu cầu.
Đọc openspec/changes/{XX-change-name}/design.md để hiểu thiết kế.
Đọc openspec/changes/{XX-change-name}/tasks.md để biết danh sách tasks.

Thực hiện từng task trong tasks.md theo thứ tự.
Sau mỗi task, đánh dấu [x] trong tasks.md.
Commit sau mỗi nhóm tasks hoàn thành.
```

---

## Thứ tự triển khai chi tiết

### Change 01: Project Setup (2 ngày)
```bash
claude
> Đọc CLAUDE.md và openspec/changes/01-project-setup/
> Thực hiện tất cả tasks trong tasks.md
```
**Verify:** Django admin accessible, Swagger UI works, Frontend dev server runs

### Change 02: RBAC Module (3 ngày)
```bash
claude
> Đọc CLAUDE.md và openspec/changes/02-rbac-module/
> Bắt đầu từ task 1 (Models), sau đó task 2 (Permission system)...
```
**Verify:** Seed data created, all RBAC APIs work in Swagger, permission checks pass

### Change 03: CTĐT Core (3 ngày)
```bash
claude
> Đọc openspec/changes/03-ctdt-core/ 
> Implement models → serializers → viewsets → tests
```
**Verify:** TrainingProgram CRUD works, PLO/PO/PI nested APIs work

### Change 04: Course Management (2 ngày)
```bash
claude
> Đọc openspec/changes/04-ctdt-courses/
> Implement Course, ProgramCourse, prerequisites, semester plan
```
**Verify:** Course master list, ProgramCourse linking, prerequisite validation

### Change 05: Matrices (2 ngày)
```bash
claude
> Đọc openspec/changes/05-ctdt-matrices/
> Implement HP-PLO-PI matrix + Assessment plans
> Focus on bulk update performance
```
**Verify:** Matrix bulk read/write API, pivot format correct

### Change 06: Approval Workflow (3 ngày)
```bash
claude
> Đọc openspec/changes/06-approval-workflow/
> Implement WorkflowService state machine first, then APIs
```
**Verify:** Full DRAFT→PUBLISHED flow works, reject/revision works, versions created

### Change 07: Word Import (3 ngày)
```bash
claude
> Đọc openspec/changes/07-word-import/
> Copy file mẫu mo-ta-chuong-trinh-cu-nhan-NNTQ2025.docx vào test fixtures
> Implement parser table by table
```
**Verify:** Upload NNTQ2025 file → all data parsed correctly → preview → confirm → data in DB

### Change 08: Frontend Setup (2 ngày)
```bash
claude
> Đọc openspec/changes/08-frontend-setup/
> Scaffold React app, layout, routing, auth flow
```
**Verify:** Login works, sidebar navigation, permission guard

### Change 09: Frontend RBAC (2 ngày)
```bash
claude
> Đọc openspec/changes/09-frontend-rbac/
> Build user/role/department management pages
```
**Verify:** CRUD users, assign roles, department tree

### Change 10: Frontend CTĐT (5-7 ngày)
```bash
claude
> Đọc openspec/changes/10-frontend-ctdt/
> Implement phase by phase (7 phases)
> Phase 4 (HP-PLO-PI Matrix) là phức tạp nhất — dedicate 1-2 ngày
```
**Verify:** Full CTĐT management flow: create/import → edit all tabs → submit → approve

---

## Tips quan trọng

### Context Management
- Mỗi khi bắt đầu session Claude Code mới, luôn bắt đầu bằng:
  `Đọc CLAUDE.md trước`
- Khi implement change, chỉ load spec của change đó (không load tất cả)

### Incremental Development
- Không yêu cầu Claude Code implement toàn bộ 1 change cùng lúc
- Chia thành sessions: Models → APIs → Tests → Integration
- Commit thường xuyên

### Testing
- Yêu cầu Claude Code viết tests cùng lúc với implementation
- Run tests sau mỗi task group: `pytest hutech_program/rbac/tests/`

### Git Branching
```bash
git checkout -b feature/01-project-setup
# ... implement ...
git add . && git commit -m "feat(setup): init cookiecutter django project"
git checkout main && git merge feature/01-project-setup

git checkout -b feature/02-rbac-module
# ... implement ...
```

---

## Tổng thời gian ước tính: 25-30 ngày (solo vibe coding)

| # | Change | Thời gian |
|---|--------|-----------|
| 01 | Project Setup | 2 ngày |
| 02 | RBAC Module | 3 ngày |
| 03 | CTĐT Core | 3 ngày |
| 04 | Course Management | 2 ngày |
| 05 | Matrices | 2 ngày |
| 06 | Approval Workflow | 3 ngày |
| 07 | Word Import | 3 ngày |
| 08 | Frontend Setup | 2 ngày |
| 09 | Frontend RBAC | 2 ngày |
| 10 | Frontend CTĐT | 5-7 ngày |
