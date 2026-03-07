from django.contrib import admin

from .models import (
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
    SemesterPlan,
    TrainingProgram,
)


class ProgramObjectiveInline(admin.TabularInline):
    model = ProgramObjective
    extra = 1
    fields = ["code", "description", "order_index"]


class PLOInline(admin.TabularInline):
    model = ProgramLearningOutcome
    extra = 1
    fields = ["code", "description", "competency_level", "competency_label", "order_index"]


@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = [
        "program_code",
        "program_name_vi",
        "managing_department",
        "status",
        "version",
        "education_level",
        "total_credits",
        "created_at",
    ]
    list_filter = ["status", "education_level", "managing_department"]
    search_fields = ["program_code", "program_name_vi", "program_name_en"]
    inlines = [ProgramObjectiveInline, PLOInline]
    raw_id_fields = ["managing_department", "created_by", "last_modified_by"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ProgramObjective)
class ProgramObjectiveAdmin(admin.ModelAdmin):
    list_display = ["code", "program", "description", "order_index"]
    list_filter = ["program"]
    search_fields = ["code", "description"]
    raw_id_fields = ["program"]


class PIInline(admin.TabularInline):
    model = PerformanceIndicator
    extra = 1
    fields = ["code", "description", "order_index"]


class PLOPOMappingInline(admin.TabularInline):
    model = PLOPOMapping
    extra = 1
    raw_id_fields = ["po"]


@admin.register(ProgramLearningOutcome)
class PLOAdmin(admin.ModelAdmin):
    list_display = ["code", "program", "description", "competency_level", "order_index"]
    list_filter = ["program"]
    search_fields = ["code", "description"]
    raw_id_fields = ["program"]
    inlines = [PIInline, PLOPOMappingInline]


@admin.register(PerformanceIndicator)
class PIAdmin(admin.ModelAdmin):
    list_display = ["code", "plo", "description", "order_index"]
    list_filter = ["plo__program"]
    search_fields = ["code", "description"]
    raw_id_fields = ["plo"]


@admin.register(KnowledgeBlock)
class KnowledgeBlockAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "program",
        "parent",
        "total_credits",
        "required_credits",
        "elective_credits",
        "percentage",
    ]
    list_filter = ["program"]
    search_fields = ["name"]
    raw_id_fields = ["program", "parent"]


# ────────────────────────── Course Management ──────────────────────────


@admin.register(CourseGroup)
class CourseGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]


class CoursePrerequisiteInline(admin.TabularInline):
    model = CoursePrerequisite
    fk_name = "program_course"
    extra = 1
    raw_id_fields = ["prerequisite_course"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name_vi",
        "total_credits",
        "theory_credits",
        "practice_credits",
        "managing_department",
        "course_group",
        "is_active",
    ]
    list_filter = ["managing_department", "course_group", "is_active"]
    search_fields = ["code", "name_vi", "name_en"]
    raw_id_fields = ["managing_department", "course_group"]


@admin.register(ProgramCourse)
class ProgramCourseAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "course",
        "program",
        "knowledge_block",
        "is_required",
        "semester",
        "batch",
    ]
    list_filter = ["program", "is_required", "semester", "knowledge_block"]
    search_fields = ["course__code", "course__name_vi"]
    raw_id_fields = ["program", "course", "knowledge_block"]
    inlines = [CoursePrerequisiteInline]


@admin.register(SemesterPlan)
class SemesterPlanAdmin(admin.ModelAdmin):
    list_display = ["program", "semester_number", "program_course", "order_index"]
    list_filter = ["program", "semester_number"]
    raw_id_fields = ["program", "program_course"]


# ────────────────────────── Matrices & Assessment Plan ──────────────────────────


@admin.register(CoursePLOContribution)
class CoursePLOContributionAdmin(admin.ModelAdmin):
    list_display = ["program_course", "pi", "contribution_level"]
    list_filter = ["contribution_level", "pi__plo__program"]
    raw_id_fields = ["program_course", "pi"]


@admin.register(PLOAssessmentPlan)
class PLOAssessmentPlanAdmin(admin.ModelAdmin):
    list_display = [
        "program",
        "pi",
        "direct_evidence",
        "assessment_tool",
        "expected_standard",
    ]
    list_filter = ["program"]
    search_fields = ["pi__code", "direct_evidence", "assessment_tool"]
    raw_id_fields = ["program", "pi", "sample_course"]


