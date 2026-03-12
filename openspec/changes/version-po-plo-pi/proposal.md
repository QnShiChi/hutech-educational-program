## Why

The previous `training-program-versioning` change scoped `KnowledgeBlock`, `CourseGroup`, and `ProgramCourse` under `TrainingProgramVersion`. However, `ProgramObjective` (PO), `ProgramLearningOutcome` (PLO), `PerformanceIndicator` (PI), and `PLOAssessmentPlan` still link directly to `TrainingProgram`. This means all versions share the same POs/PLOs/PIs, making it impossible for different academic years to have different learning outcomes or assessment plans — which is a common real-world need when curriculum evolves across years.

## What Changes

- **BREAKING**: `ProgramObjective`, `ProgramLearningOutcome`, and `PLOAssessmentPlan` will be scoped to `TrainingProgramVersion` instead of `TrainingProgram`.
- `PerformanceIndicator` inherits version scope via its parent PLO (no direct FK change needed).
- `PLOPOMapping` inherits version scope via its PLO/PO (no direct FK change needed).
- Data migration will safely transfer existing rows to their program's first version (same pattern as migration `0007`).
- The deep-clone service (`clone_program_version`) will be extended to also clone POs, PLOs, PIs, PLOPOMappings, PLOAssessmentPlans, SemesterPlans, and CoursePLOContributions.
- API endpoints remain at `/programs/{id}/plos/...` but resolve the version via `?version=` query parameter (backward compatible).
- Admin UI gains a version dropdown to switch between versions when managing POs/PLOs/PIs.

## Capabilities

### New Capabilities

- `version-po-plo-pi`: Scope PO, PLO, PI, and PLOAssessmentPlan under TrainingProgramVersion. Includes data migration, extended clone service, API version resolution, and admin version selector.

### Modified Capabilities

- `training-program-versioning`: The clone service is extended to also deep-clone PO/PLO/PI/PLOPOMapping/PLOAssessmentPlan/SemesterPlan/CoursePLOContribution.

## Impact

- **Models**: `ProgramObjective`, `ProgramLearningOutcome`, `PLOAssessmentPlan` — add `version` FK, make `program` FK legacy.
- **Database**: 3 new migrations (schema + data + finalize). Existing data is preserved.
- **Admin UI**: Version dropdown on program change form; PO/PLO/PI/Assessment admin views filtered by version.
- **APIs**: All views that query PO/PLO/PI/Assessment by `program` must now resolve version. Optional `?version=` query param added.
- **Services**: `clone_program_version` extended for full deep-clone.
- **Tests**: All test factories and test cases updated to create versions.
