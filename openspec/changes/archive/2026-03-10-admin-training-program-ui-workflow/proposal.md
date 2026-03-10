## Why

The current admin interface lacks a clear, hierarchical workflow for managing training programs and their associated tasks (like POs, PLOs, Courses, Semester Plans). This makes it difficult for users to maintain context when navigating between a parent training program and its child models. This change introduces a structured UI workflow that persists the selected Training Program's context across all its child task pages, significantly improving administrative efficiency and user experience.

## What Changes

- Implement a context-preserving navigation system for Training Programs.
- When a Training Program is selected, its context (state/ID) will be maintained across all related child task views (PO, PLO, ProgramCourse, etc.).
- Navigation to a child task will route to that task's dedicated form while keeping the parent Training Program context active and visible.

## Capabilities

### New Capabilities

- `admin-training-program-workflow`: Defines the context-preserving UI workflow for managing a training program and navigating to its child models without losing the parent context.

### Modified Capabilities

## Impact

- Django Admin UI templates, specifically overriding layout or adding a persistent contextual sidebar/header for Training Programs.
- Admin view controllers (ModelAdmins) for TrainingProgram and its related child models to handle routing and context preservation.
