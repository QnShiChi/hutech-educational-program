## Why

Hệ thống quản lý CTĐT hiện tại chưa có dữ liệu mẫu để demo và kiểm thử. Cần tạo management command để seeding dữ liệu thực tế từ file mô tả chương trình Cử nhân Ngôn ngữ Trung Quốc (NNTQ2025), giúp team phát triển và demo hệ thống với dữ liệu đầy đủ.

## What Changes

- Tạo Django management command `seed_nntq2025` để import toàn bộ dữ liệu CTĐT từ file Word NNTQ2025 vào database
- Seed dữ liệu bao gồm: TrainingProgram, PO (4), PLO (7), PO-PLO mapping, KnowledgeBlock (14), Course (~60 học phần), ProgramCourse, CoursePrerequisite, PI, CoursePLOContribution, SemesterPlan, PLOAssessmentPlan
- Tạo Department mặc định "Khoa Ngoại ngữ" nếu chưa tồn tại
- Command có thể chạy lại (idempotent) - xóa dữ liệu cũ trước khi tạo mới
- Viết test cho management command

## Capabilities

### New Capabilities

- `seed-command`: Django management command sử dụng DocxParser đã có để parse file Word NNTQ2025 và tạo toàn bộ dữ liệu mẫu vào database

### Modified Capabilities

_(Không thay đổi capabilities hiện có)_

## Impact

- **Code mới**: `hutech_program/programs/management/commands/seed_nntq2025.py`
- **Test mới**: `hutech_program/programs/tests/test_seed_command.py`
- **Dependencies**: Sử dụng `DocxParser` từ `hutech_program/imports/parser.py` (đã có)
- **File Word**: `wiki/mo-ta-chuong-trinh-cu-nhan-NNTQ2025.docx` (đã có trong repo)
- **Không ảnh hưởng**: API, serializers, frontend - đây chỉ là data seeding command
