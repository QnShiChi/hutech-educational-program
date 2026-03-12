# Data migration: populate version FK for PO, PLO, PLOAssessmentPlan

from django.db import migrations


def populate_version_fk(apps, schema_editor):
    """
    For each PO/PLO/PLOAssessmentPlan, find its program's first version
    and set the version FK. If no version exists, create a default one.
    """
    TrainingProgram = apps.get_model('programs', 'TrainingProgram')
    TrainingProgramVersion = apps.get_model('programs', 'TrainingProgramVersion')
    ProgramObjective = apps.get_model('programs', 'ProgramObjective')
    ProgramLearningOutcome = apps.get_model('programs', 'ProgramLearningOutcome')
    PLOAssessmentPlan = apps.get_model('programs', 'PLOAssessmentPlan')

    # Build a cache of program_id -> first version
    version_cache = {}

    for program in TrainingProgram.objects.all():
        first_version = TrainingProgramVersion.objects.filter(
            program=program
        ).order_by('academic_year').first()

        if not first_version:
            # Create a default version for orphan programs
            first_version = TrainingProgramVersion.objects.create(
                program=program,
                academic_year='default',
                status='DRAFT',
            )

        version_cache[program.id] = first_version

    # Update ProgramObjective
    for obj in ProgramObjective.objects.filter(version__isnull=True).select_related('program'):
        if obj.program_id and obj.program_id in version_cache:
            obj.version = version_cache[obj.program_id]
            obj.save(update_fields=['version'])

    # Update ProgramLearningOutcome
    for plo in ProgramLearningOutcome.objects.filter(version__isnull=True).select_related('program'):
        if plo.program_id and plo.program_id in version_cache:
            plo.version = version_cache[plo.program_id]
            plo.save(update_fields=['version'])

    # Update PLOAssessmentPlan
    for plan in PLOAssessmentPlan.objects.filter(version__isnull=True).select_related('program'):
        if plan.program_id and plan.program_id in version_cache:
            plan.version = version_cache[plan.program_id]
            plan.save(update_fields=['version'])


def reverse_populate(apps, schema_editor):
    """Reverse: nothing to undo since we're just populating a new field."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('programs', '0008_add_version_to_po_plo_assessment'),
    ]

    operations = [
        migrations.RunPython(populate_version_fk, reverse_populate),
    ]
