## 1. Model Changes — Move Existing Fields to Version

- [x] 1.1 Add existing content fields to `TrainingProgramVersion` (total_credits, training_duration, decision_number, decision_date, general_objective, admission_requirements, graduation_requirements, career_opportunities, further_education, teaching_methodology, assessment_methodology, implementation_guide)
- [x] 1.2 Update `clone_program_version` service to copy all content fields

## 2. Model Changes — Rename Labels (verbose_name)

- [x] 2.1 Rename verbose_name cho các field hiện có

## 3. Model Changes — Add New Fields

- [x] 3.1 Thêm field `training_mode` trên TrainingProgram
- [x] 3.2 Thêm 5 fields mới trên TrainingProgramVersion

## 4. Migrations

- [x] 4.1 Create migration: add fields to Version + new fields + rename verbose_names
- [x] 4.2 Create data migration: copy field values from TrainingProgram → all linked versions
- [x] 4.3 Create migration: remove migrated fields from TrainingProgram

## 5. Admin Updates

- [x] 5.1 Update `TrainingProgramAdmin`: remove content fields, keep identity fields + training_mode
- [x] 5.2 Update `TrainingProgramVersionAdmin`: add all content fields to change form
- [x] 5.3 Verify admin UI labels match document names

## 6. Serializer & View Updates

- [x] 6.1 Update `TrainingProgramVersionSerializer` to include all content fields
- [x] 6.2 Update `TrainingProgramSerializer` — remove migrated fields, add backward compat

## 7. Seed Command & Tests

- [x] 7.1 Update `seed_nntq2025` management command
- [x] 7.2 Update factories
- [x] 7.3 Update existing tests
- [x] 7.4 Run full test suite — ✅ 97 passed, 0 failed
