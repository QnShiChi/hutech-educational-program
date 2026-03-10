## Context

The current admin interface treats all models as flat, independent entities. When administrators manage a `TrainingProgram` and need to edit its child tasks (e.g., `ProgramObjective`, `ProgramLearningOutcome`, `ProgramCourse`), they lose the context of the parent program upon navigating to the child's edit page. Stakeholders need a unified "Workflow UI" where selecting a Training Program keeps that program active, and navigating to any child task maintains this association and visual context.

## Goals / Non-Goals

**Goals:**

- Provide a persistent contextual state in the Django admin (or custom admin views) so that once a Training Program is selected, it remains the active "Parent" across subsequent child views.
- Allow administrators to navigate to dedicated forms for child tasks while understanding which Training Program they are currently modifying.
- Enforce appropriate permissions (e.g., only allowing edits when the program is in `DRAFT` or `REVISION_REQUIRED` state) consistently across this workflow.

**Non-Goals:**

- Using heavy client-side frameworks (like React) if standard Django Admin with custom templates/JavaScript can achieve the goal natively.
- Implementing drag-and-drop or pagination for child tasks (explicitly excluded based on requirements).

## Decisions

- **Decision 1:** Implement a custom Admin UI Layout (e.g., a persistent sidebar or contextual header).
  - _Rationale:_ To maintain the state across all child tasks when a Training Program is selected, we need a layout element that persists. We can pass the `program_id` as a query parameter or store it in the session, and use a custom base template for these specific admin views to render the persistent context navigation.
- **Decision 2:** Child tasks will open in their own dedicated forms rather than as inline forms on the parent page.
  - _Rationale:_ As per requirements, the flow is to navigate to the child task's form while keeping the parent state, avoiding a massively bloated single parent page if everything were an `InlineModelAdmin`.
- **Decision 3:** Leverage existing `can_edit` properties for status-based access control.
  - _Rationale:_ The `TrainingProgram` model already has `can_edit` and workflow status logic. The child views will inherit or check this parent status to enable/disable form fields appropriately.

## Risks / Trade-offs

- **Risk:** Modifying standard Django admin routing to enforce parent-child context via URLs or sessions can be complex and may conflict with standard admin breadcrumbs or URL generation.
  - _Mitigation:_ Carefully override `get_urls` and change view contexts in the relevant `ModelAdmin` classes, explicitly passing the `program_id` where needed to construct correct contextual links.
