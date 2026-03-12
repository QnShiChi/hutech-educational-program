"""
CTĐT models: TrainingProgram, PO, PLO, PLOPOMapping, PI, KnowledgeBlock,
CourseGroup, Course, ProgramCourse, CoursePrerequisite, SemesterPlan,
CoursePLOContribution, PLOAssessmentPlan.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from hutech_program.common import BaseModel, UUIDModel


# ────────────────────────── Choices ──────────────────────────


class ProgramStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Bản nháp")
    SUBMITTED = "SUBMITTED", _("Đã nộp")
    KHOA_REVIEWING = "KHOA_REVIEWING", _("Khoa đang xét duyệt")
    KHOA_APPROVED = "KHOA_APPROVED", _("Khoa đã duyệt")
    PDT_REVIEWING = "PDT_REVIEWING", _("Phòng ĐT đang xét duyệt")
    PDT_APPROVED = "PDT_APPROVED", _("Phòng ĐT đã duyệt")
    BGH_REVIEWING = "BGH_REVIEWING", _("BGH đang xét duyệt")
    PUBLISHED = "PUBLISHED", _("Đã công bố")
    REVISION_REQUIRED = "REVISION_REQUIRED", _("Cần chỉnh sửa")


class VersionStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Bản nháp")
    ACTIVE = "ACTIVE", _("Đang áp dụng")
    ARCHIVED = "ARCHIVED", _("Lưu trữ")


class EducationLevel(models.TextChoices):
    DAI_HOC = "DAI_HOC", _("Đại học")
    THAC_SI = "THAC_SI", _("Thạc sĩ")
    TIEN_SI = "TIEN_SI", _("Tiến sĩ")


# ────────────────────────── Models ──────────────────────────


class TrainingMode(models.TextChoices):
    CHINH_QUY = "CHINH_QUY", _("Chính quy")
    TAI_CHUC = "TAI_CHUC", _("Tại chức")
    TU_XA = "TU_XA", _("Từ xa")


class TrainingProgram(BaseModel):
    """
    Chương trình đào tạo (CTĐT).
    Chứa các trường định danh chung cho tất cả phiên bản.
    """

    # Thông tin định danh
    program_name_vi = models.CharField(
        max_length=300, verbose_name=_("Tên ngành đào tạo (VN)")
    )
    program_name_en = models.CharField(
        max_length=300, blank=True, verbose_name=_("Tên ngành đào tạo (EN)")
    )
    program_code = models.CharField(
        max_length=20, unique=True, verbose_name=_("Mã ngành")
    )
    degree_name = models.CharField(
        max_length=200, verbose_name=_("Tên gọi văn bằng")
    )
    education_level = models.CharField(
        max_length=20,
        choices=EducationLevel.choices,
        default=EducationLevel.DAI_HOC,
        verbose_name=_("Trình độ đào tạo"),
    )
    managing_department = models.ForeignKey(
        "rbac.Department",
        on_delete=models.PROTECT,
        related_name="training_programs",
        verbose_name=_("Đơn vị quản lý"),
    )
    issuing_institution = models.CharField(
        max_length=200,
        default="Trường Đại học Công nghệ TP.HCM",
        verbose_name=_("Trường cấp bằng"),
    )
    training_mode = models.CharField(
        max_length=20,
        choices=TrainingMode.choices,
        default=TrainingMode.CHINH_QUY,
        verbose_name=_("Hình thức đào tạo"),
    )

    # Status & versioning
    status = models.CharField(
        max_length=20,
        choices=ProgramStatus.choices,
        default=ProgramStatus.DRAFT,
        verbose_name=_("Trạng thái"),
    )
    version = models.PositiveIntegerField(default=1, verbose_name=_("Phiên bản"))

    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_programs",
        verbose_name=_("Người tạo"),
    )
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="modified_programs",
        verbose_name=_("Người sửa cuối"),
    )

    class Meta:
        verbose_name = _("Chương trình đào tạo")
        verbose_name_plural = _("Chương trình đào tạo")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["program_code"]),
            models.Index(fields=["status"]),
            models.Index(fields=["managing_department"]),
        ]

    def __str__(self) -> str:
        return f"{self.program_code} - {self.program_name_vi}"

    @property
    def is_editable(self) -> bool:
        return self.status in (ProgramStatus.DRAFT, ProgramStatus.REVISION_REQUIRED)

    @property
    def can_edit(self) -> bool:
        """True only if status allows editing (DRAFT or REVISION_REQUIRED)."""
        return self.status in (ProgramStatus.DRAFT, ProgramStatus.REVISION_REQUIRED)

    @property
    def can_submit(self) -> bool:
        """True if DRAFT or REVISION_REQUIRED."""
        return self.status in (ProgramStatus.DRAFT, ProgramStatus.REVISION_REQUIRED)

    @property
    def active_workflow(self):
        """Returns current IN_PROGRESS workflow or None."""
        from hutech_program.workflows.models import ApprovalWorkflow, WorkflowStatus

        return ApprovalWorkflow.objects.filter(
            entity_type="TrainingProgram",
            entity_id=self.id,
            status=WorkflowStatus.IN_PROGRESS,
        ).first()


class TrainingProgramVersion(BaseModel):
    """
    Phiên bản Chương trình đào tạo theo năm học.
    Chứa tất cả nội dung mô tả có thể thay đổi giữa các phiên bản.
    """

    program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name=_("Chương trình"),
    )
    academic_year = models.CharField(
        max_length=20, verbose_name=_("Năm học"), help_text=_("VD: 2024-2025")
    )
    status = models.CharField(
        max_length=20,
        choices=VersionStatus.choices,
        default=VersionStatus.DRAFT,
        verbose_name=_("Trạng thái"),
    )

    # ── Tín chỉ & thời gian ──
    total_credits = models.PositiveIntegerField(
        default=0, verbose_name=_("Số tín chỉ")
    )
    training_duration = models.CharField(
        max_length=50, default="4 năm", verbose_name=_("Thời gian đào tạo")
    )

    # ── Văn bản pháp lý ──
    decision_number = models.CharField(
        max_length=100, blank=True, verbose_name=_("Số quyết định")
    )
    decision_date = models.DateField(
        null=True, blank=True, verbose_name=_("Ngày quyết định")
    )

    # ── Nội dung mô tả (theo văn bản CTĐT) ──
    general_objective = models.TextField(
        blank=True, verbose_name=_("Mục tiêu chung")
    )
    admission_requirements = models.TextField(
        blank=True, verbose_name=_("Chuẩn đầu vào")
    )
    admission_target = models.TextField(
        blank=True, verbose_name=_("Đối tượng tuyển sinh")
    )
    admission_criteria = models.TextField(
        blank=True, verbose_name=_("Tiêu chí tuyển sinh")
    )
    graduation_requirements = models.TextField(
        blank=True, verbose_name=_("Điều kiện tốt nghiệp")
    )
    career_opportunities = models.TextField(
        blank=True, verbose_name=_("Vị trí việc làm")
    )
    further_education = models.TextField(
        blank=True, verbose_name=_("Học tập nâng cao trình độ")
    )
    teaching_methodology = models.TextField(
        blank=True, verbose_name=_("Phương pháp giảng dạy")
    )
    assessment_methodology = models.TextField(
        blank=True, verbose_name=_("Thang điểm đánh giá và cách thức đánh giá")
    )
    implementation_guide = models.TextField(
        blank=True, verbose_name=_("Hướng dẫn thực hiện")
    )
    reference_programs = models.TextField(
        blank=True, verbose_name=_("Chương trình tham khảo khi xây dựng")
    )
    description_update_period = models.TextField(
        blank=True, verbose_name=_("Thời gian cập nhật bản mô tả CTĐT")
    )
    training_process = models.TextField(
        blank=True, verbose_name=_("Quy trình đào tạo")
    )

    class Meta:
        verbose_name = _("Phiên bản CTĐT")
        verbose_name_plural = _("Phiên bản CTĐT")
        ordering = ["-academic_year"]
        unique_together = ["program", "academic_year"]

    def __str__(self) -> str:
        return f"{self.program.program_code} - Dành cho NH {self.academic_year}"

    @property
    def is_editable(self) -> bool:
        return self.status == VersionStatus.DRAFT

    def delete(self, *args, **kwargs):
        if self.status == VersionStatus.ACTIVE:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                "Không thể xóa phiên bản đang được áp dụng. "
                "Hãy chuyển sang phiên bản khác trước."
            )
        return super().delete(*args, **kwargs)


class ProgramObjective(BaseModel):
    """Mục tiêu đào tạo (PO)."""

    version = models.ForeignKey(
        TrainingProgramVersion,
        on_delete=models.CASCADE,
        related_name="objectives",
        verbose_name=_("Phiên bản CTĐT"),
    )
    program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="objectives_legacy",
        verbose_name=_("Chương trình (Legacy)"),
    )
    code = models.CharField(max_length=10, verbose_name=_("Mã PO"))
    description = models.TextField(verbose_name=_("Mô tả"))
    order_index = models.PositiveIntegerField(default=0, verbose_name=_("Thứ tự"))

    class Meta:
        verbose_name = _("Mục tiêu đào tạo (PO)")
        verbose_name_plural = _("Mục tiêu đào tạo (PO)")
        unique_together = ["version", "code"]
        ordering = ["order_index"]

    def __str__(self) -> str:
        return f"{self.version.program.program_code} / {self.code}"


class ProgramLearningOutcome(BaseModel):
    """Chuẩn đầu ra (PLO)."""

    version = models.ForeignKey(
        TrainingProgramVersion,
        on_delete=models.CASCADE,
        related_name="plos",
        verbose_name=_("Phiên bản CTĐT"),
    )
    program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="plos_legacy",
        verbose_name=_("Chương trình (Legacy)"),
    )
    code = models.CharField(max_length=10, verbose_name=_("Mã PLO"))
    description = models.TextField(verbose_name=_("Mô tả"))
    competency_level = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        verbose_name=_("Mức năng lực (Bloom)"),
        help_text=_("0.0 - 6.0"),
    )
    competency_label = models.CharField(
        max_length=50, blank=True, verbose_name=_("Nhãn năng lực")
    )
    order_index = models.PositiveIntegerField(default=0, verbose_name=_("Thứ tự"))
    objectives = models.ManyToManyField(
        ProgramObjective,
        through="PLOPOMapping",
        blank=True,
        related_name="plos",
        verbose_name=_("Mục tiêu liên quan"),
    )

    class Meta:
        verbose_name = _("Chuẩn đầu ra (PLO)")
        verbose_name_plural = _("Chuẩn đầu ra (PLO)")
        unique_together = ["version", "code"]
        ordering = ["order_index"]

    def __str__(self) -> str:
        return f"{self.version.program.program_code} / {self.code}"


class PLOPOMapping(models.Model):
    """Ma trận PO-PLO."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plo = models.ForeignKey(
        ProgramLearningOutcome,
        on_delete=models.CASCADE,
        verbose_name=_("PLO"),
    )
    po = models.ForeignKey(
        ProgramObjective,
        on_delete=models.CASCADE,
        verbose_name=_("PO"),
    )

    class Meta:
        verbose_name = _("PO-PLO Mapping")
        verbose_name_plural = _("PO-PLO Mapping")
        unique_together = ["plo", "po"]

    def __str__(self) -> str:
        return f"{self.plo.code} ↔ {self.po.code}"


