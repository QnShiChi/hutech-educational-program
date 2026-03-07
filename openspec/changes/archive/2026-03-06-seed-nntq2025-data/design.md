## Context

Hệ thống quản lý CTĐT đã có đầy đủ models (`TrainingProgram`, `PO`, `PLO`, `KnowledgeBlock`, `Course`, `ProgramCourse`, `PI`, `CoursePLOContribution`, `PLOAssessmentPlan`, ...) và `DocxParser` để parse file Word. Cần một management command kết hợp parser với logic tạo dữ liệu vào database.

File Word `wiki/mo-ta-chuong-trinh-cu-nhan-NNTQ2025.docx` chứa CTĐT Cử nhân Ngôn ngữ Trung Quốc với:

- 4 POs, 7 PLOs với mapping
- 14 khối kiến thức (có cấu trúc cha-con)
- ~60 học phần phân bổ 8 học kỳ
- Ma trận đóng góp HP-PLO-PI
- Kế hoạch đánh giá PLO

## Goals / Non-Goals

**Goals:**

- Tạo management command `seed_nntq2025` chạy đúng 1 lần hoặc nhiều lần (idempotent)
- Parse file Word bằng `DocxParser` đã có
- Tạo đầy đủ dữ liệu: Department, TrainingProgram, PO, PLO, PLOPOMapping, KnowledgeBlock, Course, ProgramCourse, CoursePrerequisite, SemesterPlan, PI, CoursePLOContribution, PLOAssessmentPlan
- Có option `--flush` để xóa dữ liệu cũ trước khi seed

**Non-Goals:**

- Không cải tiến DocxParser (dùng như hiện tại, bổ sung hardcode cho data mà parser chưa extract được)
- Không tạo API endpoint - chỉ là management command
- Không seed user data hay RBAC roles

## Decisions

### 1. Sử dụng DocxParser + hardcode bổ sung

**Rationale**: DocxParser đã parse được courses, knowledge_blocks, course_plo_matrix. Tuy nhiên general_info, PLOs, POs, PIs, assessment_plans chưa được parse đúng do format đặc thù. Thay vì sửa parser, sẽ hardcode các trường này trong seed command vì dữ liệu cố định cho 1 chương trình cụ thể.

### 2. Idempotent với `--flush` flag

**Rationale**: Dùng flag `--flush` để xóa CTĐT cũ (cascade delete) trước khi tạo mới. Mặc định sẽ skip nếu program_code đã tồn tại.

### 3. Atomic transaction

**Rationale**: Toàn bộ seed chạy trong `transaction.atomic()` để đảm bảo tính toàn vẹn - nếu fail ở bất kỳ bước nào thì rollback toàn bộ.

### 4. Tạo Department mặc định

**Rationale**: TrainingProgram và Course cần FK đến Department. Sẽ tạo "Khoa Ngoại ngữ" nếu chưa có, dùng `get_or_create`.

## Risks / Trade-offs

- **[Parser data thiếu]** → Hardcode PO/PLO/PI data trực tiếp trong command, đối chiếu với file Word gốc
- **[Course credits validation]** → Skip `clean()` validation khi tạo Course vì parser có thể trả về theory/practice hours thay vì credits → sẽ set `total_credits` và bỏ qua breakdown nếu không chính xác
- **[Cascade delete risk]** → `--flush` xóa toàn bộ CTĐT và data liên quan, cần cảnh báo người dùng
