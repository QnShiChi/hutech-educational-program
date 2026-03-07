# Proposal: Approval Workflow & Versioning

## Summary
Implement quy trình phê duyệt đa cấp cho CTĐT (Khoa → Phòng ĐT → BGH), version control với JSONB snapshot, và notification system.

## State Machine
```
                    ┌─────────────────────────────────────────────┐
                    │              REVISION_REQUIRED               │
                    │         (bị trả về, cần chỉnh sửa)          │
                    └──────┬──────────────────────────────────────┘
                           │ (user sửa xong)
                           ▼
    DRAFT ──submit──► SUBMITTED ──auto──► KHOA_REVIEWING
                                              │
                              approve ────────┤──── reject ──► REVISION_REQUIRED
                                              ▼
                                        KHOA_APPROVED ──auto──► PDT_REVIEWING
                                                                      │
                                                      approve ───────┤──── reject ──► REVISION_REQUIRED
                                                                      ▼
                                                                PDT_APPROVED ──auto──► BGH_REVIEWING
                                                                                            │
                                                                            approve ───────┤──── reject ──► REVISION_REQUIRED
                                                                                            ▼
                                                                                      PUBLISHED
                                                                                    (+ create version snapshot)
```

## Models

### ApprovalWorkflow
```python
class ApprovalWorkflow(UUIDModel, TimeStampedModel):
    entity_type = CharField(max_length=50)    # "TrainingProgram", "PLO", "Syllabus"
    entity_id = UUIDField()
    current_step = PositiveIntegerField(default=0)
    status = CharField(choices=WorkflowStatus)
    initiated_by = ForeignKey(User, related_name='initiated_workflows')
```

### ApprovalStep
```python
class ApprovalStep(UUIDModel, TimeStampedModel):
    workflow = ForeignKey(ApprovalWorkflow, related_name='steps')
    step_number = PositiveIntegerField()        # 1=Khoa, 2=PDT, 3=BGH
    step_name = CharField(max_length=100)       # "Xét duyệt cấp Khoa"
    approver_role = ForeignKey(Role)
    approver = ForeignKey(User, null=True)       # Người duyệt thực tế
    status = CharField(choices=StepStatus)       # PENDING, APPROVED, REJECTED
    comment = TextField(blank=True)              # Phản hồi
    acted_at = DateTimeField(null=True)
```

### ProgramVersion
```python
class ProgramVersion(UUIDModel):
    program = ForeignKey(TrainingProgram, related_name='versions')
    version_number = PositiveIntegerField()
    snapshot_data = JSONField()                  # Full CTDT data at approval time
    change_summary = TextField(blank=True)
    approved_by = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True)
```

### Notification
```python
class Notification(UUIDModel):
    user = ForeignKey(User, related_name='notifications')
    title = CharField(max_length=200)
    message = TextField()
    link = CharField(max_length=500, blank=True)
    is_read = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
```

## API Endpoints
```
# Workflow actions (on TrainingProgram)
POST /api/v1/programs/{id}/submit/          # DRAFT → SUBMITTED
POST /api/v1/programs/{id}/approve/         # Approve current step
POST /api/v1/programs/{id}/reject/          # Reject with comment
GET  /api/v1/programs/{id}/workflow/         # Current workflow status + all steps

# Version management
GET  /api/v1/programs/{id}/versions/         # List all versions
GET  /api/v1/programs/{id}/versions/{v}/     # Version detail (snapshot)
GET  /api/v1/programs/{id}/versions/compare/?v1=1&v2=2  # Diff two versions
POST /api/v1/programs/{id}/versions/{v}/rollback/       # Rollback

# Notifications
GET   /api/v1/notifications/                 # My notifications
PUT   /api/v1/notifications/{id}/read/       # Mark as read
POST  /api/v1/notifications/read-all/        # Mark all as read
GET   /api/v1/notifications/unread-count/    # Badge count

# Pending approvals
GET   /api/v1/workflows/pending/             # My pending approvals
```

## Business Rules
1. Submit: chỉ creator hoặc LANH_DAO_KHOA của cùng department
2. Approve: kiểm tra user có đúng role cho step hiện tại không
3. Reject: bắt buộc comment, reset status về REVISION_REQUIRED
4. BGH approve → auto create ProgramVersion + status = PUBLISHED
5. Notification triggers: submit, approve, reject, HP change
6. Snapshot data: serialize toàn bộ CTDT (PO, PLO, PI, courses, matrix, plans)
