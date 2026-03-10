import pytest
from django.urls import reverse
from hutech_program.programs.models import ProgramObjective, ProgramStatus
from hutech_program.programs.tests.factories import TrainingProgramFactory

pytestmark = pytest.mark.django_db

def test_admin_training_program_context_set(admin_client, admin_user):
    """Test that visiting a Training Program's change view sets the context in session."""
    program = TrainingProgramFactory(
        program_code="TEST-001",
        program_name_vi="Test Program",
        status=ProgramStatus.DRAFT,
        education_level="DAI_HOC",
    )
    
    url = reverse("admin:programs_trainingprogram_change", args=[program.id])
    response = admin_client.get(url)
    
    assert response.status_code == 200
    assert admin_client.session.get("active_program_id") == str(program.id)
    assert response.context_data["active_program"] == program

def test_admin_po_changelist_filters_by_context(admin_client, admin_user):
    """Test that POs list is filtered by active program context."""
    p1 = TrainingProgramFactory(program_code="P1", status=ProgramStatus.DRAFT)
    p2 = TrainingProgramFactory(program_code="P2", status=ProgramStatus.DRAFT)
    
    po1 = ProgramObjective.objects.create(code="PO1", program=p1, description="Desc")
    po2 = ProgramObjective.objects.create(code="PO2", program=p2, description="Desc")
    
    # Set context
    admin_client.get(reverse("admin:programs_trainingprogram_change", args=[p1.id]))
    
    url = reverse("admin:programs_programobjective_changelist")
    response = admin_client.get(url)
    
    assert response.status_code == 200
    # The active program should be p1
    assert response.context_data["active_program"] == p1
    
    # The queryset should only contain po1
    cl = response.context_data["cl"]
    qs = cl.queryset
    assert po1 in qs
    assert po2 not in qs

def test_admin_po_readonly_when_parent_locked(admin_client, admin_user):
    """Test that child forms are read-only when parent is locked."""
    # Create locked program
    p1 = TrainingProgramFactory(program_code="P1", status="KHOA_APPROVED")
    po1 = ProgramObjective.objects.create(code="PO1", program=p1, description="Desc")
    
    # Set context
    admin_client.get(reverse("admin:programs_trainingprogram_change", args=[p1.id]))
    
    # Try to GET the change form - should be 200
    url = reverse("admin:programs_programobjective_change", args=[po1.id])
    response = admin_client.get(url)
    assert response.status_code == 200
    
    # Try to POST a change - should be forbidden because has_change_permission is False
    data = {"code": "PO1-MOD", "description": "Mod", "program": p1.id}
    post_response = admin_client.post(url, data)
    assert post_response.status_code == 403

def test_admin_po_editable_when_parent_draft(admin_client, admin_user):
    """Test that child forms are editable when parent is draft."""
    p1 = TrainingProgramFactory(program_code="P1", status=ProgramStatus.DRAFT)
    po1 = ProgramObjective.objects.create(code="PO1", program=p1, description="Desc")
    
    # Set context
    admin_client.get(reverse("admin:programs_trainingprogram_change", args=[p1.id]))
    
    url = reverse("admin:programs_programobjective_change", args=[po1.id])
    data = {"code": "PO1-MOD", "description": "Mod", "program": p1.id, "order_index": 1}
    post_response = admin_client.post(url, data)
    
    # Should redirect indicating success
    assert post_response.status_code == 302
    
    po1.refresh_from_db()
    assert po1.code == "PO1-MOD"
