## 1. Context and Layout Implementation

- [x] 1.1 Create a custom Django admin template extension (e.g., a persistent contextual header or sidebar) for Training Programs.
- [x] 1.2 Implement the mechanism to pass and maintain the active `program_id` context (via URL parameters or session) across related admin views.

## 2. Navigation and Routing

- [x] 2.1 Override `ModelAdmin.get_urls` or `change_view` methods for TrainingProgram to enable the context-aware workflow UI.
- [x] 2.2 Update the `ModelAdmin` classes for child entities (PO, PLO, ProgramCourse, etc.) to recognize the active parent context and filter querysets accordingly.

## 3. Access Control and Status Enforcement

- [x] 3.1 Implement logic in child `ModelAdmin` classes to check the parent TrainingProgram's `can_edit` status.
- [x] 3.2 Ensure child task forms are rendered as read-only when the parent TrainingProgram is in a non-editable state.

## 4. Testing and Verification

- [x] 4.1 Verify that selecting a Training Program establishes a persistent context across child task pages.
- [x] 4.2 Validate that child forms correctly associate with the active parent program.
- [x] 4.3 Test status-based access control to ensure child tasks cannot be edited if the parent program is locked.
