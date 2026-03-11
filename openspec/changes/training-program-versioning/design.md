## Context

The current `TrainingProgram` system links structural components (`KnowledgeBlock`, `CourseGroup`, `ProgramCourse`) directly to the `TrainingProgram`. This means changes to a curriculum for a new academic year modify the global structure affecting all past and present students. A versioning system tied to the academic year is required.

## Goals / Non-Goals

**Goals:**

- Separate the general concept of a Training Program (e.g., "Information Technology") from its specific academic year version.
- Ensure structural components are scoped strictly to a version.
- Automate the deep-cloning process so creating a new year's version from the latest one is a 1-click operation for administrators.
- Implement version lifecycle (Draft -> Active -> Archived). Active and Archived versions cannot be altered structurally.

**Non-Goals:**

- Versioning the `Course` catalog itself. Courses remain globally shared. If a course's core properties (like credits) must change, a new `Course` record (e.g., with a different code) should be created and referenced in the new program version.

## Decisions

**Decision 1: Normalized Database Schema (Program vs Version)**
Instead of cloning the `TrainingProgram` row and changing a year flag, we will split the models. `TrainingProgram` becomes a lightweight container (code, name). `TrainingProgramVersion` holds the `academic_year`, `status`, and acts as the foreign key target for `KnowledgeBlock`.
_Rationale_: This normalized approach prevents duplication of core program metadata and aligns perfectly with the Domain model where a Major has many Year-Versions.

**Decision 2: 3-State Workflow (Draft, Active, Archived)**
Versions will strictly follow this lifecycle.

- _Draft_: Full edit access.
- _Active_: Read-only structure, but can be used for assigning to students.
- _Archived_: Read-only, historical.
  _Rationale_: Protects data integrity for cohorts currently studying or already graduated.

**Decision 3: Deep Clone via Django ORM/Custom Action**
Creating a new version will trigger a custom Django Admin action (or API endpoint) that creates a new `TrainingProgramVersion` in `Draft` state and synchronously (or via Celery if too slow, but synchronous transaction is preferred for data consistency since it's an infrequent admin action) deep-copies all `KnowledgeBlock`, `CourseGroup`, and `ProgramCourse` objects, remaping foreign keys to the new clones.
_Rationale_: Simplifies the admin experience.

## Risks / Trade-offs

- **Risk: Breaking existing APIs/Queries** → **Mitigation**: Any API relying on `TrainingProgram` directly must be updated to either accept a `version_id` or default to the currently `Active` version.
- **Risk: Deep Clone Performance** → **Mitigation**: While a deep clone of hundreds of rows could be slow, it happens rarely (once a year per program). We will wrap the clone in a single database atomic transaction.
- **Risk: Data Migration** → **Mitigation**: We must write a data migration script that creates a default `TrainingProgramVersion` for every existing `TrainingProgram` and points all existing `KnowledgeBlock` records to it.
