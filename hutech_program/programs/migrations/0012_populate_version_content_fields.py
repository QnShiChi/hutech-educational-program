"""Copy content fields from TrainingProgram to all linked TrainingProgramVersion records."""
from django.db import migrations


FIELDS_TO_COPY = [
    "total_credits",
    "training_duration",
    "decision_number",
    "decision_date",
    "general_objective",
    "admission_requirements",
    "graduation_requirements",
    "career_opportunities",
    "further_education",
    "teaching_methodology",
    "assessment_methodology",
    "implementation_guide",
]


def copy_fields_to_versions(apps, schema_editor):
    TrainingProgram = apps.get_model("programs", "TrainingProgram")
    TrainingProgramVersion = apps.get_model("programs", "TrainingProgramVersion")

    for program in TrainingProgram.objects.all():
        versions = TrainingProgramVersion.objects.filter(program=program)

        if not versions.exists():
            version = TrainingProgramVersion.objects.create(
                program=program,
                academic_year="default",
                status="DRAFT",
            )
            versions = TrainingProgramVersion.objects.filter(pk=version.pk)

        update_kwargs = {}
        for field in FIELDS_TO_COPY:
            value = getattr(program, field, None)
            if value is not None:
                update_kwargs[field] = value

        if update_kwargs:
            versions.update(**update_kwargs)


def reverse_copy(apps, schema_editor):
    TrainingProgram = apps.get_model("programs", "TrainingProgram")
    TrainingProgramVersion = apps.get_model("programs", "TrainingProgramVersion")

    for program in TrainingProgram.objects.all():
        version = TrainingProgramVersion.objects.filter(program=program).first()
        if version:
            for field in FIELDS_TO_COPY:
                setattr(program, field, getattr(version, field, None))
            program.save()


class Migration(migrations.Migration):

    dependencies = [
        ("programs", "0011_move_fields_to_version"),
    ]

    operations = [
        migrations.RunPython(copy_fields_to_versions, reverse_copy),
    ]
