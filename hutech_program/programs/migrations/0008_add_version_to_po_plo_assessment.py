# Generated manually for version-po-plo-pi change

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programs', '0007_make_course_semester_plan_version_aware'),
    ]

    operations = [
        # ── ProgramObjective ──
        migrations.AlterUniqueTogether(
            name='programobjective',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='programobjective',
            name='version',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='objectives',
                to='programs.trainingprogramversion',
                verbose_name='Phiên bản CTĐT',
            ),
        ),

        # ── ProgramLearningOutcome ──
        migrations.AlterUniqueTogether(
            name='programlearningoutcome',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='programlearningoutcome',
            name='version',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='plos',
                to='programs.trainingprogramversion',
                verbose_name='Phiên bản CTĐT',
            ),
        ),

        # ── PLOAssessmentPlan ──
        migrations.AddField(
            model_name='ploassessmentplan',
            name='version',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='assessment_plans',
                to='programs.trainingprogramversion',
                verbose_name='Phiên bản CTĐT',
            ),
        ),
    ]
