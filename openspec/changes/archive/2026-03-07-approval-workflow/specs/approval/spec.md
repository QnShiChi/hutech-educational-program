# Spec: Approval Workflow

## REQ-WF-001: Workflow Creation on Submit

WHEN a user submits an entity (TrainingProgram, PLO, or Syllabus) for approval,
the system SHALL create an `ApprovalWorkflow` record linked to that entity
AND generate the appropriate number of `ApprovalStep` records based on entity type
AND set the entity status to the first reviewing state
AND set the first step status to `IN_REVIEW`.

### Scenario: Submit CTĐT for approval
```
GIVEN a TrainingProgram with status DRAFT
AND the current user is the creator OR has role LANH_DAO_KHOA in the program's department
WHEN the user calls POST /api/v1/programs/{id}/submit/
THEN the system creates an ApprovalWorkflow with:
  - entity_type = "TrainingProgram"
  - entity_id = {program.id}
  - initiated_by = {current_user}
  - status = "IN_PROGRESS"
AND creates 3 ApprovalStep records:
  | step_number | step_name              | required_role    | status   |
  |-------------|------------------------|------------------|----------|
  | 1           | Xét duyệt cấp Khoa    | LANH_DAO_KHOA    | IN_REVIEW|
  | 2           | Xét duyệt Phòng ĐT    | PHONG_DAO_TAO    | PENDING  |
  | 3           | Phê duyệt BGH         | BAN_GIAM_HIEU    | PENDING  |
AND sets TrainingProgram.status = "KHOA_REVIEWING"
AND creates Notification for all users with role LANH_DAO_KHOA in the program's department
AND returns HTTP 200 with workflow status
```

### Scenario: Submit Syllabus for approval (5 steps)
```
GIVEN a Syllabus with status DRAFT
AND the current user is the assigned lecturer OR the creator
WHEN the user calls POST /api/v1/syllabi/{id}/submit/
THEN the system creates an ApprovalWorkflow
AND creates 5 ApprovalStep records:
  | step_number | step_name                  | required_role    | status   |
  |-------------|----------------------------|------------------|----------|
  | 1           | Trưởng bộ môn kiểm tra     | TRUONG_NGANH     | IN_REVIEW|
  | 2           | Trưởng Khoa xét duyệt      | LANH_DAO_KHOA    | PENDING  |
  | 3           | Phòng Đào tạo xét duyệt    | PHONG_DAO_TAO    | PENDING  |
  | 4           | Ban Giám Hiệu phê duyệt    | BAN_GIAM_HIEU    | PENDING  |
AND sets Syllabus.status = "TBM_REVIEWING"
```

### Scenario: Submit fails — wrong status
```
GIVEN a TrainingProgram with status PUBLISHED
WHEN the user calls POST /api/v1/programs/{id}/submit/
THEN the system returns HTTP 400 with message "Chỉ có thể nộp duyệt từ trạng thái Bản nháp hoặc Cần chỉnh sửa"
AND no workflow is created
```

### Scenario: Submit fails — no permission
```
GIVEN a TrainingProgram with status DRAFT in department "Khoa CNTT"
AND the current user has role GIANG_VIEN (not the creator)
WHEN the user calls POST /api/v1/programs/{id}/submit/
THEN the system returns HTTP 403
```

### Scenario: Submit fails — already has active workflow
```
GIVEN a TrainingProgram with status KHOA_REVIEWING (already in approval)
WHEN the user calls POST /api/v1/programs/{id}/submit/
THEN the system returns HTTP 400 with message "Tài liệu đang trong quy trình phê duyệt"
```

---

## REQ-WF-002: Approve a Step

WHEN an authorized approver approves the current step,
the system SHALL mark the current step as APPROVED,
AND advance the workflow to the next step,
AND update the entity status to the next reviewing state,
AND notify the next level approvers.

IF the approved step is the final step,
the system SHALL mark the workflow as COMPLETED,
AND set the entity status to PUBLISHED,
AND create an EntityVersion snapshot.

### Scenario: Khoa approves → advance to PDT
```
GIVEN a TrainingProgram with status KHOA_REVIEWING
AND an ApprovalWorkflow with current_step_number = 1 (Khoa)
AND the current user has role LANH_DAO_KHOA in the program's department
WHEN the user calls POST /api/v1/programs/{id}/approve/ with body:
  { "comment": "Nội dung đạt yêu cầu, đồng ý chuyển Phòng ĐT" }
THEN the system updates step 1:
  - status = "APPROVED"
  - approved_by = {current_user}
  - acted_at = {now}
  - comment = "Nội dung đạt yêu cầu, đồng ý chuyển Phòng ĐT"
AND updates step 2: status = "IN_REVIEW"
AND updates workflow: current_step_number = 2
AND sets TrainingProgram.status = "PDT_REVIEWING"
AND creates Notification for all users with role PHONG_DAO_TAO
AND creates AuditLog entry with action = "APPROVE"
AND returns HTTP 200 with updated workflow status
```

