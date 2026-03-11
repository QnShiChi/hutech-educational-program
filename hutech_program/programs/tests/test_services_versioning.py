import pytest
from hutech_program.programs.models import (
    TrainingProgram,
    TrainingProgramVersion,
    KnowledgeBlock,
    CourseGroup,
    Course,
    ProgramCourse,
    VersionStatus,
)
from hutech_program.programs.services.versioning import clone_program_version
from hutech_program.users.models import User

pytestmark = pytest.mark.django_db

def test_clone_program_version():
    user = User.objects.create(username="testuser")
    
    # 1. Setup Source Data
    program = TrainingProgram.objects.create(
        program_code="TEST01",
        program_name_vi="Chương trình Test",
        managing_department_id=1,  # Assuming a department exists
        total_credits=120
    )
    
    source_version = TrainingProgramVersion.objects.create(
        program=program,
        academic_year="2024-2025",
        status=VersionStatus.ACTIVE
    )
    
    # Knowledge Blocks
    kb_parent = KnowledgeBlock.objects.create(
        version=source_version,
        name="Khối kiến thức chung",
    )
    
    kb_child = KnowledgeBlock.objects.create(
        version=source_version,
        parent=kb_parent,
        name="Lý luận chính trị",
    )
    
    # Course Group
    cg = CourseGroup.objects.create(
        knowledge_block=kb_child,
        name="Nhóm tự chọn LLCT"
    )
    
    # Course
    course = Course.objects.create(
        code="CS01",
        name_vi="Cơ sở lập trình",
        total_credits=3,
        managing_department_id=1
    )
    
    # Program Course
    pc = ProgramCourse.objects.create(
        version=source_version,
        course=course,
        knowledge_block=kb_child,
        course_group=cg
    )
    
    # 2. Clone it
    new_version = clone_program_version(source_version, "2025-2026", user)
    
    # 3. Assertions
    assert new_version.academic_year == "2025-2026"
    assert new_version.status == VersionStatus.DRAFT
    
    # Validate KB cloning
    new_kbs = KnowledgeBlock.objects.filter(version=new_version)
    assert new_kbs.count() == 2
    
    new_parent = new_kbs.get(name="Khối kiến thức chung")
    new_child = new_kbs.get(name="Lý luận chính trị")
    assert new_child.parent == new_parent
    
    # Validate CG cloning
    new_cgs = CourseGroup.objects.filter(knowledge_block__version=new_version)
    assert new_cgs.count() == 1
    new_cg = new_cgs.first()
    assert new_cg.knowledge_block == new_child
    
    # Validate PC cloning
    new_pcs = ProgramCourse.objects.filter(version=new_version)
    assert new_pcs.count() == 1
    new_pc = new_pcs.first()
    assert new_pc.knowledge_block == new_child
    assert new_pc.course_group == new_cg
    assert new_pc.course == course  # Course isn't cloned, just ref'd
