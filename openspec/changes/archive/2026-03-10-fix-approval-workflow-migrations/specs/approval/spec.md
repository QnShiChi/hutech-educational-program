## MODIFIED Requirements

### Requirement: Database schema matches model code

The system SHALL have database migrations that exactly match the model definitions in `workflows/models.py`.

#### Scenario: ApprovalWorkflow table has correct columns

- **WHEN** migrations are applied
- **THEN** table `workflows_approvalworkflow` SHALL have columns: `id`, `created_at`, `updated_at`, `entity_type`, `entity_id`, `status`, `current_step_number`, `total_steps`, `initiated_by_id`, `completed_at`

#### Scenario: ApprovalStep table has correct columns

- **WHEN** migrations are applied
- **THEN** table `workflows_approvalstep` SHALL have columns: `id`, `created_at`, `updated_at`, `workflow_id`, `step_number`, `step_name`, `required_role_id`, `required_department_scope`, `status`, `acted_by_id`, `acted_at`, `action_comment`, `version`

#### Scenario: EntityVersion table replaces ProgramVersion

- **WHEN** migrations are applied
- **THEN** table `workflows_entityversion` SHALL exist with columns: `id`, `created_at`, `updated_at`, `entity_type`, `entity_id`, `version_number`, `snapshot_data`, `change_summary`, `created_by_id`, `workflow_id`

#### Scenario: ApprovalComment table exists

- **WHEN** migrations are applied
- **THEN** table `workflows_approvalcomment` SHALL exist with columns: `id`, `created_at`, `updated_at`, `step_id`, `author_id`, `content`, `parent_id`

#### Scenario: Server starts without migration errors

- **WHEN** Django server is started
- **THEN** no `ProgrammingError` about missing columns SHALL occur

### Requirement: Tests match service API

The test suite SHALL use the current service method signatures and model field names.

#### Scenario: Tests use correct field names

- **WHEN** tests reference `ApprovalWorkflow` fields
- **THEN** tests SHALL use `current_step_number` (not `current_step`)

#### Scenario: Tests use correct service signatures

- **WHEN** tests call `WorkflowService.submit()`
- **THEN** tests SHALL pass `entity_type` parameter matching the new signature

#### Scenario: Tests use correct status values

- **WHEN** tests assert workflow completion status
- **THEN** tests SHALL use `WorkflowStatus.COMPLETED` (not `APPROVED`)
