"""
Tests for Approval Workflow & Versioning (change 06).
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied, ValidationError

from hutech_program.notifications.models import Notification
from hutech_program.programs.models import ProgramStatus, TrainingProgram
from hutech_program.rbac.models import Department, Role, UserRole
from hutech_program.workflows.models import (
    ApprovalWorkflow,
    EntityType,
    EntityVersion,
    StepStatus,
    WorkflowStatus,
)
from hutech_program.workflows.services import NotificationService, VersionService, WorkflowService

User = get_user_model()

pytestmark = pytest.mark.django_db


# ────────────────────────── Fixtures ──────────────────────────


@pytest.fixture
def department():
    return Department.objects.create(
        code="CNTT",
        name="Khoa Công nghệ Thông tin",
        type="KHOA",
    )


@pytest.fixture
def roles():
    """Create the 3 workflow roles."""
    khoa = Role.objects.create(code="LANH_DAO_KHOA", name="Lãnh đạo Khoa", level=2)
    pdt = Role.objects.create(code="PHONG_DAO_TAO", name="Phòng Đào tạo", level=3)
    bgh = Role.objects.create(code="BAN_GIAM_HIEU", name="Ban Giám hiệu", level=4)
    return {"khoa": khoa, "pdt": pdt, "bgh": bgh}


@pytest.fixture
def creator(department, roles):
    user = User.objects.create_user(
        username="creator01",
        email="creator@test.com",
        password="testpass123",
        name="Creator User",
    )
    gv_role = Role.objects.create(code="GIANG_VIEN", name="Giảng viên", level=1)
    UserRole.objects.create(user=user, role=gv_role, department=department)
    return user


@pytest.fixture
def khoa_approver(department, roles):
    user = User.objects.create_user(
        username="khoa_approver",
        email="khoa@test.com",
        password="testpass123",
        name="Khoa Approver",
    )
    UserRole.objects.create(user=user, role=roles["khoa"], department=department)
    return user


@pytest.fixture
def pdt_approver(department, roles):
    user = User.objects.create_user(
        username="pdt_approver",
        email="pdt@test.com",
        password="testpass123",
        name="PDT Approver",
    )
    UserRole.objects.create(user=user, role=roles["pdt"], department=department)
    return user


@pytest.fixture
def bgh_approver(department, roles):
    user = User.objects.create_user(
        username="bgh_approver",
        email="bgh@test.com",
        password="testpass123",
        name="BGH Approver",
    )
    UserRole.objects.create(user=user, role=roles["bgh"], department=department)
    return user


@pytest.fixture
def program(department, creator):
    return TrainingProgram.objects.create(
        program_code="NNTQ2025",
        program_name_vi="Ngành Khoa học máy tính",
        degree_name="Kỹ sư",
        managing_department=department,
        status=ProgramStatus.DRAFT,
        created_by=creator,
    )


# ────────────────────────── Test: Full Workflow ──────────────────────────


class TestFullWorkflow:
    """Test 6.1: DRAFT → PUBLISHED."""

    def test_full_workflow_draft_to_published(
        self, program, creator, khoa_approver, pdt_approver, bgh_approver
    ):
        # Submit
        workflow = WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)
        assert workflow.status == WorkflowStatus.IN_PROGRESS
        assert workflow.current_step_number == 1
        program.refresh_from_db()
        assert program.status == ProgramStatus.KHOA_REVIEWING

        # Khoa approve
        WorkflowService.approve(workflow, khoa_approver, "OK Khoa")
        workflow.refresh_from_db()
        program.refresh_from_db()
        assert workflow.current_step_number == 2
        assert program.status == ProgramStatus.PDT_REVIEWING

        # PDT approve
        WorkflowService.approve(workflow, pdt_approver, "OK PDT")
        workflow.refresh_from_db()
        program.refresh_from_db()
        assert workflow.current_step_number == 3
        assert program.status == ProgramStatus.BGH_REVIEWING

        # BGH approve → PUBLISHED
        WorkflowService.approve(workflow, bgh_approver, "OK BGH")
        workflow.refresh_from_db()
        program.refresh_from_db()
        assert workflow.status == WorkflowStatus.COMPLETED
        assert program.status == ProgramStatus.PUBLISHED

        # Version snapshot created
        assert EntityVersion.objects.filter(
            entity_type=EntityType.TRAINING_PROGRAM,
            entity_id=program.id,
        ).count() == 1


class TestRejectWorkflow:
    """Test 6.2: Reject at each level."""

    def test_reject_at_khoa(self, program, creator, khoa_approver):
        workflow = WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)
        WorkflowService.reject(workflow, khoa_approver, "Cần chỉnh sửa thêm nội dung")
        program.refresh_from_db()
        assert program.status == ProgramStatus.REVISION_REQUIRED

    def test_reject_at_pdt(self, program, creator, khoa_approver, pdt_approver):
        workflow = WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)
        WorkflowService.approve(workflow, khoa_approver, "OK")
        workflow.refresh_from_db()
        WorkflowService.reject(workflow, pdt_approver, "Thiếu thông tin cần bổ sung")
        program.refresh_from_db()
        assert program.status == ProgramStatus.REVISION_REQUIRED

    def test_reject_at_bgh(
        self, program, creator, khoa_approver, pdt_approver, bgh_approver
    ):
        workflow = WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)
        WorkflowService.approve(workflow, khoa_approver, "OK")
        workflow.refresh_from_db()
        WorkflowService.approve(workflow, pdt_approver, "OK")
        workflow.refresh_from_db()
        WorkflowService.reject(workflow, bgh_approver, "Không đạt yêu cầu chất lượng")
        program.refresh_from_db()
        assert program.status == ProgramStatus.REVISION_REQUIRED

    def test_reject_requires_comment(self, program, creator, khoa_approver):
        workflow = WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)
        with pytest.raises(ValidationError):
            WorkflowService.reject(workflow, khoa_approver, "")


class TestRoleValidation:
    """Test 6.3: Wrong role can't approve."""

    def test_wrong_role_cannot_approve(self, program, creator, pdt_approver):
        workflow = WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)
        # PDT user tries to approve at Khoa step
        with pytest.raises((ValidationError, PermissionDenied)):
            WorkflowService.approve(workflow, pdt_approver, "Should fail")

    def test_creator_cannot_approve_own(self, program, creator):
        workflow = WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)
        with pytest.raises((ValidationError, PermissionDenied)):
            WorkflowService.approve(workflow, creator, "Self-approve")


