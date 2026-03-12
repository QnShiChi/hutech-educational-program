import uuid
from django.db import transaction

from hutech_program.programs.models import (
    CoursePLOContribution,
    TrainingProgramVersion,
    KnowledgeBlock,
    CourseGroup,
    ProgramCourse,
    ProgramObjective,
    ProgramLearningOutcome,
    PerformanceIndicator,
    PLOPOMapping,
    PLOAssessmentPlan,
    SemesterPlan,
    VersionStatus,
)


@transaction.atomic
def clone_program_version(source_version: TrainingProgramVersion, new_academic_year: str, user=None) -> TrainingProgramVersion:
    """
    Deep-clones a TrainingProgramVersion and its recursive structure for a new academic year.
    Returns the newly created TrainingProgramVersion in DRAFT state.

    Clones (in order):
    1. KnowledgeBlock tree
    2. CourseGroup
    3. ProgramCourse
    4. ProgramObjective (PO)
    5. ProgramLearningOutcome (PLO)
    6. PerformanceIndicator (PI)
    7. PLOPOMapping
    8. SemesterPlan
    9. CoursePLOContribution
    10. PLOAssessmentPlan
    """

    new_version = TrainingProgramVersion.objects.create(
        program=source_version.program,
        academic_year=new_academic_year,
        status=VersionStatus.DRAFT,
    )

    # ── 1. Clone KnowledgeBlocks (parents first) ──
    block_mapping = {}  # old_id -> new_knowledge_block_instance

    # Sort so that root blocks (parent=None) come first
    from django.db.models import F
    all_blocks = list(
        source_version.knowledge_blocks.all()
        .order_by(F('parent_id').asc(nulls_first=True))
    )

    for block in all_blocks:
        old_id = block.id
        new_parent = None
        if block.parent_id and block.parent_id in block_mapping:
            new_parent = block_mapping[block.parent_id]

        new_block = KnowledgeBlock.objects.create(
            version=new_version,
            name=block.name,
            parent=new_parent,
            required_credits=block.required_credits,
            elective_credits=block.elective_credits,
            order_index=block.order_index,
        )
        block_mapping[old_id] = new_block

    # ── 2. Clone CourseGroups ──
    group_mapping = {}  # old_id -> new_group_instance
    old_block_ids = list(block_mapping.keys())

    all_groups = CourseGroup.objects.filter(knowledge_block_id__in=old_block_ids)
    for group in all_groups:
        old_id = group.id
        group.pk = uuid.uuid4()
        if group.knowledge_block_id in block_mapping:
            group.knowledge_block = block_mapping[group.knowledge_block_id]
        group.save()
        group_mapping[old_id] = group

    # ── 3. Clone ProgramCourses ──
    pc_mapping = {}  # old_id -> new_program_course_instance
    all_program_courses = ProgramCourse.objects.filter(version=source_version)
    for pc in all_program_courses:
        old_id = pc.id
        pc.pk = uuid.uuid4()
        pc.version = new_version

        if pc.knowledge_block_id and pc.knowledge_block_id in block_mapping:
            pc.knowledge_block = block_mapping[pc.knowledge_block_id]

        if pc.course_group_id and pc.course_group_id in group_mapping:
            pc.course_group = group_mapping[pc.course_group_id]

        pc.save()
        pc_mapping[old_id] = pc

    # ── 4. Clone ProgramObjectives (PO) ──
    po_mapping = {}  # old_id -> new_po_instance
    all_pos = ProgramObjective.objects.filter(version=source_version).order_by('order_index')
    for po in all_pos:
        old_id = po.id
        po.pk = uuid.uuid4()
        po.version = new_version
        po.program = None  # legacy field
        po.save()
        po_mapping[old_id] = po

    # ── 5. Clone ProgramLearningOutcomes (PLO) ──
    plo_mapping = {}  # old_id -> new_plo_instance
    all_plos = ProgramLearningOutcome.objects.filter(version=source_version).order_by('order_index')
    for plo in all_plos:
        old_id = plo.id
        plo.pk = uuid.uuid4()
        plo.version = new_version
        plo.program = None  # legacy field
        plo.save()
        plo_mapping[old_id] = plo

    # ── 6. Clone PerformanceIndicators (PI) ──
    pi_mapping = {}  # old_id -> new_pi_instance
    old_plo_ids = list(plo_mapping.keys())
    all_pis = PerformanceIndicator.objects.filter(plo_id__in=old_plo_ids).order_by('order_index')
    for pi in all_pis:
        old_id = pi.id
        pi.pk = uuid.uuid4()
        if pi.plo_id in plo_mapping:
            pi.plo = plo_mapping[pi.plo_id]
        pi.save()
        pi_mapping[old_id] = pi

    # ── 7. Clone PLOPOMappings ──
    all_mappings = PLOPOMapping.objects.filter(plo_id__in=old_plo_ids)
    for mapping in all_mappings:
        mapping.pk = None  # auto-increment
        if mapping.plo_id in plo_mapping:
            mapping.plo = plo_mapping[mapping.plo_id]
        if mapping.po_id in po_mapping:
            mapping.po = po_mapping[mapping.po_id]
        mapping.save()

    # ── 8. Clone SemesterPlans ──
    all_semester_plans = SemesterPlan.objects.filter(version=source_version)
    for sp in all_semester_plans:
        sp.pk = uuid.uuid4()
        sp.version = new_version
        sp.program = None  # legacy

        if sp.program_course_id and sp.program_course_id in pc_mapping:
            sp.program_course = pc_mapping[sp.program_course_id]

        sp.save()

    # ── 9. Clone CoursePLOContributions ──
    old_pc_ids = list(pc_mapping.keys())
    all_contributions = CoursePLOContribution.objects.filter(program_course_id__in=old_pc_ids)
    for contrib in all_contributions:
        contrib.pk = uuid.uuid4()
        if contrib.program_course_id in pc_mapping:
            contrib.program_course = pc_mapping[contrib.program_course_id]
        if contrib.pi_id in pi_mapping:
            contrib.pi = pi_mapping[contrib.pi_id]
        contrib.save()

    # ── 10. Clone PLOAssessmentPlans ──
    all_plans = PLOAssessmentPlan.objects.filter(version=source_version)
    for plan in all_plans:
        plan.pk = uuid.uuid4()
        plan.version = new_version
        plan.program = None  # legacy

        if plan.pi_id and plan.pi_id in pi_mapping:
            plan.pi = pi_mapping[plan.pi_id]

        plan.save()

    return new_version
