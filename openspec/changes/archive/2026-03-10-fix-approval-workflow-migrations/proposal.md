## Why

Ứng dụng đang gặp lỗi `ProgrammingError: column workflows_approvalworkflow.current_step_number does not exist` khi truy cập quy trình phê duyệt. Model `ApprovalWorkflow` đã được refactor đáng kể so với migration ban đầu nhưng không có migration nào được tạo để đồng bộ schema database.

## What Changes

- **Tạo migration mới** để đồng bộ database schema với model code hiện tại:
  - Rename `current_step` → `current_step_number` trong `ApprovalWorkflow`
  - Thêm field `total_steps`, `completed_at` vào `ApprovalWorkflow`
  - Cập nhật `status` choices (`PENDING`/`IN_PROGRESS`/`APPROVED`/`REJECTED` → `IN_PROGRESS`/`COMPLETED`/`REJECTED`/`CANCELLED`)
  - Thêm model `ApprovalComment`
  - Refactor `ProgramVersion` → `EntityVersion` (rename model, đổi fields)
  - Cập nhật `ApprovalStep` fields (thêm `version`, `required_department_scope`, rename `approver`→`acted_by`, `comment`→`action_comment`, thêm `action_comment`, cập nhật choices)
  - Thêm indexes và constraints mới
- **Cập nhật tests** để phù hợp với API mới của services (tests dùng `current_step` thay vì `current_step_number`, `WorkflowStatus.APPROVED` thay vì `COMPLETED`, v.v.)

## Capabilities

### New Capabilities

_(Không có capability mới - đây là fix bug đồng bộ migration)_

### Modified Capabilities

- `approval`: Cập nhật migration schema để khớp với model code đã được refactor — không thay đổi behavior, chỉ đồng bộ database.

## Impact

- **Database**: Cần chạy migration để cập nhật schema. Dữ liệu cũ trong `ApprovalWorkflow` sẽ cần rename column `current_step` → `current_step_number`.
- **Model `ProgramVersion`**: Rename thành `EntityVersion` với structure mới (generic `entity_type`/`entity_id` thay vì `program` FK). Dữ liệu cũ cần migrate.
- **Tests**: File `tests.py` sử dụng API cũ cần cập nhật để match service signatures hiện tại.
- **Không ảnh hưởng API/Frontend**: Model/service code đã đúng, chỉ cần migration + test sync.