class PerformanceIndicator(BaseModel):
    """Chỉ số đo lường (PI)."""

    plo = models.ForeignKey(
        ProgramLearningOutcome,
        on_delete=models.CASCADE,
        related_name="performance_indicators",
        verbose_name=_("PLO"),
    )
    code = models.CharField(max_length=20, verbose_name=_("Mã PI"))
    description = models.TextField(verbose_name=_("Mô tả"))
    order_index = models.PositiveIntegerField(default=0, verbose_name=_("Thứ tự"))

    class Meta:
        verbose_name = _("Chỉ số đo lường (PI)")
        verbose_name_plural = _("Chỉ số đo lường (PI)")
        unique_together = ["plo", "code"]
        ordering = ["order_index"]

    def __str__(self) -> str:
        return f"{self.plo.code} / {self.code}"


class KnowledgeBlock(BaseModel):
    """Khối kiến thức."""

    version = models.ForeignKey(
        TrainingProgramVersion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="knowledge_blocks",
        verbose_name=_("Phiên bản CTĐT"),
    )
    name = models.CharField(max_length=200, verbose_name=_("Tên khối kiến thức"))
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Khối cha"),
    )
    total_credits = models.PositiveIntegerField(
        default=0, verbose_name=_("Tổng tín chỉ")
    )
    required_credits = models.PositiveIntegerField(
        default=0, verbose_name=_("Tín chỉ bắt buộc")
    )
    elective_credits = models.PositiveIntegerField(
        default=0, verbose_name=_("Tín chỉ tự chọn")
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name=_("Tỷ lệ (%)"),
    )
    order_index = models.PositiveIntegerField(default=0, verbose_name=_("Thứ tự"))

    class Meta:
        verbose_name = _("Khối kiến thức")
        verbose_name_plural = _("Khối kiến thức")
        ordering = ["order_index"]

    def __str__(self) -> str:
        if self.version:
            return f"{self.version.program.program_code} / {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        # Auto-calculate total_credits
        self.total_credits = self.required_credits + self.elective_credits
        super().save(*args, **kwargs)


