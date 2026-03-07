"""
Celery tasks for async Word file import.
"""

import logging
import tempfile

from celery import shared_task
from django.db import transaction

from .models import ImportStatus, ImportTask
from .parser import DocxParser

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=1)
def import_training_program_task(self, task_id):
    """
    Async task to parse a .docx file and store parsed data for preview.
    Steps: upload → parse → store preview → wait for confirm.
    """
    try:
        import_task = ImportTask.objects.get(id=task_id)
    except ImportTask.DoesNotExist:
        logger.error(f"ImportTask {task_id} not found")
        return

    try:
        import_task.status = ImportStatus.PROCESSING
        import_task.progress = 10
        import_task.save(update_fields=["status", "progress"])

        # Parse the uploaded file
        parser = DocxParser(import_task.file.path)
        parsed_data = parser.parse_all()

        import_task.progress = 80
        import_task.parsed_data = parsed_data
        import_task.status = ImportStatus.PREVIEW
        import_task.progress = 100
        import_task.result = {
            "warnings": parser.warnings,
            "errors": parser.errors,
            "summary": {
                "plos": len(parsed_data.get("plos", [])),
                "courses": len(parsed_data.get("courses", [])),
                "knowledge_blocks": len(parsed_data.get("knowledge_blocks", [])),
                "course_plo_matrix": len(parsed_data.get("course_plo_matrix", [])),
                "assessment_plans": len(parsed_data.get("assessment_plans", [])),
            },
        }
        import_task.save()

    except Exception as e:
        import_task.status = ImportStatus.FAILED
        import_task.error_message = str(e)
        import_task.save(update_fields=["status", "error_message"])
        logger.exception(f"Import task {task_id} failed")


@shared_task
def confirm_import_task(task_id):
    """
    Confirm and save parsed data to database.
    """
    try:
        import_task = ImportTask.objects.get(id=task_id)
    except ImportTask.DoesNotExist:
        logger.error(f"ImportTask {task_id} not found")
        return

    if import_task.status != ImportStatus.PREVIEW:
        logger.error(f"ImportTask {task_id} not in PREVIEW status")
        return

    try:
        import_task.status = ImportStatus.PROCESSING
        import_task.save(update_fields=["status"])

        program = _save_parsed_data(import_task)

        import_task.program = program
        import_task.status = ImportStatus.COMPLETED
        import_task.result = {
            **(import_task.result or {}),
            "program_id": str(program.id),
        }
        import_task.save()

    except Exception as e:
        import_task.status = ImportStatus.FAILED
        import_task.error_message = str(e)
        import_task.save(update_fields=["status", "error_message"])
        logger.exception(f"Confirm import {task_id} failed")


