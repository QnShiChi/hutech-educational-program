"""
Management command: seed_nntq2025
Seed sample data for CTĐT "Ngôn ngữ Trung Quốc" (NNTQ2025) from the Word document.
Uses DocxParser for courses/knowledge_blocks, hardcodes PO/PLO/PI data.
"""

import os
import re
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from hutech_program.imports.parser import DocxParser
from hutech_program.programs.models import (
    ContributionLevel,
    Course,
    CoursePLOContribution,
    CoursePrerequisite,
    KnowledgeBlock,
    PerformanceIndicator,
    PLOAssessmentPlan,
    PLOPOMapping,
    PrerequisiteType,
    ProgramCourse,
    ProgramLearningOutcome,
    ProgramObjective,
    ProgramStatus,
    SemesterPlan,
    TrainingProgram,
    TrainingProgramVersion,
    VersionStatus,
)
from hutech_program.rbac.models import Department

# ─── Path to the Word document ───────────────────────────────────────────────

DOCX_PATH = os.path.join(
    settings.BASE_DIR, "wiki", "mo-ta-chuong-trinh-cu-nhan-NNTQ2025.docx"
)

PROGRAM_CODE = "NNTQ2025"

# ─── Hardcoded data (not reliably parsed from the Word document) ─────────────

PO_DATA = [
    {
        "code": "PO1",
        "description": (
            "Vận dụng được kiến thức giáo dục đại cương và kiến thức cơ sở ngành "
            "để hỗ trợ việc học tập, nghiên cứu chuyên ngành Ngôn ngữ Trung Quốc."
        ),
        "order_index": 1,
    },
    {
        "code": "PO2",
        "description": (
            "Sử dụng thành thạo tiếng Trung ở cấp độ HSK 5, có khả năng giao tiếp "
            "và làm việc trong môi trường sử dụng tiếng Trung."
        ),
        "order_index": 2,
    },
    {
        "code": "PO3",
        "description": (
            "Có năng lực chuyên môn trong lĩnh vực biên phiên dịch, giảng dạy "
            "hoặc thương mại quốc tế sử dụng tiếng Trung."
        ),
        "order_index": 3,
    },
    {
        "code": "PO4",
        "description": (
            "Có kỹ năng mềm, thái độ nghề nghiệp và năng lực tự học, nghiên cứu "
            "để phát triển bản thân và thích ứng trong môi trường làm việc."
        ),
        "order_index": 4,
    },
]

PLO_DATA = [
    {
        "code": "PLO1",
        "description": (
            "Vận dụng kiến thức khoa học xã hội, nhân văn, pháp luật và kiến thức "
            "cơ sở ngành ngôn ngữ Trung Quốc vào học tập và nghiên cứu."
        ),
        "competency_level": Decimal("3.0"),
        "competency_label": "Vận dụng",
        "order_index": 1,
    },
    {
        "code": "PLO2",
        "description": (
            "Sử dụng tiếng Trung ở trình độ HSK 5 trong giao tiếp, đọc hiểu "
            "và viết các văn bản chuyên ngành."
        ),
        "competency_level": Decimal("4.0"),
        "competency_label": "Phân tích",
        "order_index": 2,
    },
    {
        "code": "PLO3",
        "description": (
            "Biên dịch và phiên dịch tiếng Trung - tiếng Việt trong các lĩnh vực "
            "kinh tế, thương mại, du lịch và các lĩnh vực chuyên ngành."
        ),
        "competency_level": Decimal("4.0"),
        "competency_label": "Phân tích",
        "order_index": 3,
    },
    {
        "code": "PLO4",
        "description": (
            "Áp dụng kiến thức ngôn ngữ và phương pháp giảng dạy để dạy tiếng Trung "
            "ở trình độ cơ bản."
        ),
        "competency_level": Decimal("3.0"),
        "competency_label": "Vận dụng",
        "order_index": 4,
    },
    {
        "code": "PLO5",
        "description": (
            "Sử dụng tiếng Anh ở trình độ tương đương IELTS 4.0 trong giao tiếp "
            "và đọc hiểu tài liệu cơ bản."
        ),
        "competency_level": Decimal("3.0"),
        "competency_label": "Vận dụng",
        "order_index": 5,
    },
    {
        "code": "PLO6",
        "description": (
            "Vận dụng kỹ năng mềm (làm việc nhóm, giao tiếp, tư duy phản biện) "
            "và ứng dụng công nghệ thông tin trong công việc."
        ),
        "competency_level": Decimal("3.0"),
        "competency_label": "Vận dụng",
        "order_index": 6,
    },
    {
        "code": "PLO7",
        "description": (
            "Thể hiện thái độ nghề nghiệp đúng đắn, ý thức trách nhiệm xã hội, "
            "tôn trọng đa dạng văn hóa và tuân thủ pháp luật."
        ),
        "competency_level": Decimal("3.0"),
        "competency_label": "Vận dụng",
        "order_index": 7,
    },
]

