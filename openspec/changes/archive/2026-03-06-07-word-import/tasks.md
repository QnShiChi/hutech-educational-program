# Tasks: 07 - Word File Import

## 1. Setup

- [x] 1.1 Add python-docx to requirements
- [x] 1.2 Create `hutech_program/imports/` app structure
- [x] 1.3 Create ImportTask model (track task status + result)

## 2. Parser

- [x] 2.1 Create `DocxParser` base class with table detection logic
- [x] 2.2 Implement `parse_general_info(table)` → TrainingProgram fields
- [x] 2.3 Implement `parse_plos(table)` → PLO list
- [x] 2.4 Implement `parse_po_plo_matrix(table)` → PLOPOMapping list
- [x] 2.5 Implement `parse_knowledge_blocks(table)` → KnowledgeBlock tree
- [x] 2.6 Implement `parse_courses(table)` → Course + ProgramCourse list
- [x] 2.7 Implement `parse_course_plo_matrix(table)` → CoursePLOContribution list
- [x] 2.8 Implement `parse_course_descriptions(table)` → Course.description updates
- [x] 2.9 Implement `parse_semester_plan(table)` → SemesterPlan list
- [x] 2.10 Implement `parse_pis(table)` → PerformanceIndicator list
- [x] 2.11 Implement `parse_assessment_plans(table)` → PLOAssessmentPlan list

## 3. Celery Task

- [x] 3.1 Create `import_training_program_task` Celery task
- [x] 3.2 Implement file upload → save to temp → trigger task
- [x] 3.3 Implement progress tracking (update ImportTask model)
- [x] 3.4 Implement preview mode (parse but don't save)
- [x] 3.5 Implement confirm mode (save parsed data to DB)

## 4. APIs

- [x] 4.1 Upload endpoint (POST multipart)
- [x] 4.2 Status polling endpoint
- [x] 4.3 Preview endpoint
- [x] 4.4 Confirm endpoint

## 5. Tests

- [x] 5.1 Test with actual NNTQ2025 sample file
- [x] 5.2 Test each parser individually with mock tables
- [x] 5.3 Test error handling: invalid format, missing tables
- [x] 5.4 Test duplicate course code handling
- [x] 5.5 Test Celery task async flow
