## 1. Core Model Changes

- [x] 1.1 Create `TrainingProgramVersion` model (academic_year, status: Draft/Active/Archived, fk to TrainingProgram)
- [x] 1.2 Update `KnowledgeBlock` model: Add `version` ForeignKey to `TrainingProgramVersion`. Make existing `training_program` field nullable for migration.
- [x] 1.3 Add database constraints to ensure a `TrainingProgram` cannot have duplicate versions for the exact same `academic_year`.

## 2. Data Migration

- [x] 2.1 Write a data migration script to create a default `TrainingProgramVersion` (e.g., "2024-2025", Active) for every existing `TrainingProgram`.
- [x] 2.2 Update the data migration to link all existing `KnowledgeBlock` records to the newly created default `TrainingProgramVersion` of their respective `TrainingProgram`.
- [x] 2.3 Create a schema migration to drop the old `training_program` ForeignKey from `KnowledgeBlock` once data is safely migrated.

## 3. Cloning Logic and State Validation

- [ ] 3.1 Implement a service function `clone_program_version(source_version_id, new_academic_year)` wrapped in an atomic transaction.
- [ ] 3.2 Add deep-cloning logic inside the service to recursively copy `KnowledgeBlock`, `CourseGroup`, and `ProgramCourse` objects to the new version.
- [ ] 3.3 Add model validation (clean methods or pre-save signals) on `KnowledgeBlock`, `CourseGroup`, and `ProgramCourse` to reject structural changes if the parent `TrainingProgramVersion` is not `Draft`.

## 4. Admin Interface Updates

- [ ] 4.1 Create `TrainingProgramVersionAdmin` and update `TrainingProgramAdmin` to display versions via inline or linked list.
- [ ] 4.2 Update `KnowledgeBlockAdmin` to filter and select by `TrainingProgramVersion` instead of `TrainingProgram`.
- [ ] 4.3 Add a custom admin action to `TrainingProgramVersionAdmin` to trigger the "Clone Version" service function.

## 5. API and Test Updates

- [ ] 5.1 Update public/student APIs that fetch the curriculum structure to either require a `version_id` or automatically default to the program's `Active` version.
- [ ] 5.2 Write unit tests verifying the deep-cloning recursive logic.
- [ ] 5.3 Write unit tests verifying the Draft/Active/Archived state validation.
