## ADDED Requirements

### Requirement: Assigning a Course to a Local Course Group

The system MUST allow a course within a `TrainingProgram` (a `ProgramCourse` record) to be optionally assigned to a `CourseGroup`.

#### Scenario: Categorizing a course as part of an elective group

- **WHEN** an admin links a `Course` to a `TrainingProgram`
- **THEN** they can select a `CourseGroup` to which this course belongs.

### Requirement: Group-Block Consistency Validation

The system MUST validate that any `CourseGroup` assigned to a `ProgramCourse` belongs to the exact same `KnowledgeBlock` that the `ProgramCourse` is assigned to.

#### Scenario: Preventing cross-block mismatch

- **WHEN** an admin assigns a `ProgramCourse` to Knowledge Block A but selects a Course Group belonging to Knowledge Block B
- **THEN** the system MUST reject the assignment and return a validation error indicating the mismatch.
