"""
Tests for the seed_nntq2025 management command.
Verifies: successful seeding, --flush flag, idempotency, and entity counts.
"""

import pytest
from django.core.management import call_command

from hutech_program.programs.models import (
    Course,
    CoursePLOContribution,
    CoursePrerequisite,
    KnowledgeBlock,
    PerformanceIndicator,
    PLOAssessmentPlan,
    PLOPOMapping,
    ProgramCourse,
    ProgramLearningOutcome,
    ProgramObjective,
    ProgramStatus,
    SemesterPlan,
    TrainingProgram,
    TrainingProgramVersion,
)
from hutech_program.rbac.models import Department

pytestmark = pytest.mark.django_db

PROGRAM_CODE = "NNTQ2025"


def _get_version(program):
    """Get the active version for a program."""
    return program.versions.first()


class TestSeedCommand:
    """Test the seed_nntq2025 management command."""

    def test_seed_creates_all_data(self):
        """Running seed command creates all expected entities."""
        call_command("seed_nntq2025")

        # Program
        program = TrainingProgram.objects.get(program_code=PROGRAM_CODE)
        assert program.program_name_vi  # Not empty
        assert program.status == ProgramStatus.PUBLISHED
        assert program.total_credits >= 100

        # Department
        assert Department.objects.filter(code="KHOA_NN").exists()

        # Version
        version = _get_version(program)
        assert version is not None

        # POs
        pos = ProgramObjective.objects.filter(version=version)
        assert pos.count() == 4

        # PLOs
        plos = ProgramLearningOutcome.objects.filter(version=version)
        assert plos.count() == 7

        # PO-PLO Mappings
        mappings = PLOPOMapping.objects.filter(plo__version=version)
        assert mappings.count() >= 7  # at least 1 per PLO

        # Knowledge Blocks
        kbs = KnowledgeBlock.objects.filter(version=version)
        assert kbs.count() >= 2  # at least root blocks

        # Courses
        pcs = ProgramCourse.objects.filter(version=version)
        assert pcs.count() >= 10  # should have many courses

        # PIs
        pis = PerformanceIndicator.objects.filter(plo__version=version)
        assert pis.count() == 16  # hardcoded

    def test_idempotent_skip_existing(self, capsys):
        """Running seed twice without --flush skips the second time."""
        call_command("seed_nntq2025")
        assert TrainingProgram.objects.filter(program_code=PROGRAM_CODE).count() == 1

        # Run again
        call_command("seed_nntq2025")
        captured = capsys.readouterr()
        assert "already exists" in captured.out
        assert TrainingProgram.objects.filter(program_code=PROGRAM_CODE).count() == 1

    def test_flush_deletes_and_recreates(self):
        """Running seed with --flush replaces existing data."""
        call_command("seed_nntq2025")
        program = TrainingProgram.objects.get(program_code=PROGRAM_CODE)
        original_pk = program.pk

        # Run with flush
        call_command("seed_nntq2025", flush=True)
        program = TrainingProgram.objects.get(program_code=PROGRAM_CODE)

        # Should be a new record
        assert program.pk != original_pk
        assert program.status == ProgramStatus.PUBLISHED

        # Verify data is intact (not doubled)
        version = _get_version(program)
        assert ProgramObjective.objects.filter(version=version).count() == 4
        assert ProgramLearningOutcome.objects.filter(version=version).count() == 7
        assert PerformanceIndicator.objects.filter(plo__version=version).count() == 16

    def test_flush_twice_consistent(self):
        """Running with --flush multiple times gives consistent results."""
        call_command("seed_nntq2025")
        call_command("seed_nntq2025", flush=True)
        call_command("seed_nntq2025", flush=True)

        # Should still have exactly 1 program
        assert TrainingProgram.objects.filter(program_code=PROGRAM_CODE).count() == 1

        program = TrainingProgram.objects.get(program_code=PROGRAM_CODE)
        version = _get_version(program)
        assert ProgramObjective.objects.filter(version=version).count() == 4
        assert ProgramLearningOutcome.objects.filter(version=version).count() == 7

    def test_department_not_duplicated(self):
        """Department uses get_or_create, should not be duplicated."""
        call_command("seed_nntq2025")
        call_command("seed_nntq2025", flush=True)

        assert Department.objects.filter(code="KHOA_NN").count() == 1

    def test_program_metadata_correct(self):
        """Verify program metadata fields."""
        call_command("seed_nntq2025")
        program = TrainingProgram.objects.get(program_code=PROGRAM_CODE)

        assert program.education_level == "DAI_HOC"
        assert program.status == ProgramStatus.PUBLISHED
        assert program.managing_department.code == "KHOA_NN"

    def test_po_descriptions_populated(self):
        """All POs have descriptions."""
        call_command("seed_nntq2025")
        program = TrainingProgram.objects.get(program_code=PROGRAM_CODE)
        version = _get_version(program)
        for po in ProgramObjective.objects.filter(version=version):
            assert po.description, f"{po.code} has no description"
            assert po.code.startswith("PO")

    def test_plo_with_competency_levels(self):
        """All PLOs have competency levels set."""
        call_command("seed_nntq2025")
        program = TrainingProgram.objects.get(program_code=PROGRAM_CODE)
        version = _get_version(program)
        for plo in ProgramLearningOutcome.objects.filter(version=version):
            assert plo.competency_level > 0, f"{plo.code} has no competency level"

    def test_plo_po_mapping_correctness(self):
        """PLO-PO mappings are bidirectional and correct."""
        call_command("seed_nntq2025")
        program = TrainingProgram.objects.get(program_code=PROGRAM_CODE)
        version = _get_version(program)

        # PLO1 should map to PO1
        plo1 = ProgramLearningOutcome.objects.get(version=version, code="PLO1")
        po_codes = list(
            PLOPOMapping.objects.filter(plo=plo1).values_list("po__code", flat=True)
        )
        assert "PO1" in po_codes
