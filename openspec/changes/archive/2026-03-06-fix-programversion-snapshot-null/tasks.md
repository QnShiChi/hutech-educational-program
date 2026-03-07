## 1. Model Fix

- [x] 1.1 Thêm `default=dict` cho field `snapshot_data` trong `ProgramVersion` model
- [x] 1.2 Override `save()` method để auto-generate snapshot khi `snapshot_data` rỗng

## 2. Migration

- [x] 2.1 Tạo migration `0002_alter_programversion_snapshot_data.py`
- [x] 2.2 Chạy migration và verify thành công

## 3. Testing

- [x] 3.1 Test tạo ProgramVersion không truyền snapshot_data → auto-generate
- [x] 3.2 Test tạo ProgramVersion với snapshot_data có sẵn → không bị override
- [x] 3.3 Test VersionService.create_snapshot() vẫn hoạt động bình thường
