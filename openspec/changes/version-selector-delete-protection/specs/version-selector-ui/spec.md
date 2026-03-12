## ADDED Requirements

### Requirement: Linked program-version dropdown selector
The admin SHALL display two linked dropdown selectors at the top of every ProgramContextMixin page:
1. Dropdown 1: Select CTĐT (all programs)
2. Dropdown 2: Select Phiên bản (versions of the selected program)

When the program dropdown changes, the version dropdown SHALL reload via AJAX to show only versions belonging to the selected program.

#### Scenario: User selects a program
- **WHEN** user selects a program from the first dropdown
- **THEN** the version dropdown SHALL reload to show all versions of that program, ordered by academic_year descending
- **AND** the latest version SHALL be auto-selected
- **AND** the session SHALL store both `active_program_id` and `active_version_id`
- **AND** the page SHALL reload to filter content by the selected version

#### Scenario: User selects a specific version
- **WHEN** user selects a version from the second dropdown
- **THEN** the session SHALL update `active_version_id`
- **AND** the page SHALL reload to filter content by the selected version

#### Scenario: No program selected
- **WHEN** no program is selected (initial state)
- **THEN** all data SHALL be displayed unfiltered
- **AND** the version dropdown SHALL be disabled

### Requirement: Content filtering by version context
All ProgramContextMixin pages SHALL filter their queryset based on the active version stored in session.

#### Scenario: PO list filtered by version
- **WHEN** user navigates to ProgramObjective changelist
- **AND** session has `active_version_id` set
- **THEN** only POs belonging to that version SHALL be displayed

#### Scenario: PLO list filtered by version
- **WHEN** user navigates to ProgramLearningOutcome changelist
- **AND** session has `active_version_id` set
- **THEN** only PLOs belonging to that version SHALL be displayed

#### Scenario: Switching programs clears version
- **WHEN** user selects a different program from the dropdown
- **THEN** the `active_version_id` SHALL be cleared
- **AND** a new default version (latest) SHALL be set for the new program

### Requirement: Version status badge
The admin context bar SHALL display the version's status (DRAFT/ACTIVE/ARCHIVED) as a color-coded badge next to the version selector.

#### Scenario: ACTIVE version selected
- **WHEN** the selected version has status ACTIVE
- **THEN** a green badge with text "Đang áp dụng" SHALL be displayed

#### Scenario: DRAFT version selected
- **WHEN** the selected version has status DRAFT
- **THEN** a yellow badge with text "Bản nháp" SHALL be displayed

#### Scenario: ARCHIVED version selected
- **WHEN** the selected version has status ARCHIVED
- **THEN** a gray badge with text "Đã lưu trữ" SHALL be displayed

### Requirement: AJAX endpoints for version selector
The admin SHALL expose JSON endpoints for the version selector:
- `GET admin/programs/get-versions/?program_id=<id>` — returns versions of a program
- `POST admin/programs/set-context/` — sets both program_id and version_id in session

#### Scenario: Get versions for a program
- **WHEN** client sends GET to `get-versions/?program_id=<id>`
- **THEN** response SHALL contain a JSON array of `{id, academic_year, status}` for that program
- **AND** results SHALL be ordered by academic_year descending
