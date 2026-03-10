# Design: Approval Workflow & Versioning

## Architecture Overview
```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (ViewSets)                   │
│  ProgramWorkflowView  SyllabusWorkflowView  PendingView │
└───────────────┬─────────────────┬───────────────────────┘
                │                 │
┌───────────────▼─────────────────▼───────────────────────┐
│                  Service Layer                            │
│  WorkflowService   VersionService   NotificationService  │
└───────────────┬─────────────────┬───────────────────────┘
                │                 │
┌───────────────▼─────────────────▼───────────────────────┐
│                    Model Layer                            │
│  ApprovalWorkflow  ApprovalStep  ApprovalComment         │
│  EntityVersion     Notification  AuditLog (existing)     │
└──────────────────────────────────────────────────────────┘
```

## Models

### WorkflowStatus
```python
class WorkflowStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "Đang xử lý"
    COMPLETED = "COMPLETED", "Hoàn thành"
    REJECTED = "REJECTED", "Bị từ chối"
    CANCELLED = "CANCELLED", "Đã hủy"
```

### StepStatus
```python
class StepStatus(models.TextChoices):
    PENDING = "PENDING", "Chờ đến lượt"
    IN_REVIEW = "IN_REVIEW", "Đang xét duyệt"
    APPROVED = "APPROVED", "Đã duyệt"
    REJECTED = "REJECTED", "Từ chối"
    SKIPPED = "SKIPPED", "Bỏ qua"
```

### EntityType
```python
class EntityType(models.TextChoices):
    TRAINING_PROGRAM = "TrainingProgram", "Chương trình đào tạo"
    PLO = "ProgramLearningOutcome", "Chuẩn đầu ra"
    SYLLABUS = "Syllabus", "Đề cương chi tiết"
```

### ApprovalWorkflow
```python
class ApprovalWorkflow(UUIDModel, TimeStampedModel):
    """
    Quy trình phê duyệt gắn với 1 entity (CTĐT, PLO, hoặc Đề cương).
    Mỗi entity có thể có nhiều workflows (nếu bị reject rồi submit lại).
    Chỉ 1 workflow active tại 1 thời điểm.
    """
    entity_type = models.CharField(max_length=50, choices=EntityType.choices)
    entity_id = models.UUIDField(db_index=True)
    
    status = models.CharField(max_length=20, choices=WorkflowStatus.choices,
                              default=WorkflowStatus.IN_PROGRESS)
    current_step_number = models.PositiveIntegerField(default=1)
    total_steps = models.PositiveIntegerField()
    
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='initiated_workflows'
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['status']),
            models.Index(fields=['initiated_by', '-created_at']),
        ]
        constraints = [
            # Chỉ 1 workflow IN_PROGRESS per entity tại 1 thời điểm
            models.UniqueConstraint(
                fields=['entity_type', 'entity_id'],
                condition=models.Q(status='IN_PROGRESS'),
                name='unique_active_workflow_per_entity'
            )
        ]
    
    @property
    def current_step(self):
        return self.steps.filter(step_number=self.current_step_number).first()
    
    @property
    def is_final_step(self):
        return self.current_step_number == self.total_steps
    
    def get_entity(self):
        """Resolve the actual entity object."""
        from hutech_program.programs.models import TrainingProgram
        from hutech_program.programs.models import ProgramLearningOutcome
        # Future: from hutech_program.syllabi.models import Syllabus
        model_map = {
            EntityType.TRAINING_PROGRAM: TrainingProgram,
            EntityType.PLO: ProgramLearningOutcome,
        }
        model_class = model_map.get(self.entity_type)
        if model_class:
            return model_class.objects.filter(id=self.entity_id).first()
        return None
```

### ApprovalStep
```python
class ApprovalStep(UUIDModel, TimeStampedModel):
    """
    Một bước trong quy trình phê duyệt.
    Mỗi workflow có N steps (3 cho CTĐT/PLO, 5 cho Đề cương).
    """
    workflow = models.ForeignKey(
        ApprovalWorkflow, on_delete=models.CASCADE, related_name='steps'
    )
    step_number = models.PositiveIntegerField()
    step_name = models.CharField(max_length=100)       # "Xét duyệt cấp Khoa"
    
    required_role = models.ForeignKey(
        'rbac.Role', on_delete=models.PROTECT,
        help_text="Vai trò cần có để duyệt bước này"
    )
    required_department_scope = models.BooleanField(
        default=True,
        help_text="True = phải cùng department với entity. "
                  "False = cross-department (PDT, BGH)"
    )
    
    status = models.CharField(
        max_length=20, choices=StepStatus.choices, default=StepStatus.PENDING
    )
    
    # Người thực hiện (filled when action taken)
    acted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approval_actions'
    )
    acted_at = models.DateTimeField(null=True, blank=True)
    action_comment = models.TextField(blank=True)
    
    # Optimistic locking
    version = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['step_number']
        unique_together = ['workflow', 'step_number']
        indexes = [
            models.Index(fields=['status', 'required_role']),
        ]
```

