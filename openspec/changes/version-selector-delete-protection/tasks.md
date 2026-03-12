## 1. Delete Protection — Model & API

- [x] 1.1 Override `delete()` trên `TrainingProgramVersion` model: raise `ValidationError` nếu status=ACTIVE
- [x] 1.2 Override `destroy()` trên `TrainingProgramVersionViewSet`: return 400 nếu version ACTIVE
- [x] 1.3 Tighten `TrainingProgramViewSet.destroy()`: block nếu program có version ACTIVE

## 2. Admin Delete Protection

- [x] 2.1 Override `has_delete_permission()` trên `TrainingProgramVersionAdmin` — block nếu ACTIVE
- [x] 2.2 Override `has_delete_permission()` trên `TrainingProgramVersionInline` — block inline delete nếu ACTIVE
- [x] 2.3 Override `delete_model()` trên `TrainingProgramVersionAdmin` — hiển thị error message

## 3. Version Selector UI — AJAX Endpoints

- [x] 3.1 Thêm admin endpoint `get-versions/` trả về JSON danh sách phiên bản theo program_id
- [x] 3.2 Thêm admin endpoint `set-context/` nhận POST program_id + version_id lưu vào session
- [x] 3.3 Cập nhật `ProgramContextMixin.get_urls()` để đăng ký các endpoints mới

## 4. Version Selector UI — Template

- [x] 4.1 Rewrite `workflow_snippet.html`: thêm 2 dropdown (chọn CTĐT, chọn phiên bản)
- [x] 4.2 Thêm vanilla JS AJAX: khi chọn CTĐT → load phiên bản, khi chọn phiên bản → set context + reload
- [x] 4.3 Thêm version status badge (DRAFT=vàng, ACTIVE=xanh, ARCHIVED=xám)
- [x] 4.4 Cập nhật `changelist_view()` truyền `all_programs` vào template context

## 5. Session Logic Update

- [x] 5.1 Cập nhật `get_active_version()` validate version thuộc active program
- [x] 5.2 Khi chọn program mới → tự động clear version_id, set default version mới nhất
- [x] 5.3 Cập nhật `TrainingProgramAdmin.change_view()` để sync session đúng

## 6. Tests

- [x] 6.1 Test delete ACTIVE version bị block (model-level)
- [x] 6.2 Test delete DRAFT version thành công, không ảnh hưởng program/versions khác
- [x] 6.3 Test API DELETE version ACTIVE → 400
- [x] 6.4 Test API DELETE version DRAFT → 204
- [x] 6.5 Run full test suite để verify không regression
