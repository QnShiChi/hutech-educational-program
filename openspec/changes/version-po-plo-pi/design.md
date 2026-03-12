## Context

The `training-program-versioning` change (now archived) scoped `KnowledgeBlock`, `CourseGroup`, `ProgramCourse`, and `SemesterPlan` under `TrainingProgramVersion`. However, `ProgramObjective`, `ProgramLearningOutcome`, `PerformanceIndicator`, and `PLOAssessmentPlan` remain linked directly to `TrainingProgram`, creating an inconsistency — courses are versioned but learning outcomes are not.

Current FK relationships:
- `ProgramObjective.program` → `TrainingProgram` ✗ (needs version)
- `ProgramLearningOutcome.program` → `TrainingProgram` ✗ (needs version)
- `PerformanceIndicator.plo` → PLO (inherits scope) ✓
- `PLOAssessmentPlan.program` → `TrainingProgram` ✗ (needs version)
- `PLOPOMapping.plo/po` → PLO/PO (inherits scope) ✓

## Goals / Non-Goals

**Goals:**

- Scope PO, PLO, and PLOAssessmentPlan under `TrainingProgramVersion` so each version can evolve independently.
- Safe data migration preserving all existing data (same pattern as migration `0007`).
- Extend deep-clone service to copy PO/PLO/PI/PLOPOMapping/PLOAssessmentPlan/SemesterPlan/CoursePLOContribution.
- Keep API backward compatible via optional `?version=` query param (defaults to latest version).
- Add version selector dropdown in Django admin for PO/PLO/PI management.

**Non-Goals:**

- Changing the `PerformanceIndicator` or `PLOPOMapping` FK structure (they inherit scope via PLO/PO).
- Redesigning the admin UI layout — only adding a version dropdown.
- Versioning the `Course` catalog itself.

## Decisions

**Decision 1: Add `version` FK + keep `program` FK as legacy**
Add a new `version` ForeignKey to PO/PLO/PLOAssessmentPlan. Keep the old `program` FK renamed as `_legacy` (nullable, `SET_NULL`). This matches the safe pattern already used for `ProgramCourse` and `SemesterPlan` in migration `0007`.
_Rationale_: Allows rollback and prevents data loss. The legacy field can be removed in a future cleanup migration.

**Decision 2: 3-migration approach (schema → data → finalize)**
1. Schema migration: add nullable `version` FK
2. Data migration: populate `version` from each row's `program.versions.first()`
3. Schema migration: update `unique_together`, rename old FK
_Rationale_: Separating schema and data changes makes each step individually reversible.

**Decision 3: API version resolution via query param**
All PO/PLO/PI/Assessment API endpoints (currently nested under `/programs/{id}/...`) will accept an optional `?version={uuid}` parameter. If omitted, the program's most recent version (by `academic_year` DESC) is used.
_Rationale_: Backward compatible — existing clients continue working without changes.

**Decision 4: Deep clone remapping with ID mapping dicts**
The `clone_program_version` service will maintain `old_id → new_obj` mapping dictionaries for PO, PLO, PI, and use them to remap FKs in dependent objects (PLOPOMapping, CoursePLOContribution, PLOAssessmentPlan).
_Rationale_: Proven pattern already used for KnowledgeBlock/CourseGroup/ProgramCourse cloning.

## Risks / Trade-offs

- **Risk: Data migration fails if a program has no versions** → Mitigation: Create a default version (`academic_year="default"`, DRAFT status) during data migration for orphan programs.
- **Risk: Clone performance for large programs** → Mitigation: Wrap in `@transaction.atomic` (same as existing service). PO/PLO/PI counts are small (~10-50 per program), so performance is not a concern.
- **Risk: Tests break due to FK changes** → Mitigation: Update all test factories to create a version first, then pass `version` instead of `program` to PO/PLO factories.
