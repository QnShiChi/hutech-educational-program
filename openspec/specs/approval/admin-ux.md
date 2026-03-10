# Approval Admin UX Spec

## ApprovalWorkflowAdmin

### List Display

- `entity_type` — loại đối tượng
- `entity_display` — tên entity (resolve từ UUID, fallback UUID nếu entity deleted)
- `status` với colored badge
- `step_progress` — "2/3" format
- `initiated_by` — người khởi tạo
- `created_at`
- `completed_at`

### List Filters

- `status`
- `entity_type`
- `created_at` (DateFieldListFilter)

### Search Fields

- `entity_id`
- `initiated_by__name`
- `initiated_by__email`

### Readonly Fields

Tất cả fields readonly — workflow chỉ tạo qua service layer:

- `entity_type`, `entity_id`, `status`, `current_step_number`, `total_steps`
- `initiated_by`, `completed_at`, `created_at`, `updated_at`

### Custom Methods

- `entity_display()` — resolve entity name từ `get_entity()`
- `step_progress()` — "{current}/{total}" display

### Permissions

- `has_add_permission()` → `False` (không cho tạo mới qua admin)
- `has_change_permission()` → `False` (không cho sửa)
- `has_delete_permission()` → giữ mặc định (superuser có thể xóa nếu cần)

## ApprovalStepInline

- Tất cả fields readonly
- Hiển thị: step_number, step_name, required_role, status, acted_by, acted_at, action_comment
- `extra = 0`, `can_delete = False`
- `has_add_permission()` → `False`

## EntityVersionAdmin

### List Display

- `entity_type`, `entity_id`, `version_number`, `change_summary`, `created_by`, `created_at`

### Readonly Fields

- Tất cả fields readonly (versions immutable)

### Permissions

- `has_add_permission()` → `False`
- `has_change_permission()` → `False`

## ApprovalCommentAdmin

### List Display

- `step`, `author`, `content_preview` (truncated 100 chars), `created_at`

### Readonly Fields

- Tất cả readonly
