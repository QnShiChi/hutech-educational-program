## Context

Hệ thống CTĐT HUTECH sử dụng Django Admin để quản lý chương trình đào tạo và các phiên bản. Hiện tại:
- `ProgramContextMixin` lưu `active_program_id` và `active_version_id` vào session khi vào change_view của TrainingProgram
- `workflow_snippet.html` hiển thị program context nhưng **không có dropdown chọn phiên bản**
- Xóa phiên bản không có bảo vệ nào — xóa ACTIVE version vẫn được phép
- Admin inline cho version có nút "Xóa" nhưng cũng không kiểm tra trạng thái

Các model đã có structure đúng: PO, PLO, PI, KB, ProgramCourse đều có FK `version` → `TrainingProgramVersion`.

## Goals / Non-Goals

**Goals:**
- Cung cấp 2 dropdown liên kết (CTĐT → Phiên bản) trong admin, hoạt động AJAX không reload toàn trang
- Session lưu cặp (program_id, version_id) → tất cả changelist tự filter theo version đã chọn
- Cấm xóa phiên bản ACTIVE ở tất cả layers (admin, API, model)
- Xóa 1 phiên bản DRAFT/ARCHIVED không ảnh hưởng program gốc hay versions khác

**Non-Goals:**
- Không cần drag-and-drop reorder versions
- Không cần version comparison (so sánh 2 phiên bản)
- Không cần frontend React/Vue cho version selector — dùng Django templates + vanilla JS

## Decisions

### 1. AJAX-based version selector
**Chọn:** Vanilla JS + AJAX POST/GET trên admin template
**Lý do:** Django Admin đã có jQuery, không cần thêm dependency. AJAX cho phép load danh sách phiên bản mà không reload trang.
**Thay thế:** Full page reload khi chọn → chậm, UX kém

### 2. Session-based filtering
**Chọn:** Tiếp tục dùng `request.session` cho `active_program_id` + `active_version_id`
**Lý do:** Đã có sẵn pattern này trong `ProgramContextMixin`, chỉ cần mở rộng. Đơn giản, không cần thay đổi URL routing.

### 3. Multi-layer delete protection
**Chọn:** Protect ở 3 layers — Model `delete()`, Admin `has_delete_permission()`, API ViewSet `destroy()`
**Lý do:** Defense-in-depth — nếu 1 layer bị bypass, còn layers khác chặn. Đảm bảo ACTIVE version không bị xóa dù qua đường nào.

### 4. AJAX endpoints on ProgramContextMixin
**Chọn:** Thêm custom URLs trên mixin thông qua admin-level views
**Lý do:** Các endpoints `set-program/`, `set-version/`, `get-versions/` cần auth admin. Đặt ở admin level đảm bảo auth tự động.

## Risks / Trade-offs

- **[Risk] Session mismatch**: User mở 2 tabs, chọn version khác nhau → session bị ghi đè → **Mitigation**: Chấp nhận hạn chế (session-based), ghi rõ trong UX.
- **[Risk] Orphan version_id**: Chuyển program mà quên clear version_id → filter sai → **Mitigation**: Khi select program mới, tự động clear `active_version_id` và set về version mới nhất.
- **[Risk] Delete bypass via Django shell**: Model-level protection only works if `delete()` is called → **Mitigation**: Sử dụng `pre_delete` signal hoặc override `delete()` trên model.
