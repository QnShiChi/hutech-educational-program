## ADDED Requirements

### Requirement: Dependent Dropdown on Popup Selection

The system SHALL load the related Course Groups when a Knowledge Block is selected via the raw_id_field popup in the Django admin interface.

#### Scenario: User selects Knowledge Block via popup

- **WHEN** user clicks the magnifying glass to select a Knowledge Block and chooses one
- **THEN** the Course Group dropdown is populated with the corresponding groups for that Knowledge Block