### Scenario: BGH approves (final step) → PUBLISHED + version snapshot
```
GIVEN a TrainingProgram with status BGH_REVIEWING
AND an ApprovalWorkflow with current_step_number = 3 (BGH, final)
AND the current user has role BAN_GIAM_HIEU
WHEN the user calls POST /api/v1/programs/{id}/approve/ with body:
  { "comment": "Phê duyệt. Cho phép công bố chính thức." }
THEN the system updates step 3: status = "APPROVED"
AND updates workflow: status = "COMPLETED"
AND sets TrainingProgram.status = "PUBLISHED"
AND increments TrainingProgram.version
AND creates EntityVersion with:
  - entity_type = "TrainingProgram"
  - entity_id = {program.id}
  - version_number = {program.version}
  - snapshot_data = {full serialized program JSON including POs, PLOs, PIs, courses, matrices, plans}
  - created_by = {current_user}
AND creates Notification for the workflow initiator with message "CTĐT đã được BGH phê duyệt"
AND creates AuditLog entry
```

### Scenario: Approve fails — wrong role for current step
```
GIVEN a TrainingProgram with status PDT_REVIEWING (step 2 — requires PHONG_DAO_TAO)
AND the current user has role LANH_DAO_KHOA (step 1 role, not step 2)
WHEN the user calls POST /api/v1/programs/{id}/approve/
THEN the system returns HTTP 403 with message "Bạn không có quyền phê duyệt ở bước này"
```

### Scenario: Approve fails — user in wrong department
```
GIVEN a TrainingProgram belonging to "Khoa CNTT" with status KHOA_REVIEWING
AND the current user has role LANH_DAO_KHOA in "Khoa Ngoại ngữ" (different department)
WHEN the user calls POST /api/v1/programs/{id}/approve/
THEN the system returns HTTP 403
```
Note: PHONG_DAO_TAO and BAN_GIAM_HIEU roles are cross-department — no department check needed.

---

## REQ-WF-003: Reject a Step

WHEN an authorized approver rejects the current step,
the system SHALL mark the current step as REJECTED with a mandatory comment,
AND set the workflow status to REJECTED,
AND set the entity status to REVISION_REQUIRED,
AND notify the workflow initiator with the rejection reason.

### Scenario: PDT rejects → revision required
```
GIVEN a TrainingProgram with status PDT_REVIEWING
AND the current user has role PHONG_DAO_TAO
WHEN the user calls POST /api/v1/programs/{id}/reject/ with body:
  { "comment": "Ma trận HP-PLO chưa đầy đủ. PLO3 chưa có HP nào đóng góp. Yêu cầu bổ sung." }
THEN the system updates current step:
  - status = "REJECTED"
  - comment = "Ma trận HP-PLO chưa đầy đủ..."
  - acted_at = {now}
  - rejected_by = {current_user}
AND sets workflow.status = "REJECTED"
AND sets TrainingProgram.status = "REVISION_REQUIRED"
AND creates Notification for the workflow initiator:
  - title = "CTĐT bị từ chối bởi Phòng Đào tạo"
  - message = "Ma trận HP-PLO chưa đầy đủ..."
  - link = "/programs/{id}?tab=workflow"
AND creates AuditLog entry with action = "REJECT"
```

### Scenario: Reject fails — empty comment
```
GIVEN any entity in a reviewing state
WHEN the user calls POST /api/v1/programs/{id}/reject/ with body:
  { "comment": "" }
THEN the system returns HTTP 400 with message "Vui lòng nhập lý do từ chối"
```

### Scenario: Reject fails — comment is null
```
GIVEN any entity in a reviewing state
WHEN the user calls POST /api/v1/programs/{id}/reject/ with body:
  {}
THEN the system returns HTTP 400 with field error on "comment": "Trường này là bắt buộc"
```

---

## REQ-WF-004: Revision and Resubmit

WHEN an entity has status REVISION_REQUIRED,
the system SHALL allow the original submitter to edit the entity
AND resubmit it for approval.

### Scenario: Edit after rejection
```
GIVEN a TrainingProgram with status REVISION_REQUIRED
AND the current user is the workflow initiator
WHEN the user edits the program (PUT /api/v1/programs/{id}/)
THEN the edit is allowed
AND TrainingProgram.status remains REVISION_REQUIRED
AND AuditLog records the changes
```