### ApprovalComment
```python
class ApprovalComment(UUIDModel, TimeStampedModel):
    """
    Comment thread trên từng bước duyệt.
    Cho phép trao đổi giữa người duyệt và người nộp mà không cần reject.
    """
    step = models.ForeignKey(
        ApprovalStep, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    content = models.TextField()
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='replies'
    )
    
    class Meta:
        ordering = ['created_at']
```

### EntityVersion
```python
class EntityVersion(UUIDModel):
    """
    Snapshot toàn bộ dữ liệu entity tại thời điểm phê duyệt cuối.
    Sử dụng JSONB cho PostgreSQL.
    """
    entity_type = models.CharField(max_length=50, choices=EntityType.choices)
    entity_id = models.UUIDField()
    version_number = models.PositiveIntegerField()
    
    snapshot_data = models.JSONField(
        help_text="Full serialized entity data at approval time"
    )
    change_summary = models.TextField(blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Metadata for the approval that created this version
    workflow = models.ForeignKey(
        ApprovalWorkflow, on_delete=models.SET_NULL, null=True,
        related_name='resulting_version'
    )
    
    class Meta:
        ordering = ['-version_number']
        unique_together = ['entity_type', 'entity_id', 'version_number']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id', '-version_number']),
        ]
```

### Notification
```python
class Notification(UUIDModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    
    # Categorization
    category = models.CharField(max_length=30, default='WORKFLOW')
    # WORKFLOW, COURSE_CHANGE, SYSTEM, REMINDER
    
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]
```

---

## Service Layer

### WorkflowService
```python
class WorkflowService:
    """
    Core service handling all workflow state transitions.
    All public methods are wrapped in database transactions.
    """
    
    # Workflow step configurations per entity type
    WORKFLOW_CONFIGS = {
        EntityType.TRAINING_PROGRAM: [
            {"step": 1, "name": "Xét duyệt cấp Khoa/Viện", "role": "LANH_DAO_KHOA", "dept_scope": True},
            {"step": 2, "name": "Xét duyệt Phòng Đào tạo", "role": "PHONG_DAO_TAO", "dept_scope": False},
            {"step": 3, "name": "Phê duyệt Ban Giám Hiệu", "role": "BAN_GIAM_HIEU", "dept_scope": False},
        ],
        EntityType.PLO: [
            # Same as TRAINING_PROGRAM
        ],
        EntityType.SYLLABUS: [
            {"step": 1, "name": "Trưởng bộ môn kiểm tra", "role": "TRUONG_NGANH", "dept_scope": True},
            {"step": 2, "name": "Trưởng Khoa/Viện xét duyệt", "role": "LANH_DAO_KHOA", "dept_scope": True},
            {"step": 3, "name": "Phòng Đào tạo xét duyệt", "role": "PHONG_DAO_TAO", "dept_scope": False},
            {"step": 4, "name": "Ban Giám Hiệu phê duyệt", "role": "BAN_GIAM_HIEU", "dept_scope": False},
        ],
    }
    
    # Entity status mapping: step_number → entity status while that step is IN_REVIEW
    STATUS_MAPS = {
        EntityType.TRAINING_PROGRAM: {
            1: "KHOA_REVIEWING", 2: "PDT_REVIEWING", 3: "BGH_REVIEWING",
        },
        EntityType.SYLLABUS: {
            1: "TBM_REVIEWING", 2: "TK_REVIEWING", 3: "PDT_REVIEWING", 4: "BGH_REVIEWING",
        },
    }
    
    @transaction.atomic
    def submit(self, entity, entity_type: str, user: User) -> ApprovalWorkflow:
        """Validate and create workflow + steps."""
        ...
    
    @transaction.atomic
    def approve(self, workflow: ApprovalWorkflow, user: User, comment: str = "") -> ApprovalStep:
        """Approve current step. If final, complete workflow + create version."""
        ...
    
    @transaction.atomic
    def reject(self, workflow: ApprovalWorkflow, user: User, comment: str) -> ApprovalStep:
        """Reject current step. Set entity to REVISION_REQUIRED."""
        ...
    
    def _validate_approver(self, step: ApprovalStep, user: User, entity) -> None:
        """Check user has correct role + department for this step. Raise PermissionDenied."""
        ...
    
    def _advance_to_next_step(self, workflow: ApprovalWorkflow) -> None:
        """Set next step to IN_REVIEW, update workflow.current_step_number."""
        ...
    
    def _complete_workflow(self, workflow: ApprovalWorkflow, user: User) -> EntityVersion:
        """Set entity PUBLISHED, create version snapshot."""
        ...
    
    def _get_notifiable_users(self, step: ApprovalStep, entity) -> QuerySet:
        """Find all users with the required role (+ department if scoped)."""
        ...
```

