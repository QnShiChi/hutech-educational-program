## Why

Khi thêm phiên bản CTĐT (ProgramVersion), hệ thống báo lỗi `IntegrityError: null value in column "snapshot_data"` vì trường `snapshot_data` (JSONField) không có giá trị mặc định và không cho phép null. Hiện tại chỉ `VersionService.create_snapshot()` đặt giá trị đúng, nhưng các đường dẫn khác (Django Admin, API trực tiếp) không tự động tạo snapshot, gây crash.

## What Changes

- Thêm `default=dict` cho trường `snapshot_data` trong model `ProgramVersion` để tránh IntegrityError khi tạo trực tiếp
- Override `save()` trên model `ProgramVersion` để tự động gọi `VersionService._serialize_program()` nếu `snapshot_data` rỗng
- Tạo migration cho thay đổi model

## Capabilities

### New Capabilities

- `auto-snapshot`: Tự động tạo snapshot_data khi tạo ProgramVersion mà không cung cấp giá trị snapshot

### Modified Capabilities

_(Không có)_

## Impact

- **Model**: `ProgramVersion` trong `hutech_program/workflows/models.py`
- **Migration**: Thêm migration mới cho thay đổi default
- **Admin**: Không ảnh hưởng cấu trúc admin, nhưng giờ có thể tạo version từ admin mà không lỗi
- **API**: Không ảnh hưởng API hiện tại
