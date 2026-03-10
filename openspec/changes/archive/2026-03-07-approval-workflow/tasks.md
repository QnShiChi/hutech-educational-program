# Tasks: Approval Workflow & Versioning

---

## Group 1: Models & Migrations

**Acceptance criteria:** All models created, migrations applied, Django Admin configured.

- [x] 1.1 Create `hutech_program/workflows/` app (if not exists), add to INSTALLED_APPS
- [x] 1.2 Create `WorkflowStatus`, `StepStatus`, `EntityType` TextChoices enums
- [x] 1.3 Create `ApprovalWorkflow` model with UniqueConstraint for active workflow per entity
- [x] 1.4 Create `ApprovalStep` model with optimistic locking `version` field
- [x] 1.5 Create `ApprovalComment` model with self-referencing `parent` for threading
- [x] 1.6 Create `EntityVersion` model with JSONField `snapshot_data`
- [x] 1.7 Create `Notification` model with compound index (user, is_read, created_at)
- [x] 1.8 Run `makemigrations workflows` and `migrate`
- [x] 1.9 Register all models in `admin.py` with:
  - ApprovalWorkflow: list_display=[entity_type, entity_id, status, initiated_by, created_at], list_filter=[status, entity_type]
  - ApprovalStep: inline under Workflow
  - Notification: list_display=[user, title, is_read, created_at], list_filter=[is_read, category]
  - EntityVersion: list_display=[entity_type, version_number, created_by, created_at], readonly_fields=[snapshot_data]
- [x] 1.10 Verify: `python manage.py check` passes, admin loads correctly

---

## Group 2: Service Layer — WorkflowService

**Acceptance criteria:** All state transitions work correctly, validation prevents invalid transitions.
**Depends on:** Group 1

- [x] 2.1 Create `hutech_program/workflows/services/__init__.py`
- [x] 2.2 Create `WorkflowService` class with `WORKFLOW_CONFIGS` and `STATUS_MAPS` dicts
- [x] 2.3 Implement `submit(entity, entity_type, user)`:
  - Validate entity status is DRAFT or REVISION_REQUIRED
  - Validate no active workflow exists for this entity
  - Validate user permission (creator or LANH_DAO_KHOA for CTDT, assigned_to for syllabus)
  - Create ApprovalWorkflow + all ApprovalStep records in transaction
  - Set first step to IN_REVIEW, update entity status
  - Return created workflow
- [x] 2.4 Implement `approve(workflow, user, comment)`:
  - Validate user has correct role for current step
  - Validate department scope (if required_department_scope=True)
  - Use optimistic locking: check step.version before update
  - Mark current step APPROVED with comment, acted_by, acted_at
  - If not final: advance to next step, update entity status
  - If final: call `_complete_workflow()`
- [x] 2.5 Implement `reject(workflow, user, comment)`:
  - Validate comment is not empty
  - Validate user role + department
  - Mark current step REJECTED
  - Set workflow status REJECTED
  - Set entity status REVISION_REQUIRED
- [x] 2.6 Implement `_validate_approver(step, user, entity)`:
  - Check UserRole exists with matching role
  - If dept_scope=True: check UserRole.department matches entity.managing_department
  - Raise PermissionDenied with Vietnamese message if invalid
- [x] 2.7 Implement `_advance_to_next_step(workflow)`:
  - Set next step status to IN_REVIEW
  - Update workflow.current_step_number
  - Update entity status from STATUS_MAPS
- [x] 2.8 Implement `_complete_workflow(workflow, user)`:
  - Set workflow status COMPLETED, completed_at
  - Set entity status PUBLISHED
  - Increment entity.version
  - Call VersionService.create_snapshot()
