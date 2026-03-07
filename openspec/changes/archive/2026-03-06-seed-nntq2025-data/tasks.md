## 1. Setup & Structure

- [x] 1.1 Tạo thư mục management command: `hutech_program/programs/management/commands/`
- [x] 1.2 Tạo file `__init__.py` cho thư mục management và commands

## 2. Core Command Implementation

- [x] 2.1 Tạo file `seed_nntq2025.py` với class `Command` kế thừa `BaseCommand`
- [x] 2.2 Implement argument `--flush` để xóa dữ liệu cũ
- [x] 2.3 Implement `handle()` method chính với `transaction.atomic()`
- [x] 2.4 Implement hàm tạo Department ("Khoa Ngoại ngữ") bằng `get_or_create`
- [x] 2.5 Implement hàm tạo TrainingProgram với metadata đầy đủ (code, name, credits, status=PUBLISHED)

## 3. PO / PLO / Mapping Data

- [x] 3.1 Implement hàm tạo 4 ProgramObjective (PO1-PO4) với description hardcode từ document
- [x] 3.2 Implement hàm tạo 7 ProgramLearningOutcome (PLO1-PLO7) với description và competency_level hardcode
- [x] 3.3 Implement hàm tạo PLOPOMapping từ ma trận PO-PLO trong document

## 4. Knowledge Blocks & Courses

- [x] 4.1 Implement hàm tạo KnowledgeBlock từ DocxParser data (có cấu trúc cha-con)
- [x] 4.2 Implement hàm tạo Course từ DocxParser data (lọc header rows, parse credits)
- [x] 4.3 Implement hàm tạo ProgramCourse liên kết Course với TrainingProgram (semester assignment)
- [x] 4.4 Implement hàm tạo CoursePrerequisite từ cột "Mã HP học trước" và "Mã HP song hành"

## 5. PI & Assessment

- [x] 5.1 Implement hàm tạo PerformanceIndicator từ bảng PI trong document (hardcode nếu parser không extract được)
- [x] 5.2 Implement hàm tạo CoursePLOContribution từ course_plo_matrix (DocxParser data)
- [x] 5.3 Implement hàm tạo PLOAssessmentPlan từ bảng assessment (hardcode nếu cần)

## 6. Progress Output

- [x] 6.1 Implement stdout output hiển thị số lượng entities đã tạo (POs, PLOs, Courses, etc.)
- [x] 6.2 Implement colored output với `self.style.SUCCESS` / `self.style.WARNING`

## 7. Testing

- [x] 7.1 Viết test `test_seed_command.py`: test chạy command thành công, verify entity counts
- [x] 7.2 Test `--flush` flag: chạy 2 lần với flush, verify dữ liệu đúng
- [x] 7.3 Test idempotent: chạy 2 lần không flush, verify skip message
- [x] 7.4 Chạy command thực tế trong Docker và verify dữ liệu qua Django admin
