"""
Comprehensive tests for CTĐT Matrices & Assessment Plan module.
Covers: CoursePLOContribution matrix (bulk update, pivot read),
        PLO Assessment Plan (CRUD, bulk upsert),
        PLO coverage validation,
        Performance for large matrix (70x21).
"""

import time

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from hutech_program.programs.models import (
    CoursePLOContribution,
    PLOAssessmentPlan,
    ProgramStatus,
)
from hutech_program.rbac.models import Permission, PermissionModule, RolePermission
from hutech_program.rbac.tests.factories import (
    DepartmentFactory,
    RoleFactory,
    UserFactory,
    UserRoleFactory,
)

from .factories import (
    CourseFactory,
    CoursePLOContributionFactory,
    PerformanceIndicatorFactory,
    PLOAssessmentPlanFactory,
    ProgramCourseFactory,
    ProgramLearningOutcomeFactory,
    TrainingProgramFactory,
    TrainingProgramVersionFactory,
)

pytestmark = pytest.mark.django_db


# ──────── Helpers ────────


def _auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _setup_admin_user():
    user = UserFactory()
    dept = DepartmentFactory()
    admin_role = RoleFactory(code="ADMIN")
    UserRoleFactory(user=user, role=admin_role, department=dept)
    return user, dept


def _setup_matrix_data(dept, n_courses=5, n_plos=3, pis_per_plo=2):
    """Create a program with version, courses, PLOs, and PIs."""
    prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
    version = TrainingProgramVersionFactory(program=prog, academic_year="2024-2025")
    courses = []
    for i in range(n_courses):
        pc = ProgramCourseFactory(version=version)
        courses.append(pc)

    plos = []
    pis = []
    for j in range(n_plos):
        plo = ProgramLearningOutcomeFactory(version=version, code=f"PLO{j}")
        plos.append(plo)
        for k in range(pis_per_plo):
            pi = PerformanceIndicatorFactory(plo=plo, code=f"PI.{j}.{k}")
            pis.append(pi)

    return prog, courses, plos, pis


# ════════════════════════════════════════════════════════════
# 4.1 — Matrix Bulk Update (including ~1000 cells)
# ════════════════════════════════════════════════════════════


