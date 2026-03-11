## Why

Currently, the Training Program is managed as a single global entity without versioning by academic year. When a new academic year starts, administrators need to modify the program (e.g., adding/removing courses, changing credits) for new students without affecting the historical records of previous cohorts. This change introduces versioning for Training Programs, ensuring historical data integrity while providing an automated cloning mechanism to streamline the creation of new academic year versions.

## What Changes

- Introduce a new `TrainingProgramVersion` model representing a specific academic year's version of a `TrainingProgram`.
- Refactor existing structures (`KnowledgeBlock`, `CourseGroup`, `ProgramCourse`) to be children of `TrainingProgramVersion` instead of `TrainingProgram`.
- Implement a 3-state lifecycle for versions: Draft (editable), Active (read-only for structure, applies to current students), and Archived (historical).
- Add an automated deep-cloning mechanism to copy all blocks, groups, and courses when initializing a new version from the most recent one.
- **BREAKING**: The relationship hierarchy changes. Queries that previously looked up `KnowledgeBlock` by `TrainingProgram` must now query by `TrainingProgramVersion`.

## Capabilities

### New Capabilities

- `training-program-versioning`: Management of program versions with academic year, lifecycle states (Draft, Active, Archived), and the deep-cloning operation. Includes the refactoring of TrainingProgram, KnowledgeBlock, CourseGroup, and ProgramCourse to support versions.

### Modified Capabilities

## Impact

- **Models**: `TrainingProgram`, `KnowledgeBlock`, `CourseGroup`, `ProgramCourse`
- **Database**: Significant schema changes and data migration required to wrap existing programs into a default initial version.
- **Admin UI**: Need new screens to manage versions within a program and trigger the cloning action.
- **APIs**: Endpoints fetching the curriculum must now require a version context (or default to the Active version).
