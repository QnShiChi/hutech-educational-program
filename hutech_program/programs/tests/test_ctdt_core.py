"""
Comprehensive tests for Programs (CTĐT Core) module.
Covers: CRUD, PO/PLO reorder, PO-PLO matrix, PI, KnowledgeBlock tree,
        status-based edit restrictions, department-scoped access.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from hutech_program.programs.models import (
    KnowledgeBlock,
    PerformanceIndicator,
    PLOPOMapping,
    ProgramLearningOutcome,
    ProgramObjective,
    ProgramStatus,
    TrainingProgram,
)
from hutech_program.rbac.models import Permission, PermissionModule, RolePermission
from hutech_program.rbac.tests.factories import (
    DepartmentFactory,
    PermissionFactory,
    RoleFactory,
    UserFactory,
    UserRoleFactory,
)

from .factories import (
    KnowledgeBlockFactory,
    PerformanceIndicatorFactory,
    PLOPOMappingFactory,
    ProgramLearningOutcomeFactory,
    ProgramObjectiveFactory,
    TrainingProgramFactory,
    TrainingProgramVersionFactory,
)

pytestmark = pytest.mark.django_db


# ──────── Helpers ────────


def _auth_client(user):
    """Return an APIClient authenticated as user."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _setup_user_with_programs_perms(department=None):
    """Create a user with full programs permissions in a department."""
    dept = department or DepartmentFactory()
    user = UserFactory()
    role = RoleFactory(code=f"TRUONG_NGANH_{dept.code}")
    for perm_code in [
        "programs.view", "programs.create", "programs.edit", "programs.delete",
        "plo.create", "plo.edit", "plo.delete",
    ]:
        perm, _ = Permission.objects.get_or_create(
            code=perm_code,
            defaults={"name": perm_code, "module": PermissionModule.PROGRAMS},
        )
        RolePermission.objects.get_or_create(role=role, permission=perm)
    UserRoleFactory(user=user, role=role, department=dept)
    return user, dept


def _setup_admin_user():
    """Create an ADMIN user that bypasses all permission checks."""
    user = UserFactory()
    dept = DepartmentFactory()
    admin_role = RoleFactory(code="ADMIN")
    UserRoleFactory(user=user, role=admin_role, department=dept)
    return user, dept


def _make_version(prog):
    """Helper to create a default version for a program."""
    return TrainingProgramVersionFactory(program=prog, academic_year="2024-2025")


# ════════════════════════════════════════════════════════════
# 5.2 — Test TrainingProgram CRUD
# ════════════════════════════════════════════════════════════


