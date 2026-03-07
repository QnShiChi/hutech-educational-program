"""
Tests for the imports app: parser, Celery tasks, and API endpoints.
"""

import io
import uuid
from unittest.mock import MagicMock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from hutech_program.imports.models import ImportStatus, ImportTask
from hutech_program.imports.parser import DocxParser
from hutech_program.imports.tasks import _save_parsed_data, confirm_import_task, import_training_program_task
from hutech_program.rbac.tests.factories import DepartmentFactory, UserFactory


# ───────────────────────────── Helper: mock table ─────────────────────────────


def _make_mock_table(header_row, data_rows):
    """Create a mock docx table with given header and data rows."""
    table = MagicMock()
    rows = []

    def _make_row(cell_texts):
        row = MagicMock()
        cells = []
        for text in cell_texts:
            cell = MagicMock()
            cell.text = str(text)
            cells.append(cell)
        row.cells = cells
        return row

    rows.append(_make_row(header_row))
    for data in data_rows:
        rows.append(_make_row(data))

    table.rows = rows
    table.columns = [MagicMock()] * len(header_row)
    return table


# ───────────────────────────── Parser Tests ─────────────────────────────


@pytest.mark.django_db
class TestDocxParserTableIdentification(TestCase):
    """Test table identification by header patterns."""

    def _make_parser_with_tables(self, tables):
        parser = DocxParser.__new__(DocxParser)
        parser.tables = tables
        parser.warnings = []
        parser.errors = []
        parser.doc = MagicMock()
        return parser

    def test_identify_plos_table(self):
        table = _make_mock_table(
            ["Chuẩn đầu ra", "Mô tả"], [["PLO1", "Desc"]]
        )
        parser = self._make_parser_with_tables([table])
        assert parser._identify_table(table) == "plos"

    def test_identify_po_plo_matrix(self):
        table = _make_mock_table(
            ["Mục tiêu", "PO1", "PLO1"], [["PLO1", "X", ""]]
        )
        parser = self._make_parser_with_tables([table])
        assert parser._identify_table(table) == "po_plo_matrix"

    def test_identify_knowledge_blocks(self):
        table = _make_mock_table(
            ["Khối kiến thức", "TC"], [["KT1", "30"]]
        )
        parser = self._make_parser_with_tables([table])
        assert parser._identify_table(table) == "knowledge_blocks"

    def test_identify_courses(self):
        table = _make_mock_table(
            ["STT", "Mã học phần", "Tên"], [["1", "CS101", "Intro"]]
        )
        parser = self._make_parser_with_tables([table])
        assert parser._identify_table(table) == "courses"

    def test_identify_course_plo_matrix(self):
        table = _make_mock_table(
            ["STT", "Mã HP", "PLO1.1", "PLO1.2"], [["1", "CS101", "1", "2"]]
        )
        parser = self._make_parser_with_tables([table])
        assert parser._identify_table(table) == "course_plo_matrix"

    def test_identify_course_descriptions(self):
        table = _make_mock_table(
            ["STT", "Mô tả tóm tắt học phần"], [["1", "A course"]]
        )
        parser = self._make_parser_with_tables([table])
        assert parser._identify_table(table) == "course_descriptions"

    def test_identify_semester_plan(self):
        table = _make_mock_table(
            ["Học kỳ", "Kế hoạch"], [["1", "CS101"]]
        )
        parser = self._make_parser_with_tables([table])
        assert parser._identify_table(table) == "semester_plan"

    def test_identify_pis(self):
        table = _make_mock_table(
            ["Chỉ số", "PI", "Mô tả"], [["PI1.1", "desc"]]
        )
        parser = self._make_parser_with_tables([table])
        assert parser._identify_table(table) == "pis"

    def test_identify_assessment_plans(self):
        table = _make_mock_table(
            ["Đánh giá", "PLO", "HP"], [["PLO1", "CS101", "..."]]
        )
        parser = self._make_parser_with_tables([table])
        assert parser._identify_table(table) == "assessment_plans"

    def test_identify_general_info(self):
        table = _make_mock_table(
            ["Tên chương trình", "CNTT"],
            [["Mã chương trình", "7480201"]],
        )
        # General info tables have 2 columns
        table.columns = [MagicMock(), MagicMock()]
        parser = self._make_parser_with_tables([table])
        assert parser._identify_table(table) == "general_info"

    def test_identify_unknown_returns_none(self):
        table = _make_mock_table(
            ["Random", "Header", "Nobody knows"], [["a", "b", "c"]]
        )
        parser = self._make_parser_with_tables([table])
        assert parser._identify_table(table) is None


@pytest.mark.django_db
class TestDocxParserParsing(TestCase):
    """Test individual parser methods with mock tables."""

    def _make_parser(self):
        parser = DocxParser.__new__(DocxParser)
        parser.tables = []
        parser.warnings = []
        parser.errors = []
        parser.doc = MagicMock()
        return parser

    def test_parse_general_info(self):
        table = _make_mock_table(
            ["Tên chương trình", "CNTT"],
            [
                ["Mã chương trình", "7480201"],
                ["Tổng tín chỉ", "150"],
                ["Trình độ đào tạo", "Đại học"],
            ],
        )
        parser = self._make_parser()
        result = parser._parse_general_info(table)
        assert result["program_name_vi"] == "CNTT"
        assert result["program_code"] == "7480201"
        assert result["total_credits"] == 150
        assert result["education_level"] == "Đại học"

    def test_parse_plos(self):
        table = _make_mock_table(
            ["Chuẩn đầu ra", "Mô tả", "Trình độ", "Mức"],
            [
                ["PLO1", "Apply knowledge", "Lv3", "Apply"],
                ["PLO2", "Analyze problems", "Lv4", "Analyze"],
            ],
        )
        parser = self._make_parser()
        result = parser._parse_plos(table)
        assert len(result) == 2
        assert result[0]["code"] == "PLO1"
        assert result[0]["description"] == "Apply knowledge"
        assert result[1]["code"] == "PLO2"

    def test_parse_po_plo_matrix(self):
        table = _make_mock_table(
            ["", "PO1", "PO2"],
            [
                ["PLO1", "X", ""],
                ["PLO2", "", "X"],
            ],
        )
        parser = self._make_parser()
        result = parser._parse_po_plo_matrix(table)
        assert len(result) == 2
        assert result[0]["plo_code"] == "PLO1"
        assert result[0]["po_code"] == "PO1"
        assert result[1]["plo_code"] == "PLO2"
        assert result[1]["po_code"] == "PO2"

    def test_parse_knowledge_blocks(self):
        table = _make_mock_table(
            ["Khối kiến thức", "TC", "BB", "TC", "%"],
            [["GDDC", "30", "20", "10", "20%"]],
        )
        parser = self._make_parser()
        result = parser._parse_knowledge_blocks(table)
        assert len(result) == 1
        assert result[0]["name"] == "GDDC"
        assert result[0]["total_credits"] == 30
        assert result[0]["required_credits"] == 20
        assert result[0]["elective_credits"] == 10

    def test_parse_courses(self):
        table = _make_mock_table(
            ["STT", "Mã HP", "Tên", "TC", "LT", "TH", "", "HK"],
            [["1", "CS101", "Intro CS", "3", "2", "1", "", "1"]],
        )
        parser = self._make_parser()
        result = parser._parse_courses(table)
        assert len(result) == 1
        assert result[0]["code"] == "CS101"
        assert result[0]["name_vi"] == "Intro CS"
        assert result[0]["total_credits"] == 3

    def test_parse_course_descriptions(self):
        table = _make_mock_table(
            ["Mã HP", "Mô tả"],
            [["CS101", "Intro to CS fundamentals"]],
        )
        parser = self._make_parser()
        result = parser._parse_course_descriptions(table)
        assert len(result) == 1
        assert result[0]["code"] == "CS101"
        assert result[0]["description"] == "Intro to CS fundamentals"

    def test_parse_pis(self):
        table = _make_mock_table(
            ["Chỉ số PI", "Mô tả"],
            [["PLO1.1", "Apply math"], ["PLO1.2", "Apply stats"]],
        )
        parser = self._make_parser()
        result = parser._parse_pis(table)
        assert len(result) == 2
        assert result[0]["code"] == "PLO1.1"
        assert result[0]["plo_code"] == "PLO1"

    def test_parse_assessment_plans(self):
        table = _make_mock_table(
            ["PI", "HP đóng góp", "HP lấy mẫu", "Minh chứng", "Công cụ", "Tiêu chuẩn", "Lịch"],
            [["PLO1.1", "CS101 CS102", "CS101", "Báo cáo", "Rubric", "70%", "HK1"]],
        )
        parser = self._make_parser()
        result = parser._parse_assessment_plans(table)
        assert len(result) == 1
        assert result[0]["pi_code"] == "PLO1.1"
        assert result[0]["contributing_courses_text"] == "CS101 CS102"

    def test_parse_course_plo_matrix(self):
        table = _make_mock_table(
            ["STT", "Mã HP", "PI1.1", "PI1.2"],
            [["1", "CS101", "2", "3"]],
        )
        parser = self._make_parser()
        result = parser._parse_course_plo_matrix(table)
        assert len(result) == 2
        assert result[0]["course_code"] == "CS101"
        assert result[0]["contribution_level"] == 2

    def test_safe_int_valid(self):
        assert DocxParser._safe_int("42") == 42

    def test_safe_int_with_text(self):
        assert DocxParser._safe_int("30 TC") == 30

    def test_safe_int_invalid(self):
        assert DocxParser._safe_int("abc") == 0

    def test_safe_int_empty(self):
        assert DocxParser._safe_int("") == 0


@pytest.mark.django_db
class TestDocxParserParseAll(TestCase):
    """Test parse_all error handling."""

    def test_parse_all_handles_missing_tables(self):
        parser = DocxParser.__new__(DocxParser)
        parser.tables = []
        parser.warnings = []
        parser.errors = []
        parser.doc = MagicMock()

        result = parser.parse_all()
        assert result["general_info"] == {}
        assert result["plos"] == []
        assert result["courses"] == []

    def test_parse_all_handles_table_errors(self):
        # Create a table whose _identify_table raises internally
        bad_table = MagicMock()
        bad_cell = MagicMock()
        bad_cell.text = property(lambda self: (_ for _ in ()).throw(Exception("Bad table")))
        type(bad_cell).text = property(lambda self: (_ for _ in ()).throw(Exception("Bad table")))
        row_mock = MagicMock()
        row_mock.cells = [bad_cell]
        bad_table.rows = [row_mock]

        parser = DocxParser.__new__(DocxParser)
        parser.tables = [bad_table]
        parser.warnings = []
        parser.errors = []
        parser.doc = MagicMock()

        result = parser.parse_all()
        assert len(parser.errors) == 1
        assert "Error parsing table 0" in parser.errors[0]


# ───────────────────── Save Parsed Data Tests ─────────────────────


@pytest.mark.django_db
class TestSaveParsedData(TestCase):
    """Test _save_parsed_data creates all related entities."""

    def setUp(self):
        self.user = UserFactory()
        self.department = DepartmentFactory()

    def _create_task_with_data(self, parsed_data):
        task = ImportTask.objects.create(
            file_name="test.docx",
            file="imports/test.docx",
            department=self.department,
            uploaded_by=self.user,
            status=ImportStatus.PREVIEW,
            parsed_data=parsed_data,
        )
        return task

    def test_creates_program_with_general_info(self):
        task = self._create_task_with_data({
            "general_info": {
                "program_code": "7480201",
                "program_name_vi": "CNTT",
                "program_name_en": "IT",
                "total_credits": 150,
            },
            "plos": [],
            "po_plo_matrix": [],
            "knowledge_blocks": [],
            "courses": [],
            "course_descriptions": [],
            "course_plo_matrix": [],
            "semester_plan": [],
            "performance_indicators": [],
            "assessment_plans": [],
        })

        from hutech_program.programs.models import TrainingProgram
        program = _save_parsed_data(task)

        assert program.program_code == "7480201"
        assert program.program_name_vi == "CNTT"
        assert program.total_credits == 150
        assert TrainingProgram.objects.count() == 1

    def test_creates_plos(self):
        task = self._create_task_with_data({
            "general_info": {"program_code": "TEST01"},
            "plos": [
                {"code": "PLO1", "description": "Apply knowledge", "order_index": 1},
                {"code": "PLO2", "description": "Analyze", "order_index": 2},
            ],
            "po_plo_matrix": [],
            "knowledge_blocks": [],
            "courses": [],
            "course_descriptions": [],
            "course_plo_matrix": [],
            "semester_plan": [],
            "performance_indicators": [],
            "assessment_plans": [],
        })

        from hutech_program.programs.models import ProgramLearningOutcome
        program = _save_parsed_data(task)

        plos = ProgramLearningOutcome.objects.filter(program=program)
        assert plos.count() == 2
        assert plos.filter(code="PLO1").exists()

    def test_creates_po_plo_mappings(self):
        task = self._create_task_with_data({
            "general_info": {"program_code": "TEST02"},
            "plos": [
                {"code": "PLO1", "description": "D1", "order_index": 1},
            ],
            "po_plo_matrix": [
                {"plo_code": "PLO1", "po_code": "PO1"},
            ],
            "knowledge_blocks": [],
            "courses": [],
            "course_descriptions": [],
            "course_plo_matrix": [],
            "semester_plan": [],
            "performance_indicators": [],
            "assessment_plans": [],
        })

        from hutech_program.programs.models import PLOPOMapping, ProgramObjective
        _save_parsed_data(task)

        assert ProgramObjective.objects.filter(code="PO1").exists()
        assert PLOPOMapping.objects.count() == 1

    def test_creates_courses_and_handles_duplicates(self):
        from hutech_program.programs.models import Course

        # Pre-create a course to test duplicate handling
        Course.objects.create(
            code="CS101",
            name_vi="Existing",
            total_credits=3,
            managing_department=self.department,
        )

        task = self._create_task_with_data({
            "general_info": {"program_code": "TEST03"},
            "plos": [],
            "po_plo_matrix": [],
            "knowledge_blocks": [],
            "courses": [
                {"code": "CS101", "name_vi": "New Name", "total_credits": 4},
                {"code": "CS102", "name_vi": "New Course", "total_credits": 3},
            ],
            "course_descriptions": [],
            "course_plo_matrix": [],
            "semester_plan": [],
            "performance_indicators": [],
            "assessment_plans": [],
        })

        _save_parsed_data(task)

        # CS101 should keep original name (get_or_create)
        cs101 = Course.objects.get(code="CS101")
        assert cs101.name_vi == "Existing"
        # CS102 should be created
        assert Course.objects.filter(code="CS102").exists()

    def test_creates_complete_pipeline(self):
        """Test full pipeline: PLOs → PIs → courses → contributions → semester → assessment."""
        task = self._create_task_with_data({
            "general_info": {"program_code": "FULL01"},
            "plos": [
                {"code": "PLO1", "description": "D1", "order_index": 1},
            ],
            "po_plo_matrix": [
                {"plo_code": "PLO1", "po_code": "PO1"},
            ],
            "knowledge_blocks": [
                {"name": "GDDC", "required_credits": 20, "elective_credits": 10, "order_index": 1},
            ],
            "courses": [
                {"code": "CS101", "name_vi": "Intro", "total_credits": 3},
            ],
            "course_descriptions": [
                {"code": "CS101", "description": "Updated desc"},
            ],
            "performance_indicators": [
                {"plo_code": "PLO1", "code": "PLO1.1", "description": "Apply math", "order_index": 1},
            ],
            "course_plo_matrix": [
                {"course_code": "CS101", "pi_code": "PLO1.1", "contribution_level": 2},
            ],
            "semester_plan": [
                {"semester_number": 1, "course_code": "CS101", "order_index": 1},
            ],
            "assessment_plans": [
                {
                    "pi_code": "PLO1.1",
                    "contributing_courses_text": "CS101",
                    "sample_course_code": "CS101",
                    "direct_evidence": "Báo cáo",
                    "assessment_tool": "Rubric",
                    "expected_standard": "70%",
                    "assessment_schedule": "HK1",
                },
            ],
        })

        from hutech_program.programs.models import (
            Course,
            CoursePLOContribution,
            KnowledgeBlock,
            PerformanceIndicator,
            PLOAssessmentPlan,
            PLOPOMapping,
            ProgramCourse,
            ProgramLearningOutcome,
            SemesterPlan,
        )

        program = _save_parsed_data(task)

        assert ProgramLearningOutcome.objects.filter(program=program).count() == 1
        assert PLOPOMapping.objects.count() == 1
        assert KnowledgeBlock.objects.filter(program=program).count() == 1
        assert ProgramCourse.objects.filter(program=program).count() == 1
        assert PerformanceIndicator.objects.count() == 1
        assert CoursePLOContribution.objects.count() == 1
        assert SemesterPlan.objects.filter(program=program).count() == 1
        assert PLOAssessmentPlan.objects.filter(program=program).count() == 1

        # Verify course description was updated
        cs101 = Course.objects.get(code="CS101")
        assert cs101.description == "Updated desc"


