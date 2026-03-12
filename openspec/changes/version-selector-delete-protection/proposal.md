## Why

Hiện tại admin Django hiển thị tất cả dữ liệu chung mà không có cơ chế chọn CTĐT + phiên bản cụ thể. Người dùng không thể dễ dàng chuyển đổi giữa các phiên bản của cùng 1 chương trình đào tạo. Ngoài ra, hệ thống hiện không có bảo vệ chống xóa nhầm — xóa 1 phiên bản có thể cascade xóa toàn bộ dữ liệu, và phiên bản đang ACTIVE có thể bị xóa gây gián đoạn hệ thống.

## What Changes

- **Linked dropdowns trong admin**: Thêm 2 dropdown liên kết ở đầu các trang admin (change_list, change_form): Dropdown 1 chọn CTĐT → Dropdown 2 tự động load danh sách phiên bản của CTĐT đó → Tất cả nội dung bên dưới tự động lọc theo cặp (CTĐT + Phiên bản) đã chọn.
- **Version delete protection**: Cấm xóa phiên bản đang ở trạng thái ACTIVE, cả trong admin và API.
- **Safe version deletion**: Xóa 1 phiên bản chỉ xóa phiên bản đó và dữ liệu con (PO, PLO, PI, KB, etc.), KHÔNG ảnh hưởng chương trình gốc hay các phiên bản khác.
- **AJAX endpoints**: Thêm API endpoints phục vụ dropdown liên kết (set-program, set-version, get-versions).

## Capabilities

### New Capabilities
- `version-selector-ui`: Admin UI với 2 dropdown liên kết để chọn CTĐT và phiên bản, lọc nội dung theo context đã chọn
- `version-delete-protection`: Bảo vệ chống xóa nhầm phiên bản ACTIVE, cả trong admin, API, và model-level

### Modified Capabilities
- `admin-training-program-workflow`: Workflow snippet cần cập nhật để hiển thị version selector thay vì chỉ program context

## Impact

- **Admin templates**: `workflow_snippet.html` — rewrite để thêm linked dropdowns + AJAX
- **Admin backend**: `admin.py` — thêm AJAX endpoints, override delete permissions
- **API Views**: `views.py` — thêm destroy override cho `TrainingProgramVersionViewSet`
- **Models**: `models.py` — thêm delete safeguard trên `TrainingProgramVersion`
- **Tests**: Thêm tests cho delete protection logic