class TestTrainingProgramCRUD:
    def _url_list(self):
        return "/api/v1/programs/"

    def _url_detail(self, pk):
        return f"/api/v1/programs/{pk}/"

    def test_list_programs(self):
        user, dept = _setup_admin_user()
        TrainingProgramFactory.create_batch(3, managing_department=dept)
        client = _auth_client(user)

        resp = client.get(self._url_list())
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 3

    def test_create_program(self):
        user, dept = _setup_user_with_programs_perms()
        client = _auth_client(user)

        data = {
            "program_code": "7220204",
            "program_name_vi": "Ngôn ngữ Trung Quốc",
            "program_name_en": "Chinese Language",
            "degree_name": "Cử nhân Ngôn ngữ Trung Quốc",
            "education_level": "DAI_HOC",
            "managing_department": str(dept.pk),
            "total_credits": 125,
            "training_duration": "4 năm",
        }
        resp = client.post(self._url_list(), data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert TrainingProgram.objects.filter(program_code="7220204").exists()
        prog = TrainingProgram.objects.get(program_code="7220204")
        assert prog.created_by == user
        assert prog.status == ProgramStatus.DRAFT

    def test_retrieve_program_detail(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept)
        version = _make_version(prog)
        # Add some POs and PLOs
        ProgramObjectiveFactory.create_batch(2, version=version)
        ProgramLearningOutcomeFactory.create_batch(3, version=version)
        client = _auth_client(user)

        resp = client.get(self._url_detail(prog.pk))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["program_code"] == prog.program_code
        assert len(resp.data["objectives"]) == 2
        assert len(resp.data["plos"]) == 3

    def test_update_program(self):
        user, dept = _setup_user_with_programs_perms()
        prog = TrainingProgramFactory(
            managing_department=dept, status=ProgramStatus.DRAFT
        )
        client = _auth_client(user)

        resp = client.patch(
            self._url_detail(prog.pk),
            {"program_name_vi": "Updated Name"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        prog.refresh_from_db()
        assert prog.program_name_vi == "Updated Name"

    def test_delete_draft_program(self):
        user, dept = _setup_user_with_programs_perms()
        prog = TrainingProgramFactory(
            managing_department=dept, status=ProgramStatus.DRAFT
        )
        client = _auth_client(user)

        resp = client.delete(self._url_detail(prog.pk))
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not TrainingProgram.objects.filter(pk=prog.pk).exists()

    def test_cannot_delete_non_draft_program(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(
            managing_department=dept, status=ProgramStatus.SUBMITTED
        )
        client = _auth_client(user)

        resp = client.delete(self._url_detail(prog.pk))
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_filter_by_status(self):
        user, dept = _setup_admin_user()
        TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        TrainingProgramFactory(managing_department=dept, status=ProgramStatus.PUBLISHED)
        client = _auth_client(user)

        resp = client.get(self._url_list(), {"status": "DRAFT"})
        assert resp.status_code == status.HTTP_200_OK
        assert all(r["status"] == "DRAFT" for r in resp.data["results"])

    def test_search_by_name(self):
        user, dept = _setup_admin_user()
        TrainingProgramFactory(
            managing_department=dept, program_name_vi="Công nghệ thông tin"
        )
        TrainingProgramFactory(managing_department=dept, program_name_vi="Kinh tế")
        client = _auth_client(user)

        resp = client.get(self._url_list(), {"search": "Công nghệ"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["results"]) == 1

    def test_unauthenticated_access_denied(self):
        client = APIClient()
        resp = client.get(self._url_list())
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ════════════════════════════════════════════════════════════
# 5.3 — Test PO/PLO CRUD + Reorder
# ════════════════════════════════════════════════════════════


class TestPOCRUD:
    def test_list_pos(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept)
        version = _make_version(prog)
        ProgramObjectiveFactory.create_batch(3, version=version)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/objectives/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data.get("results", resp.data)
        assert len(results) == 3

    def test_create_po(self):
        user, dept = _setup_user_with_programs_perms()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = _make_version(prog)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/objectives/"
        data = {"code": "PO1", "description": "Mô tả mục tiêu", "order_index": 0}
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert ProgramObjective.objects.filter(version=version, code="PO1").exists()

    def test_reorder_pos(self):
        user, dept = _setup_user_with_programs_perms()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = _make_version(prog)
        po1 = ProgramObjectiveFactory(version=version, code="PO1", order_index=0)
        po2 = ProgramObjectiveFactory(version=version, code="PO2", order_index=1)
        po3 = ProgramObjectiveFactory(version=version, code="PO3", order_index=2)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/objectives/reorder/"
        data = {"ordered_ids": [str(po3.pk), str(po1.pk), str(po2.pk)]}
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK

        po3.refresh_from_db()
        po1.refresh_from_db()
        po2.refresh_from_db()
        assert po3.order_index == 0
        assert po1.order_index == 1
        assert po2.order_index == 2


class TestPLOCRUD:
    def test_list_plos(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept)
        version = _make_version(prog)
        ProgramLearningOutcomeFactory.create_batch(4, version=version)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/plos/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data.get("results", resp.data)
        assert len(results) == 4

    def test_create_plo(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = _make_version(prog)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/plos/"
        data = {
            "code": "PLO1",
            "description": "Áp dụng kiến thức cơ bản",
            "competency_level": "3.0",
            "competency_label": "Thành thạo",
            "order_index": 0,
        }
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED

    def test_plo_competency_level_validation(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = _make_version(prog)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/plos/"
        data = {
            "code": "PLO1",
            "description": "Test",
            "competency_level": "7.0",
            "order_index": 0,
        }
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_reorder_plos(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept)
        version = _make_version(prog)
        plo1 = ProgramLearningOutcomeFactory(version=version, order_index=0)
        plo2 = ProgramLearningOutcomeFactory(version=version, order_index=1)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/plos/reorder/"
        data = {"ordered_ids": [str(plo2.pk), str(plo1.pk)]}
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK

        plo2.refresh_from_db()
        plo1.refresh_from_db()
        assert plo2.order_index == 0
        assert plo1.order_index == 1


# ════════════════════════════════════════════════════════════
# 5.4 — Test PO-PLO Matrix Bulk Update
# ════════════════════════════════════════════════════════════


class TestPOPLOMatrix:
    def test_get_matrix(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept)
        version = _make_version(prog)
        po1 = ProgramObjectiveFactory(version=version, code="PO1")
        plo1 = ProgramLearningOutcomeFactory(version=version, code="PLO1")
        PLOPOMappingFactory(plo=plo1, po=po1)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/po-plo-matrix/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["mappings"]) == 1

    def test_bulk_update_matrix(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = _make_version(prog)
        po1 = ProgramObjectiveFactory(version=version, code="PO1")
        po2 = ProgramObjectiveFactory(version=version, code="PO2")
        plo1 = ProgramLearningOutcomeFactory(version=version, code="PLO1")
        plo2 = ProgramLearningOutcomeFactory(version=version, code="PLO2")
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/po-plo-matrix/"
        data = {
            "mappings": [
                {"plo_id": str(plo1.pk), "po_id": str(po1.pk)},
                {"plo_id": str(plo1.pk), "po_id": str(po2.pk)},
                {"plo_id": str(plo2.pk), "po_id": str(po1.pk)},
            ]
        }
        resp = client.put(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 3
        assert PLOPOMapping.objects.filter(plo__version=version).count() == 3

    def test_matrix_replace_all(self):
        """Bulk update replaces all existing mappings."""
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = _make_version(prog)
        po1 = ProgramObjectiveFactory(version=version, code="PO1")
        plo1 = ProgramLearningOutcomeFactory(version=version, code="PLO1")
        PLOPOMappingFactory(plo=plo1, po=po1)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/po-plo-matrix/"
        # Send empty to clear all
        data = {"mappings": []}
        resp = client.put(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert PLOPOMapping.objects.filter(plo__version=version).count() == 0


# ════════════════════════════════════════════════════════════
# 5.5 — Test PI CRUD
# ════════════════════════════════════════════════════════════


class TestPerformanceIndicatorCRUD:
    def test_list_pis(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept)
        version = _make_version(prog)
        plo = ProgramLearningOutcomeFactory(version=version)
        PerformanceIndicatorFactory.create_batch(3, plo=plo)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/plos/{plo.pk}/pis/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data.get("results", resp.data)
        assert len(results) == 3

    def test_create_pi(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = _make_version(prog)
        plo = ProgramLearningOutcomeFactory(version=version)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/plos/{plo.pk}/pis/"
        data = {
            "code": "PI.1.1",
            "description": "Mô tả chỉ số",
            "order_index": 0,
        }
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert PerformanceIndicator.objects.filter(plo=plo, code="PI.1.1").exists()

    def test_update_pi(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept)
        version = _make_version(prog)
        plo = ProgramLearningOutcomeFactory(version=version)
        pi = PerformanceIndicatorFactory(plo=plo)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/plos/{plo.pk}/pis/{pi.pk}/"
        resp = client.patch(url, {"description": "Updated"}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        pi.refresh_from_db()
        assert pi.description == "Updated"

    def test_delete_pi(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept)
        version = _make_version(prog)
        plo = ProgramLearningOutcomeFactory(version=version)
        pi = PerformanceIndicatorFactory(plo=plo)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/plos/{plo.pk}/pis/{pi.pk}/"
        resp = client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT


# ════════════════════════════════════════════════════════════
# 5.6 — Test KnowledgeBlock Tree
# ════════════════════════════════════════════════════════════


class TestKnowledgeBlockTree:
    def test_list_returns_only_root_nodes(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept)
        version = _make_version(prog)
        root = KnowledgeBlockFactory(version=version, parent=None, name="Root")
        KnowledgeBlockFactory(version=version, parent=root, name="Child")
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/knowledge-blocks/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data.get("results", resp.data)
        assert len(results) == 1
        assert results[0]["name"] == "Root"
        assert len(results[0]["children"]) == 1

    def test_create_knowledge_block(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = _make_version(prog)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/knowledge-blocks/"
        data = {
            "name": "Kiến thức đại cương",
            "required_credits": 30,
            "elective_credits": 5,
            "order_index": 0,
        }
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        kb = KnowledgeBlock.objects.get(pk=resp.data["id"])
        assert kb.total_credits == 35  # auto-calculated

    def test_auto_calculate_total_credits(self):
        """KnowledgeBlock.save() auto-calculates total_credits."""
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept)
        version = _make_version(prog)
        kb = KnowledgeBlockFactory(
            version=version, required_credits=20, elective_credits=10
        )
        assert kb.total_credits == 30

    def test_nested_children(self):
        """3-level deep tree structure."""
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept)
        version = _make_version(prog)
        root = KnowledgeBlockFactory(version=version, parent=None, name="L1")
        child = KnowledgeBlockFactory(version=version, parent=root, name="L2")
        KnowledgeBlockFactory(version=version, parent=child, name="L3")
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/knowledge-blocks/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data.get("results", resp.data)
        assert results[0]["children"][0]["children"][0]["name"] == "L3"


# ════════════════════════════════════════════════════════════
# 5.7 — Test Status-based Edit Restrictions
# ════════════════════════════════════════════════════════════


class TestStatusBasedRestrictions:
    def test_cannot_edit_published_program(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(
            managing_department=dept, status=ProgramStatus.PUBLISHED
        )
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/"
        resp = client.patch(
            url, {"program_name_vi": "New Name"}, format="json"
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_can_edit_draft_program(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(
            managing_department=dept, status=ProgramStatus.DRAFT
        )
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/"
        resp = client.patch(
            url, {"program_name_vi": "New Name"}, format="json"
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_can_edit_revision_required_program(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(
            managing_department=dept, status=ProgramStatus.REVISION_REQUIRED
        )
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/"
        resp = client.patch(
            url, {"program_name_vi": "Revised Name"}, format="json"
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_cannot_update_matrix_on_non_editable(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(
            managing_department=dept, status=ProgramStatus.PUBLISHED
        )
        version = _make_version(prog)
        po1 = ProgramObjectiveFactory(version=version, code="PO1")
        plo1 = ProgramLearningOutcomeFactory(version=version, code="PLO1")
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/po-plo-matrix/"
        data = {"mappings": [{"plo_id": str(plo1.pk), "po_id": str(po1.pk)}]}
        resp = client.put(url, data, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_is_editable_property(self):
        draft = TrainingProgramFactory(status=ProgramStatus.DRAFT)
        submitted = TrainingProgramFactory(status=ProgramStatus.SUBMITTED)
        revision = TrainingProgramFactory(status=ProgramStatus.REVISION_REQUIRED)
        published = TrainingProgramFactory(status=ProgramStatus.PUBLISHED)

        assert draft.is_editable is True
        assert submitted.is_editable is False
        assert revision.is_editable is True
        assert published.is_editable is False


# ════════════════════════════════════════════════════════════
# 5.8 — Test Department-scoped Access
# ════════════════════════════════════════════════════════════


class TestDepartmentScopedAccess:
    def test_user_can_access_own_department_program(self):
        dept = DepartmentFactory(code="CNTT")
        user, _ = _setup_user_with_programs_perms(department=dept)
        prog = TrainingProgramFactory(managing_department=dept)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK

    def test_user_cannot_access_other_department_program(self):
        dept_a = DepartmentFactory(code="CNTT")
        dept_b = DepartmentFactory(code="KINH_TE")
        user, _ = _setup_user_with_programs_perms(department=dept_a)
        prog = TrainingProgramFactory(managing_department=dept_b)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_access_any_department(self):
        dept = DepartmentFactory(code="KINH_TE")
        admin_user, _ = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept)
        client = _auth_client(admin_user)

        url = f"/api/v1/programs/{prog.pk}/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK

    def test_no_permission_user_denied(self):
        """A user with no roles at all gets 403."""
        user = UserFactory()
        prog = TrainingProgramFactory()
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN
