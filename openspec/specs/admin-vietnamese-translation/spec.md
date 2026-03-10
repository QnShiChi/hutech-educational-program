## ADDED Requirements

### Requirement: Dịch giao diện Admin sang Tiếng Việt

Hệ thống hiển thị tất cả ngôn ngữ mặc định của trang Admin bằng Tiếng Việt.

#### Scenario: Admin đăng nhập và thao tác

- **WHEN** Quản trị viên truy cập vào bất kỳ trang nào của admin (ví dụ `/admin/`)
- **THEN** Giao diện chính, menu, thư mục, các thông báo lỗi và thành công đều hiển thị bằng ngôn ngữ Việt Nam.

### Requirement: Dịch tên Ứng dụng và Mô hình

Tất cả các tên ứng dụng (app labels) và tên mô hình (model names) phải được hiển thị bằng tiếng Việt trên trang chủ quản trị.

#### Scenario: Xem danh sách menu Admin

- **WHEN** Quản trị viên xem sidebar hoặc trang dashboard của Admin
- **THEN** Các mục hiển thị tên rõ ràng (vd: "Quản lý chương trình đào tạo", "Bài đăng", v.v.) thay vì tên gốc bằng tiếng Anh.
