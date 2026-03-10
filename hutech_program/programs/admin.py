from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

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


class ProgramContextMixin:
    change_list_template = "admin/programs/workflow_change_list.html"
    change_form_template = "admin/programs/workflow_change_form.html"
    program_relation_field = "program"

    def get_active_program(self, request):
        program_id = request.session.get('active_program_id')
        if program_id:
            from .models import TrainingProgram
            return TrainingProgram.objects.filter(id=program_id).first()
        return None

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['active_program'] = self.get_active_program(request)
        return super().changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['active_program'] = self.get_active_program(request)
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['active_program'] = self.get_active_program(request)
        return super().add_view(request, form_url, extra_context=extra_context)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        active_program = self.get_active_program(request)
        if active_program:
            qs = qs.filter(**{self.program_relation_field: active_program})
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        active_program = self.get_active_program(request)
        if active_program and db_field.name == self.program_relation_field:
            kwargs["initial"] = active_program.id
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request):
        active_program = self.get_active_program(request)
        if active_program and not active_program.can_edit:
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        active_program = self.get_active_program(request)
        if active_program and not active_program.can_edit:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        active_program = self.get_active_program(request)
        if active_program and not active_program.can_edit:
            return False
        return super().has_delete_permission(request, obj)



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
    change_form_template = "admin/programs/workflow_change_form.html"
    
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

    def change_view(self, request, object_id, form_url='', extra_context=None):
        request.session['active_program_id'] = object_id
        extra_context = extra_context or {}
        program = self.model.objects.filter(id=object_id).first()
        extra_context['active_program'] = program
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


@admin.register(ProgramObjective)
class ProgramObjectiveAdmin(ProgramContextMixin, admin.ModelAdmin):
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
class PLOAdmin(ProgramContextMixin, admin.ModelAdmin):
    list_display = ["code", "program", "description", "competency_level", "order_index"]
    list_filter = ["program"]
    search_fields = ["code", "description"]
    raw_id_fields = ["program"]
    inlines = [PIInline, PLOPOMappingInline]


@admin.register(PerformanceIndicator)
class PIAdmin(ProgramContextMixin, admin.ModelAdmin):
    program_relation_field = "plo__program"
    list_display = ["code", "plo", "description", "order_index"]
    list_filter = ["plo__program"]
    search_fields = ["code", "description"]
    raw_id_fields = ["plo"]


class CourseGroupInline(admin.TabularInline):
    model = CourseGroup
    extra = 1
    fields = ["name", "total_credits", "elective_credits", "description"]

@admin.register(CourseGroup)
class CourseGroupAdmin(ProgramContextMixin, admin.ModelAdmin):
    program_relation_field = "knowledge_block__program"
    list_display = ["name", "knowledge_block", "total_credits", "elective_credits"]
    list_filter = ["knowledge_block__program"]
    search_fields = ["name"]
    raw_id_fields = ["knowledge_block"]


@admin.register(KnowledgeBlock)
class KnowledgeBlockAdmin(ProgramContextMixin, admin.ModelAdmin):
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
    inlines = [CourseGroupInline]


# ────────────────────────── Course Management ──────────────────────────





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
        "is_active",
    ]
    list_filter = ["managing_department", "is_active"]
    search_fields = ["code", "name_vi", "name_en"]
    raw_id_fields = ["managing_department"]


@admin.register(ProgramCourse)
class ProgramCourseAdmin(ProgramContextMixin, admin.ModelAdmin):
    list_display = [
        "order_number",
        "course",
        "program",
        "knowledge_block",
        "course_group",
        "is_required",
        "semester",
        "batch",
    ]
    list_filter = ["program", "is_required", "semester", "knowledge_block", "course_group"]
    search_fields = ["course__code", "course__name_vi"]
    raw_id_fields = ["program", "course", "knowledge_block"]
    inlines = [CoursePrerequisiteInline]

    class Media:
        js = ("admin/js/program_course_dependent_dropdown.js",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "get-course-groups/",
                self.admin_site.admin_view(self.get_course_groups),
                name="programs_programcourse_get_course_groups",
            ),
        ]
        return custom_urls + urls

    def get_course_groups(self, request):
        kb_id = request.GET.get("kb_id")
        if not kb_id:
            return JsonResponse({"results": []})
        from .models import CourseGroup

        groups = CourseGroup.objects.filter(knowledge_block_id=kb_id).values("id", "name")
        return JsonResponse({"results": list(groups)})
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "course_group":
            active_program = self.get_active_program(request)
            if active_program:
                from .models import CourseGroup
                kwargs["queryset"] = CourseGroup.objects.filter(knowledge_block__program=active_program)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(SemesterPlan)
class SemesterPlanAdmin(ProgramContextMixin, admin.ModelAdmin):
    list_display = ["program", "semester_number", "program_course", "order_index"]
    list_filter = ["program", "semester_number"]
    raw_id_fields = ["program", "program_course"]


# ────────────────────────── Matrices & Assessment Plan ──────────────────────────


@admin.register(CoursePLOContribution)
class CoursePLOContributionAdmin(ProgramContextMixin, admin.ModelAdmin):
    program_relation_field = "program_course__program"
    list_display = ["program_course", "pi", "contribution_level"]
    list_filter = ["contribution_level", "pi__plo__program"]
    raw_id_fields = ["program_course", "pi"]


@admin.register(PLOAssessmentPlan)
class PLOAssessmentPlanAdmin(ProgramContextMixin, admin.ModelAdmin):
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


