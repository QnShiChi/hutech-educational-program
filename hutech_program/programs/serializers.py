"""
CTĐT serializers.
"""

from rest_framework import serializers

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
    ProgramStatus,
    SemesterPlan,
    TrainingProgram,
)


# ────────────────── TrainingProgram ──────────────────


class TrainingProgramListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="managing_department.name", read_only=True
    )
    po_count = serializers.IntegerField(source="objectives.count", read_only=True)
    plo_count = serializers.IntegerField(source="plos.count", read_only=True)

    class Meta:
        model = TrainingProgram
        fields = [
            "id",
            "program_code",
            "program_name_vi",
            "program_name_en",
            "education_level",
            "managing_department",
            "department_name",
            "status",
            "version",
            "total_credits",
            "po_count",
            "plo_count",
            "created_at",
        ]


class ProgramObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramObjective
        fields = ["id", "code", "description", "order_index"]
        read_only_fields = ["id"]


class PLOSummarySerializer(serializers.ModelSerializer):
    pi_count = serializers.IntegerField(
        source="performance_indicators.count", read_only=True
    )
    po_codes = serializers.SerializerMethodField()

    class Meta:
        model = ProgramLearningOutcome
        fields = [
            "id",
            "code",
            "description",
            "competency_level",
            "competency_label",
            "order_index",
            "pi_count",
            "po_codes",
        ]

    def get_po_codes(self, obj):
        return list(obj.objectives.values_list("code", flat=True))


class TrainingProgramDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="managing_department.name", read_only=True
    )
    objectives = ProgramObjectiveSerializer(many=True, read_only=True)
    plos = PLOSummarySerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.name", read_only=True, default=None
    )

    class Meta:
        model = TrainingProgram
        fields = [
            "id",
            "program_code",
            "program_name_vi",
            "program_name_en",
            "degree_name",
            "education_level",
            "managing_department",
            "department_name",
            "total_credits",
            "training_duration",
            "decision_number",
            "decision_date",
            "issuing_institution",
            "general_objective",
            "admission_requirements",
            "graduation_requirements",
            "career_opportunities",
            "further_education",
            "teaching_methodology",
            "assessment_methodology",
            "implementation_guide",
            "status",
            "version",
            "created_by",
            "created_by_name",
            "last_modified_by",
            "objectives",
            "plos",
            "created_at",
            "updated_at",
        ]


class TrainingProgramCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingProgram
        fields = [
            "program_code",
            "program_name_vi",
            "program_name_en",
            "degree_name",
            "education_level",
            "managing_department",
            "total_credits",
            "training_duration",
            "decision_number",
            "decision_date",
            "issuing_institution",
            "general_objective",
            "admission_requirements",
            "graduation_requirements",
            "career_opportunities",
            "further_education",
            "teaching_methodology",
            "assessment_methodology",
            "implementation_guide",
        ]

    def validate(self, data):
        instance = self.instance
        if instance and not instance.is_editable:
            raise serializers.ValidationError(
                "Chỉ có thể sửa CTĐT ở trạng thái Bản nháp hoặc Cần chỉnh sửa."
            )
        return data


# ────────────────── PLO ──────────────────


class PLOSerializer(serializers.ModelSerializer):
    po_codes = serializers.SerializerMethodField()

    class Meta:
        model = ProgramLearningOutcome
        fields = [
            "id",
            "code",
            "description",
            "competency_level",
            "competency_label",
            "order_index",
            "po_codes",
        ]
        read_only_fields = ["id"]

    def get_po_codes(self, obj):
        return list(obj.objectives.values_list("code", flat=True))

    def validate_competency_level(self, value):
        if value < 0 or value > 6:
            raise serializers.ValidationError("Mức năng lực phải từ 0.0 đến 6.0")
        return value


# ────────────────── PI ──────────────────


class PerformanceIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceIndicator
        fields = ["id", "code", "description", "order_index"]
        read_only_fields = ["id"]


# ────────────────── KnowledgeBlock ──────────────────


class KnowledgeBlockSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeBlock
        fields = [
            "id",
            "name",
            "parent",
            "total_credits",
            "required_credits",
            "elective_credits",
            "percentage",
            "order_index",
            "children",
        ]
        read_only_fields = ["id", "total_credits"]

    def get_children(self, obj):
        children = obj.children.all()
        if children.exists():
            return KnowledgeBlockSerializer(children, many=True).data
        return []