### VersionService
```python
class VersionService:
    
    def create_snapshot(self, entity, entity_type: str, user: User, workflow=None) -> EntityVersion:
        """Serialize entity + all nested data into JSONB snapshot."""
        ...
    
    def compare_versions(self, entity_type, entity_id, v1: int, v2: int) -> dict:
        """Deep diff two version snapshots. Returns structured changes."""
        ...
    
    @transaction.atomic
    def rollback(self, entity_type, entity_id, target_version: int, user: User) -> EntityVersion:
        """Restore entity from snapshot. Creates new version recording rollback."""
        ...
    
    def _serialize_training_program(self, program) -> dict:
        """Full serialization including POs, PLOs, PIs, courses, matrices, plans."""
        ...
    
    def _deep_diff(self, old: dict, new: dict) -> dict:
        """Recursive JSON diff. Returns {added, removed, modified} per section."""
        ...
```

### NotificationService
```python
class NotificationService:
    
    def notify_users(self, users: QuerySet, title: str, message: str,
                     link: str = "", category: str = "WORKFLOW") -> list[Notification]:
        """Bulk create notifications."""
        ...
    
    def notify_step_approvers(self, step: ApprovalStep, entity) -> None:
        """Notify all users who can approve this step."""
        ...
    
    def notify_initiator(self, workflow: ApprovalWorkflow, title: str, message: str) -> None:
        """Notify the person who started the workflow."""
        ...
    
    def send_reminders(self, overdue_days: int = 7) -> int:
        """Celery task: find overdue steps and send reminders. Returns count sent."""
        ...
```

---

## API Endpoints

### Workflow Actions (on entity)
```
POST /api/v1/programs/{id}/submit/
POST /api/v1/programs/{id}/approve/        Body: {"comment": "..."}
POST /api/v1/programs/{id}/reject/         Body: {"comment": "..."} (required)
GET  /api/v1/programs/{id}/workflow/        Current active workflow + steps
GET  /api/v1/programs/{id}/workflow-history/ All workflows (including rejected)
```
Same pattern for `/api/v1/syllabi/{id}/submit/`, etc.

### Workflow Comments
```
GET  /api/v1/workflows/{wf_id}/steps/{step_id}/comments/
POST /api/v1/workflows/{wf_id}/steps/{step_id}/comments/  Body: {"content": "...", "parent_id": null}
```

### Versions
```
GET  /api/v1/programs/{id}/versions/                     List all versions
GET  /api/v1/programs/{id}/versions/{version_number}/    Version detail (snapshot)
GET  /api/v1/programs/{id}/versions/compare/?v1=1&v2=2   Diff
POST /api/v1/programs/{id}/versions/{version_number}/rollback/
```

### Notifications
```
GET   /api/v1/notifications/                  List my notifications (paginated)
GET   /api/v1/notifications/unread-count/     Badge count
PATCH /api/v1/notifications/{id}/             Mark read: {"is_read": true}
POST  /api/v1/notifications/mark-all-read/
```

### Pending Approvals
```
GET /api/v1/workflows/pending/               My pending items
GET /api/v1/workflows/pending/?entity_type=TrainingProgram  Filter by type
```

---

## Celery Tasks

### `check_overdue_approvals`
- Schedule: daily at 08:00 AM (Asia/Ho_Chi_Minh)
- Logic: find all ApprovalSteps with status=IN_REVIEW and created_at < now - 7 days
- Action: create reminder Notification for potential approvers
- Config: overdue threshold configurable via Django settings

### `cleanup_old_notifications`
- Schedule: weekly
- Logic: delete read notifications older than 90 days

---

## Database Indexes Summary
```sql
-- ApprovalWorkflow
CREATE INDEX idx_workflow_entity ON workflows_approvalworkflow(entity_type, entity_id);
CREATE INDEX idx_workflow_status ON workflows_approvalworkflow(status);
CREATE UNIQUE INDEX idx_workflow_active_per_entity
  ON workflows_approvalworkflow(entity_type, entity_id)
  WHERE status = 'IN_PROGRESS';

-- ApprovalStep
CREATE INDEX idx_step_status_role ON workflows_approvalstep(status, required_role_id);

-- EntityVersion
CREATE INDEX idx_version_entity ON workflows_entityversion(entity_type, entity_id, version_number DESC);

-- Notification
CREATE INDEX idx_notif_user_unread ON workflows_notification(user_id, is_read, created_at DESC);
```
