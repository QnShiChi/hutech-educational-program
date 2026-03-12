## ADDED Requirements

### Requirement: Block deletion of ACTIVE versions
The system SHALL prevent deletion of any TrainingProgramVersion that has status ACTIVE, at all layers (model, admin, API).

#### Scenario: Attempt to delete ACTIVE version via admin
- **WHEN** admin user tries to delete a version with status ACTIVE
- **THEN** the delete action SHALL be blocked
- **AND** an error message "Không thể xóa phiên bản đang được áp dụng. Hãy chuyển sang phiên bản khác trước." SHALL be displayed

#### Scenario: Attempt to delete ACTIVE version via API
- **WHEN** client sends DELETE request to `/programs/{program_pk}/versions/{pk}/`
- **AND** the version has status ACTIVE
- **THEN** response SHALL be 400 Bad Request
- **AND** response body SHALL contain error message explaining version is ACTIVE

#### Scenario: Delete DRAFT version via admin
- **WHEN** admin user deletes a version with status DRAFT
- **THEN** the version and all its children (PO, PLO, PI, KB, ProgramCourse, SemesterPlan, etc.) SHALL be deleted
- **AND** the parent TrainingProgram SHALL NOT be affected
- **AND** other versions of the same program SHALL NOT be affected

#### Scenario: Delete ARCHIVED version via API
- **WHEN** client sends DELETE request to a version with status ARCHIVED
- **THEN** the version and its children SHALL be deleted successfully
- **AND** response SHALL be 204 No Content

### Requirement: Admin inline delete protection
The TrainingProgramVersionInline on TrainingProgramAdmin SHALL prevent deletion of ACTIVE version rows.

#### Scenario: Inline delete checkbox disabled for ACTIVE version
- **WHEN** admin views TrainingProgram change form with version inline
- **AND** a version row has status ACTIVE
- **THEN** the delete checkbox for that row SHALL be disabled or hidden

#### Scenario: Inline delete allowed for DRAFT version
- **WHEN** admin views TrainingProgram change form with version inline
- **AND** a version row has status DRAFT
- **THEN** the delete checkbox SHALL be available

### Requirement: Version delete does not cascade to program
Deleting a TrainingProgramVersion SHALL only delete that version and its direct children. It SHALL NOT cascade up to delete the TrainingProgram or other versions.

#### Scenario: Delete version preserves other versions
- **WHEN** a program has 3 versions (2019-2020, 2020-2021, 2021-2022)
- **AND** version 2020-2021 (DRAFT) is deleted
- **THEN** program SHALL still exist
- **AND** versions 2019-2020 and 2021-2022 SHALL still exist with all their data intact