class KnowledgeBlockFlatSerializer(serializers.ModelSerializer):
    """Flat serializer for create/update."""

    class Meta:
        model = KnowledgeBlock
        fields = [
            "id",
            "name",
            "parent",
            "required_credits",
            "elective_credits",
            "percentage",
            "order_index",
        ]
        read_only_fields = ["id"]


# ────────────────── PO-PLO Matrix ──────────────────


class POPLOMatrixSerializer(serializers.Serializer):
    """
    Bulk read/write for PO-PLO matrix.
    Format: { "mappings": [{"plo_id": "...", "po_id": "..."}, ...] }
    """

    mappings = serializers.ListField(
        child=serializers.DictField(child=serializers.UUIDField())
    )

    def validate_mappings(self, value):
        for m in value:
            if "plo_id" not in m or "po_id" not in m:
                raise serializers.ValidationError(
                    "Mỗi mapping cần có plo_id và po_id."
                )
        return value


class ReorderSerializer(serializers.Serializer):
    """Reorder items by ID list."""

    ordered_ids = serializers.ListField(child=serializers.UUIDField())


# ────────────────── Course Management ──────────────────


class CourseGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseGroup
        fields = ["id", "knowledge_block", "name", "description", "total_credits", "elective_credits"]
        read_only_fields = ["id"]


class CourseListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="managing_department.name", read_only=True
    )
    program_count = serializers.IntegerField(
        source="program_courses.count", read_only=True
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "code",
            "name_vi",
            "name_en",
            "total_credits",
            "theory_credits",
            "practice_credits",
            "project_credits",
            "internship_credits",
            "managing_department",
            "department_name",
            "is_active",
            "program_count",
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="managing_department.name", read_only=True
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "code",
            "name_vi",
            "name_en",
            "total_credits",
            "theory_credits",
            "practice_credits",
            "project_credits",
            "internship_credits",
            "total_hours",
            "theory_hours",
            "practice_hours",
            "managing_department",
            "department_name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "code",
            "name_vi",
            "name_en",
            "total_credits",
            "theory_credits",
            "practice_credits",
            "project_credits",
            "internship_credits",
            "total_hours",
            "theory_hours",
            "practice_hours",
            "managing_department",
            "description",
            "is_active",
        ]

    def validate(self, data):
        total = data.get("total_credits", getattr(self.instance, "total_credits", 0))
        theory = data.get("theory_credits", getattr(self.instance, "theory_credits", 0))
        practice = data.get("practice_credits", getattr(self.instance, "practice_credits", 0))
        project = data.get("project_credits", getattr(self.instance, "project_credits", 0))
        internship = data.get("internship_credits", getattr(self.instance, "internship_credits", 0))

        expected = theory + practice + project + internship
        if total != expected:
            raise serializers.ValidationError(
                {
                    "total_credits": (
                        f"Tổng tín chỉ ({total}) phải bằng "
                        f"lý thuyết + thực hành + đồ án + thực tập ({expected})."
                    )
                }
            )
        return data


class CourseUsageSerializer(serializers.ModelSerializer):
    """Shows which programs use a course."""

    program_code = serializers.CharField(source="program.program_code", read_only=True)
    program_name = serializers.CharField(source="program.program_name_vi", read_only=True)
    program_status = serializers.CharField(source="program.status", read_only=True)

    class Meta:
        model = ProgramCourse
        fields = [
            "id",
            "program",
            "program_code",
            "program_name",
            "program_status",
            "knowledge_block",
            "semester",
            "is_required",
        ]


# ────────────────── ProgramCourse ──────────────────


class CoursePrerequisiteSerializer(serializers.ModelSerializer):
    prerequisite_code = serializers.CharField(
        source="prerequisite_course.code", read_only=True
    )
    prerequisite_name = serializers.CharField(
        source="prerequisite_course.name_vi", read_only=True
    )

    class Meta:
        model = CoursePrerequisite
        fields = [
            "id",
            "prerequisite_course",
            "prerequisite_code",
            "prerequisite_name",
            "type",
        ]
        read_only_fields = ["id"]


class ProgramCourseSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="course.code", read_only=True)
    course_name = serializers.CharField(source="course.name_vi", read_only=True)
    total_credits = serializers.IntegerField(source="course.total_credits", read_only=True)
    knowledge_block_name = serializers.CharField(
        source="knowledge_block.name", read_only=True, default=None
    )
    course_group_name = serializers.CharField(
        source="course_group.name", read_only=True, default=None
    )
    prerequisites = CoursePrerequisiteSerializer(many=True, read_only=True)

    class Meta:
        model = ProgramCourse
        fields = [
            "id",
            "course",
            "course_code",
            "course_name",
            "total_credits",
            "knowledge_block",
            "knowledge_block_name",
            "course_group",
            "course_group_name",
            "order_number",
            "is_required",
            "semester",
            "batch",
            "software_required",
            "notes",
            "prerequisites",
        ]
        read_only_fields = ["id"]