@transaction.atomic
def _save_parsed_data(import_task):
    """Save parsed data to create TrainingProgram and related entities."""
    from hutech_program.programs.models import (
        Course,
        CoursePLOContribution,
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

    data = import_task.parsed_data
    general = data.get("general_info", {})

    # Create TrainingProgram
    program = TrainingProgram.objects.create(
        program_code=general.get("program_code", f"IMPORT-{import_task.id}"[:20]),
        program_name_vi=general.get("program_name_vi", "Imported Program"),
        program_name_en=general.get("program_name_en", ""),
        degree_name=general.get("degree_name", ""),
        total_credits=general.get("total_credits", 0),
        training_duration=general.get("training_duration", "4 năm"),
        decision_number=general.get("decision_number", ""),
        general_objective=general.get("general_objective", ""),
        admission_requirements=general.get("admission_requirements", ""),
        graduation_requirements=general.get("graduation_requirements", ""),
        career_opportunities=general.get("career_opportunities", ""),
        managing_department=import_task.department,
        created_by=import_task.uploaded_by,
    )

    # PLOs
    plo_map = {}
    for plo_data in data.get("plos", []):
        plo = ProgramLearningOutcome.objects.create(
            program=program,
            code=plo_data["code"],
            description=plo_data.get("description", ""),
            order_index=plo_data.get("order_index", 0),
        )
        plo_map[plo.code] = plo

    # PO-PLO mappings — create POs on the fly if referenced
    po_map = {}
    for mapping_data in data.get("po_plo_matrix", []):
        plo_code = mapping_data.get("plo_code", "")
        po_code = mapping_data.get("po_code", "")
        plo = plo_map.get(plo_code)
        if not plo or not po_code:
            continue
        if po_code not in po_map:
            po, _ = ProgramObjective.objects.get_or_create(
                program=program,
                code=po_code,
                defaults={"description": po_code, "order_index": len(po_map)},
            )
            po_map[po_code] = po
        PLOPOMapping.objects.get_or_create(
            plo=plo,
            po=po_map[po_code],
        )

    # Knowledge blocks
    for kb_data in data.get("knowledge_blocks", []):
        KnowledgeBlock.objects.create(
            program=program,
            name=kb_data["name"],
            required_credits=kb_data.get("required_credits", 0),
            elective_credits=kb_data.get("elective_credits", 0),
            order_index=kb_data.get("order_index", 0),
        )

    # Courses
    course_map = {}
    for c_data in data.get("courses", []):
        code = c_data.get("code", "")
        if not code:
            continue

        course, _ = Course.objects.get_or_create(
            code=code,
            defaults={
                "name_vi": c_data.get("name_vi", code),
                "total_credits": c_data.get("total_credits", 0),
                "theory_credits": c_data.get("theory_credits", 0),
                "practice_credits": c_data.get("practice_credits", 0),
                "managing_department": import_task.department,
            },
        )
        pc = ProgramCourse.objects.create(
            program=program,
            course=course,
            order_number=c_data.get("order_number", ""),
            is_required=c_data.get("is_required", True),
            semester=c_data.get("semester") or None,
        )
        course_map[code] = pc

    # Course descriptions
    for desc in data.get("course_descriptions", []):
        code = desc.get("code", "")
        try:
            course = Course.objects.get(code=code)
            course.description = desc.get("description", "")
            course.save(update_fields=["description"])
        except Course.DoesNotExist:
            pass

    # Performance indicators
    pi_map = {}
    for pi_data in data.get("performance_indicators", []):
        plo_code = pi_data.get("plo_code", "")
        plo = plo_map.get(plo_code)
        if not plo:
            continue
        pi = PerformanceIndicator.objects.create(
            plo=plo,
            code=pi_data["code"],
            description=pi_data.get("description", ""),
            order_index=pi_data.get("order_index", 0),
        )
        pi_map[pi.code] = pi

    # Course-PLO contributions
    for contrib_data in data.get("course_plo_matrix", []):
        course_code = contrib_data.get("course_code", "")
        pi_code = contrib_data.get("pi_code", "")
        pc = course_map.get(course_code)
        pi = pi_map.get(pi_code)
        if not pc or not pi:
            continue
        CoursePLOContribution.objects.get_or_create(
            program_course=pc,
            pi=pi,
            defaults={"contribution_level": contrib_data.get("contribution_level", 1)},
        )

    # Semester plans
    for sp_data in data.get("semester_plan", []):
        course_code = sp_data.get("course_code", "")
        pc = course_map.get(course_code)
        if not pc:
            continue
        SemesterPlan.objects.get_or_create(
            program=program,
            program_course=pc,
            defaults={
                "semester_number": sp_data.get("semester_number", 1),
                "order_index": sp_data.get("order_index", 0),
            },
        )

    # Assessment plans
    for ap_data in data.get("assessment_plans", []):
        pi_code = ap_data.get("pi_code", "")
        pi = pi_map.get(pi_code)
        if not pi:
            continue
        sample_course = None
        sample_code = ap_data.get("sample_course_code", "")
        if sample_code:
            sample_course = Course.objects.filter(code=sample_code).first()

        PLOAssessmentPlan.objects.create(
            program=program,
            pi=pi,
            contributing_courses_text=ap_data.get("contributing_courses_text", ""),
            sample_course=sample_course,
            direct_evidence=ap_data.get("direct_evidence", ""),
            assessment_tool=ap_data.get("assessment_tool", ""),
            expected_standard=ap_data.get("expected_standard", ""),
            assessment_schedule=ap_data.get("assessment_schedule", ""),
        )

    return program
