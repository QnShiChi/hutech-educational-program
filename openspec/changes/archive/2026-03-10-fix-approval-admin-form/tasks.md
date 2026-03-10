## 1. Refactor ApprovalWorkflowAdmin

- [x] 1.1 Thêm readonly cho tất cả fields (`entity_type`, `entity_id`, `status`, `current_step_number`, `total_steps`, `initiated_by`, `completed_at`, `created_at`, `updated_at`)
- [x] 1.2 Override `has_add_permission()` → `False`
- [x] 1.3 Override `has_change_permission()` → `False`
- [x] 1.4 Thêm method `entity_display()` — resolve entity name từ `get_entity()`
- [x] 1.5 Thêm method `step_progress()` — hiển thị "{current_step_number}/{total_steps}"
- [x] 1.6 Cập nhật `list_display` thêm `entity_display`, `step_progress`
- [x] 1.7 Thêm `list_filter` cho `created_at` (DateFieldListFilter)
- [x] 1.8 Mở rộng `search_fields` thêm `initiated_by__name`, `initiated_by__email`

## 2. Refactor ApprovalStepInline

- [x] 2.1 Chuyển tất cả fields sang readonly
- [x] 2.2 Set `can_delete = False`
- [x] 2.3 Override `has_add_permission()` → `False`
- [x] 2.4 Thêm hiển thị `required_role`, `action_comment` trong readonly_fields

## 3. Refactor EntityVersionAdmin & ApprovalCommentAdmin

- [x] 3.1 EntityVersionAdmin: thêm `change_summary` vào `list_display`, readonly tất cả fields
- [x] 3.2 EntityVersionAdmin: override `has_add_permission()` và `has_change_permission()` → `False`
- [x] 3.3 ApprovalCommentAdmin: thêm `content_preview` method (truncate 100 chars)
- [x] 3.4 ApprovalCommentAdmin: readonly tất cả fields, override add/change permissions → `False`

## 4. Verify

- [x] 4.1 Khởi động server, truy cập admin — verify không có nút "Add" cho ApprovalWorkflow
- [x] 4.2 Verify workflow list hiển thị đúng entity name và step progress
- [x] 4.3 Verify click vào workflow detail — tất cả fields readonly
- [x] 4.4 Verify ApprovalStep inline readonly, không có nút thêm/xóa
- [x] 4.5 Chạy `pytest hutech_program/workflows/tests.py` — verify tests vẫn pass
