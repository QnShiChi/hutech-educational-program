import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def admin_user(db):
    user = User.objects.create_superuser("admin", "admin@example.com", "password")
    return user

@pytest.fixture
def setup_data(db, admin_user):
    from .factories import TrainingProgramFactory, KnowledgeBlockFactory, CourseGroupFactory
    
    tp = TrainingProgramFactory(status="DRAFT")
    kb1 = KnowledgeBlockFactory(program=tp, name="KB 1")
    kb2 = KnowledgeBlockFactory(program=tp, name="KB 2")
    
    cg1 = CourseGroupFactory(knowledge_block=kb1, name="CG 1")
    cg2 = CourseGroupFactory(knowledge_block=kb1, name="CG 2")
    cg3 = CourseGroupFactory(knowledge_block=kb2, name="CG 3")
    
    return {
        "admin_user": admin_user,
        "kb1": kb1,
        "kb2": kb2,
        "cg1": cg1,
        "cg2": cg2,
        "cg3": cg3,
    }

@pytest.mark.django_db
class TestProgramCourseAdmin:
    def test_get_course_groups(self, client, setup_data):
        client.force_login(setup_data["admin_user"])
        
        # Test KB1
        url = reverse("admin:programs_programcourse_get_course_groups")
        response = client.get(url, {"kb_id": setup_data["kb1"].id})
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
        names = [item["name"] for item in data["results"]]
        assert "CG 1" in names
        assert "CG 2" in names
        
        # Test KB2
        response = client.get(url, {"kb_id": setup_data["kb2"].id})
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "CG 3"
        
        # Test missing kb_id
        response = client.get(url)
        data = response.json()
        assert data["results"] == []
