## Context

Hiện tại `TrainingProgram` chứa cả thông tin định danh (tên, mã, khoa) lẫn thông tin nội dung (tín chỉ, thời gian, mục tiêu, điều kiện). Khi hệ thống versioning được thêm vào, các trường nội dung vẫn nằm trên program nên mọi phiên bản chia sẻ cùng giá trị. Cần tách các trường nội dung sang `TrainingProgramVersion`.

## Goals / Non-Goals

**Goals:**
- Di chuyển 11 trường nội dung từ `TrainingProgram` → `TrainingProgramVersion`
- Migration an toàn: copy dữ liệu cũ → tất cả versions hiện có trước khi xóa
- Admin change form hiển thị trường nội dung trên version, không trên program
- Backward compatibility cho API responses

**Non-Goals:**
- Không di chuyển trường định danh (tên, mã, khoa, trình độ)
- Không thay đổi logic phê duyệt workflow
- Không thay đổi cấu trúc URL

## Decisions

### 1. Three-step migration (add → populate → remove)
**Chọn:** Tách thành 3 migration files
**Lý do:** An toàn — nếu populate fail, có thể rollback. Đã dùng pattern này thành công với PO/PLO/PI.

### 2. Giữ trường cũ trên TrainingProgram dưới dạng nullable
**Chọn:** Bước 1 thêm trường mới lên Version, bước 2 copy data, bước 3 xóa trường cũ
**Lý do:** Đảm bảo không mất dữ liệu trong quá trình migrate

### 3. Admin: Chỉnh sửa trường nội dung trên TrainingProgramVersionAdmin
**Chọn:** Di chuyển các trường nội dung vào form của Version, TrainingProgram form chỉ còn trường định danh
**Lý do:** Đúng logic — người dùng sửa nội dung theo phiên bản

## Risks / Trade-offs

- **[Risk] Dữ liệu trống trên version**: Nếu program có version nhưng dữ liệu chưa được copy → **Mitigation**: populate migration chạy trước remove
- **[Risk] API breaking change**: Field `total_credits` ở response program sẽ mất → **Mitigation**: Thêm field nested từ active version vào serializer