### Scenario: Resubmit after revision
```
GIVEN a TrainingProgram with status REVISION_REQUIRED
WHEN the user calls POST /api/v1/programs/{id}/submit/
THEN the system creates a NEW ApprovalWorkflow (old one stays as REJECTED for history)
AND the new workflow starts from step 1 (Khoa)
AND sets TrainingProgram.status = "KHOA_REVIEWING"
```

### Scenario: Cannot edit while in review
```
GIVEN a TrainingProgram with status PDT_REVIEWING
WHEN ANY user calls PUT /api/v1/programs/{id}/
THEN the system returns HTTP 400 with message "Không thể chỉnh sửa khi đang trong quy trình phê duyệt"
```

---

## REQ-WF-005: Approval Comments Thread

The system SHALL support a threaded comment system for each workflow step,
allowing back-and-forth discussion between the submitter and approver.

### Scenario: Approver requests clarification (without rejecting)
```
GIVEN a TrainingProgram with status KHOA_REVIEWING
AND the current user has role LANH_DAO_KHOA
WHEN the user calls POST /api/v1/workflows/{wf_id}/steps/{step_id}/comments/ with body:
  { "content": "CLO5 và CLO6 có overlap. Giải thích sự khác biệt?" }
THEN the system creates an ApprovalComment linked to the step
AND creates Notification for the workflow initiator
AND the step remains IN_REVIEW (not rejected)
```

### Scenario: Submitter replies to comment
```
GIVEN an ApprovalComment on step 1 by the approver
AND the current user is the workflow initiator
WHEN the user calls POST /api/v1/workflows/{wf_id}/steps/{step_id}/comments/ with body:
  { "content": "CLO5 focuses on..., CLO6 focuses on...", "parent_id": "{parent_comment_id}" }
THEN the system creates a reply comment
AND creates Notification for the step approver
```

---

## REQ-WF-006: Version Snapshot

WHEN a final approval (BGH) is granted,
the system SHALL create a complete snapshot of all related data.

### Scenario: CTĐT version snapshot contents
```
GIVEN a TrainingProgram being approved by BGH
THEN the snapshot_data JSON SHALL contain:
  {
    "program": { ...all TrainingProgram fields... },
    "objectives": [ ...all POs... ],
    "plos": [
      { ...PLO fields...,
        "pis": [ ...performance indicators... ],
        "po_mappings": [ ...PO-PLO links... ]
      }
    ],
    "knowledge_blocks": [ ...tree... ],
    "courses": [
      { ...ProgramCourse fields...,
        "course": { ...Course fields... },
        "prerequisites": [ ...prerequisite codes... ],
        "plo_contributions": [ ...matrix cells... ]
      }
    ],
    "semester_plans": [ ...by semester... ],
    "assessment_plans": [ ...PLO assessment plans... ]
  }
```

---

## REQ-WF-007: Version Comparison

WHEN a user requests comparison between two versions,
the system SHALL return a structured diff showing added, removed, and changed fields.

### Scenario: Compare version 1 and version 2
```
GIVEN TrainingProgram with version 1 and version 2
WHEN the user calls GET /api/v1/programs/{id}/versions/compare/?v1=1&v2=2
THEN the system returns:
  {
    "v1": 1, "v2": 2,
    "changes": {
      "program": {
        "total_credits": {"old": 120, "new": 125}
      },
      "plos": {
        "added": [{"code": "PLO8", "description": "..."}],
        "removed": [],
        "modified": [{"code": "PLO3", "field": "description", "old": "...", "new": "..."}]
      },
      "courses": {
        "added": [{"code": "CHN550", "name": "..."}],
        "removed": [{"code": "CHN201", "name": "..."}],
        "modified": []
      }
    }
  }
```

---

## REQ-WF-008: Version Rollback

WHEN an authorized user rolls back to a previous version,
the system SHALL restore the entity to the snapshot state
AND create a new version recording the rollback.

### Scenario: Rollback CTĐT to version 1
```
GIVEN a TrainingProgram currently at version 3
AND the current user has role PHONG_DAO_TAO or ADMIN
WHEN the user calls POST /api/v1/programs/{id}/versions/1/rollback/
THEN the system restores TrainingProgram fields from version 1 snapshot
AND restores all nested entities (POs, PLOs, PIs, courses, matrices) from snapshot
AND sets TrainingProgram.status = DRAFT
AND increments version to 4
AND creates EntityVersion(version_number=4) with:
  - snapshot_data = {version 1 snapshot}
  - change_summary = "Rollback từ phiên bản 3 về phiên bản 1"
AND creates AuditLog with action = "ROLLBACK"
```