# ───────────────────── Celery Task Tests ─────────────────────


@pytest.mark.django_db
class TestCeleryTasks(TestCase):
    """Test Celery import and confirm tasks."""

    def setUp(self):
        self.user = UserFactory()
        self.department = DepartmentFactory()

    def test_import_task_not_found(self):
        """Task should handle missing ImportTask gracefully."""
        import_training_program_task(str(uuid.uuid4()))
        # Should not raise

    @patch("hutech_program.imports.tasks.DocxParser")
    def test_import_task_success(self, MockParser):
        mock_parser = MagicMock()
        mock_parser.parse_all.return_value = {
            "general_info": {},
            "plos": [],
            "po_plo_matrix": [],
            "knowledge_blocks": [],
            "courses": [],
            "course_plo_matrix": [],
            "course_descriptions": [],
            "semester_plan": [],
            "performance_indicators": [],
            "assessment_plans": [],
        }
        mock_parser.warnings = []
        mock_parser.errors = []
        MockParser.return_value = mock_parser

        task = ImportTask.objects.create(
            file_name="test.docx",
            file="imports/test.docx",
            department=self.department,
            uploaded_by=self.user,
            status=ImportStatus.PENDING,
        )

        import_training_program_task(str(task.id))

        task.refresh_from_db()
        assert task.status == ImportStatus.PREVIEW
        assert task.progress == 100
        assert task.parsed_data is not None

    @patch("hutech_program.imports.tasks.DocxParser")
    def test_import_task_failure(self, MockParser):
        MockParser.side_effect = Exception("File corrupt")

        task = ImportTask.objects.create(
            file_name="bad.docx",
            file="imports/bad.docx",
            department=self.department,
            uploaded_by=self.user,
            status=ImportStatus.PENDING,
        )

        import_training_program_task(str(task.id))

        task.refresh_from_db()
        assert task.status == ImportStatus.FAILED
        assert "File corrupt" in task.error_message

    def test_confirm_task_not_in_preview(self):
        """Confirm should not proceed if not in PREVIEW status."""
        task = ImportTask.objects.create(
            file_name="test.docx",
            file="imports/test.docx",
            department=self.department,
            uploaded_by=self.user,
            status=ImportStatus.PENDING,
        )

        confirm_import_task(str(task.id))

        task.refresh_from_db()
        assert task.status == ImportStatus.PENDING  # No change

    def test_confirm_task_success(self):
        task = ImportTask.objects.create(
            file_name="test.docx",
            file="imports/test.docx",
            department=self.department,
            uploaded_by=self.user,
            status=ImportStatus.PREVIEW,
            parsed_data={
                "general_info": {"program_code": "CONF01"},
                "plos": [],
                "po_plo_matrix": [],
                "knowledge_blocks": [],
                "courses": [],
                "course_descriptions": [],
                "course_plo_matrix": [],
                "semester_plan": [],
                "performance_indicators": [],
                "assessment_plans": [],
            },
        )

        confirm_import_task(str(task.id))

        task.refresh_from_db()
        assert task.status == ImportStatus.COMPLETED
        assert task.program is not None


