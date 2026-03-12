## 1. Database Migrations

- [x] 1.1 Create schema migration `0008`: add nullable `version` FK to `ProgramObjective`, `ProgramLearningOutcome`, `PLOAssessmentPlan`
- [x] 1.2 Create data migration `0009`: populate `version` FK from each record's `program.versions.first()`, create default version for orphan programs
- [x] 1.3 Create schema migration `0010`: update `unique_together` constraints (`version, code` for PO/PLO; `version, pi` for PLOAssessmentPlan), rename `program` FK to legacy (nullable, SET_NULL)

## 2. Model Changes

- [x] 2.1 Update `ProgramObjective`: add `version` FK, change `program` to legacy, update `unique_together` and `__str__`
- [x] 2.2 Update `ProgramLearningOutcome`: add `version` FK, change `program` to legacy, update `unique_together` and `__str__`
- [x] 2.3 Update `PLOAssessmentPlan`: add `version` FK, change `program` to legacy

## 3. Clone Service Extension

- [x] 3.1 Extend `clone_program_version` to clone `ProgramObjective` records with `old_id → new_obj` mapping
- [x] 3.2 Clone `ProgramLearningOutcome` records with mapping
- [x] 3.3 Clone `PerformanceIndicator` records, remapping `plo` to cloned PLOs
- [x] 3.4 Clone `PLOPOMapping` records, remapping `plo` and `po` to cloned objects
- [x] 3.5 Clone `SemesterPlan` records, remapping `version` and `program_course`
- [x] 3.6 Clone `CoursePLOContribution` records, remapping `program_course` and `pi`
- [x] 3.7 Clone `PLOAssessmentPlan` records, remapping `version` and `pi`

## 4. Serializer Updates

- [x] 4.1 Add `TrainingProgramVersionSerializer` (list/detail)
- [x] 4.2 Update `TrainingProgramDetailSerializer` to include `versions` list
- [x] 4.3 Update `TrainingProgramListSerializer` PO/PLO counts to reference active version

## 5. View & URL Updates

- [x] 5.1 Add `_get_version()` helper for version resolution via `?version=` query param
- [x] 5.2 Update `ProgramObjectiveViewSet` and `PLOViewSet` to filter by version
- [x] 5.3 Update `PerformanceIndicatorViewSet` to filter by PLO's version
- [x] 5.4 Update `POPLOMatrixView`, `CoursePLOMatrixView`, `PLOCoverageValidationView` to use version
- [x] 5.5 Update `PLOAssessmentPlanViewSet` to filter by version
- [x] 5.6 Add `TrainingProgramVersionViewSet` with CRUD + clone + set-active actions
- [x] 5.7 Add version routes in `urls.py`

## 6. Admin Updates

- [x] 6.1 Register `TrainingProgramVersion` in admin with inline on `TrainingProgramAdmin`
- [x] 6.2 Add version selector/dropdown on program change form template
- [x] 6.3 Store `active_version_id` in session, update `ProgramContextMixin`
- [x] 6.4 Update `ProgramObjectiveAdmin`, `PLOAdmin`, `PIAdmin`, `PLOAssessmentPlanAdmin` to filter by active version

## 7. Test Updates

- [x] 7.1 Add `TrainingProgramVersionFactory`, update PO/PLO/PLOAssessmentPlan factories to use `version` FK
- [ ] 7.2 Update `test_ctdt_core.py` tests to create version before POs/PLOs
- [ ] 7.3 Update `test_ctdt_matrices.py` and `test_courses.py` tests
- [ ] 7.4 Extend `test_services_versioning.py` to verify PO/PLO/PI/PLOPOMapping/PLOAssessmentPlan cloning
- [ ] 7.5 Run full test suite and fix any remaining failures

## 8. Verification

- [ ] 8.1 Run migrations on live database and verify data integrity
- [ ] 8.2 Manual admin UI verification: version dropdown, PO/PLO CRUD, clone
- [ ] 8.3 Run full test suite: `pytest -x -v`
