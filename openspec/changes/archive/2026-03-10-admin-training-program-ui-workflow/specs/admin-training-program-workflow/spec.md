## ADDED Requirements

### Requirement: Persistent Training Program Context

The system SHALL maintain and display the context of a selected Training Program when navigating through its associated child models (POs, PLOs, Courses, etc.) in the administrative interface.

#### Scenario: Selecting a training program establishes context

- **WHEN** an administrator selects a specific Training Program from the list
- **THEN** an active contextual state is established for that program, visibly indicating it is the current "Parent" focus

#### Scenario: Navigating to child tasks preserves context

- **WHEN** an administrator navigates to a child task (e.g., adding a new PLO) from the active Training Program view
- **THEN** the system routes to the dedicated form for that child task
- **AND** the UI continues to display the active Training Program context

### Requirement: Context-Aware Navigation

The system SHALL provide navigation mechanisms (like a contextual sidebar or menu) that allow switching between different types of child tasks while the parent Training Program remains active.

#### Scenario: Switching between child task types

- **WHEN** an administrator is viewing POs for "Program A" and clicks to view PLOs
- **THEN** the system displays the PLOs specifically for "Program A" without losing the contextual state

### Requirement: Status-Based Access Control

The system SHALL enforce the editability of child tasks based on the workflow status of the parent Training Program.

#### Scenario: Editing child tasks of a draft program

- **WHEN** the active Training Program is in an editable state (e.g., DRAFT)
- **THEN** the administrator can add, edit, or delete its child tasks

#### Scenario: Viewing child tasks of a locked program

- **WHEN** the active Training Program is in a locked state (e.g., KHOA_APPROVED)
- **THEN** the child task forms are displayed in a read-only mode, preventing modifications
