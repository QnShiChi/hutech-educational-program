## ADDED Requirements

### Requirement: Academic Year Versioning for Training Programs

The system SHALL allow creation of discrete versions of a Training Program bound to a specific academic year.

#### Scenario: Admin creates a new program version from scratch

- **WHEN** an administrator creates a new Training Program Version for an existing Training Program without specifying a source version
- **THEN** an empty version is created in the Draft state with the specified academic year

#### Scenario: Admin clones an existing program version

- **WHEN** an administrator creates a new Training Program Version and selects a previous version to clone
- **THEN** the system creates a new version in the Draft state and deep-copies all KnowledgeBlocks, CourseGroups, and ProgramCourses into the new version

### Requirement: Version Lifecycle Management

The system SHALL enforce a 3-state lifecycle for Training Program Versions: Draft, Active, and Archived.

#### Scenario: Version is in Draft state

- **WHEN** a version is in the Draft state
- **THEN** administrators can freely add, remove, and modify KnowledgeBlocks, CourseGroups, and ProgramCourses

#### Scenario: Version transitions to Active state

- **WHEN** an administrator changes a version's state from Draft to Active
- **THEN** the system validates the version structure and transitions the state, locking all structural entities (KnowledgeBlocks, CourseGroups, ProgramCourses) from structural deletion or addition

#### Scenario: Modifying an Active or Archived version

- **WHEN** an administrator attempts to add, remove, or modify the structure of an Active or Archived version
- **THEN** the system blocks the action and responds with a validation error

### Requirement: Version-scoped Program Structure

The system SHALL scope all curriculum structures (KnowledgeBlocks, CourseGroups, ProgramCourses) strictly to a Training Program Version rather than the parent Training Program.

#### Scenario: Fetching knowledge blocks

- **WHEN** a user or API requests the knowledge blocks for a training program
- **THEN** the request must specify the version, or the system defaults to the currently Active version, returning only blocks belonging to that specific version

#### Scenario: Course code evolution

- **WHEN** the credit requirement for a globally shared Course changes
- **THEN** the administrator must create a new global Course record and assign it to the Draft version of the new academic year's Training Program Version, leaving the older version unaffected