class ProgramCourseBulkSerializer(serializers.Serializer):
    """Bulk add courses to a program."""

    courses = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of {course, knowledge_block, order_number, is_required, semester, batch}",
    )

    def validate_courses(self, value):
        for item in value:
            if "course" not in item:
                raise serializers.ValidationError("Mỗi item cần có trường 'course'.")
        return value


# ────────────────── Prerequisite Matrix ──────────────────


class PrerequisiteMatrixSerializer(serializers.Serializer):
    """
    Bulk read/write for all prerequisites in a CTĐT.
    Format: { "prerequisites": [
        {"program_course_id": "...", "prerequisite_course_id": "...", "type": "PREREQUISITE"},
        ...
    ] }
    """

    prerequisites = serializers.ListField(
        child=serializers.DictField()
    )

    def validate_prerequisites(self, value):
        for item in value:
            if "program_course_id" not in item or "prerequisite_course_id" not in item:
                raise serializers.ValidationError(
                    "Mỗi item cần có program_course_id và prerequisite_course_id."
                )
        return value


# ────────────────── SemesterPlan ──────────────────


class SemesterPlanItemSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="program_course.course.code", read_only=True)
    course_name = serializers.CharField(source="program_course.course.name_vi", read_only=True)
    total_credits = serializers.IntegerField(
        source="program_course.course.total_credits", read_only=True
    )

    class Meta:
        model = SemesterPlan
        fields = [
            "id",
            "semester_number",
            "program_course",
            "course_code",
            "course_name",
            "total_credits",
            "order_index",
        ]
        read_only_fields = ["id"]


class SemesterPlanBulkSerializer(serializers.Serializer):
    """
    Full 8-semester plan update.
    Format: { "semesters": [
        {"semester_number": 1, "courses": [
            {"program_course_id": "...", "order_index": 0}, ...
        ]}, ...
    ] }
    """

    semesters = serializers.ListField(child=serializers.DictField())

    def validate_semesters(self, value):
        for sem in value:
            if "semester_number" not in sem or "courses" not in sem:
                raise serializers.ValidationError(
                    "Mỗi semester cần có semester_number và courses."
                )
            sem_num = sem["semester_number"]
            if not (1 <= sem_num <= 8):
                raise serializers.ValidationError(
                    f"semester_number phải từ 1 đến 8, nhận được {sem_num}."
                )
        return value


# ────────────────── HP-PLO-PI Matrix ──────────────────


class CoursePLOContributionCellSerializer(serializers.Serializer):
    """Single cell: (program_course_id, pi_id, level)."""

    program_course_id = serializers.UUIDField()
    pi_id = serializers.UUIDField()
    contribution_level = serializers.IntegerField(min_value=0, max_value=3)


class CoursePLOMatrixBulkSerializer(serializers.Serializer):
    """PUT body for bulk matrix update."""

    contributions = serializers.ListField(
        child=CoursePLOContributionCellSerializer(),
        help_text="List of {program_course_id, pi_id, contribution_level}",
    )


# ────────────────── PLO Assessment Plan ──────────────────


class PLOAssessmentPlanSerializer(serializers.ModelSerializer):
    pi_code = serializers.CharField(source="pi.code", read_only=True)
    plo_code = serializers.CharField(source="pi.plo.code", read_only=True)
    sample_course_code = serializers.CharField(
        source="sample_course.code", read_only=True, default=None
    )

    class Meta:
        model = PLOAssessmentPlan
        fields = [
            "id",
            "pi",
            "pi_code",
            "plo_code",
            "contributing_courses_text",
            "sample_course",
            "sample_course_code",
            "direct_evidence",
            "assessment_tool",
            "expected_standard",
            "assessment_schedule",
            "responsible_lecturer",
            "managing_unit",
        ]
        read_only_fields = ["id"]


class PLOAssessmentPlanBulkSerializer(serializers.Serializer):
    """Bulk create/update assessment plans."""

    plans = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of assessment plan dicts with pi + fields",
    )

    def validate_plans(self, value):
        for item in value:
            if "pi" not in item:
                raise serializers.ValidationError(
                    "Mỗi plan cần có trường 'pi'."
                )
        return value
