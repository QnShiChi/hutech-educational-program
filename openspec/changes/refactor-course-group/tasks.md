## 1. Domain Models Refactoring

- [x] 1.1 Update `CourseGroup` model: Remove global uniqueness, add `ForeignKey` to `KnowledgeBlock`. Add `total_credits` and `elective_credits` fields.
- [x] 1.2 Update `Course` model: Remove `course_group` ForeignKey.
- [x] 1.3 Update `ProgramCourse` model: Add `course_group` ForeignKey.
- [x] 1.4 Add `clean()` validation to `ProgramCourse` to ensure the assigned `CourseGroup` belongs to the same `KnowledgeBlock` as the `ProgramCourse`.

## 2. Database Migrations

- [x] 2.1 Generate `makemigrations` for the changes in `programs` app.
- [x] 2.2 Handle data migration if necessary or ensure local SQLite reset is communicated for testing.
- [x] 2.3 Run `migrate` to apply changes.

## 3. Admin Dashboard Updates

- [x] 3.1 Remove `CourseGroupAdmin` from being registered as a standalone global model in `admin.py`.
- [x] 3.2 Add `CourseGroupInline` to `KnowledgeBlockAdmin` or manage it contextually so users can create groups inside blocks.
- [x] 3.3 Update `CourseAdmin` form to remove the `course_group` field.
- [x] 3.4 Update `ProgramCourseAdmin` or `ProgramCourseInline` to include the new `course_group` field.
- [x] 3.5 Ensure the `course_group` dropdown in `ProgramCourse` form is filtered dynamically based on the associated `KnowledgeBlock` (may require custom admin form or AJAX, or simple validation depending on current UI approach).

## 4. API & Serializer Updates (If Applicable)

- [x] 4.1 Update any read/write serializers in `api/` or `views/` that currently expose `course_group` from the global `Course`.
- [x] 4.2 Update `ProgramCourseSerializer` or equivalent to include the new local `course_group` data.

## 5. Testing & Verification

- [x] 5.1 Write/update unit tests for `ProgramCourse` validation logic (cross-block mismatch).
- [x] 5.2 Write/update unit tests to verify `CourseGroup` operations inside a `KnowledgeBlock`.
- [x] 5.3 Run `pytest` or `manage.py test` to ensure all tests pass.
