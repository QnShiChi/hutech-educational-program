## Why

Menu "Chương trình đào tạo" (programs) hiện nằm ở vị trí thứ 3 trong sidebar admin, sau "Người dùng" và "Phân quyền & Vai trò". Đây là chức năng chính của hệ thống nên cần hiển thị đầu tiên để người dùng truy cập nhanh hơn.

## What Changes

- Thay đổi thứ tự `LOCAL_APPS` trong `config/settings/base.py` để `hutech_program.programs` đứng đầu tiên
- Django admin hiển thị các app theo thứ tự trong `INSTALLED_APPS`, nên chỉ cần đổi thứ tự là đủ

## Capabilities

### New Capabilities

- `admin-menu-reorder`: Di chuyển app "Chương trình đào tạo" lên đầu menu admin sidebar

### Modified Capabilities

_(Không có capability nào bị thay đổi)_

## Impact

- **File thay đổi**: `config/settings/base.py` - chỉ thay đổi thứ tự trong `LOCAL_APPS`
- **Không có breaking change**: Thứ tự INSTALLED_APPS không ảnh hưởng đến logic, chỉ ảnh hưởng thứ tự hiển thị trên admin
