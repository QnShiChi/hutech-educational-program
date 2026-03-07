# Tasks: 05 - Matrices & Assessment Plan

## 1. Models

- [x] 1.1 Create CoursePLOContribution model
- [x] 1.2 Create PLOAssessmentPlan model
- [x] 1.3 Migrations

## 2. APIs

- [x] 2.1 CoursePLOMatrixView (GET pivot format, PUT bulk update)
- [x] 2.2 PLOAssessmentPlanViewSet (CRUD + bulk)
- [x] 2.3 Matrix validation endpoint: check PLO coverage

## 3. Matrix Pivot Logic

- [x] 3.1 GET returns: {columns: [PI headers grouped by PLO], rows: [{course info, cells}]}
- [x] 3.2 PUT accepts flat array of {program_course_id, pi_id, level}
- [x] 3.3 Efficient bulk upsert (delete + create, or update_or_create)

## 4. Tests

- [x] 4.1 Matrix bulk update with ~1000 cells
- [x] 4.2 PLO coverage validation
- [x] 4.3 Assessment plan CRUD
- [x] 4.4 Performance test: matrix read < 500ms for 70x21
