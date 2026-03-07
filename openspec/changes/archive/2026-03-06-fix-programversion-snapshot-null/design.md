## Context

Model `ProgramVersion` trong `hutech_program/workflows/models.py` có trường `snapshot_data = models.JSONField()` **không có `default`** và database column có ràng buộc NOT NULL. Hiện tại, snapshot chỉ được tạo đúng qua `VersionService.create_snapshot()` (service gọi `_serialize_program()` → truyền kết quả vào `snapshot_data`).

Khi tạo `ProgramVersion` qua đường khác (ví dụ Django Admin, management command, hoặc code trực tiếp) mà không truyền `snapshot_data`, Django sẽ gửi `NULL` → PostgreSQL reject vì NOT NULL constraint.

**Lỗi cụ thể:**

```
django.db.utils.IntegrityError: null value in column "snapshot_data" of relation "workflows_programversion" violates not-null constraint
```

## Goals / Non-Goals

**Goals:**

- Fix IntegrityError khi tạo ProgramVersion mà không truyền snapshot_data
- Tự động tạo snapshot từ program liên kết khi snapshot_data trống
- Đảm bảo backward-compatible với `VersionService.create_snapshot()` hiện tại

**Non-Goals:**

- Thay đổi logic phê duyệt workflow
- Thay đổi cấu trúc dữ liệu snapshot
- Thay đổi API endpoints

## Decisions

### 1. Thêm `default=dict` cho `snapshot_data`

**Lý do:** Cho phép tạo ProgramVersion mà không cần truyền snapshot_data ngay, tránh IntegrityError ở cấp database.

**Alternatives:**

- `null=True, blank=True`: Cho phép NULL trong DB → phải xử lý None ở mọi nơi đọc snapshot_data → phức tạp hơn
- `default=dict`: Giá trị mặc định là `{}` → mọi code đọc snapshot_data luôn nhận dict, dễ xử lý hơn

### 2. Override `save()` để tự động generate snapshot

**Lý do:** Khi `snapshot_data` rỗng (empty dict) và `program` đã được gán, model tự động gọi `VersionService._serialize_program()` để tạo snapshot đầy đủ. Điều này đảm bảo không bao giờ có version với snapshot rỗng.

**Alternatives:**

- Signal `pre_save`: Tương đương nhưng khó test hơn, và logic bị tách ra ngoài model
- Validate ở serializer: Chỉ bao phủ API, không bao phủ Admin/command

### 3. Tạo migration

**Lý do:** Thay đổi `default` trên model field cần migration để Django tracking đúng, dù PostgreSQL column đã có NOT NULL.

## Risks / Trade-offs

- **[Performance]** Auto-snapshot trong `save()` sẽ query DB để serialize program data → Mitigation: Chỉ chạy khi snapshot_data rỗng (dict trống), và `VersionService.create_snapshot()` vẫn set trước khi save nên không bị query thừa.
- **[Circular import]** `models.py` import `VersionService` từ `services.py` → Mitigation: Dùng lazy import trong `save()` method.
