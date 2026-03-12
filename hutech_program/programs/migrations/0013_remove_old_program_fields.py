"""Step 3: Remove migrated content fields from TrainingProgram (data already copied to versions)."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("programs", "0012_populate_version_content_fields"),
    ]

    operations = [
        migrations.RemoveField(model_name="trainingprogram", name="total_credits"),
        migrations.RemoveField(model_name="trainingprogram", name="training_duration"),
        migrations.RemoveField(model_name="trainingprogram", name="decision_number"),
        migrations.RemoveField(model_name="trainingprogram", name="decision_date"),
        migrations.RemoveField(model_name="trainingprogram", name="general_objective"),
        migrations.RemoveField(model_name="trainingprogram", name="admission_requirements"),
        migrations.RemoveField(model_name="trainingprogram", name="graduation_requirements"),
        migrations.RemoveField(model_name="trainingprogram", name="career_opportunities"),
        migrations.RemoveField(model_name="trainingprogram", name="further_education"),
        migrations.RemoveField(model_name="trainingprogram", name="teaching_methodology"),
        migrations.RemoveField(model_name="trainingprogram", name="assessment_methodology"),
        migrations.RemoveField(model_name="trainingprogram", name="implementation_guide"),
    ]
