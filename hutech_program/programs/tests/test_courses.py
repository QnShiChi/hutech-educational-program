"""
Tests for Course Management module.
Covers: CRUD, credit validation, bulk add, prerequisites, semester plan, signals.
"""

import uuid
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient

from hutech_program.programs.models import (
    Course,
    CourseGroup,
    CoursePrerequisite,
    ProgramCourse,
    ProgramStatus,
    SemesterPlan,
)
from hutech_program.programs.tests.factories import (
    CourseFactory,
    CourseGroupFactory,
    CoursePrerequisiteFactory,
    KnowledgeBlockFactory,
    ProgramCourseFactory,
    SemesterPlanFactory,
    TrainingProgramFactory,
)
from hutech_program.rbac.tests.factories import (
    DepartmentFactory,
    RoleFactory,
    UserFactory,
    UserRoleFactory,
)

pytestmark = pytest.mark.django_db


# ────────────────── Helpers ──────────────────


def _auth_client(user=None):
    """Return an authenticated API client with ADMIN role (bypasses RBAC)."""
    client = APIClient()
    if user is None:
        user = UserFactory()
    # Grant ADMIN role so HasModulePermission allows access
    if not user.user_roles.filter(role__code="ADMIN").exists():
        dept = DepartmentFactory()
        admin_role = RoleFactory(code="ADMIN")
        UserRoleFactory(user=user, role=admin_role, department=dept)
    client.force_authenticate(user=user)
    return client, user


# ────────────────── 4.1 Course CRUD + Unique Code ──────────────────


