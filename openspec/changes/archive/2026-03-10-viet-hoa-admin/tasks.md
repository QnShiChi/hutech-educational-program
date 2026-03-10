## 1. Cấu hình ngôn ngữ hệ thống

- [x] 1.1 Kiểm tra và cập nhật `LANGUAGE_CODE = 'vi'` trong `settings.py`.
- [x] 1.2 Đảm bảo `USE_I18N = True` và cấu hình `LOCALE_PATHS` đã được thiết lập đúng trong `settings.py`.

## 2. Việt hoá dữ liệu Models và Apps

- [x] 2.1 Thêm/Cập nhật `verbose_name` và `verbose_name_plural` cho tất cả các class Models với `gettext_lazy` (ví dụ `_('Chương trình đào tạo')`).
- [x] 2.2 Thêm/Cập nhật `verbose_name` trong `apps.py` của từng ứng dụng để hiển thị tên ứng dụng bằng tiếng Việt.

## 3. Tạo và biên dịch tệp ngôn ngữ

- [x] 3.1 Chạy lệnh `django-admin makemessages -l vi` (hoặc `python manage.py makemessages -l vi`) để tạo file `.po`.
- [x] 3.2 Tuỳ chỉnh hoặc sửa đổi các bản dịch trong `.po` file thuộc thư mục `locale/vi/LC_MESSAGES/django.po` nếu các chuỗi gettext tự định nghĩa chưa được dịch đúng.
- [x] 3.3 Chạy lệnh `django-admin compilemessages` (hoặc `python manage.py compilemessages`) để tạo file `.mo`.

## 4. Kiểm tra trên Admin

- [x] 4.1 Khởi động lại server và đăng nhập vào trang `/admin/`.
- [x] 4.2 Kiểm tra xem tất cả các nhãn, menu, và thông báo lỗi có hiển thị đúng bằng tiếng Việt không.