---

## REQ-WF-009: Notification System

### Scenario: Notification on submit
```
WHEN a user submits an entity
THEN the system creates Notification records for ALL users who have the required role for step 1
  in the entity's department (for Khoa-level) or globally (for PDT/BGH)
```

### Scenario: Notification on approve (non-final)
```
WHEN a step is approved and there's a next step
THEN notify ALL users with the next step's required role
AND notify the workflow initiator with status update
```

### Scenario: Notification on reject
```
WHEN a step is rejected
THEN notify the workflow initiator with:
  - The rejection comment
  - Link to the entity's workflow tab
```

### Scenario: Notification on final approve
```
WHEN BGH approves (final step)
THEN notify the workflow initiator: "Đã được phê duyệt và công bố"
AND notify all users in the entity's department: "CTĐT {name} đã được công bố phiên bản {version}"
```

---

## REQ-WF-010: Auto-Reminder

WHEN an approval step has been IN_REVIEW for more than N days (configurable, default 7),
the system SHALL send a reminder notification to the approver(s).

### Scenario: Reminder after 7 days
```
GIVEN an ApprovalStep with status IN_REVIEW
AND the step has been in IN_REVIEW for 8 days
WHEN the daily Celery beat task runs
THEN the system creates Notification for all potential approvers:
  - title = "Nhắc nhở: CTĐT chờ phê duyệt"
  - message = "CTĐT {program.name} đã chờ duyệt {8} ngày tại bước {step.step_name}"
```

---

## REQ-WF-011: Pending Approvals List

WHEN an approver accesses the pending approvals endpoint,
the system SHALL return all entities waiting for their approval.

### Scenario: Phòng ĐT views pending items
```
GIVEN user with role PHONG_DAO_TAO
WHEN they call GET /api/v1/workflows/pending/
THEN the system returns all workflows where:
  - current step's required_role = PHONG_DAO_TAO
  - current step's status = IN_REVIEW
  - ordered by oldest first (submitted_at ASC)
With each item containing:
  - entity_type, entity_id, entity_name
  - submitted_by (name)
  - submitted_at
  - days_waiting
  - department_name
```

---

## REQ-WF-012: Workflow History and Audit Trail

WHEN a user views workflow history for an entity,
the system SHALL display all past workflows (including rejected ones)
with full step details and comments.

### Scenario: View workflow history
```
GIVEN a TrainingProgram that was rejected once and then approved
WHEN the user calls GET /api/v1/programs/{id}/workflow-history/
THEN the system returns:
  [
    {
      "workflow_id": "...",
      "status": "COMPLETED",
      "initiated_by": "Nguyễn Văn A",
      "initiated_at": "2025-03-15T10:00:00Z",
      "completed_at": "2025-03-22T14:30:00Z",
      "steps": [
        {"step": 1, "name": "Khoa", "status": "APPROVED", "by": "Trần Thị B", "at": "...", "comment": "..."},
        {"step": 2, "name": "Phòng ĐT", "status": "APPROVED", "by": "Lê Văn C", "at": "...", "comment": "..."},
        {"step": 3, "name": "BGH", "status": "APPROVED", "by": "Phạm Văn D", "at": "...", "comment": "..."}
      ]
    },
    {
      "workflow_id": "...",
      "status": "REJECTED",
      "initiated_by": "Nguyễn Văn A",
      "initiated_at": "2025-02-01T09:00:00Z",
      "rejected_at": "2025-02-05T11:00:00Z",
      "steps": [
        {"step": 1, "name": "Khoa", "status": "APPROVED", "by": "...", "at": "...", "comment": "..."},
        {"step": 2, "name": "Phòng ĐT", "status": "REJECTED", "by": "...", "at": "...", "comment": "Ma trận chưa đầy đủ"}
      ]
    }
  ]
```

---

## Non-Functional Requirements

### NFR-WF-001: Concurrency
WHEN two users attempt to approve the same step simultaneously,
the system SHALL use optimistic locking (version check on ApprovalStep)
AND only the first approve succeeds; the second receives HTTP 409 Conflict.

### NFR-WF-002: Performance
The pending approvals query SHALL execute in < 100ms for up to 500 pending items.

### NFR-WF-003: Data Integrity
All workflow state transitions SHALL be wrapped in database transactions.
If any step fails (e.g., notification creation), the entire transition SHALL be rolled back.

### NFR-WF-004: Audit Completeness
Every state change on workflow, step, or entity status SHALL generate an AuditLog entry.
No state change is allowed to bypass audit logging.