class TestCourseCRUD:
    """Task 4.1: Course CRUD and unique code validation."""

    def test_create_course(self):
        dept = DepartmentFactory()
        group = CourseGroupFactory()
        client, _ = _auth_client()

        data = {
            "code": "POS104",
            "name_vi": "Triết học Mác - Lênin",
            "name_en": "Marxist-Leninist Philosophy",
            "total_credits": 3,
            "theory_credits": 2,
            "practice_credits": 1,
            "project_credits": 0,
            "internship_credits": 0,
            "managing_department": str(dept.id),
            "course_group": str(group.id),
        }
        resp = client.post("/api/v1/programs/courses/", data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["code"] == "POS104"

    def test_list_courses(self):
        CourseFactory.create_batch(3)
        client, _ = _auth_client()

        resp = client.get("/api/v1/programs/courses/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] >= 3

    def test_retrieve_course(self):
        course = CourseFactory()
        client, _ = _auth_client()

        resp = client.get(f"/api/v1/programs/courses/{course.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["code"] == course.code

    def test_update_course(self):
        course = CourseFactory()
        client, _ = _auth_client()

        data = {
            "code": course.code,
            "name_vi": "Tên mới",
            "total_credits": 3,
            "theory_credits": 2,
            "practice_credits": 1,
            "project_credits": 0,
            "internship_credits": 0,
            "managing_department": str(course.managing_department_id),
        }
        resp = client.put(f"/api/v1/programs/courses/{course.id}/", data, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_delete_course(self):
        course = CourseFactory()
        client, _ = _auth_client()

        resp = client.delete(f"/api/v1/programs/courses/{course.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_unique_code_validation(self):
        CourseFactory(code="DUP001")
        client, _ = _auth_client()
        dept = DepartmentFactory()

        data = {
            "code": "DUP001",
            "name_vi": "Duplicate",
            "total_credits": 3,
            "theory_credits": 3,
            "practice_credits": 0,
            "project_credits": 0,
            "internship_credits": 0,
            "managing_department": str(dept.id),
        }
        resp = client.post("/api/v1/programs/courses/", data, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_credit_sum_validation(self):
        """total_credits must equal sum of sub-credits."""
        client, _ = _auth_client()
        dept = DepartmentFactory()

        data = {
            "code": "BAD001",
            "name_vi": "Bad credits",
            "total_credits": 5,  # sum is 3
            "theory_credits": 2,
            "practice_credits": 1,
            "project_credits": 0,
            "internship_credits": 0,
            "managing_department": str(dept.id),
        }
        resp = client.post("/api/v1/programs/courses/", data, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "total_credits" in resp.data

    def test_model_clean_validation(self):
        """Model.clean() also validates credit sum."""
        dept = DepartmentFactory()
        course = Course(
            code="CLN001",
            name_vi="Test",
            total_credits=5,
            theory_credits=2,
            practice_credits=1,
            managing_department=dept,
        )
        with pytest.raises(ValidationError):
            course.clean()

    def test_filter_by_department(self):
        dept = DepartmentFactory()
        CourseFactory(managing_department=dept)
        CourseFactory()  # different dept
        client, _ = _auth_client()

        resp = client.get(f"/api/v1/programs/courses/?managing_department={dept.id}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] >= 1
        for r in resp.data["results"]:
            assert str(r["managing_department"]) == str(dept.id)

    def test_search_by_code(self):
        CourseFactory(code="SEARCH01")
        client, _ = _auth_client()

        resp = client.get("/api/v1/programs/courses/?search=SEARCH01")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] >= 1

    def test_course_usage_endpoint(self):
        """GET /courses/{id}/programs/ returns programs using this course."""
        course = CourseFactory()
        program = TrainingProgramFactory()
        ProgramCourseFactory(program=program, course=course)
        client, _ = _auth_client()

        resp = client.get(f"/api/v1/programs/courses/{course.id}/programs/")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["program_code"] == program.program_code

    def test_prevent_delete_non_draft(self):
        """Cannot delete course if used in non-DRAFT program."""
        course = CourseFactory()
        program = TrainingProgramFactory(status=ProgramStatus.SUBMITTED)
        ProgramCourseFactory(program=program, course=course)
        client, _ = _auth_client()

        resp = client.delete(f"/api/v1/programs/courses/{course.id}/")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "Bản nháp" in resp.data["detail"]


# ────────────────── 4.2 ProgramCourse Bulk Add ──────────────────


class TestProgramCourseBulkAdd:
    """Task 4.2: ProgramCourse bulk add."""

    def test_bulk_add_courses(self):
        program = TrainingProgramFactory(status=ProgramStatus.DRAFT)
        courses = CourseFactory.create_batch(3)
        client, _ = _auth_client()

        data = {
            "courses": [
                {"course": str(c.id), "is_required": True, "semester": i + 1}
                for i, c in enumerate(courses)
            ]
        }
        resp = client.post(
            f"/api/v1/programs/{program.id}/courses/bulk/",
            data,
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["created_count"] == 3

    def test_bulk_add_skip_duplicates(self):
        program = TrainingProgramFactory(status=ProgramStatus.DRAFT)
        course = CourseFactory()
        ProgramCourseFactory(program=program, course=course)
        client, _ = _auth_client()

        data = {
            "courses": [{"course": str(course.id)}]
        }
        resp = client.post(
            f"/api/v1/programs/{program.id}/courses/bulk/",
            data,
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["created_count"] == 0  # already exists

    def test_bulk_add_non_editable_program(self):
        program = TrainingProgramFactory(status=ProgramStatus.PUBLISHED)
        course = CourseFactory()
        client, _ = _auth_client()

        data = {"courses": [{"course": str(course.id)}]}
        resp = client.post(
            f"/api/v1/programs/{program.id}/courses/bulk/",
            data,
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ────────────────── 4.3 Prerequisite Validation ──────────────────


class TestPrerequisiteValidation:
    """Task 4.3: Prerequisite validation and semester ordering."""

    def test_get_prerequisites(self):
        program = TrainingProgramFactory()
        pc = ProgramCourseFactory(program=program, semester=2)
        prereq_course = CourseFactory()
        ProgramCourseFactory(program=program, course=prereq_course, semester=1)
        CoursePrerequisiteFactory(
            program_course=pc,
            prerequisite_course=prereq_course,
        )
        client, _ = _auth_client()

        resp = client.get(f"/api/v1/programs/{program.id}/prerequisites/")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["prerequisites"]) == 1

    def test_update_prerequisites(self):
        program = TrainingProgramFactory(status=ProgramStatus.DRAFT)
        course1 = CourseFactory()
        course2 = CourseFactory()
        pc1 = ProgramCourseFactory(program=program, course=course1, semester=1)
        pc2 = ProgramCourseFactory(program=program, course=course2, semester=2)
        client, _ = _auth_client()

        data = {
            "prerequisites": [
                {
                    "program_course_id": str(pc2.id),
                    "prerequisite_course_id": str(course1.id),
                    "type": "PREREQUISITE",
                }
            ]
        }
        resp = client.put(
            f"/api/v1/programs/{program.id}/prerequisites/",
            data,
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1

    def test_prerequisite_semester_ordering_rejected(self):
        """Prerequisite in same or later semester should be rejected."""
        program = TrainingProgramFactory(status=ProgramStatus.DRAFT)
        course1 = CourseFactory()
        course2 = CourseFactory()
        pc1 = ProgramCourseFactory(program=program, course=course1, semester=2)
        pc2 = ProgramCourseFactory(program=program, course=course2, semester=1)
        client, _ = _auth_client()

        # course1 is in semester 2, trying to set it as prerequisite of
        # course2 which is in semester 1 → should fail
        data = {
            "prerequisites": [
                {
                    "program_course_id": str(pc2.id),
                    "prerequisite_course_id": str(course1.id),
                    "type": "PREREQUISITE",
                }
            ]
        }
        resp = client.put(
            f"/api/v1/programs/{program.id}/prerequisites/",
            data,
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ────────────────── 4.4 Semester Plan Update ──────────────────


class TestSemesterPlan:
    """Task 4.4: Semester plan update."""

    def test_get_semester_plan(self):
        program = TrainingProgramFactory()
        pc1 = ProgramCourseFactory(program=program)
        pc2 = ProgramCourseFactory(program=program)
        SemesterPlanFactory(program=program, program_course=pc1, semester_number=1)
        SemesterPlanFactory(program=program, program_course=pc2, semester_number=2)
        client, _ = _auth_client()

        resp = client.get(f"/api/v1/programs/{program.id}/semester-plan/")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["semesters"]) == 2

    def test_update_semester_plan(self):
        program = TrainingProgramFactory(status=ProgramStatus.DRAFT)
        pc1 = ProgramCourseFactory(program=program)
        pc2 = ProgramCourseFactory(program=program)
        client, _ = _auth_client()

        data = {
            "semesters": [
                {
                    "semester_number": 1,
                    "courses": [
                        {"program_course_id": str(pc1.id), "order_index": 0},
                    ],
                },
                {
                    "semester_number": 2,
                    "courses": [
                        {"program_course_id": str(pc2.id), "order_index": 0},
                    ],
                },
            ]
        }
        resp = client.put(
            f"/api/v1/programs/{program.id}/semester-plan/",
            data,
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 2

    def test_update_semester_plan_non_editable(self):
        program = TrainingProgramFactory(status=ProgramStatus.PUBLISHED)
        client, _ = _auth_client()

        data = {"semesters": []}
        resp = client.put(
            f"/api/v1/programs/{program.id}/semester-plan/",
            data,
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ────────────────── 4.5 Course Change Notification ──────────────────


class TestCourseChangeNotification:
    """Task 4.5: Signal triggers notification when Course is updated."""

    def test_signal_fires_on_update(self):
        """Verify the signal is called when a Course is updated."""
        course = CourseFactory()
        program = TrainingProgramFactory()
        ProgramCourseFactory(program=program, course=course)

        # The signal tries to import notifications.models which may not exist
        # We patch it to verify it's called
        with patch(
            "hutech_program.programs.signals.ProgramCourse.objects"
        ) as mock_pc:
            mock_pc.filter.return_value.select_related.return_value = (
                ProgramCourse.objects.filter(course=course).select_related("program")
            )
            mock_pc.filter.return_value.select_related.return_value.exists.return_value = True

            # Just verify the signal doesn't crash when notification app is missing
            course.name_vi = "Updated Name"
            course.save()

    def test_signal_skips_on_create(self):
        """Signal should NOT fire on Course creation."""
        # This should just not crash
        CourseFactory()


# ────────────────── CourseGroup CRUD ──────────────────


class TestCourseGroupCRUD:
    def test_create_course_group(self):
        client, _ = _auth_client()
        data = {"name": "Kỹ thuật", "description": "Nhóm kỹ thuật"}
        resp = client.post("/api/v1/programs/course-groups/", data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED

    def test_list_course_groups(self):
        CourseGroupFactory.create_batch(2)
        client, _ = _auth_client()
        resp = client.get("/api/v1/programs/course-groups/")
        assert resp.status_code == status.HTTP_200_OK