- [x] 2.9 Implement `_get_notifiable_users(step, entity)`:
  - Query UserRole for matching role
  - If dept_scope: filter by entity's department
  - Exclude the current actor (don't notify yourself)

---

## Group 3: Service Layer — VersionService

**Acceptance criteria:** Snapshots capture all nested data, diff and rollback work correctly.
**Depends on:** Group 1

- [x] 3.1 Create `VersionService` class
- [x] 3.2 Implement `create_snapshot(entity, entity_type, user, workflow)`:
  - For TrainingProgram: serialize with POs, PLOs (with PIs, PO mappings), KnowledgeBlocks, ProgramCourses (with Course, prerequisites, PLO contributions), SemesterPlans, AssessmentPlans
  - Use DRF serializers for consistent output
  - Store as EntityVersion record
- [x] 3.3 Implement `_serialize_training_program(program)`:
  - Use select_related and prefetch_related for performance
  - Output flat JSON (no nested model references, only data)
  - Include all field values, not just IDs
- [x] 3.4 Implement `compare_versions(entity_type, entity_id, v1, v2)`:
  - Load both snapshots
  - Deep diff: iterate keys, detect added/removed/modified
  - For arrays (PLOs, courses): match by code field, detect item-level changes
  - Return structured diff: `{program: {...}, plos: {added, removed, modified}, courses: {added, removed, modified}}`
- [x] 3.5 Implement `rollback(entity_type, entity_id, target_version, user)`:
  - Load target snapshot
  - Delete current nested entities (POs, PLOs, PIs, etc.)
  - Recreate from snapshot data
  - Set entity status DRAFT, reset any active workflow
  - Create new EntityVersion with change_summary "Rollback từ v{current} về v{target}"
- [x] 3.6 Implement `_deep_diff(old, new)` utility:
  - Handle nested dicts, lists of dicts (match by 'code' or 'id' key)
  - Return only changed fields (not full objects)

---

## Group 4: Service Layer — NotificationService

**Acceptance criteria:** Notifications created for all workflow events, reminders work.
**Depends on:** Group 1

- [x] 4.1 Create `NotificationService` class
- [x] 4.2 Implement `notify_users(users_qs, title, message, link, category)`:
  - Bulk create Notification records (Notification.objects.bulk_create)
  - Return created notifications
- [x] 4.3 Implement `notify_step_approvers(step, entity)`:
  - Find users with step.required_role (+ department filter if scoped)
  - Create notification with link to entity workflow tab
- [x] 4.4 Implement `notify_initiator(workflow, title, message)`:
  - Notify workflow.initiated_by
  - Include rejection comment if applicable
- [x] 4.5 Implement `notify_department_users(department, title, message, link)`:
  - For final approval: notify all users in entity's department
- [x] 4.6 Create Celery task `check_overdue_approvals`:
  - Find IN_REVIEW steps where `updated_at < now - timedelta(days=settings.APPROVAL_OVERDUE_DAYS)`
  - Call notify_step_approvers for each overdue step
  - Register in Celery beat schedule (daily 08:00)
- [x] 4.7 Create Celery task `cleanup_old_notifications`:
  - Delete read notifications older than 90 days
  - Register weekly

---

## Group 5: Serializers

**Acceptance criteria:** All API request/response shapes match spec scenarios.
**Depends on:** Group 1

- [x] 5.1 `ApprovalWorkflowSerializer`:
  - Read: id, entity_type, entity_id, status, current_step_number, total_steps, initiated_by (name), created_at, completed_at
  - Nested: steps (list of ApprovalStepSerializer)
- [x] 5.2 `ApprovalStepSerializer`:
  - Read: id, step_number, step_name, required_role (code + name), status, acted_by (name), acted_at, action_comment
  - Nested: comments (list of ApprovalCommentSerializer)
- [x] 5.3 `ApprovalCommentSerializer`:
  - Read: id, author (name), content, parent_id, created_at
  - Write: content, parent_id (optional)
- [x] 5.4 `SubmitSerializer`: (empty or with optional comment)
- [x] 5.5 `ApproveSerializer`: comment (optional string)
- [x] 5.6 `RejectSerializer`: comment (required string, min_length=10)
- [x] 5.7 `EntityVersionSerializer`:
  - Read: id, version_number, change_summary, created_by (name), created_at
  - Detail: + snapshot_data
- [x] 5.8 `VersionComparisonSerializer`:
  - v1, v2, changes (nested diff structure)
- [x] 5.9 `NotificationSerializer`:
  - Read: id, title, message, link, category, is_read, created_at
  - Write (PATCH): is_read
- [x] 5.10 `PendingApprovalSerializer`:
  - entity_type, entity_id, entity_name, submitted_by, submitted_at, days_waiting, department_name, step_name

---

## Group 6: API Views & URLs

**Acceptance criteria:** All endpoints from spec work, permissions enforced, Swagger documented.
**Depends on:** Groups 2, 3, 4, 5

- [x] 6.1 Create `WorkflowActionMixin` (reusable for Program/PLO/Syllabus views):
  - `submit()` action
  - `approve()` action
  - `reject()` action
  - `workflow()` action (GET current)
  - `workflow_history()` action (GET all)
- [x] 6.2 Add mixin to `TrainingProgramViewSet` (extra actions: submit, approve, reject, workflow, workflow_history)
- [x] 6.3 Create `ApprovalCommentViewSet`:
  - POST /workflows/{wf_id}/steps/{step_id}/comments/
  - GET /workflows/{wf_id}/steps/{step_id}/comments/
  - Permission: workflow initiator OR users with step's required role
- [x] 6.4 Create `EntityVersionViewSet`:
  - GET /programs/{id}/versions/ (list)
  - GET /programs/{id}/versions/{version_number}/ (detail with snapshot)
  - GET /programs/{id}/versions/compare/?v1=X&v2=Y
  - POST /programs/{id}/versions/{version_number}/rollback/ (PDT/ADMIN only)
- [x] 6.5 Create `NotificationViewSet`:
  - GET /notifications/ (filtered by current user, paginated)
  - GET /notifications/unread-count/
  - PATCH /notifications/{id}/ (mark read)
  - POST /notifications/mark-all-read/
- [x] 6.6 Create `PendingApprovalsView`:
  - GET /workflows/pending/ (filtered by current user's roles)
  - Query: find all steps with status=IN_REVIEW where user has matching role (+dept)
  - Annotate with days_waiting
  - Filter: ?entity_type=TrainingProgram
- [x] 6.7 Register all URLs in `config/api_router.py`:

  ```python
  # Workflow comments
  router.register(r'workflows/(?P<workflow_id>[^/.]+)/steps/(?P<step_id>[^/.]+)/comments',
                  ApprovalCommentViewSet, basename='approval-comments')

  # Notifications
  router.register(r'notifications', NotificationViewSet, basename='notifications')

  # Pending (function-based or ViewSet)
  path('api/v1/workflows/pending/', PendingApprovalsView.as_view()),

  # Version endpoints added as extra actions on ProgramViewSet
  ```

- [x] 6.8 Add drf-spectacular `@extend_schema` decorators with examples for all endpoints

---

## Group 7: Entity Integration

**Acceptance criteria:** TrainingProgram (and later PLO, Syllabus) properly integrates with workflow.
**Depends on:** Group 6

- [x] 7.1 Add helper methods to `TrainingProgram` model:
  - `can_edit` property: True only if status in (DRAFT, REVISION_REQUIRED)
  - `can_submit` property: True if DRAFT or REVISION_REQUIRED
  - `active_workflow` property: returns current IN_PROGRESS workflow or None
- [x] 7.2 Add edit protection to `TrainingProgramViewSet.update()`:
  - If not program.can_edit: raise ValidationError
- [x] 7.3 Add signals/hooks: on TrainingProgram save → create AuditLog entry
- [x] 7.4 (Future prep) Add same pattern to PLO model
- [x] 7.5 (Future prep) Document integration pattern for Syllabus (V2)

---

## Group 8: Tests

**Acceptance criteria:** >90% coverage on workflows app, all spec scenarios covered.
**Depends on:** All groups

- [x] 8.1 Create `factories.py`:
  - ApprovalWorkflowFactory (with related steps)
  - ApprovalStepFactory
  - ApprovalCommentFactory
  - EntityVersionFactory
  - NotificationFactory
  - Helper: `create_workflow_for_program(program, initiated_by)` → full workflow + steps
- [x] 8.2 **Test submit:**
  - Happy path: DRAFT → KHOA_REVIEWING + workflow created + notifications
  - Fail: wrong status (PUBLISHED)
  - Fail: no permission (GIANG_VIEN who is not creator)
  - Fail: already has active workflow
- [x] 8.3 **Test approve:**
  - Happy path: Khoa approves → PDT_REVIEWING
  - Happy path: BGH approves (final) → PUBLISHED + version created
  - Fail: wrong role
  - Fail: wrong department
  - Fail: optimistic lock conflict (concurrent approve)
- [x] 8.4 **Test reject:**
  - Happy path: PDT rejects → REVISION_REQUIRED + notification
  - Fail: empty comment
  - Fail: wrong role
- [x] 8.5 **Test revision + resubmit:**
  - Edit while REVISION_REQUIRED → allowed
  - Submit again → new workflow created, old stays REJECTED
  - Full cycle: submit → reject → revise → submit → approve all → PUBLISHED
- [x] 8.6 **Test comments:**
  - Create comment on step
  - Reply to comment (threading)
  - Permission: only initiator + approvers can comment
- [x] 8.7 **Test version snapshot:**
  - Snapshot contains all nested data (POs, PLOs, PIs, courses, matrix)
  - Snapshot is complete (can reconstruct entity from snapshot alone)
- [x] 8.8 **Test version comparison:**
  - Compare 2 versions: detect added/removed/modified items
  - Handle added PLO, removed course, changed credit count
- [x] 8.9 **Test rollback:**
  - Rollback to v1 from v3 → entity restored, new v4 created
  - Status reset to DRAFT
  - Active workflow cancelled
- [x] 8.10 **Test notifications:**
  - Submit → approvers notified
  - Approve → next approvers + initiator notified
  - Reject → initiator notified with comment
  - Final approve → initiator + department notified
- [x] 8.11 **Test pending approvals:**
  - PDT user sees only items at PDT step
  - Khoa user sees only items in their department
  - Days waiting calculated correctly
- [x] 8.12 **Test auto-reminder:**
  - Step overdue 8 days → reminder notification created
  - Step overdue 3 days → no reminder (threshold 7)
- [x] 8.13 **Test concurrency:**
  - Two users approve same step simultaneously → one 409 Conflict
- [x] 8.14 **Test full end-to-end:**
  - Create program → add PLOs + courses → submit → approve Khoa → approve PDT → approve BGH → verify PUBLISHED + version 1 exists
  - Edit PUBLISHED program → submit again → reject at Khoa → revise → submit → approve all → version 2 exists → compare v1 vs v2
- [x] 8.15 Run coverage: `pytest --cov=hutech_program/workflows/ --cov-report=term-missing`
