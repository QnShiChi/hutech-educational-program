## Context

`ApprovalWorkflowAdmin` hiện tại là basic `ModelAdmin` registration — chỉ có `list_display`, `list_filter`, `search_fields` và `TabularInline` cho steps. Form tạo mới yêu cầu nhập UUID thủ công cho `entity_id`, không có entity picker, và không readonly protect computed fields.

Service layer (`WorkflowService.submit()`) đã xử lý toàn bộ logic tạo workflow + steps, nhưng admin form cho phép tạo thủ công → dễ tạo data không hợp lệ.

## Goals / Non-Goals

**Goals:**

- Admin form chỉ hiển thị (readonly) cho workflow, không cho phép tạo thủ công qua form
- List view hiển thị đầy đủ thông tin hữu ích (entity name, step progress)
- Approval steps inline hoàn toàn readonly
- Admin list view có search/filter tốt hơn

**Non-Goals:**

- Tạo custom admin page để submit workflow (workflow submit qua API/Frontend)
- Thay đổi models hoặc service layer
- Thêm admin permission checks (dùng Django admin permissions mặc định)

## Decisions

### 1. Readonly admin thay vì custom form

**Quyết định**: Chuyển `ApprovalWorkflowAdmin` sang chế độ readonly — không cho phép tạo/sửa workflow qua admin. Admin chỉ để xem và kiểm tra data.

**Lý do**: Workflow phải được tạo qua `WorkflowService.submit()` để đảm bảo:

- Steps được tạo đúng theo WORKFLOW_CONFIGS
- Entity status được cập nhật
- Notifications được gửi
- Audit log được tạo

Tạo qua admin form bỏ qua tất cả logic này.

### 2. Thêm computed display fields

**Quyết định**: Thêm methods hiển thị entity name (resolve từ UUID), step progress bar, và link đến entity trong admin.

**Lý do**: Admin hiện tại chỉ hiển thị raw UUID — không hữu ích. Cần entity name và progress để hỗ trợ monitoring.

## Risks / Trade-offs

- **[Risk]** Admin không thể tạo workflow mới → **Mitigation**: Workflow luôn phải tạo qua API/Frontend đã implement. Admin chỉ monitoring.
- **[Trade-off]** Readonly admin hạn chế khả năng fix data lỗi → superuser vẫn có thể dùng Django shell. Có thể thêm admin action "Cancel workflow" sau.
