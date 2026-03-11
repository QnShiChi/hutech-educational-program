import uuid
from django.db import transaction

from hutech_program.programs.models import (
    TrainingProgramVersion,
    KnowledgeBlock,
    CourseGroup,
    ProgramCourse,
    VersionStatus,
)


@transaction.atomic
def clone_program_version(source_version: TrainingProgramVersion, new_academic_year: str, user=None) -> TrainingProgramVersion:
    """
    Deep-clones a TrainingProgramVersion and its recursive structure for a new academic year.
    Returns the newly created TrainingProgramVersion in DRAFT state.
    """
    
    new_version = TrainingProgramVersion.objects.create(
        program=source_version.program,
        academic_year=new_academic_year,
        status=VersionStatus.DRAFT,
        created_by=user,
        last_modified_by=user,
    )

    # First, clone all knowledge blocks (top-level first to maintain hierarchy)
    block_mapping = {}  # old_id -> new_knowledge_block_instance
    
    # Needs to sort by parent_id logically so parents are cloned first
    # In django, using related queries or recursive approach is possible. 
    # Since tree depth is usually small (1-2), a simple pass works.
    all_blocks = list(source_version.knowledge_blocks.all().order_by('parent_id'))
    
    for block in all_blocks:
        old_id = block.id
        # clone object
        block.pk = uuid.uuid4()
        block.version = new_version
        # setup new parent logic
        if block.parent_id and block.parent_id in block_mapping:
            block.parent = block_mapping[block.parent_id]
        elif block.parent_id:
            # edge case logic for out of order processing. 
            pass 
        block.save()
        block_mapping[old_id] = block
        
    # Then clone Course Groups
    group_mapping = {} # old_id -> new_group_instance
    old_blocks_ids = list(block_mapping.keys())
    
    all_groups = CourseGroup.objects.filter(knowledge_block_id__in=old_blocks_ids)
    for group in all_groups:
        old_id = group.id
        group.pk = uuid.uuid4()
        if group.knowledge_block_id in block_mapping:
            group.knowledge_block = block_mapping[group.knowledge_block_id]
        group.save()
        group_mapping[old_id] = group
        
    # Clone Program Courses
    all_program_courses = ProgramCourse.objects.filter(version=source_version)
    for pc in all_program_courses:
        pc.pk = uuid.uuid4()
        pc.version = new_version
        
        if pc.knowledge_block_id and pc.knowledge_block_id in block_mapping:
            pc.knowledge_block = block_mapping[pc.knowledge_block_id]
            
        if pc.course_group_id and pc.course_group_id in group_mapping:
            pc.course_group = group_mapping[pc.course_group_id]
            
        pc.save()

    return new_version
