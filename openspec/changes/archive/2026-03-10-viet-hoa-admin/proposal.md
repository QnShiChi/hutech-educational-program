## Why

Trang Admin hiện tại đang hiển thị một số thông báo, nhãn, và thông báo lỗi bằng tiếng Anh, gây trở ngại cho việc sử dụng hệ thống của người quản trị (Admin) người Việt Nam. Việc Việt hoá toàn bộ giao diện Admin sẽ giúp nâng cao trải nghiệm, đảm bảo quản trị viên có thể dễ dàng hiểu và thao tác chính xác.

## What Changes

- Dịch các thông báo lỗi (error messages), thông báo thành công (success messages), nhãn trường (field labels), và các thành phần hiển thị khác, button, text sang tiếng Việt.
- Dịch `verbose_name`, `verbose_name_plural` của Models, Apps.
- Cập nhật cấu hình dịch thuật (`LANGUAGE_CODE` trong `settings.py`) nếu cần và tạo/cập nhật các file ngôn ngữ `.po`/`.mo`.

## Capabilities

### New Capabilities

- `admin-vietnamese-translation`: Việt hoá các thông báo và giao diện hiển thị trong Admin.

### Modified Capabilities

## Impact

- Mã nguồn: Các thư mục `locale/vi`, cấu hình `settings.py`, `apps.py`, `admin.py`, và `models.py`.
