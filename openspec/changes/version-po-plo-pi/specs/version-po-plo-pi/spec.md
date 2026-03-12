## ADDED Requirements

### Requirement: PO scoped to version
The system SHALL store `ProgramObjective` records under a `TrainingProgramVersion` instead of directly under `TrainingProgram`. Each version SHALL have its own independent set of POs.

#### Scenario: Creating a PO for a specific version
- **WHEN** a user creates a ProgramObjective and specifies a version
- **THEN** the PO is stored with `version` FK pointing to that TrainingProgramVersion

#### Scenario: Listing POs returns only version-scoped results
- **WHEN** a user queries POs for a program with a `?version=` parameter
- **THEN** only POs belonging to that specific version are returned

#### Scenario: Default version resolution
- **WHEN** a user queries POs for a program without a `?version=` parameter
- **THEN** POs belonging to the program's most recent version (by `academic_year` DESC) are returned

### Requirement: PLO scoped to version
The system SHALL store `ProgramLearningOutcome` records under a `TrainingProgramVersion` instead of `TrainingProgram`. Each version SHALL have its own independent set of PLOs.

#### Scenario: Creating a PLO for a specific version
- **WHEN** a user creates a ProgramLearningOutcome and specifies a version
- **THEN** the PLO is stored with `version` FK pointing to that TrainingProgramVersion

#### Scenario: Listing PLOs returns version-scoped results
- **WHEN** a user queries PLOs for a program with `?version=` parameter
- **THEN** only PLOs belonging to that version are returned

### Requirement: PI inherits version scope via PLO
The system SHALL scope `PerformanceIndicator` to a version indirectly through its parent PLO. No direct `version` FK is needed on PI.

#### Scenario: PI inherits its PLO's version
- **WHEN** a PI is created under a PLO
- **THEN** the PI is associated with the same version as the PLO via the `plo.version` chain

### Requirement: PLOAssessmentPlan scoped to version
The system SHALL store `PLOAssessmentPlan` records under a `TrainingProgramVersion` instead of `TrainingProgram`.

#### Scenario: Creating an assessment plan for a version
- **WHEN** a user creates a PLOAssessmentPlan for a specific version
- **THEN** the plan is stored with `version` FK pointing to that TrainingProgramVersion

#### Scenario: Assessment plans filtered by version
- **WHEN** a user queries assessment plans with `?version=` parameter
- **THEN** only plans belonging to that version are returned

### Requirement: Unique constraints per version
The system SHALL enforce `unique_together` on `(version, code)` for PO and PLO, and on `(version, pi)` for PLOAssessmentPlan.

#### Scenario: Duplicate PO code across versions allowed
- **WHEN** version A has PO code "PO1" and version B creates PO code "PO1"
- **THEN** both are allowed because they belong to different versions

#### Scenario: Duplicate PO code within same version rejected
- **WHEN** a version already has PO code "PO1" and another PO with "PO1" is created for the same version
- **THEN** the system rejects the creation with a uniqueness error

### Requirement: Safe data migration
The system SHALL migrate existing PO/PLO/PLOAssessmentPlan records to their program's first version without data loss. The old `program` FK SHALL be kept as a nullable legacy field.

#### Scenario: Existing records get version FK populated
- **WHEN** the data migration runs
- **THEN** all existing PO/PLO/PLOAssessmentPlan records have their `version` field set to the program's first TrainingProgramVersion

#### Scenario: Program without existing version
- **WHEN** a program has no TrainingProgramVersion during migration
- **THEN** a default version with `academic_year="default"` is created and assigned

### Requirement: Admin version selector
The admin interface SHALL display a version dropdown on the program change form. PO/PLO/PI/Assessment admin views SHALL filter records by the selected version.

#### Scenario: Admin selects a version
- **WHEN** an admin selects a version from the dropdown on the program change form
- **THEN** the session stores the active version ID and all related admin views filter by that version

### Requirement: Extended deep-clone
The deep-clone service SHALL clone PO, PLO, PI, PLOPOMapping, PLOAssessmentPlan, SemesterPlan, and CoursePLOContribution in addition to KnowledgeBlock, CourseGroup, and ProgramCourse.

#### Scenario: Clone version includes PO/PLO/PI
- **WHEN** a version is cloned to a new academic year
- **THEN** the new version has copies of all POs, PLOs, PIs, PLOPOMappings, PLOAssessmentPlans, SemesterPlans, and CoursePLOContributions with correctly remapped FKs

#### Scenario: Cloned PIs reference cloned PLOs
- **WHEN** a version is cloned
- **THEN** each cloned PI references its corresponding cloned PLO (not the source PLO)

#### Scenario: Cloned CoursePLOContribution references cloned entities
- **WHEN** a version is cloned
- **THEN** each cloned CoursePLOContribution references the cloned ProgramCourse and cloned PI
