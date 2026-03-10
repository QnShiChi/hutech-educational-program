"""
Factory Boy factories for Programs models.
"""

import factory
from factory.django import DjangoModelFactory

from hutech_program.programs.models import (
    Course,
    CourseGroup,
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
)
from hutech_program.rbac.tests.factories import DepartmentFactory, UserFactory


class TrainingProgramFactory(DjangoModelFactory):
    class Meta:
        model = TrainingProgram

    program_name_vi = factory.Sequence(lambda n: f"Chương trình {n}")
    program_name_en = factory.Sequence(lambda n: f"Program {n}")
    program_code = factory.Sequence(lambda n: f"720000{n:02d}")
    degree_name = factory.LazyAttribute(lambda obj: f"Cử nhân {obj.program_name_vi}")
    education_level = "DAI_HOC"
    managing_department = factory.SubFactory(DepartmentFactory)
    total_credits = 125
    training_duration = "4 năm"
    status = ProgramStatus.DRAFT
    created_by = factory.SubFactory(UserFactory)


class ProgramObjectiveFactory(DjangoModelFactory):
    class Meta:
        model = ProgramObjective

    program = factory.SubFactory(TrainingProgramFactory)
    code = factory.Sequence(lambda n: f"PO{n}")
    description = factory.Faker("sentence")
    order_index = factory.Sequence(lambda n: n)


class ProgramLearningOutcomeFactory(DjangoModelFactory):
    class Meta:
        model = ProgramLearningOutcome

    program = factory.SubFactory(TrainingProgramFactory)
    code = factory.Sequence(lambda n: f"PLO{n}")
    description = factory.Faker("sentence")
    competency_level = factory.Faker("pydecimal", left_digits=1, right_digits=1, min_value=0, max_value=6)
    competency_label = "Đạt yêu cầu"
    order_index = factory.Sequence(lambda n: n)


class PLOPOMappingFactory(DjangoModelFactory):
    class Meta:
        model = PLOPOMapping

    plo = factory.SubFactory(ProgramLearningOutcomeFactory)
    po = factory.SubFactory(ProgramObjectiveFactory)


class PerformanceIndicatorFactory(DjangoModelFactory):
    class Meta:
        model = PerformanceIndicator

    plo = factory.SubFactory(ProgramLearningOutcomeFactory)
    code = factory.Sequence(lambda n: f"PI.1.{n}")
    description = factory.Faker("sentence")
    order_index = factory.Sequence(lambda n: n)


class KnowledgeBlockFactory(DjangoModelFactory):
    class Meta:
        model = KnowledgeBlock

    program = factory.SubFactory(TrainingProgramFactory)
    name = factory.Sequence(lambda n: f"Khối kiến thức {n}")
    parent = None
    required_credits = 20
    elective_credits = 10
    order_index = factory.Sequence(lambda n: n)


# ────────────────── Course Management Factories ──────────────────


class CourseGroupFactory(DjangoModelFactory):
    class Meta:
        model = CourseGroup

    name = factory.Sequence(lambda n: f"Nhóm HP {n}")
    description = factory.Faker("sentence")
    knowledge_block = factory.SubFactory(KnowledgeBlockFactory)
    total_credits = 10
    elective_credits = 5


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course

    code = factory.Sequence(lambda n: f"HP{n:03d}")
    name_vi = factory.Sequence(lambda n: f"Học phần {n}")
    name_en = factory.Sequence(lambda n: f"Course {n}")
    total_credits = 3
    theory_credits = 2
    practice_credits = 1
    project_credits = 0
    internship_credits = 0
    managing_department = factory.SubFactory(DepartmentFactory)


class ProgramCourseFactory(DjangoModelFactory):
    class Meta:
        model = ProgramCourse

    program = factory.SubFactory(TrainingProgramFactory)
    course = factory.SubFactory(CourseFactory)
    knowledge_block = factory.SubFactory(
        KnowledgeBlockFactory,
        program=factory.SelfAttribute("..program"),
    )
    order_number = factory.Sequence(lambda n: f"I.{n:02d}")
    is_required = True
    semester = 1


class CoursePrerequisiteFactory(DjangoModelFactory):
    class Meta:
        model = CoursePrerequisite

    program_course = factory.SubFactory(ProgramCourseFactory)
    prerequisite_course = factory.SubFactory(CourseFactory)
    type = "PREREQUISITE"


class SemesterPlanFactory(DjangoModelFactory):
    class Meta:
        model = SemesterPlan

    program = factory.SubFactory(TrainingProgramFactory)
    semester_number = 1
    program_course = factory.SubFactory(
        ProgramCourseFactory,
        program=factory.SelfAttribute("..program"),
    )
    order_index = factory.Sequence(lambda n: n)


# ────────────────── Matrices & Assessment Plan Factories ──────────────────


class CoursePLOContributionFactory(DjangoModelFactory):
    class Meta:
        model = CoursePLOContribution

    program_course = factory.SubFactory(ProgramCourseFactory)
    pi = factory.SubFactory(PerformanceIndicatorFactory)
    contribution_level = 2  # MEDIUM


class PLOAssessmentPlanFactory(DjangoModelFactory):
    class Meta:
        model = PLOAssessmentPlan

    program = factory.SubFactory(TrainingProgramFactory)
    pi = factory.SubFactory(PerformanceIndicatorFactory)
    contributing_courses_text = "HP001 HP002"
    direct_evidence = "Báo cáo cuối kỳ"
    assessment_tool = "Rubric"
    expected_standard = "Tối thiểu 70% người học đáp ứng"
    assessment_schedule = "HK1 / năm 3"
    responsible_lecturer = "GV1"
    managing_unit = "Khoa CNTT"