# ───────────────────── API Tests ─────────────────────


@pytest.mark.django_db
class TestImportAPI(TestCase):
    """Test import API endpoints."""

    def setUp(self):
        from hutech_program.rbac.models import (
            Permission,
            PermissionModule,
            Role,
            RolePermission,
            UserRole,
        )

        self.user = UserFactory()
        self.department = DepartmentFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Setup permissions
        role = Role.objects.create(code="ADMIN", name="Admin", level=0)
        for action in ["view", "create"]:
            perm, _ = Permission.objects.get_or_create(
                code=f"programs.{action}",
                defaults={"name": f"Programs {action}", "module": PermissionModule.PROGRAMS},
            )
            RolePermission.objects.get_or_create(role=role, permission=perm)
        UserRole.objects.create(user=self.user, role=role, department=self.department)

    @patch("hutech_program.imports.views.import_training_program_task")
    def test_upload_endpoint(self, mock_task):
        mock_task.delay = MagicMock()
        file = SimpleUploadedFile("test.docx", b"PK...", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        response = self.client.post(
            "/api/v1/imports/training-program/",
            {"file": file, "department_id": str(self.department.pk)},
            format="multipart",
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "id" in response.data
        assert response.data["status"] == ImportStatus.PENDING
        mock_task.delay.assert_called_once()

    def test_upload_invalid_file_type(self):
        file = SimpleUploadedFile("test.pdf", b"...", content_type="application/pdf")

        response = self.client.post(
            "/api/v1/imports/training-program/",
            {"file": file, "department_id": str(self.department.pk)},
            format="multipart",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_status_endpoint(self):
        task = ImportTask.objects.create(
            file_name="test.docx",
            file="imports/test.docx",
            department=self.department,
            uploaded_by=self.user,
            status=ImportStatus.PROCESSING,
            progress=50,
        )

        response = self.client.get(f"/api/v1/imports/{task.pk}/status/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == ImportStatus.PROCESSING
        assert response.data["progress"] == 50

    def test_preview_endpoint_ready(self):
        task = ImportTask.objects.create(
            file_name="test.docx",
            file="imports/test.docx",
            department=self.department,
            uploaded_by=self.user,
            status=ImportStatus.PREVIEW,
            parsed_data={"plos": [{"code": "PLO1"}]},
        )

        response = self.client.get(f"/api/v1/imports/{task.pk}/preview/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["parsed_data"]["plos"][0]["code"] == "PLO1"

    def test_preview_endpoint_not_ready(self):
        task = ImportTask.objects.create(
            file_name="test.docx",
            file="imports/test.docx",
            department=self.department,
            uploaded_by=self.user,
            status=ImportStatus.PROCESSING,
        )

        response = self.client.get(f"/api/v1/imports/{task.pk}/preview/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("hutech_program.imports.views.confirm_import_task")
    def test_confirm_endpoint(self, mock_task):
        mock_task.delay = MagicMock()
        task = ImportTask.objects.create(
            file_name="test.docx",
            file="imports/test.docx",
            department=self.department,
            uploaded_by=self.user,
            status=ImportStatus.PREVIEW,
        )

        response = self.client.post(f"/api/v1/imports/{task.pk}/confirm/")

        assert response.status_code == status.HTTP_202_ACCEPTED
        mock_task.delay.assert_called_once()

    def test_confirm_endpoint_wrong_status(self):
        task = ImportTask.objects.create(
            file_name="test.docx",
            file="imports/test.docx",
            department=self.department,
            uploaded_by=self.user,
            status=ImportStatus.COMPLETED,
        )

        response = self.client.post(f"/api/v1/imports/{task.pk}/confirm/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_status_endpoint_other_user_not_visible(self):
        other_user = UserFactory(username="other")
        task = ImportTask.objects.create(
            file_name="test.docx",
            file="imports/test.docx",
            department=self.department,
            uploaded_by=other_user,
            status=ImportStatus.PREVIEW,
        )

        response = self.client.get(f"/api/v1/imports/{task.pk}/status/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