# PO-PLO mapping matrix: PLO_code -> list of PO_codes
PLO_PO_MAPPING = {
    "PLO1": ["PO1"],
    "PLO2": ["PO2"],
    "PLO3": ["PO2", "PO3"],
    "PLO4": ["PO3"],
    "PLO5": ["PO2"],
    "PLO6": ["PO4"],
    "PLO7": ["PO4"],
}

# PI data: hardcoded because parser may not reliably extract
PI_DATA = [
    {"plo_code": "PLO1", "code": "PI1.1", "description": "Trình bày được kiến thức pháp luật, xã hội và nhân văn cơ bản.", "order_index": 1},
    {"plo_code": "PLO1", "code": "PI1.2", "description": "Vận dụng kiến thức cơ sở ngành vào các tình huống học thuật.", "order_index": 2},
    {"plo_code": "PLO2", "code": "PI2.1", "description": "Nghe và hiểu các bài nói tiếng Trung chuyên ngành ở tốc độ bình thường.", "order_index": 1},
    {"plo_code": "PLO2", "code": "PI2.2", "description": "Nói tiếng Trung lưu loát trong giao tiếp hàng ngày và công việc.", "order_index": 2},
    {"plo_code": "PLO2", "code": "PI2.3", "description": "Đọc hiểu các văn bản tiếng Trung chuyên ngành.", "order_index": 3},
    {"plo_code": "PLO2", "code": "PI2.4", "description": "Viết được các văn bản tiếng Trung đúng ngữ pháp, rõ ràng.", "order_index": 4},
    {"plo_code": "PLO3", "code": "PI3.1", "description": "Biên dịch văn bản Trung-Việt trong các lĩnh vực chuyên ngành.", "order_index": 1},
    {"plo_code": "PLO3", "code": "PI3.2", "description": "Phiên dịch nói Trung-Việt trong các cuộc họp, hội nghị.", "order_index": 2},
    {"plo_code": "PLO4", "code": "PI4.1", "description": "Soạn giáo án và thiết kế bài giảng tiếng Trung.", "order_index": 1},
    {"plo_code": "PLO4", "code": "PI4.2", "description": "Thực hiện giảng dạy tiếng Trung ở trình độ cơ bản.", "order_index": 2},
    {"plo_code": "PLO5", "code": "PI5.1", "description": "Giao tiếp bằng tiếng Anh ở trình độ IELTS 4.0.", "order_index": 1},
    {"plo_code": "PLO5", "code": "PI5.2", "description": "Đọc hiểu tài liệu tiếng Anh cơ bản liên quan đến chuyên ngành.", "order_index": 2},
    {"plo_code": "PLO6", "code": "PI6.1", "description": "Làm việc nhóm hiệu quả và thể hiện kỹ năng giao tiếp tốt.", "order_index": 1},
    {"plo_code": "PLO6", "code": "PI6.2", "description": "Sử dụng công nghệ thông tin trong công việc chuyên môn.", "order_index": 2},
    {"plo_code": "PLO7", "code": "PI7.1", "description": "Thể hiện đạo đức nghề nghiệp và trách nhiệm xã hội.", "order_index": 1},
    {"plo_code": "PLO7", "code": "PI7.2", "description": "Tuân thủ pháp luật và tôn trọng đa dạng văn hóa.", "order_index": 2},
]


