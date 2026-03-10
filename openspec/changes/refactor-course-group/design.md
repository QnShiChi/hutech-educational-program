## Context

The `CourseGroup` model currently acts as a global lookup table where a `Course` has a ForeignKey to `CourseGroup`. When building a `TrainingProgram` with `KnowledgeBlock`s, administrators must use this predefined global list of groups.
This design fails to capture the true nature of university curricula, where a "Group of Elective Courses" is typically scoped only to a specific Knowledge Block within a specific Training Program. A group named "Elective 1" in IT Program 2026 has no relation to "Elective 1" in Business Program 2026.

By changing `CourseGroup` to belong to `KnowledgeBlock`, we can enforce the rule that students must choose one group and complete all courses within that chosen group.

## Goals / Non-Goals

**Goals:**

- Refactor `CourseGroup` to include a `ForeignKey` to `KnowledgeBlock`.
- Remove `CourseGroup` dependency from the global master `Course` model.
- Add `CourseGroup` dependency to `ProgramCourse` (which links a `Course` to a `TrainingProgram` and `KnowledgeBlock`).
- Enforce validation: A `ProgramCourse` can only be assigned to a `CourseGroup` if that `CourseGroup` belongs to the same `KnowledgeBlock` as the `ProgramCourse`.
- Update Admin forms and APIs to reflect these hierarchical changes.

**Non-Goals:**

- We are not changing how `ProgramLearningOutcome` or `PerformanceIndicator` models work.
- We are not building out the student registration frontend in this spec, only the curriculum backend definitions.

## Decisions

1. **CourseGroup relationship**: Move it to be a child of `KnowledgeBlock`.
   _Rationale_: A group of courses only exists within the context of a knowledge block in a specific training program.
2. **Total/Elective Credits on CourseGroup**:
   _Rationale_: Adding `total_credits` and `elective_credits` directly to `CourseGroup` allows the system to validate if a student has met the specific requirements for that group when they choose it.
3. **Data Migration Strategy**:
   _Rationale_: Since the structural meaning is fundamentally changing and the system is likely in early development/testing, we will clear existing `CourseGroup` data during migration to avoid complex and likely invalid data mapping, or provide a default fallback if required by Django migrations.

## Risks / Trade-offs

- **Risk: Admin UI Complexity** → Mitigation: Use Django's inline formsets to allow creating/managing `CourseGroup`s directly within the `KnowledgeBlock` admin page, keeping the workflow intuitive.
- **Risk: Orphaned Data** → Mitigation: Deleting global `CourseGroup`s will require updating existing `ProgramCourse` logic. We will wipe old groups and require re-entry according to the new schema.
