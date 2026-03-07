# Tasks: 06 - Approval Workflow & Versioning

## 1. Models

- [x] 1.1 Create ApprovalWorkflow + ApprovalStep models
- [x] 1.2 Create ProgramVersion model (JSONB snapshot)
- [x] 1.3 Create Notification model
- [x] 1.4 Migrations

## 2. Workflow Service

- [x] 2.1 Create `WorkflowService` class with state machine logic
- [x] 2.2 Implement `submit(program, user)` → creates workflow + 3 steps
- [x] 2.3 Implement `approve(program, user, comment)` → advance step
- [x] 2.4 Implement `reject(program, user, comment)` → reset to REVISION_REQUIRED
- [x] 2.5 Role validation: check user has correct role for current step
- [x] 2.6 Auto-advance: SUBMITTED→KHOA_REVIEWING, KHOA_APPROVED→PDT_REVIEWING, etc.

## 3. Versioning Service

- [x] 3.1 Create `VersionService.create_snapshot(program)` → serialize all nested data
- [x] 3.2 Create `VersionService.compare(v1, v2)` → JSON diff
- [x] 3.3 Create `VersionService.rollback(program, version)` → restore from snapshot

## 4. Notification Service

- [x] 4.1 Create `NotificationService.notify(users, title, message, link)`
- [x] 4.2 Signal handlers: on submit → notify approvers
- [x] 4.3 Signal handlers: on approve → notify creator + next approvers
- [x] 4.4 Signal handlers: on reject → notify creator with feedback

## 5. APIs

- [x] 5.1 Submit/Approve/Reject endpoints
- [x] 5.2 Workflow status endpoint
- [x] 5.3 Version list/detail/compare/rollback endpoints
- [x] 5.4 Notification CRUD endpoints
- [x] 5.5 Pending approvals endpoint (filtered by current user's role)

## 6. Tests

- [x] 6.1 Test full workflow: DRAFT → PUBLISHED
- [x] 6.2 Test reject at each level
- [x] 6.3 Test role validation (wrong role can't approve)
- [x] 6.4 Test version snapshot completeness
- [x] 6.5 Test version comparison
- [x] 6.6 Test notification creation triggers
- [x] 6.7 Test concurrent submit prevention