class Command(BaseCommand):
    help = "Seed sample data for CTĐT Ngôn ngữ Trung Quốc (NNTQ2025) from the Word document."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing NNTQ2025 data before seeding.",
        )

    def handle(self, *args, **options):
        flush = options["flush"]

        # Check idempotency
        existing = TrainingProgram.objects.filter(program_code=PROGRAM_CODE).first()
        if existing and not flush:
            self.stdout.write(
                self.style.WARNING(
                    f"Program '{PROGRAM_CODE}' already exists. "
                    f"Use --flush to delete and recreate. Skipping."
                )
            )
            return

        # Parse the Word document
        if not os.path.exists(DOCX_PATH):
            self.stderr.write(self.style.ERROR(f"Word file not found: {DOCX_PATH}"))
            return

        self.stdout.write(f"Parsing Word document: {DOCX_PATH}")
        parser = DocxParser(DOCX_PATH)
        parsed = parser.parse_all()

        if parser.errors:
            for err in parser.errors:
                self.stderr.write(self.style.WARNING(f"Parser error: {err}"))

        with transaction.atomic():
            # Flush existing data
            if flush and existing:
                self.stdout.write(
                    self.style.WARNING(f"Flushing existing program '{PROGRAM_CODE}'...")
                )
                existing.delete()

            # Create Department
            department = self._create_department()

            # Create TrainingProgram
            program = self._create_program(department, parsed.get("general_info", {}))

            # Create Version
            version = self._create_version(program, parsed.get("general_info", {}))

            # Create POs
            po_map = self._create_pos(version)

            # Create PLOs
            plo_map = self._create_plos(version)

            # Create PO-PLO Mappings
            mapping_count = self._create_plo_po_mappings(po_map, plo_map)

            # Create Knowledge Blocks
            kb_map = self._create_knowledge_blocks(version, parsed.get("knowledge_blocks", []))

            # Create Courses
            course_map = self._create_courses(department, parsed.get("courses", []))

            # Create ProgramCourse (link courses to program with semester)
            pc_map = self._create_program_courses(
                version, course_map, kb_map,
                parsed.get("courses", []),
                parsed.get("semester_plan", []),
            )

            # Create CoursePrerequisites
            prereq_count = self._create_prerequisites(
                pc_map, course_map, parsed.get("courses", [])
            )

            # Create PIs
            pi_map = self._create_pis(plo_map)

            # Create CoursePLOContributions
            contrib_count = self._create_course_plo_contributions(
                pc_map, pi_map, parsed.get("course_plo_matrix", [])
            )

            # Create PLOAssessmentPlans
            assessment_count = self._create_assessment_plans(
                version, pi_map, course_map, parsed.get("assessment_plans", [])
            )

        # Print summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS(f"Seed NNTQ2025 complete!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"  Department:          1")
        self.stdout.write(f"  TrainingProgram:     1")
        self.stdout.write(f"  POs:                 {len(po_map)}")
        self.stdout.write(f"  PLOs:                {len(plo_map)}")
        self.stdout.write(f"  PO-PLO Mappings:     {mapping_count}")
        self.stdout.write(f"  KnowledgeBlocks:     {len(kb_map)}")
        self.stdout.write(f"  Courses:             {len(course_map)}")
        self.stdout.write(f"  ProgramCourses:      {len(pc_map)}")
        self.stdout.write(f"  Prerequisites:       {prereq_count}")
        self.stdout.write(f"  PIs:                 {len(pi_map)}")
        self.stdout.write(f"  CoursePLOContrib:    {contrib_count}")
        self.stdout.write(f"  AssessmentPlans:     {assessment_count}")

    # ─── Private helper methods ──────────────────────────────────────────────

    def _create_department(self):
        """Create or get the 'Khoa Ngoại ngữ' department."""
        dept, created = Department.objects.get_or_create(
            code="KHOA_NN",
            defaults={
                "name": "Khoa Ngoại ngữ",
                "name_en": "Faculty of Foreign Languages",
            },
        )
        action = "Created" if created else "Found existing"
        self.stdout.write(f"  {action} Department: {dept.name}")
        return dept

    def _create_program(self, department, general_info):
        """Create the TrainingProgram."""
        program = TrainingProgram.objects.create(
            program_code=PROGRAM_CODE,
            program_name_vi=general_info.get(
                "program_name_vi", "Ngôn ngữ Trung Quốc"
            ),
            program_name_en=general_info.get(
                "program_name_en", "Chinese Language"
            ),
            degree_name=general_info.get("degree_name", "Cử nhân"),
            education_level="DAI_HOC",
            managing_department=department,
            status=ProgramStatus.PUBLISHED,
        )
        self.stdout.write(f"  Created TrainingProgram: {program}")
        return program

    def _create_version(self, program, general_info=None):
        """Create a default TrainingProgramVersion for the program."""
        general_info = general_info or {}
        version = TrainingProgramVersion.objects.create(
            program=program,
            academic_year="2025-2026",
            status=VersionStatus.ACTIVE,
            total_credits=general_info.get("total_credits", 125),
            training_duration=general_info.get("training_duration", "4 năm"),
            general_objective=general_info.get("general_objective", ""),
            admission_requirements=general_info.get("admission_requirements", ""),
            graduation_requirements=general_info.get("graduation_requirements", ""),
            career_opportunities=general_info.get("career_opportunities", ""),
        )
        self.stdout.write(f"  Created TrainingProgramVersion: {version.academic_year}")
        return version

    def _create_pos(self, version):
        """Create ProgramObjective records. Returns {code: obj}."""
        po_map = {}
        for data in PO_DATA:
            po = ProgramObjective.objects.create(
                version=version,
                code=data["code"],
                description=data["description"],
                order_index=data["order_index"],
            )
            po_map[data["code"]] = po
        self.stdout.write(f"  Created {len(po_map)} POs")
        return po_map

    def _create_plos(self, version):
        """Create ProgramLearningOutcome records. Returns {code: obj}."""
        plo_map = {}
        for data in PLO_DATA:
            plo = ProgramLearningOutcome.objects.create(
                version=version,
                code=data["code"],
                description=data["description"],
                competency_level=data["competency_level"],
                competency_label=data.get("competency_label", ""),
                order_index=data["order_index"],
            )
            plo_map[data["code"]] = plo
        self.stdout.write(f"  Created {len(plo_map)} PLOs")
        return plo_map

    def _create_plo_po_mappings(self, po_map, plo_map):
        """Create PLOPOMapping records."""
        count = 0
        for plo_code, po_codes in PLO_PO_MAPPING.items():
            plo = plo_map.get(plo_code)
            if not plo:
                continue
            for po_code in po_codes:
                po = po_map.get(po_code)
                if not po:
                    continue
                PLOPOMapping.objects.create(plo=plo, po=po)
                count += 1
        self.stdout.write(f"  Created {count} PO-PLO mappings")
        return count

    def _create_knowledge_blocks(self, version, parsed_blocks):
        """Create KnowledgeBlock records with hierarchy. Returns {name: obj}."""
        kb_map = {}

        if not parsed_blocks:
            # Fallback: hardcode if parser did not extract
            self._create_hardcoded_knowledge_blocks(version, kb_map)
            return kb_map

        # Determine parent-child from indentation or naming pattern
        # The parser returns flat list; we infer hierarchy from naming
        current_parent = None
        for block_data in parsed_blocks:
            name = block_data["name"].strip()
            if not name:
                continue

            # Parent blocks typically have higher credit totals and no sub-prefix
            total_credits = block_data.get("total_credits", 0)
            required_credits = block_data.get("required_credits", 0)
            elective_credits = block_data.get("elective_credits", 0)

            # Detect parent blocks by checking if name starts with Roman numeral or has large credits
            is_parent = bool(re.match(r"^[IVX]+\.", name)) or total_credits >= 30

            if is_parent:
                kb = KnowledgeBlock(
                    version=version,
                    name=name,
                    parent=None,
                    required_credits=required_credits,
                    elective_credits=elective_credits,
                    order_index=block_data.get("order_index", 0),
                )
                kb.save()
                current_parent = kb
                kb_map[name] = kb
            else:
                kb = KnowledgeBlock(
                    version=version,
                    name=name,
                    parent=current_parent,
                    required_credits=required_credits,
                    elective_credits=elective_credits,
                    order_index=block_data.get("order_index", 0),
                )
                kb.save()
                kb_map[name] = kb

        self.stdout.write(f"  Created {len(kb_map)} KnowledgeBlocks")
        return kb_map

    def _create_hardcoded_knowledge_blocks(self, version, kb_map):
        """Fallback hardcoded knowledge blocks."""
        parent1 = KnowledgeBlock(
            version=version,
            name="Kiến thức giáo dục đại cương",
            required_credits=33,
            elective_credits=11,
            order_index=1,
        )
        parent1.save()
        kb_map[parent1.name] = parent1

        parent2 = KnowledgeBlock(
            version=version,
            name="Kiến thức giáo dục chuyên nghiệp",
            required_credits=63,
            elective_credits=18,
            order_index=2,
        )
        parent2.save()
        kb_map[parent2.name] = parent2

        self.stdout.write(f"  Created {len(kb_map)} KnowledgeBlocks (hardcoded fallback)")

    def _create_courses(self, department, parsed_courses):
        """Create Course records. Returns {code: obj}."""
        course_map = {}

        for c_data in parsed_courses:
            code = c_data.get("code", "").strip()
            if not code:
                continue
            # Skip header/summary rows
            if not re.match(r"^[A-Z]{2,5}\d{3,4}$", code):
                continue

            name_vi = c_data.get("name_vi", "").strip()
            if not name_vi:
                continue

            total_credits = c_data.get("total_credits", 0)
            theory_credits = c_data.get("theory_credits", 0)
            practice_credits = c_data.get("practice_credits", 0)

            # Ensure total = theory + practice (skip clean() validation)
            if theory_credits + practice_credits != total_credits:
                theory_credits = total_credits
                practice_credits = 0

            course, created = Course.objects.get_or_create(
                code=code,
                defaults={
                    "name_vi": name_vi,
                    "total_credits": total_credits,
                    "theory_credits": theory_credits,
                    "practice_credits": practice_credits,
                    "managing_department": department,
                },
            )
            course_map[code] = course

        self.stdout.write(f"  Created/found {len(course_map)} Courses")
        return course_map

    def _create_program_courses(self, version, course_map, kb_map, parsed_courses, semester_plan):
        """Create ProgramCourse records. Returns {course_code: pc_obj}."""
        pc_map = {}

        # Build a semester lookup from semester_plan data
        semester_lookup = {}
        for sp in semester_plan:
            course_code = sp.get("course_code", "").strip()
            if course_code:
                semester_lookup[course_code] = sp.get("semester_number")

        for c_data in parsed_courses:
            code = c_data.get("code", "").strip()
            course = course_map.get(code)
            if not course:
                continue

            # Get semester from semester_plan or parsed course data
            semester = semester_lookup.get(code) or c_data.get("semester") or None

            order_number = c_data.get("order_number", "")
            is_required = c_data.get("is_required", True)

            pc = ProgramCourse.objects.create(
                version=version,
                course=course,
                order_number=order_number,
                is_required=is_required,
                semester=semester,
            )
            pc_map[code] = pc

        self.stdout.write(f"  Created {len(pc_map)} ProgramCourses")
        return pc_map

    def _create_prerequisites(self, pc_map, course_map, parsed_courses):
        """Create CoursePrerequisite records from parsed course data."""
        count = 0

        for c_data in parsed_courses:
            code = c_data.get("code", "").strip()
            pc = pc_map.get(code)
            if not pc:
                continue

            # Check for prerequisite columns (index 6 = "Mã HP học trước",
            # but varies by document format)
            prereq_str = ""
            coreq_str = ""

            # Try to extract from common column positions
            raw_cells = c_data.get("raw_cells", [])
            if not raw_cells:
                # The parser doesn't store raw cells, so we look for extra fields
                continue

            # Parse prerequisite codes
            for prereq_code in re.findall(r"[A-Z]{2,5}\d{3,4}", prereq_str):
                prereq_course = course_map.get(prereq_code)
                if prereq_course:
                    CoursePrerequisite.objects.create(
                        program_course=pc,
                        prerequisite_course=prereq_course,
                        type=PrerequisiteType.PREREQUISITE,
                    )
                    count += 1

            for coreq_code in re.findall(r"[A-Z]{2,5}\d{3,4}", coreq_str):
                coreq_course = course_map.get(coreq_code)
                if coreq_course:
                    CoursePrerequisite.objects.create(
                        program_course=pc,
                        prerequisite_course=coreq_course,
                        type=PrerequisiteType.COREQUISITE,
                    )
                    count += 1

        if count > 0:
            self.stdout.write(f"  Created {count} CoursePrerequisites")
        else:
            self.stdout.write(
                self.style.WARNING("  No prerequisites extracted (parser may not capture this column)")
            )
        return count

    def _create_pis(self, plo_map):
        """Create PerformanceIndicator records. Returns {code: obj}."""
        pi_map = {}
        for data in PI_DATA:
            plo = plo_map.get(data["plo_code"])
            if not plo:
                continue
            pi = PerformanceIndicator.objects.create(
                plo=plo,
                code=data["code"],
                description=data["description"],
                order_index=data["order_index"],
            )
            pi_map[data["code"]] = pi
        self.stdout.write(f"  Created {len(pi_map)} PIs")
        return pi_map

    def _create_course_plo_contributions(self, pc_map, pi_map, course_plo_matrix):
        """Create CoursePLOContribution records from the parsed matrix."""
        count = 0
        for entry in course_plo_matrix:
            course_code = entry.get("course_code", "").strip()
            pi_code = entry.get("pi_code", "").strip()
            level = entry.get("contribution_level", 0)

            pc = pc_map.get(course_code)
            pi = pi_map.get(pi_code)

            if pc and pi and level > 0:
                CoursePLOContribution.objects.create(
                    program_course=pc,
                    pi=pi,
                    contribution_level=level,
                )
                count += 1

        self.stdout.write(f"  Created {count} CoursePLOContributions")
        return count

    def _create_assessment_plans(self, version, pi_map, course_map, parsed_plans):
        """Create PLOAssessmentPlan records."""
        count = 0
        for plan_data in parsed_plans:
            pi_code = plan_data.get("pi_code", "").strip()
            pi = pi_map.get(pi_code)
            if not pi:
                continue

            sample_course_code = plan_data.get("sample_course_code", "").strip()
            sample_course = course_map.get(sample_course_code)

            PLOAssessmentPlan.objects.create(
                version=version,
                pi=pi,
                contributing_courses_text=plan_data.get("contributing_courses_text", ""),
                sample_course=sample_course,
                direct_evidence=plan_data.get("direct_evidence", ""),
                assessment_tool=plan_data.get("assessment_tool", ""),
                expected_standard=plan_data.get("expected_standard", ""),
                assessment_schedule=plan_data.get("assessment_schedule", ""),
            )
            count += 1

        self.stdout.write(f"  Created {count} PLOAssessmentPlans")
        return count
