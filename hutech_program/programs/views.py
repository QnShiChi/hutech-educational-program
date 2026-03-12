"""
CTĐT ViewSets.
"""

from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers as drf_serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from hutech_program.rbac.mixins import AuditLogMixin
from hutech_program.rbac.permissions import DepartmentScopedPermission, HasModulePermission

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
    TrainingProgramVersion,
    VersionStatus,
)
from .serializers import (
    CourseCreateUpdateSerializer,
    CourseDetailSerializer,
    CourseGroupSerializer,
    CourseListSerializer,
    CoursePLOMatrixBulkSerializer,
    CourseUsageSerializer,
    KnowledgeBlockFlatSerializer,
    KnowledgeBlockSerializer,
    PerformanceIndicatorSerializer,
    PLOAssessmentPlanBulkSerializer,
    PLOAssessmentPlanSerializer,
    PLOSerializer,
    POPLOMatrixSerializer,
    PrerequisiteMatrixSerializer,
    ProgramCourseBulkSerializer,
    ProgramCourseSerializer,
    ProgramObjectiveSerializer,
    ReorderSerializer,
    SemesterPlanBulkSerializer,
    SemesterPlanItemSerializer,
    TrainingProgramCreateUpdateSerializer,
    TrainingProgramDetailSerializer,
    TrainingProgramListSerializer,
    TrainingProgramVersionSerializer,
)
from .services.versioning import clone_program_version


class TrainingProgramViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """CRUD for Training Programs."""

    queryset = TrainingProgram.objects.select_related(
        "managing_department", "created_by"
    ).prefetch_related("versions")
    permission_classes = [IsAuthenticated, DepartmentScopedPermission]
    permission_map = {
        "list": "programs.view",
        "retrieve": "programs.view",
        "create": "programs.create",
        "update": "programs.edit",
        "partial_update": "programs.edit",
        "destroy": "programs.delete",
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "education_level", "managing_department"]
    search_fields = ["program_code", "program_name_vi", "program_name_en"]
    ordering_fields = ["program_code", "created_at", "status"]

    def get_serializer_class(self):
        if self.action == "list":
            return TrainingProgramListSerializer
        if self.action in ("create", "update", "partial_update"):
            return TrainingProgramCreateUpdateSerializer
        return TrainingProgramDetailSerializer

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        self._create_audit_log(
            self.request, "CREATE", instance,
            new_data=self._serialize_instance(instance),
        )

    def perform_update(self, serializer):
        old_data = self._serialize_instance(serializer.instance)
        instance = serializer.save(last_modified_by=self.request.user)
        self._create_audit_log(
            self.request, "UPDATE", instance,
            old_data=old_data, new_data=self._serialize_instance(instance),
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != ProgramStatus.DRAFT:
            return Response(
                {"detail": "Chỉ có thể xóa CTĐT ở trạng thái Bản nháp."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


def _get_program(view):
    """Helper to get program from URL kwargs."""
    return get_object_or_404(TrainingProgram, pk=view.kwargs["program_pk"])


def _get_version(view):
    """Get version from ?version= query param, or the program's latest version."""
    program = _get_program(view)
    version_id = view.request.query_params.get("version")
    if version_id:
        return get_object_or_404(TrainingProgramVersion, pk=version_id, program=program)
    # Default: ACTIVE version, or latest by academic_year
    version = program.versions.filter(status=VersionStatus.ACTIVE).first()
    if not version:
        version = program.versions.order_by('-academic_year').first()
    return version


def _check_editable(program):
    """Raise 400 if program is not editable."""
    if not program.is_editable:
        return Response(
            {"detail": "CTĐT không ở trạng thái cho phép sửa."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return None


class ProgramObjectiveViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """Nested under program: POs."""

    serializer_class = ProgramObjectiveSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "list": "programs.view",
        "retrieve": "programs.view",
        "create": "programs.edit",
        "update": "programs.edit",
        "partial_update": "programs.edit",
        "destroy": "programs.edit",
        "reorder": "programs.edit",
    }

    def get_queryset(self):
        version = _get_version(self)
        if version:
            return ProgramObjective.objects.filter(version=version)
        return ProgramObjective.objects.none()

    def perform_create(self, serializer):
        version = _get_version(self)
        if not version:
            raise drf_serializers.ValidationError("Không tìm thấy phiên bản CTĐT.")
        program = version.program
        err = _check_editable(program)
        if err:
            raise drf_serializers.ValidationError("CTĐT không ở trạng thái cho phép sửa.")
        instance = serializer.save(version=version)
        self._create_audit_log(
            self.request, "CREATE", instance,
            new_data=self._serialize_instance(instance),
        )

    @action(detail=False, methods=["post"])
    def reorder(self, request, program_pk=None):
        version = _get_version(self)
        ser = ReorderSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        for idx, item_id in enumerate(ser.validated_data["ordered_ids"]):
            ProgramObjective.objects.filter(
                pk=item_id, version=version
            ).update(order_index=idx)
        return Response({"status": "ok"})


class PLOViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """Nested under program: PLOs."""

    serializer_class = PLOSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "list": "programs.view",
        "retrieve": "programs.view",
        "create": "plo.create",
        "update": "plo.edit",
        "partial_update": "plo.edit",
        "destroy": "plo.delete",
        "reorder": "plo.edit",
    }

    def get_queryset(self):
        version = _get_version(self)
        if version:
            return ProgramLearningOutcome.objects.filter(
                version=version
            ).prefetch_related("objectives")
        return ProgramLearningOutcome.objects.none()

    def perform_create(self, serializer):
        version = _get_version(self)
        if not version:
            raise drf_serializers.ValidationError("Không tìm thấy phiên bản CTĐT.")
        instance = serializer.save(version=version)
        self._create_audit_log(
            self.request, "CREATE", instance,
            new_data=self._serialize_instance(instance),
        )

    @action(detail=False, methods=["post"])
    def reorder(self, request, program_pk=None):
        version = _get_version(self)
        ser = ReorderSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        for idx, item_id in enumerate(ser.validated_data["ordered_ids"]):
            ProgramLearningOutcome.objects.filter(
                pk=item_id, version=version
            ).update(order_index=idx)
        return Response({"status": "ok"})


class POPLOMatrixView(viewsets.ViewSet):
    """GET/PUT for PO-PLO matrix."""

    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "retrieve": "programs.view",
        "update": "programs.edit",
    }

    def retrieve(self, request, program_pk=None):
        version = _get_version(self)
        if not version:
            return Response({"mappings": []})
        mappings = PLOPOMapping.objects.filter(
            plo__version=version
        ).select_related("plo", "po")
        data = [
            {"plo_id": str(m.plo_id), "po_id": str(m.po_id), "plo_code": m.plo.code, "po_code": m.po.code}
            for m in mappings
        ]
        return Response({"mappings": data})

    def update(self, request, program_pk=None):
        program = get_object_or_404(TrainingProgram, pk=program_pk)
        if not program.is_editable:
            return Response(
                {"detail": "CTĐT không ở trạng thái cho phép sửa."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        version = _get_version(self)
        if not version:
            return Response(
                {"detail": "Không tìm thấy phiên bản CTĐT."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ser = POPLOMatrixSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        # Delete existing mappings for this version
        PLOPOMapping.objects.filter(plo__version=version).delete()

        # Create new mappings
        for m in ser.validated_data["mappings"]:
            PLOPOMapping.objects.create(
                plo_id=m["plo_id"],
                po_id=m["po_id"],
            )

        return Response({"status": "ok", "count": len(ser.validated_data["mappings"])})


class PerformanceIndicatorViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """Nested under PLO: PIs."""

    serializer_class = PerformanceIndicatorSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "list": "programs.view",
        "retrieve": "programs.view",
        "create": "plo.edit",
        "update": "plo.edit",
        "partial_update": "plo.edit",
        "destroy": "plo.edit",
    }

    def get_queryset(self):
        plo = get_object_or_404(
            ProgramLearningOutcome,
            pk=self.kwargs["plo_pk"],
        )
        return PerformanceIndicator.objects.filter(plo=plo)

    def perform_create(self, serializer):
        plo = get_object_or_404(
            ProgramLearningOutcome,
            pk=self.kwargs["plo_pk"],
        )
        instance = serializer.save(plo=plo)
        self._create_audit_log(
            self.request, "CREATE", instance,
            new_data=self._serialize_instance(instance),
        )


class KnowledgeBlockViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """Nested under program: KnowledgeBlocks (tree)."""

    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "list": "programs.view",
        "retrieve": "programs.view",
        "create": "programs.edit",
        "update": "programs.edit",
        "partial_update": "programs.edit",
        "destroy": "programs.edit",
    }

    def get_queryset(self):
        version = _get_version(self)
        qs = KnowledgeBlock.objects.filter(version=version)
        # For list, only show root nodes (tree)
        if self.action == "list":
            return qs.filter(parent__isnull=True)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return KnowledgeBlockSerializer
        if self.action in ("create", "update", "partial_update"):
            return KnowledgeBlockFlatSerializer
        return KnowledgeBlockSerializer

    def perform_create(self, serializer):
        version = _get_version(self)
        instance = serializer.save(version=version)
        self._create_audit_log(
            self.request, "CREATE", instance,
            new_data=self._serialize_instance(instance),
        )


# ────────────────────────── Course Management ──────────────────────────


class CourseGroupViewSet(viewsets.ModelViewSet):
    """CRUD for CourseGroups."""

    queryset = CourseGroup.objects.all()
    serializer_class = CourseGroupSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "list": "courses.view",
        "retrieve": "courses.view",
        "create": "courses.create",
        "update": "courses.edit",
        "partial_update": "courses.edit",
        "destroy": "courses.delete",
    }
    search_fields = ["name"]
    filter_backends = [filters.SearchFilter]


class CourseViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """CRUD for master Courses."""

    queryset = Course.objects.select_related(
        "managing_department"
    ).prefetch_related("program_courses")
    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "list": "courses.view",
        "retrieve": "courses.view",
        "create": "courses.create",
        "update": "courses.edit",
        "partial_update": "courses.edit",
        "destroy": "courses.delete",
        "programs": "courses.view",
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["managing_department", "is_active"]
    search_fields = ["code", "name_vi", "name_en"]
    ordering_fields = ["code", "total_credits", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        if self.action in ("create", "update", "partial_update"):
            return CourseCreateUpdateSerializer
        if self.action == "programs":
            return CourseUsageSerializer
        return CourseDetailSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        self._create_audit_log(
            self.request, "CREATE", instance,
            new_data=self._serialize_instance(instance),
        )

    def perform_update(self, serializer):
        old_data = self._serialize_instance(serializer.instance)
        instance = serializer.save()
        self._create_audit_log(
            self.request, "UPDATE", instance,
            old_data=old_data, new_data=self._serialize_instance(instance),
        )

    def destroy(self, request, *args, **kwargs):
        """Prevent delete if Course is used in non-DRAFT programs."""
        instance = self.get_object()
        non_draft_usages = ProgramCourse.objects.filter(
            course=instance
        ).exclude(
            version__program__status=ProgramStatus.DRAFT
        ).select_related("version__program")

        if non_draft_usages.exists():
            program_codes = ", ".join(
                pc.version.program.program_code for pc in non_draft_usages[:5]
                if pc.version and pc.version.program
            )
            return Response(
                {
                    "detail": (
                        f"Không thể xóa học phần đang được sử dụng trong CTĐT "
                        f"không phải Bản nháp: {program_codes}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    def programs(self, request, pk=None):
        """GET /courses/{id}/programs/ — which programs use this course."""
        course = self.get_object()
        usages = ProgramCourse.objects.filter(
            course=course
        ).select_related("program")
        serializer = CourseUsageSerializer(usages, many=True)
        return Response(serializer.data)


class ProgramCourseViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """Nested under program: ProgramCourses."""

    serializer_class = ProgramCourseSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "list": "courses.view",
        "retrieve": "courses.view",
        "create": "courses.edit",
        "update": "courses.edit",
        "partial_update": "courses.edit",
        "destroy": "courses.edit",
        "bulk_add": "courses.edit",
    }

    def get_queryset(self):
        version = _get_version(self)
        return ProgramCourse.objects.filter(
            version=version
        ).select_related(
            "course", "knowledge_block"
        ).prefetch_related("prerequisites__prerequisite_course")

    def perform_create(self, serializer):
        program = _get_program(self)
        err = _check_editable(program)
        if err:
            from rest_framework import serializers as drf_ser
            raise drf_ser.ValidationError("CTĐT không ở trạng thái cho phép sửa.")
        version = _get_version(self)
        instance = serializer.save(version=version)
        self._create_audit_log(
            self.request, "CREATE", instance,
            new_data=self._serialize_instance(instance),
        )

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_add(self, request, program_pk=None):
        """POST /programs/{id}/courses/bulk/ — bulk add courses."""
        program = get_object_or_404(TrainingProgram, pk=program_pk)
        if not program.is_editable:
            return Response(
                {"detail": "CTĐT không ở trạng thái cho phép sửa."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        version = _get_version(self)
        if not version:
            return Response(
                {"detail": "Kh\u00f4ng t\u00ecm th\u1ea5y phi\u00ean b\u1ea3n CT\u0110T."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ser = ProgramCourseBulkSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        created = []
        with transaction.atomic():
            for item in ser.validated_data["courses"]:
                pc, was_created = ProgramCourse.objects.get_or_create(
                    version=version,
                    course_id=item["course"],
                    defaults={
                        "knowledge_block_id": item.get("knowledge_block"),
                        "order_number": item.get("order_number", ""),
                        "is_required": item.get("is_required", True),
                        "semester": item.get("semester"),
                        "batch": item.get("batch", ""),
                    },
                )
                if was_created:
                    created.append(str(pc.id))

        return Response(
            {"status": "ok", "created_count": len(created), "created_ids": created},
            status=status.HTTP_201_CREATED,
        )


class PrerequisiteView(viewsets.ViewSet):
    """GET/PUT for all prerequisites in a program."""

    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "retrieve": "courses.view",
        "update": "courses.edit",
    }

    def retrieve(self, request, program_pk=None):
        program = get_object_or_404(TrainingProgram, pk=program_pk)
        version = _get_version(self)
        prereqs = CoursePrerequisite.objects.filter(
            program_course__version=version
        ).select_related(
            "program_course__course", "prerequisite_course"
        )
        data = [
            {
                "id": str(p.id),
                "program_course_id": str(p.program_course_id),
                "course_code": p.program_course.course.code,
                "prerequisite_course_id": str(p.prerequisite_course_id),
                "prerequisite_code": p.prerequisite_course.code,
                "prerequisite_name": p.prerequisite_course.name_vi,
                "type": p.type,
            }
            for p in prereqs
        ]
        return Response({"prerequisites": data})

    def update(self, request, program_pk=None):
        program = get_object_or_404(TrainingProgram, pk=program_pk)
        if not program.is_editable:
            return Response(
                {"detail": "CTĐT không ở trạng thái cho phép sửa."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        version = _get_version(self)
        ser = PrerequisiteMatrixSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        with transaction.atomic():
            # Delete existing prerequisites for this version
            CoursePrerequisite.objects.filter(
                program_course__version=version
            ).delete()

            # Create new prerequisites
            for item in ser.validated_data["prerequisites"]:
                pc = get_object_or_404(
                    ProgramCourse,
                    pk=item["program_course_id"],
                    version=version,
                )
                # Validate semester ordering for PREREQUISITE type
                prereq_type = item.get("type", "PREREQUISITE")
                if prereq_type == "PREREQUISITE" and pc.semester:
                    # Find the prerequisite course's semester in this program
                    prereq_pc = ProgramCourse.objects.filter(
                        version=version,
                        course_id=item["prerequisite_course_id"],
                    ).first()
                    if prereq_pc and prereq_pc.semester and prereq_pc.semester >= pc.semester:
                        return Response(
                            {
                                "detail": (
                                    f"Học phần tiên quyết {prereq_pc.course.code} "
                                    f"(HK{prereq_pc.semester}) phải ở học kỳ trước "
                                    f"{pc.course.code} (HK{pc.semester})."
                                )
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                CoursePrerequisite.objects.create(
                    program_course=pc,
                    prerequisite_course_id=item["prerequisite_course_id"],
                    type=prereq_type,
                )

        return Response({"status": "ok", "count": len(ser.validated_data["prerequisites"])})


class SemesterPlanView(viewsets.ViewSet):
    """GET/PUT full 8-semester plan."""

    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "retrieve": "courses.view",
        "update": "courses.edit",
    }

    def retrieve(self, request, program_pk=None):
        program = get_object_or_404(TrainingProgram, pk=program_pk)
        version = _get_version(self)
        plans = SemesterPlan.objects.filter(
            version=version
        ).select_related(
            "program_course__course"
        ).order_by("semester_number", "order_index")

        # Group by semester
        semesters = {}
        for plan in plans:
            sem_num = plan.semester_number
            if sem_num not in semesters:
                semesters[sem_num] = []
            semesters[sem_num].append(
                SemesterPlanItemSerializer(plan).data
            )

        result = [
            {"semester_number": num, "courses": courses}
            for num, courses in sorted(semesters.items())
        ]
        return Response({"semesters": result})

    def update(self, request, program_pk=None):
        program = get_object_or_404(TrainingProgram, pk=program_pk)
        if not program.is_editable:
            return Response(
                {"detail": "CTĐT không ở trạng thái cho phép sửa."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        version = _get_version(self)
        ser = SemesterPlanBulkSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        with transaction.atomic():
            # Delete existing plan
            SemesterPlan.objects.filter(version=version).delete()

            # Create new plan
            count = 0
            for sem in ser.validated_data["semesters"]:
                for course_item in sem["courses"]:
                    SemesterPlan.objects.create(
                        version=version,
                        semester_number=sem["semester_number"],
                        program_course_id=course_item["program_course_id"],
                        order_index=course_item.get("order_index", 0),
                    )
                    count += 1

        return Response({"status": "ok", "count": count})


# ─────────────────── HP-PLO-PI Matrix & Assessment Plan ───────────────────


class CoursePLOMatrixView(viewsets.ViewSet):
    """GET/PUT for HP-PLO-PI contribution matrix."""

    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "retrieve": "programs.view",
        "update": "programs.edit",
    }

    def retrieve(self, request, program_pk=None):
        """GET returns pivot format: {columns, rows}."""
        program = get_object_or_404(TrainingProgram, pk=program_pk)
        version = _get_version(self)
        if not version:
            return Response({"columns": [], "rows": []})

        # Build columns: PIs grouped by PLO
        plos = (
            ProgramLearningOutcome.objects.filter(version=version)
            .prefetch_related("performance_indicators")
            .order_by("order_index")
        )
        columns = []
        pi_ids = []
        for plo in plos:
            pis = plo.performance_indicators.order_by("order_index")
            plo_group = {
                "plo_id": str(plo.id),
                "plo_code": plo.code,
                "pis": [
                    {"pi_id": str(pi.id), "pi_code": pi.code}
                    for pi in pis
                ],
            }
            columns.append(plo_group)
            pi_ids.extend(pi.id for pi in pis)

        # Build rows: courses with contribution cells
        program_courses = (
            ProgramCourse.objects.filter(version=version)
            .select_related("course")
            .order_by("order_number")
        )

        # Fetch all contributions in one query
        contributions = {}
        for c in CoursePLOContribution.objects.filter(
            program_course__version=version
        ).values("program_course_id", "pi_id", "contribution_level"):
            contributions[(c["program_course_id"], c["pi_id"])] = c["contribution_level"]

        rows = []
        for pc in program_courses:
            cells = {}
            for pi_id in pi_ids:
                key = (pc.id, pi_id)
                cells[str(pi_id)] = contributions.get(key, 0)
            rows.append({
                "program_course_id": str(pc.id),
                "course_code": pc.course.code,
                "course_name": pc.course.name_vi,
                "total_credits": pc.course.total_credits,
                "contributions": cells,
            })

        return Response({"columns": columns, "rows": rows})

    def update(self, request, program_pk=None):
        """PUT bulk update: delete + create."""
        program = get_object_or_404(TrainingProgram, pk=program_pk)
        if not program.is_editable:
            return Response(
                {"detail": "CTĐT không ở trạng thái cho phép sửa."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        version = _get_version(self)
        if not version:
            return Response(
                {"detail": "Không tìm thấy phiên bản CTĐT."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ser = CoursePLOMatrixBulkSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        with transaction.atomic():
            # Delete all existing contributions for this version
            CoursePLOContribution.objects.filter(
                program_course__version=version
            ).delete()

            # Bulk create new contributions (only non-zero levels)
            objects = [
                CoursePLOContribution(
                    program_course_id=item["program_course_id"],
                    pi_id=item["pi_id"],
                    contribution_level=item["contribution_level"],
                )
                for item in ser.validated_data["contributions"]
                if item["contribution_level"] > 0
            ]
            CoursePLOContribution.objects.bulk_create(objects)

        return Response({
            "status": "ok",
            "count": len(objects),
        })


class PLOAssessmentPlanViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """CRUD + bulk for PLO Assessment Plans."""

    serializer_class = PLOAssessmentPlanSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "list": "programs.view",
        "retrieve": "programs.view",
        "create": "programs.edit",
        "update": "programs.edit",
        "partial_update": "programs.edit",
        "destroy": "programs.edit",
        "bulk_upsert": "programs.edit",
    }

    def get_queryset(self):
        version = _get_version(self)
        if version:
            return PLOAssessmentPlan.objects.filter(
                version=version
            ).select_related("pi__plo", "sample_course").order_by(
                "pi__plo__order_index", "pi__order_index"
            )
        return PLOAssessmentPlan.objects.none()

    def perform_create(self, serializer):
        version = _get_version(self)
        if not version:
            raise drf_serializers.ValidationError("Không tìm thấy phiên bản CTĐT.")
        instance = serializer.save(version=version)
        self._create_audit_log(
            self.request, "CREATE", instance,
            new_data=self._serialize_instance(instance),
        )

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_upsert(self, request, program_pk=None):
        """POST /programs/{id}/assessment-plans/bulk/ — bulk create/update."""
        program = get_object_or_404(TrainingProgram, pk=program_pk)
        if not program.is_editable:
            return Response(
                {"detail": "CTĐT không ở trạng thái cho phép sửa."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        version = _get_version(self)
        if not version:
            return Response(
                {"detail": "Không tìm thấy phiên bản CTĐT."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ser = PLOAssessmentPlanBulkSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        created_count = 0
        updated_count = 0
        with transaction.atomic():
            for item in ser.validated_data["plans"]:
                pi_id = item.pop("pi")
                defaults = {
                    k: v for k, v in item.items()
                    if k in (
                        "contributing_courses_text",
                        "sample_course",
                        "direct_evidence",
                        "assessment_tool",
                        "expected_standard",
                        "assessment_schedule",
                        "responsible_lecturer",
                        "managing_unit",
                    )
                }
                _, was_created = PLOAssessmentPlan.objects.update_or_create(
                    version=version,
                    pi_id=pi_id,
                    defaults=defaults,
                )
                if was_created:
                    created_count += 1
                else:
                    updated_count += 1

        return Response({
            "status": "ok",
            "created": created_count,
            "updated": updated_count,
        })


class PLOCoverageValidationView(viewsets.ViewSet):
    """Validate PLO coverage: each PLO should have at least 1 contributing course."""

    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "retrieve": "programs.view",
    }

    def retrieve(self, request, program_pk=None):
        program = get_object_or_404(TrainingProgram, pk=program_pk)
        version = _get_version(self)
        if not version:
            return Response({
                "program_id": str(program.id),
                "all_covered": True,
                "plos": [],
            })

        plos = (
            ProgramLearningOutcome.objects.filter(version=version)
            .prefetch_related("performance_indicators")
            .order_by("order_index")
        )

        # Collect all PI IDs that have at least one contribution > 0
        covered_pis = set(
            CoursePLOContribution.objects.filter(
                program_course__version=version,
                contribution_level__gt=0,
            ).values_list("pi_id", flat=True)
        )

        results = []
        all_covered = True
        for plo in plos:
            pis = plo.performance_indicators.all()
            plo_pi_ids = set(pi.id for pi in pis)
            covered = plo_pi_ids.issubset(covered_pis) and len(plo_pi_ids) > 0
            uncovered = [pi.code for pi in pis if pi.id not in covered_pis]
            if not covered:
                all_covered = False
            results.append({
                "plo_id": str(plo.id),
                "plo_code": plo.code,
                "total_pis": len(plo_pi_ids),
                "covered_pis": len(plo_pi_ids) - len(uncovered),
                "is_covered": covered,
                "uncovered_pis": uncovered,
            })

        return Response({
            "program_id": str(program.id),
            "all_covered": all_covered,
            "plos": results,
        })


class TrainingProgramVersionViewSet(viewsets.ModelViewSet):
    """CRUD + clone + set-active for TrainingProgramVersion."""

    serializer_class = TrainingProgramVersionSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    permission_map = {
        "list": "programs.view",
        "retrieve": "programs.view",
        "create": "programs.edit",
        "update": "programs.edit",
        "partial_update": "programs.edit",
        "destroy": "programs.edit",
        "clone": "programs.edit",
        "set_active": "programs.edit",
    }

    def get_queryset(self):
        return TrainingProgramVersion.objects.filter(
            program_id=self.kwargs["program_pk"]
        ).order_by('-academic_year')

    def perform_create(self, serializer):
        program = _get_program(self)
        serializer.save(
            program=program,
            created_by=self.request.user,
            last_modified_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def clone(self, request, program_pk=None, pk=None):
        """POST /programs/{program_pk}/versions/{pk}/clone/ — clone a version."""
        source_version = get_object_or_404(
            TrainingProgramVersion, pk=pk, program_id=program_pk
        )
        academic_year = request.data.get("academic_year")
        if not academic_year:
            return Response(
                {"detail": "Vui lòng nhập năm học mới (academic_year)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if version with this academic year already exists
        if TrainingProgramVersion.objects.filter(
            program_id=program_pk, academic_year=academic_year
        ).exists():
            return Response(
                {"detail": f"Phiên bản năm học '{academic_year}' đã tồn tại."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_version = clone_program_version(
            source_version, academic_year, user=request.user
        )
        serializer = self.get_serializer(new_version)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="set-active")
    def set_active(self, request, program_pk=None, pk=None):
        """POST /programs/{program_pk}/versions/{pk}/set-active/ — activate a version."""
        version = get_object_or_404(
            TrainingProgramVersion, pk=pk, program_id=program_pk
        )

        with transaction.atomic():
            # Deactivate all other versions for this program
            TrainingProgramVersion.objects.filter(
                program_id=program_pk, status=VersionStatus.ACTIVE
            ).update(status=VersionStatus.ARCHIVED)

            version.status = VersionStatus.ACTIVE
            version.save(update_fields=["status"])

        serializer = self.get_serializer(version)
        return Response(serializer.data)

