# Auto Snapshot

## Overview

Khi tạo `ProgramVersion`, hệ thống tự động tạo `snapshot_data` từ `TrainingProgram` liên kết nếu không được cung cấp.

## Requirements

### REQ-1: Default value cho snapshot_data

- Trường `snapshot_data` phải có `default=dict` để tránh NOT NULL constraint error
- Giá trị mặc định là empty dict `{}`

### REQ-2: Auto-generate snapshot trên save

- Khi `save()` được gọi và `snapshot_data` là empty dict:
  - Nếu `program` đã được gán (not None), tự động serialize program data vào `snapshot_data`
  - Nếu `program` chưa gán, giữ nguyên empty dict (cho phép tạo trước rồi gán sau)

### REQ-3: Backward compatibility

- `VersionService.create_snapshot()` hiện tại truyền `snapshot_data` đã đầy đủ → save() KHÔNG override snapshot đã có
- Chỉ auto-generate khi `snapshot_data` là empty dict hoặc falsy

### REQ-4: Auto version_number

- Khi `version_number` không được chỉ định (mặc định 0 hoặc None), tự động tính version_number tiếp theo cho program
