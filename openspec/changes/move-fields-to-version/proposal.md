## Why

Các trường mô tả nội dung CTĐT (tổng tín chỉ, thời gian đào tạo, mục tiêu, điều kiện tuyển sinh/tốt nghiệp, v.v.) hiện nằm trên model `TrainingProgram` — dùng chung cho tất cả phiên bản. Khi sửa "Thời gian đào tạo" ở phiên bản 2025-2026, nó thay đổi luôn ở phiên bản 2024-2025 vì cả hai đều trỏ đến cùng 1 bản ghi TrainingProgram. Cần di chuyển các trường này sang `TrainingProgramVersion` để mỗi phiên bản có dữ liệu độc lập.

## What Changes

- **Di chuyển 11 trường** từ `TrainingProgram` sang `TrainingProgramVersion`
  - `total_credits`, `training_duration`
  - `decision_number`, `decision_date`
  - `general_objective`, `admission_requirements`, `graduation_requirements`
  - `career_opportunities`, `further_education`
  - `teaching_methodology`, `assessment_methodology`, `implementation_guide`
- **Giữ nguyên trên `TrainingProgram`**: `program_name_vi/en`, `program_code`, `degree_name`, `education_level`, `managing_department`, `issuing_institution`, `status`
- **Migration an toàn**: copy dữ liệu từ program → tất cả versions trước khi xóa trường cũ
- **Cập nhật admin/serializers/views** để đọc/ghi các trường từ version thay vì program

## Capabilities

### New Capabilities
- `version-scoped-fields`: Các trường mô tả CTĐT được scope theo phiên bản, mỗi version có giá trị riêng

### Modified Capabilities
_(none — chỉ thay đổi vị trí dữ liệu, không thay đổi spec-level behavior)_

## Impact

- **Models**: `TrainingProgram` (xóa 11 trường), `TrainingProgramVersion` (thêm 11 trường)
- **Migrations**: 3 file (add → populate → remove)
- **Admin**: `TrainingProgramAdmin` change form, `TrainingProgramVersionAdmin`
- **Serializers**: `TrainingProgramSerializer`, `TrainingProgramVersionSerializer`
- **Views**: Các endpoint đọc program info
- **Tests**: Cập nhật factories và tests liên quan
- **Seed command**: `seed_nntq2025` cần sửa
