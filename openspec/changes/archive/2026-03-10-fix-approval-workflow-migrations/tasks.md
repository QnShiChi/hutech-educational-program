## 1. Squash Migrations

- [x] 1.1 Xóa file `0001_initial.py` và `0002_alter_programversion_snapshot_data.py` trong `workflows/migrations/`
- [x] 1.2 Xóa các file `__pycache__` tương ứng trong `workflows/migrations/__pycache__/`
- [x] 1.3 Chạy `python manage.py makemigrations workflows` để tạo lại migration mới từ models hiện tại
- [x] 1.4 Review migration mới: verify có đủ all models (`ApprovalWorkflow`, `ApprovalStep`, `ApprovalComment`, `EntityVersion`) với đúng fields

## 2. Cập nhật Tests

- [x] 2.1 Sửa `workflow.current_step` → `workflow.current_step_number` trong assertions (lines 119, 127, 134)
- [x] 2.2 Sửa `WorkflowStatus.APPROVED` → `WorkflowStatus.COMPLETED` (line 141)
- [x] 2.3 Sửa `WorkflowService.submit(program, creator)` → `WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)` (thêm entity_type param)
- [x] 2.4 Sửa `WorkflowService.approve(program, ...)` → `WorkflowService.approve(workflow, ...)` (truyền workflow thay vì program)
- [x] 2.5 Sửa `WorkflowService.reject(program, ...)` → `WorkflowService.reject(workflow, ...)` (truyền workflow thay vì program)
- [x] 2.6 Sửa `ProgramVersion` references → dùng `EntityVersion` với generic fields (`entity_type`/`entity_id` thay vì `program` FK)
- [x] 2.7 Sửa `VersionService.create_snapshot()` signature → thêm `entity_type` param
- [x] 2.8 Sửa `VersionService.compare()` → `VersionService.compare_versions()` với signature mới

## 3. Apply Migration & Verify

- [x] 3.1 Chạy migrate trong Docker container
- [x] 3.2 Verify server start không lỗi (truy cập admin)
- [x] 3.3 Chạy test suite `pytest hutech_program/workflows/tests.py` — **17/17 passed** ✅
