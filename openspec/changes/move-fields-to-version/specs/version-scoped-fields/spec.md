## ADDED Requirements

### Requirement: Version-scoped content fields
The `TrainingProgramVersion` model SHALL contain all content description fields that can vary between versions of the same program. These fields SHALL be independent per version.

#### Scenario: Edit total_credits on version A does not affect version B
- **WHEN** user edits `total_credits` on version 2025-2026
- **THEN** version 2025-2026 SHALL have the updated value
- **AND** version 2024-2025 SHALL retain its original value

#### Scenario: Clone version copies content fields
- **WHEN** a version is cloned
- **THEN** all content fields SHALL be copied to the new version
- **AND** changes to the cloned version SHALL NOT affect the source

### Requirement: Fields moved to version
The following fields SHALL exist on `TrainingProgramVersion` instead of `TrainingProgram`:
- `total_credits` (PositiveIntegerField)
- `training_duration` (CharField)
- `decision_number` (CharField)
- `decision_date` (DateField)
- `general_objective` (TextField)
- `admission_requirements` (TextField)
- `graduation_requirements` (TextField)
- `career_opportunities` (TextField)
- `further_education` (TextField)
- `teaching_methodology` (TextField)
- `assessment_methodology` (TextField)
- `implementation_guide` (TextField)

#### Scenario: Version form shows content fields
- **WHEN** admin user opens a TrainingProgramVersion change form
- **THEN** all 11 content fields SHALL be editable on that form

#### Scenario: Program form shows only identity fields
- **WHEN** admin user opens a TrainingProgram change form
- **THEN** only identity fields (name, code, degree, education level, department, issuing institution) SHALL be shown
- **AND** content fields SHALL NOT appear on the program form

### Requirement: Safe data migration
The migration SHALL copy existing data from `TrainingProgram` to all associated `TrainingProgramVersion` records before removing the fields from `TrainingProgram`.

#### Scenario: Existing data preserved during migration
- **WHEN** migration runs on a database with existing programs and versions
- **THEN** every version SHALL receive the content field values from its parent program
- **AND** no data SHALL be lost

#### Scenario: Program without versions gets a default version
- **WHEN** migration encounters a program with no versions
- **THEN** a default version with academic_year "default" SHALL be created
- **AND** the content fields SHALL be copied to this default version