class TestCoursePLOMatrixBulkUpdate:
    def test_bulk_update_matrix(self):
        user, dept = _setup_admin_user()
        prog, courses, plos, pis = _setup_matrix_data(dept, n_courses=3, n_plos=2, pis_per_plo=2)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/course-plo-matrix/"
        contributions = []
        for pc in courses:
            for pi in pis:
                contributions.append({
                    "program_course_id": str(pc.pk),
                    "pi_id": str(pi.pk),
                    "contribution_level": 2,
                })

        data = {"contributions": contributions}
        resp = client.put(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == len(contributions)
        assert CoursePLOContribution.objects.filter(
            program_course__version__program=prog
        ).count() == len(contributions)

    def test_bulk_update_replaces_existing(self):
        user, dept = _setup_admin_user()
        prog, courses, plos, pis = _setup_matrix_data(dept, n_courses=2, n_plos=1, pis_per_plo=1)
        client = _auth_client(user)

        # Create initial contribution
        CoursePLOContributionFactory(
            program_course=courses[0], pi=pis[0], contribution_level=1
        )
        assert CoursePLOContribution.objects.filter(
            program_course__version__program=prog
        ).count() == 1

        # Update with new data
        url = f"/api/v1/programs/{prog.pk}/course-plo-matrix/"
        data = {
            "contributions": [
                {
                    "program_course_id": str(courses[1].pk),
                    "pi_id": str(pis[0].pk),
                    "contribution_level": 3,
                }
            ]
        }
        resp = client.put(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        # Old contribution should be deleted, only new one exists
        assert CoursePLOContribution.objects.filter(
            program_course__version__program=prog
        ).count() == 1
        contrib = CoursePLOContribution.objects.first()
        assert contrib.contribution_level == 3
        assert contrib.program_course == courses[1]

    def test_zero_level_cells_not_stored(self):
        """Cells with contribution_level=0 should not be persisted."""
        user, dept = _setup_admin_user()
        prog, courses, plos, pis = _setup_matrix_data(dept, n_courses=2, n_plos=1, pis_per_plo=1)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/course-plo-matrix/"
        data = {
            "contributions": [
                {
                    "program_course_id": str(courses[0].pk),
                    "pi_id": str(pis[0].pk),
                    "contribution_level": 0,
                },
                {
                    "program_course_id": str(courses[1].pk),
                    "pi_id": str(pis[0].pk),
                    "contribution_level": 2,
                },
            ]
        }
        resp = client.put(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1  # Only one non-zero

    def test_bulk_update_large_matrix(self):
        """Task 4.1: ~1000 cells."""
        user, dept = _setup_admin_user()
        prog, courses, plos, pis = _setup_matrix_data(
            dept, n_courses=50, n_plos=7, pis_per_plo=3
        )
        client = _auth_client(user)

        # 50 courses × 21 PIs = 1050 cells
        url = f"/api/v1/programs/{prog.pk}/course-plo-matrix/"
        contributions = []
        for pc in courses:
            for pi in pis:
                contributions.append({
                    "program_course_id": str(pc.pk),
                    "pi_id": str(pi.pk),
                    "contribution_level": (hash(str(pc.pk) + str(pi.pk)) % 3) + 1,
                })

        data = {"contributions": contributions}
        resp = client.put(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == len(contributions)

    def test_cannot_update_non_editable_program(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(
            managing_department=dept, status=ProgramStatus.PUBLISHED
        )
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/course-plo-matrix/"
        resp = client.put(url, {"contributions": []}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_matrix_pivot_format(self):
        """Task 3.1: GET returns pivot format with columns grouped by PLO."""
        user, dept = _setup_admin_user()
        prog, courses, plos, pis = _setup_matrix_data(dept, n_courses=3, n_plos=2, pis_per_plo=2)
        # Add some contributions
        CoursePLOContributionFactory(
            program_course=courses[0], pi=pis[0], contribution_level=2
        )
        CoursePLOContributionFactory(
            program_course=courses[1], pi=pis[1], contribution_level=3
        )
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/course-plo-matrix/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert "columns" in resp.data
        assert "rows" in resp.data
        assert len(resp.data["columns"]) == 2  # 2 PLOs
        assert len(resp.data["rows"]) == 3  # 3 courses

        # Check column structure
        col = resp.data["columns"][0]
        assert "plo_id" in col
        assert "plo_code" in col
        assert "pis" in col
        assert len(col["pis"]) == 2  # 2 PIs per PLO

        # Check row structure
        row = resp.data["rows"][0]
        assert "program_course_id" in row
        assert "course_code" in row
        assert "contributions" in row


# ════════════════════════════════════════════════════════════
# 4.2 — PLO Coverage Validation
# ════════════════════════════════════════════════════════════


class TestPLOCoverageValidation:
    def test_all_plos_covered(self):
        user, dept = _setup_admin_user()
        prog, courses, plos, pis = _setup_matrix_data(dept, n_courses=3, n_plos=2, pis_per_plo=2)

        # Cover all PIs
        for pi in pis:
            CoursePLOContributionFactory(
                program_course=courses[0], pi=pi, contribution_level=1
            )
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/plo-coverage-validation/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["all_covered"] is True
        for plo_result in resp.data["plos"]:
            assert plo_result["is_covered"] is True
            assert len(plo_result["uncovered_pis"]) == 0

    def test_partial_coverage(self):
        user, dept = _setup_admin_user()
        prog, courses, plos, pis = _setup_matrix_data(dept, n_courses=3, n_plos=2, pis_per_plo=2)

        # Only cover first PLO's PIs
        CoursePLOContributionFactory(
            program_course=courses[0], pi=pis[0], contribution_level=1
        )
        CoursePLOContributionFactory(
            program_course=courses[0], pi=pis[1], contribution_level=2
        )
        # PIs[2] and PIs[3] are from PLO2 and uncovered
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/plo-coverage-validation/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["all_covered"] is False
        # First PLO should be covered
        assert resp.data["plos"][0]["is_covered"] is True
        # Second PLO should not be covered
        assert resp.data["plos"][1]["is_covered"] is False
        assert len(resp.data["plos"][1]["uncovered_pis"]) == 2

    def test_no_contributions_at_all(self):
        user, dept = _setup_admin_user()
        prog, courses, plos, pis = _setup_matrix_data(dept, n_courses=3, n_plos=2, pis_per_plo=2)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/plo-coverage-validation/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["all_covered"] is False
        for plo_result in resp.data["plos"]:
            assert plo_result["is_covered"] is False


# ════════════════════════════════════════════════════════════
# 4.3 — Assessment Plan CRUD
# ════════════════════════════════════════════════════════════


class TestAssessmentPlanCRUD:
    def test_list_assessment_plans(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept)
        version = TrainingProgramVersionFactory(program=prog, academic_year="2024-2025")
        plo = ProgramLearningOutcomeFactory(version=version)
        pi = PerformanceIndicatorFactory(plo=plo)
        PLOAssessmentPlanFactory(version=version, pi=pi)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/assessment-plans/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data.get("results", resp.data)
        assert len(results) == 1

    def test_create_assessment_plan(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = TrainingProgramVersionFactory(program=prog, academic_year="2024-2025")
        plo = ProgramLearningOutcomeFactory(version=version)
        pi = PerformanceIndicatorFactory(plo=plo)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/assessment-plans/"
        data = {
            "pi": str(pi.pk),
            "contributing_courses_text": "HP001 HP002",
            "direct_evidence": "Báo cáo cuối kỳ",
            "assessment_tool": "Rubric đánh giá",
            "expected_standard": "70% đạt",
            "assessment_schedule": "HK2 năm 4",
        }
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert PLOAssessmentPlan.objects.filter(version=version, pi=pi).exists()

    def test_update_assessment_plan(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = TrainingProgramVersionFactory(program=prog, academic_year="2024-2025")
        plo = ProgramLearningOutcomeFactory(version=version)
        pi = PerformanceIndicatorFactory(plo=plo)
        plan = PLOAssessmentPlanFactory(version=version, pi=pi)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/assessment-plans/{plan.pk}/"
        resp = client.patch(
            url, {"direct_evidence": "Updated evidence"}, format="json"
        )
        assert resp.status_code == status.HTTP_200_OK
        plan.refresh_from_db()
        assert plan.direct_evidence == "Updated evidence"

    def test_delete_assessment_plan(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = TrainingProgramVersionFactory(program=prog, academic_year="2024-2025")
        plo = ProgramLearningOutcomeFactory(version=version)
        pi = PerformanceIndicatorFactory(plo=plo)
        plan = PLOAssessmentPlanFactory(version=version, pi=pi)
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/assessment-plans/{plan.pk}/"
        resp = client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not PLOAssessmentPlan.objects.filter(pk=plan.pk).exists()

    def test_bulk_upsert_assessment_plans(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = TrainingProgramVersionFactory(program=prog, academic_year="2024-2025")
        plo = ProgramLearningOutcomeFactory(version=version)
        pi1 = PerformanceIndicatorFactory(plo=plo, code="PI.1.1")
        pi2 = PerformanceIndicatorFactory(plo=plo, code="PI.1.2")
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/assessment-plans/bulk/"
        data = {
            "plans": [
                {
                    "pi": str(pi1.pk),
                    "direct_evidence": "Bài kiểm tra",
                    "assessment_tool": "Rubric",
                    "expected_standard": "80%",
                },
                {
                    "pi": str(pi2.pk),
                    "direct_evidence": "Báo cáo",
                    "assessment_tool": "Bảng đánh giá",
                },
            ]
        }
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["created"] == 2
        assert resp.data["updated"] == 0
        assert PLOAssessmentPlan.objects.filter(version=version).count() == 2

    def test_bulk_upsert_updates_existing(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = TrainingProgramVersionFactory(program=prog, academic_year="2024-2025")
        plo = ProgramLearningOutcomeFactory(version=version)
        pi = PerformanceIndicatorFactory(plo=plo)
        PLOAssessmentPlanFactory(version=version, pi=pi, direct_evidence="Old")
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/assessment-plans/bulk/"
        data = {
            "plans": [
                {
                    "pi": str(pi.pk),
                    "direct_evidence": "New evidence",
                }
            ]
        }
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["updated"] == 1
        assert resp.data["created"] == 0
        plan = PLOAssessmentPlan.objects.get(version=version, pi=pi)
        assert plan.direct_evidence == "New evidence"

    def test_assessment_plan_with_sample_course(self):
        user, dept = _setup_admin_user()
        prog = TrainingProgramFactory(managing_department=dept, status=ProgramStatus.DRAFT)
        version = TrainingProgramVersionFactory(program=prog, academic_year="2024-2025")
        plo = ProgramLearningOutcomeFactory(version=version)
        pi = PerformanceIndicatorFactory(plo=plo)
        sample = CourseFactory()
        client = _auth_client(user)

        url = f"/api/v1/programs/{prog.pk}/assessment-plans/"
        data = {
            "pi": str(pi.pk),
            "sample_course": str(sample.pk),
            "direct_evidence": "Bài thi",
        }
        resp = client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["sample_course_code"] == sample.code


# ════════════════════════════════════════════════════════════
# 4.4 — Performance Test: Matrix Read < 500ms for 70x21
# ════════════════════════════════════════════════════════════


class TestMatrixPerformance:
    def test_matrix_read_performance_70x21(self):
        """Matrix read for 70 courses × 21 PIs should be < 500ms."""
        user, dept = _setup_admin_user()
        prog, courses, plos, pis = _setup_matrix_data(
            dept, n_courses=70, n_plos=7, pis_per_plo=3
        )

        # Add some contributions (not all, to be realistic)
        contribs = []
        for i, pc in enumerate(courses):
            for j, pi in enumerate(pis):
                if (i + j) % 3 != 0:  # ~67% fill rate
                    contribs.append(CoursePLOContribution(
                        program_course=pc,
                        pi=pi,
                        contribution_level=((i + j) % 3) + 1,
                    ))
        CoursePLOContribution.objects.bulk_create(contribs)

        client = _auth_client(user)
        url = f"/api/v1/programs/{prog.pk}/course-plo-matrix/"

        start = time.time()
        resp = client.get(url)
        elapsed_ms = (time.time() - start) * 1000

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["rows"]) == 70
        assert len(resp.data["columns"]) == 7
        # Each PLO group should have 3 PIs
        for col in resp.data["columns"]:
            assert len(col["pis"]) == 3
        # Performance check (generous threshold for CI)
        assert elapsed_ms < 500, f"Matrix read took {elapsed_ms:.0f}ms, should be < 500ms"
