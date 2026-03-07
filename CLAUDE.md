# HUTECH Program - CLAUDE.md

## Project Overview
HUTECH Program là hệ thống quản lý chương trình đào tạo (CTĐT) cho Trường Đại học Công nghệ TP.HCM (HUTECH). Hệ thống số hóa toàn bộ quy trình quản lý, phê duyệt, theo dõi và đánh giá CTĐT theo chuẩn OBE (Outcome-Based Education).

**V1 Scope:** 2 module chính:
1. Module Phân quyền & Vai trò (RBAC)
2. Module Quản lý toàn diện Chương trình đào tạo

## Tech Stack
- **Backend:** Django 5.x + Django REST Framework
- **Project Template:** Cookiecutter Django
- **Database:** PostgreSQL 16
- **Cache/Queue:** Redis + Celery
- **Frontend:** React 18 + TypeScript + Vite
- **UI Library:** Ant Design 5.x
- **State Management:** Zustand
- **API Client:** Axios + TanStack Query
- **Auth:** JWT (SimpleJWT)
- **Containerization:** Docker Compose (from Cookiecutter Django)
- **Language:** Python 3.12, Node.js 20+

## Development Methodology
- We follow **Spec-Driven Development (SDD)** using OpenSpec.
- Specs in `openspec/` are the **source of truth**.
- Always read the relevant spec BEFORE implementing.
- Each change has: proposal.md → specs/ → design.md → tasks.md

## Project Conventions

### Python/Django
- Use UUID primary keys for all models
- Models inherit from `TimeStampedModel` (created_at, updated_at)
- Use `django-model-utils` for StatusField, TimeStampedModel
- Soft delete via `is_active` field (not hard delete)
- All API responses use consistent format: `{"status": "success/error", "data": {...}, "message": ""}`
- Use `django-filter` for all list endpoints
- Vietnamese field names in comments, English in code
- Type hints on all function signatures
- Docstrings in Vietnamese for business logic explanation

### API Conventions
- RESTful endpoints under `/api/v1/`
- JWT auth header: `Authorization: Bearer <token>`
- Pagination: `?page=1&page_size=20`
- Search: `?search=keyword`
- Filter: `?status=DRAFT&department=uuid`
- Ordering: `?ordering=-created_at`
- All dates in ISO 8601 format
- All IDs are UUIDs

### Frontend/React
- Functional components with hooks only
- TypeScript strict mode
- Ant Design components as base
- Tailwind for custom styling
- File naming: PascalCase for components, camelCase for utils
- API calls through custom hooks (useQuery/useMutation)
- Path aliases: `@/` maps to `src/`

### Git Conventions
- Branch: `feature/01-project-setup`, `feature/02-rbac-module`, etc.
- Commit: `feat(rbac): add user CRUD endpoints`
- PR per spec change folder

### Testing
- Backend: pytest + pytest-django + factory_boy
- Frontend: Vitest + React Testing Library
- Minimum 80% coverage for business logic
- All approval workflow transitions must be tested

## Domain Glossary (Vietnamese ↔ English)
| Vietnamese | English | Code Name |
|-----------|---------|-----------|
| Chương trình đào tạo (CTĐT) | Training Program | TrainingProgram |
| Chuẩn đầu ra | Program Learning Outcome | PLO |
| Mục tiêu đào tạo | Program Objective | PO |
| Học phần | Course | Course |
| Đề cương chi tiết | Syllabus | Syllabus |
| Khối kiến thức | Knowledge Block | KnowledgeBlock |
| Chỉ số đo lường | Performance Indicator | PI |
| Tín chỉ | Credit | credits |
| Phê duyệt | Approval | Approval |
| Phiên bản | Version | Version |
| Khoa/Viện | Faculty/Institute | Department |
| Phòng Đào tạo | Academic Affairs Office | (role: PHONG_DAO_TAO) |
| Ban Giám Hiệu | University Board | (role: BAN_GIAM_HIEU) |
| Giảng viên | Lecturer | (role: GIANG_VIEN) |
| Trưởng ngành/bộ môn | Program Head | (role: TRUONG_NGANH) |

## Approval Workflow States
```
DRAFT → SUBMITTED → KHOA_REVIEWING → KHOA_APPROVED
→ PDT_REVIEWING → PDT_APPROVED → BGH_REVIEWING → PUBLISHED

Any step can REJECT → REVISION_REQUIRED → back to DRAFT
```

## Key Business Rules
1. Mỗi CTĐT thuộc 1 Khoa/Viện duy nhất
2. 1 Học phần có thể thuộc nhiều CTĐT
3. PLO phải map với ít nhất 1 PO
4. Mỗi PLO phải có ít nhất 1 HP đóng góp trong ma trận
5. HP tiên quyết phải thuộc HK trước HP hiện tại
6. Khi HP thay đổi → notify tất cả CTĐT liên quan
7. Mỗi lần phê duyệt cuối (BGH) → tạo version snapshot
8. Chỉ Admin mới quản lý users/roles
9. User chỉ edit được CTĐT thuộc department của mình (trừ Phòng ĐT và Admin)
