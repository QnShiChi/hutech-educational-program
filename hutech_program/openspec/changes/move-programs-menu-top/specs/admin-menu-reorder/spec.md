## ADDED Requirements

### Requirement: Admin menu hiển thị "Chương trình đào tạo" đầu tiên

App "Chương trình đào tạo" (programs) SHALL được hiển thị đầu tiên trong sidebar menu của Django admin, trước tất cả các app khác.

#### Scenario: Truy cập trang admin

- **WHEN** người dùng truy cập trang admin tại `/admin/`
- **THEN** app "Chương trình đào tạo" PHẢI hiển thị ở vị trí đầu tiên trong sidebar menu, trước "Người dùng", "Phân quyền & Vai trò", và các app khác
