# Proposal: Word File Import & Parsing

## Summary
Cho phép upload file Word (.docx) chứa bản mô tả CTĐT, tự động trích xuất dữ liệu từ các bảng trong file và lưu vào database. Sử dụng Celery cho xử lý async.

## Architecture
```
User upload .docx → API endpoint → Celery task
  → python-docx parse tables → validate data
  → create TrainingProgram + all related entities
  → return result (success/errors)
```

## File Structure Expected (from NNTQ2025 sample)
| Table # | Content | Target Model |
|---------|---------|-------------|
| 1 | Thông tin chung (20 rows key-value) | TrainingProgram |
| 2 | Chuẩn đầu ra PLO (8 rows) | ProgramLearningOutcome |
| 3 | Thang trình độ năng lực Bloom | (reference data) |
| 4 | Ma trận PO-PLO (6x9) | PLOPOMapping |
| 5 | Cấu trúc khối kiến thức (15 rows) | KnowledgeBlock |
| 6 | Danh sách học phần (88 rows, 10 cols) | Course + ProgramCourse |
| 7 | Ma trận HP-PLO-PI (81x23) | CoursePLOContribution |
| 8 | Mô tả tóm tắt HP (70 rows) | Course.description |
| 10 | Kế hoạch giảng dạy (115 rows, 13 cols) | SemesterPlan |
| 11 | Chỉ số đo lường PI (8 rows) | PerformanceIndicator |
| 13 | Kế hoạch đánh giá PLO (27 rows) | PLOAssessmentPlan |

## API Endpoints
```
POST /api/v1/imports/training-program/
  Body: multipart/form-data {file: .docx, department_id: uuid}
  Response: {task_id: "xxx", status: "PROCESSING"}

GET  /api/v1/imports/{task_id}/status/
  Response: {status: "COMPLETED/FAILED/PROCESSING", 
             progress: 75, 
             result: {program_id: uuid, warnings: [...], errors: [...]}}

GET  /api/v1/imports/{task_id}/preview/
  Response: {parsed_data: {...all extracted data before save...}}

POST /api/v1/imports/{task_id}/confirm/
  Response: {program_id: uuid}  # Actually saves to DB
```

## Parsing Strategy
1. Parse bằng python-docx: iterate tables, extract cell text
2. Table detection: dựa vào header row patterns (column names)
3. Flexible matching: skip unknown tables, log warnings for missing tables
4. Data validation: check required fields, data types
5. Two-phase: parse → preview → user confirms → save

## Error Handling
- File format not .docx → 400 immediately
- Table not found → warning (not error, continue)
- Invalid data in cell → log error per cell, continue
- Duplicate course code → link to existing Course
- Return comprehensive report: {parsed: X, created: Y, errors: [...], warnings: [...]}