# ────────────────────────── Course Management ──────────────────────────


class CourseGroup(BaseModel):
    """Nhóm học phần cục bộ trong Khối kiến thức."""

    knowledge_block = models.ForeignKey(
        KnowledgeBlock,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="course_groups",
        verbose_name=_("Khối kiến thức"),
    )
    name = models.CharField(
        max_length=200, verbose_name=_("Tên nhóm")
    )
    description = models.TextField(blank=True, verbose_name=_("Mô tả"))
    
    total_credits = models.PositiveIntegerField(
        default=0, verbose_name=_("Tổng tín chỉ")
    )
    elective_credits = models.PositiveIntegerField(
        default=0, verbose_name=_("Tín chỉ tự chọn")
    )

    class Meta:
        verbose_name = _("Nhóm học phần")
        verbose_name_plural = _("Nhóm học phần")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Course(BaseModel):
    """
    Học phần (master) — dùng chung nhiều CTĐT.
    """

    code = models.CharField(
        max_length=20, unique=True, verbose_name=_("Mã học phần")
    )
    name_vi = models.CharField(
        max_length=300, verbose_name=_("Tên học phần (VN)")
    )
    name_en = models.CharField(
        max_length=300, blank=True, verbose_name=_("Tên học phần (EN)")
    )

    # Tín chỉ
    total_credits = models.PositiveIntegerField(
        verbose_name=_("Tổng tín chỉ")
    )
    theory_credits = models.PositiveIntegerField(
        default=0, verbose_name=_("Tín chỉ lý thuyết")
    )
    practice_credits = models.PositiveIntegerField(
        default=0, verbose_name=_("Tín chỉ thực hành")
    )
    project_credits = models.PositiveIntegerField(
        default=0, verbose_name=_("Tín chỉ đồ án")
    )
    internship_credits = models.PositiveIntegerField(
        default=0, verbose_name=_("Tín chỉ thực tập")
    )

    # Giờ học
    total_hours = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("Tổng giờ")
    )
    theory_hours = models.PositiveIntegerField(
        default=0, verbose_name=_("Giờ lý thuyết")
    )
    practice_hours = models.PositiveIntegerField(
        default=0, verbose_name=_("Giờ thực hành")
    )

    managing_department = models.ForeignKey(
        "rbac.Department",
        on_delete=models.PROTECT,
        related_name="courses",
        verbose_name=_("Khoa quản lý"),
    )
    description = models.TextField(
        blank=True, verbose_name=_("Mô tả tóm tắt")
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_("Đang sử dụng")
    )

    class Meta:
        verbose_name = _("Học phần")
        verbose_name_plural = _("Học phần")
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["managing_department"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name_vi}"

    def clean(self):
        from django.core.exceptions import ValidationError

        expected = (
            self.theory_credits
            + self.practice_credits
            + self.project_credits
            + self.internship_credits
        )
        if self.total_credits != expected:
            raise ValidationError(
                {
                    "total_credits": _(
                        "Tổng tín chỉ (%(total)s) phải bằng "
                        "lý thuyết + thực hành + đồ án + thực tập (%(expected)s)."
                    )
                    % {"total": self.total_credits, "expected": expected}
                }
            )


