## ADDED Requirements

### Requirement: CourseGroup belongs to KnowledgeBlock

The system MUST ensure that every `CourseGroup` is associated with exactly one `KnowledgeBlock` within a specific `TrainingProgram`. Course Groups are no longer global entities.

#### Scenario: Creating a course group

- **WHEN** an admin creates a new Course Group
- **THEN** they MUST select a parent Knowledge Block
- **THEN** the Course Group is only available and visible within the context of that specific Knowledge Block's Training Program.

### Requirement: CourseGroup Credit Tracking

The system MUST allow defining total credits and required elective credits at the `CourseGroup` level.

#### Scenario: Defining group requirements

- **WHEN** an admin defines a Course Group
- **THEN** they can specify the `total_credits` and `elective_credits` required for a student deciding to choose this group.

### Requirement: Global Course Model Independence

The system MUST NOT link the global `Course` master records to any specific `CourseGroup`.

#### Scenario: Creating a new global course

- **WHEN** an admin creates a new master `Course`
- **THEN** they do NOT select a Course Group. The course is group-agnostic until assigned to a specific program.
