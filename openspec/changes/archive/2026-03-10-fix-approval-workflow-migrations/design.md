## Context

Migration `0001_initial.py` tạo schema ban đầu cho workflows app với:

- `ApprovalWorkflow.current_step` (PositiveIntegerField)
- `ApprovalWorkflow.status` choices: `PENDING`/`IN_PROGRESS`/`APPROVED`/`REJECTED`, default=`PENDING`
- `ProgramVersion` model với FK `program` → `TrainingProgram`
- `ApprovalStep` với fields `approver`, `comment`, `approver_role`

Code hiện tại (models.py, services.py, serializers.py, admin.py) đã refactor sang:

- `ApprovalWorkflow.current_step_number` (renamed)
- `ApprovalWorkflow.total_steps`, `completed_at` (mới)
- Status choices: `IN_PROGRESS`/`COMPLETED`/`REJECTED`/`CANCELLED`, default=`IN_PROGRESS`
- `EntityVersion` (generic, thay thế `ProgramVersion`)
- `ApprovalStep` với fields `acted_by`, `action_comment`, `required_role`, `required_department_scope`, `version`
- `ApprovalComment` model (hoàn toàn mới)
- Indexes và UniqueConstraint mới

Chỉ có 1 migration phụ (`0002`) cho `snapshot_data` default.

## Goals / Non-Goals

**Goals:**

- Tạo migration đồng bộ hoàn toàn database schema với model code hiện tại
- Sửa tests để match API signatures hiện tại của services
- Đảm bảo server start không lỗi và tests pass

**Non-Goals:**

- Thay đổi logic nghiệp vụ
- Thay đổi API endpoints
- Migrate dữ liệu production (chưa có dữ liệu production quan trọng)

## Decisions

### 1. Squash migrations thay vì thêm migration incremental

**Quyết định**: Xóa migrations cũ (`0001_initial.py`, `0002`), chạy `makemigrations` để tạo lại `0001_initial.py` mới từ model hiện tại.

**Lý do**: Project đang trong giai đoạn development, chưa có dữ liệu production. Tạo migration incremental cho hàng chục thay đổi (rename column, rename model, add/remove fields, change choices, add model) sẽ phức tạp không cần thiết. Fresh migration sạch hơn và dễ review.

**Trade-off**: Cần `flush` database hoặc drop tables workflows trước khi apply migration mới.

### 2. Cập nhật tests thay vì giữ backward compatibility

**Quyết định**: Sửa `tests.py` để dùng đúng API signatures mới (`entity_type` parameter, `current_step_number` thay vì `current_step`, `WorkflowStatus.COMPLETED` thay vì `APPROVED`, `VersionService.create_snapshot()` signature mới).

**Lý do**: Tests hiện tại call API không match service code → sẽ fail dù migration đúng.

## Risks / Trade-offs

- **[Risk]** Mất dữ liệu existing trong bảng workflows → **Mitigation**: OK vì đang development, không có dữ liệu production. Chạy `flush` hoặc re-seed.
- **[Risk]** Quên cập nhật 1 file nào đó vẫn reference field cũ → **Mitigation**: Chạy full `makemigrations` check + server start + tests để verify.