class ProgramCourse(BaseModel):
    """Học phần trong 1 CTĐT cụ thể."""

    program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="program_courses_legacy",
        verbose_name=_("Chương trình (Legacy)"),
    )
    version = models.ForeignKey(
        TrainingProgramVersion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="program_courses",
        verbose_name=_("Phiên bản CTĐT"),
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="program_courses",
        verbose_name=_("Học phần"),
    )
    knowledge_block = models.ForeignKey(
        KnowledgeBlock,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="program_courses",
        verbose_name=_("Khối kiến thức"),
    )
    course_group = models.ForeignKey(
        CourseGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="program_courses",
        verbose_name=_("Nhóm học phần"),
    )
    order_number = models.CharField(
        max_length=10, blank=True, verbose_name=_("Số thứ tự"),
        help_text=_("VD: I.01, II.03"),
    )
    is_required = models.BooleanField(
        default=True, verbose_name=_("Bắt buộc"),
        help_text=_("Bắt buộc / Tự chọn"),
    )
    semester = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("Học kỳ khuyến nghị"),
        help_text=_("1-8"),
    )
    batch = models.CharField(
        max_length=1, blank=True, verbose_name=_("Đợt"),
        help_text=_("A hoặc B"),
    )
    software_required = models.CharField(
        max_length=200, blank=True, verbose_name=_("Phần mềm yêu cầu"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Ghi chú"))

    class Meta:
        verbose_name = _("Học phần trong CTĐT")
        verbose_name_plural = _("Học phần trong CTĐT")
        unique_together = ["version", "course"]
        ordering = ["order_number"]

    def __str__(self) -> str:
        if self.version:
            return f"{self.version.program.program_code} / {self.course.code}"
        return self.course.code

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.course_group and self.course_group.knowledge_block_id != self.knowledge_block_id:
            raise ValidationError(
                {
                    "course_group": _("Nhóm học phần phải thuộc Khối kiến thức mà học phần được gán.")
                }
            )


class PrerequisiteType(models.TextChoices):
    PREREQUISITE = "PREREQUISITE", _("Học trước")
    COREQUISITE = "COREQUISITE", _("Song hành")


class CoursePrerequisite(models.Model):
    """Điều kiện tiên quyết / song hành."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_course = models.ForeignKey(
        ProgramCourse,
        on_delete=models.CASCADE,
        related_name="prerequisites",
        verbose_name=_("Học phần trong CTĐT"),
    )
    prerequisite_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_("Học phần tiên quyết"),
    )
    type = models.CharField(
        max_length=20,
        choices=PrerequisiteType.choices,
        default=PrerequisiteType.PREREQUISITE,
        verbose_name=_("Loại"),
    )

    class Meta:
        verbose_name = _("Điều kiện tiên quyết")
        verbose_name_plural = _("Điều kiện tiên quyết")
        unique_together = ["program_course", "prerequisite_course"]

    def __str__(self) -> str:
        return f"{self.program_course.course.code} ← {self.prerequisite_course.code} ({self.type})"


class SemesterPlan(BaseModel):
    """Kế hoạch giảng dạy theo học kỳ."""

    program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="semester_plans_legacy",
        verbose_name=_("Chương trình (Legacy)"),
    )
    version = models.ForeignKey(
        TrainingProgramVersion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="semester_plans",
        verbose_name=_("Phiên bản CTĐT"),
    )
    semester_number = models.PositiveIntegerField(
        verbose_name=_("Học kỳ"),
        help_text=_("1-8"),
    )
    program_course = models.ForeignKey(
        ProgramCourse,
        on_delete=models.CASCADE,
        verbose_name=_("Học phần trong CTĐT"),
    )
    order_index = models.PositiveIntegerField(
        default=0, verbose_name=_("Thứ tự")
    )

    class Meta:
        verbose_name = _("Kế hoạch học kỳ")
        verbose_name_plural = _("Kế hoạch học kỳ")
        unique_together = ["version", "program_course"]
        ordering = ["semester_number", "order_index"]

    def __str__(self) -> str:
        return f"HK{self.semester_number}: {self.program_course.course.code}"


# ────────────────────────── Matrices & Assessment Plan ──────────────────────────


class ContributionLevel(models.IntegerChoices):
    NONE = 0, _("Không đóng góp")
    LOW = 1, _("Thấp")
    MEDIUM = 2, _("Trung bình")
    HIGH = 3, _("Cao")


class CoursePLOContribution(models.Model):
    """Ma trận đóng góp HP-PLO-PI."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_course = models.ForeignKey(
        ProgramCourse,
        on_delete=models.CASCADE,
        related_name="plo_contributions",
        verbose_name=_("Học phần trong CTĐT"),
    )
    pi = models.ForeignKey(
        PerformanceIndicator,
        on_delete=models.CASCADE,
        related_name="course_contributions",
        verbose_name=_("Chỉ số PI"),
    )
    contribution_level = models.PositiveIntegerField(
        default=ContributionLevel.NONE,
        choices=ContributionLevel.choices,
        verbose_name=_("Mức đóng góp"),
    )

    class Meta:
        verbose_name = _("Đóng góp HP-PLO-PI")
        verbose_name_plural = _("Đóng góp HP-PLO-PI")
        unique_together = ["program_course", "pi"]
        indexes = [
            models.Index(fields=["program_course"]),
            models.Index(fields=["pi"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.program_course.course.code} → "
            f"{self.pi.code}: L{self.contribution_level}"
        )


class PLOAssessmentPlan(BaseModel):
    """Kế hoạch đánh giá PLO."""

    version = models.ForeignKey(
        TrainingProgramVersion,
        on_delete=models.CASCADE,
        related_name="assessment_plans",
        verbose_name=_("Phiên bản CTĐT"),
    )
    program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assessment_plans_legacy",
        verbose_name=_("Chương trình (Legacy)"),
    )
    pi = models.ForeignKey(
        PerformanceIndicator,
        on_delete=models.CASCADE,
        related_name="assessment_plans",
        verbose_name=_("Chỉ số PI"),
    )
    contributing_courses_text = models.TextField(
        blank=True,
        verbose_name=_("HP đóng góp"),
        help_text=_("VD: POS104 POS105 POS106"),
    )
    sample_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assessment_samples",
        verbose_name=_("HP lấy mẫu"),
    )
    direct_evidence = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Minh chứng trực tiếp"),
        help_text=_("VD: Chuyên cần, Báo cáo cuối kỳ"),
    )
    assessment_tool = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Công cụ đánh giá"),
        help_text=_("VD: Điểm chuyên cần, Rubric"),
    )
    expected_standard = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Tiêu chuẩn kỳ vọng"),
        help_text=_("VD: Tối thiểu 70% người học đáp ứng"),
    )
    assessment_schedule = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Lịch đánh giá"),
        help_text=_("VD: HK1 / năm 3"),
    )
    responsible_lecturer = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Giảng viên phụ trách"),
    )
    managing_unit = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Đơn vị quản lý"),
    )

    class Meta:
        verbose_name = _("Kế hoạch đánh giá PLO")
        verbose_name_plural = _("Kế hoạch đánh giá PLO")
        ordering = ["pi__plo__order_index", "pi__order_index"]
        unique_together = ["version", "pi"]
        indexes = [
            models.Index(fields=["version"]),
            models.Index(fields=["pi"]),
        ]

    def __str__(self) -> str:
        return f"{self.version.program.program_code} / {self.pi.code} assessment"


