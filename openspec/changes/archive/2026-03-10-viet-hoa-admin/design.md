## Context

Dự án Hutech Program hiện tại có một số thông báo và giao diện người dùng trên trang quản trị (Admin) hiển thị bằng tiếng Anh. Điều này không thân thiện với người dùng quản trị viên tại Việt Nam.

## Goals / Non-Goals

**Goals:**

- Dịch tất cả các thông báo lỗi, thông báo thành công và nhãn trên trang Admin sang tiếng Việt.
- Dịch tên (verbose_name) của các ứng dụng (apps) và mô hình (models) hiển thị trong danh mục quản trị.

**Non-Goals:**

- Việc dịch các nội dung do người dùng tự nhập (ví dụ: dữ liệu trong database) nằm ngoài phạm vi.
- Thay đổi cấu trúc hoặc logic nghiệp vụ của trang Admin.

## Decisions

- Cấu hình `LANGUAGE_CODE = 'vi'` trong `settings.py` để sử dụng bộ ngôn ngữ tích hợp sẵn của Django cho các text mặc định của Admin.
- Sử dụng `gettext_lazy` (`from django.utils.translation import gettext_lazy as _`) trên tất cả `verbose_name` và `verbose_name_plural` của Models và Apps.
- Cập nhật và biên dịch file `.po` (`django-admin makemessages -l vi`, `django-admin compilemessages`) cho các text tùy chỉnh (custom strings) trong các thư mục `locale/vi/LC_MESSAGES/`.

## Risks / Trade-offs

- Các package bên thứ ba có thể chưa hỗ trợ tiếng Việt đầy đủ. Cần rà soát kỹ để tự dịch hoặc override ngôn ngữ nếu cần.