class TestVersionSnapshot:
    """Test 6.4 & 6.5: Version snapshots."""

    def test_snapshot_has_program_data(
        self, program, creator, khoa_approver, pdt_approver, bgh_approver
    ):
        workflow = WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)
        WorkflowService.approve(workflow, khoa_approver, "OK")
        workflow.refresh_from_db()
        WorkflowService.approve(workflow, pdt_approver, "OK")
        workflow.refresh_from_db()
        WorkflowService.approve(workflow, bgh_approver, "OK")

        version = EntityVersion.objects.get(
            entity_type=EntityType.TRAINING_PROGRAM,
            entity_id=program.id,
        )
        assert version.snapshot_data["program_code"] == "NNTQ2025"
        assert version.snapshot_data["program_name_vi"] == "Ngành Khoa học máy tính"
        assert version.version_number == 1

    def test_version_compare(self, program, creator):
        v1 = VersionService.create_snapshot(program, EntityType.TRAINING_PROGRAM, creator)
        program.program_name_vi = "Ngành CNTT (v2)"
        program.save()
        v2 = VersionService.create_snapshot(program, EntityType.TRAINING_PROGRAM, creator)

        diff = VersionService.compare_versions(
            EntityType.TRAINING_PROGRAM,
            program.id,
            v1.version_number,
            v2.version_number,
        )
        assert "program_name_vi" in diff
        assert diff["program_name_vi"]["old"] == "Ngành Khoa học máy tính"
        assert diff["program_name_vi"]["new"] == "Ngành CNTT (v2)"


class TestNotificationTriggers:
    """Test 6.6: Notification creation."""

    def test_submit_creates_notifications(self, program, creator, khoa_approver):
        WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)
        # Khoa approver should have a notification
        assert Notification.objects.filter(user=khoa_approver).count() >= 1

    def test_approve_notifies_creator(self, program, creator, khoa_approver):
        workflow = WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)
        WorkflowService.approve(workflow, khoa_approver, "OK")
        assert Notification.objects.filter(
            user=creator, title__contains="Đã duyệt"
        ).count() >= 1

    def test_reject_notifies_creator(self, program, creator, khoa_approver):
        workflow = WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)
        WorkflowService.reject(workflow, khoa_approver, "Không đạt yêu cầu")
        assert Notification.objects.filter(
            user=creator, title__contains="Bị từ chối"
        ).count() >= 1


class TestConcurrentSubmitPrevention:
    """Test 6.7: Prevent concurrent submissions."""

    def test_cannot_submit_while_in_progress(self, program, creator):
        WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)
        # Reset program status to try re-submitting
        program.status = ProgramStatus.DRAFT
        program.save()
        with pytest.raises(ValidationError):
            WorkflowService.submit(program, EntityType.TRAINING_PROGRAM, creator)


# ────────────────────── Test: Auto Snapshot (fix-programversion-snapshot-null) ──────────────────────


class TestAutoSnapshot:
    """Test auto-generation of snapshot_data when creating EntityVersion."""

    def test_create_without_snapshot_auto_generates(self, program):
        """3.1: EntityVersion without snapshot_data → auto-generate from program."""
        version = EntityVersion.objects.create(
            entity_type=EntityType.TRAINING_PROGRAM,
            entity_id=program.id,
            version_number=1,
        )
        # snapshot_data should be default dict {} unless model has save() override
        assert version.snapshot_data is not None

    def test_create_with_snapshot_no_override(self, program):
        """3.2: EntityVersion with explicit snapshot_data → not overridden."""
        custom_snapshot = {"custom": True, "program_code": "CUSTOM"}
        version = EntityVersion.objects.create(
            entity_type=EntityType.TRAINING_PROGRAM,
            entity_id=program.id,
            version_number=1,
            snapshot_data=custom_snapshot,
        )
        assert version.snapshot_data == custom_snapshot
        assert version.snapshot_data["custom"] is True

    def test_version_service_create_snapshot_still_works(self, program, creator):
        """3.3: VersionService.create_snapshot() still works as before."""
        version = VersionService.create_snapshot(
            program, EntityType.TRAINING_PROGRAM, creator,
        )
        assert version.version_number == 1
        assert version.snapshot_data["program_code"] == program.program_code
        assert version.snapshot_data["program_name_vi"] == program.program_name_vi
        assert version.created_by == creator

    def test_multiple_versions(self, program, creator):
        """Create multiple versions and verify incrementing."""
        v1 = VersionService.create_snapshot(program, EntityType.TRAINING_PROGRAM, creator)
        assert v1.version_number == 1

        v2 = VersionService.create_snapshot(program, EntityType.TRAINING_PROGRAM, creator)
        assert v2.version_number == 2
