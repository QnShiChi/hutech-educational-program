## Why

The current architecture defines `CourseGroup` (Nhóm học phần) as a global entity shared across all training programs (CTĐT). However, in the actual university curriculum business logic, a `CourseGroup` is a local structural element within a specific `KnowledgeBlock` of a particular `TrainingProgram`.
For example, the group "Nhóm tự chọn 1" in the "Khối cơ sở ngành" of IT 2026 is entirely distinct from a group with the same name in Business Administration 2026.

This misalignment prevents us from properly enforcing the mutually exclusive elective rule: "A student must choose exactly 1 Course Group within a Knowledge Block (if groups exist) and complete all courses within that chosen group".

## What Changes

1. **Refactor `CourseGroup` Model**: Moved from being a global entity to a local entity belonging to a `KnowledgeBlock` (`ForeignKey` to `KnowledgeBlock`).
2. **Update `Course` Model**: Removed the direct dependency/link from the global `Course` master table to `CourseGroup`.
3. **Update `ProgramCourse` Model**: Added a `ForeignKey` to `CourseGroup`. This is where a global course is assigned to a specific group within a specific program.
4. **Data Integrity Enforcement**: Added validation to ensure that if a `ProgramCourse` is assigned to a `CourseGroup`, that group MUST belong to the same `KnowledgeBlock` that the `ProgramCourse` is assigned to.
5. **Admin UI Updates**: `CourseGroup` will no longer be a top-level standalone menu in the Django Admin. It will be managed inline or contextually under its parent `KnowledgeBlock`.

## Capabilities

### New Capabilities

- `course-group-local-scoping`: Ability to define mutually exclusive course groups locally within a knowledge block and track total/elective credits required specifically for that group.
- `program-course-group-assignment`: Ability to assign a course in a training program to a specific local course group, with strict validation against the parent knowledge block.

### Modified Capabilities

- `knowledge-block-management`: Knowledge blocks now act as containers for course groups.
- `course-master-management`: Courses no longer have a global group association.

## Impact

- **Database Schema**: Migrations required for `CourseGroup`, `Course`, and `ProgramCourse`. Existing `CourseGroup` data might need to be migrated or wiped (if currently safe to do so in development) as the structural meaning fundamentally changes.
- **Admin Interface**: Significant changes to how Program Managers input curriculum data. They must now define groups inside blocks before assigning courses to those groups.
- **API Endpoints**: Any APIs returning program structures will now return groups nested under blocks, changing the JSON response payload.
