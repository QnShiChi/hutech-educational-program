## Context

Django admin hiển thị các app theo thứ tự đăng ký trong `INSTALLED_APPS`. Hiện tại `LOCAL_APPS` có thứ tự:

1. `hutech_program.users` - Người dùng
2. `hutech_program.rbac` - Phân quyền & Vai trò
3. `hutech_program.programs` - Chương trình đào tạo
4. `hutech_program.workflows` - Quy trình phê duyệt
5. `hutech_program.imports` - Import Word files
6. `hutech_program.notifications` - Thông báo

"Chương trình đào tạo" là chức năng chính nhưng lại nằm ở vị trí thứ 3.

## Goals / Non-Goals

**Goals:**

- Di chuyển "Chương trình đào tạo" lên đầu menu admin sidebar

**Non-Goals:**

- Không thay đổi logic hoặc chức năng của bất kỳ app nào
- Không sử dụng custom AdminSite hay third-party package

## Decisions

**Quyết định: Reorder `LOCAL_APPS`**

Thay đổi thứ tự `LOCAL_APPS` trong `config/settings/base.py`:

```python
LOCAL_APPS = [
    "hutech_program.programs",       # ← đưa lên đầu
    "hutech_program.users",
    "hutech_program.rbac",
    "hutech_program.workflows",
    "hutech_program.imports",
    "hutech_program.notifications",
]
```

**Lý do**: Đây là cách đơn giản nhất, tận dụng hành vi mặc định của Django admin. Không cần custom code hay package bổ sung.

## Risks / Trade-offs

- **Rủi ro thấp**: Thứ tự INSTALLED_APPS chỉ ảnh hưởng thứ tự hiển thị admin và thứ tự migration. Các app hiện tại không có cross-dependency về thứ tự migration.
- **Thay đổi nhỏ**: Chỉ 1 file, chỉ thay đổi thứ tự dòng.
