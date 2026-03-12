# Finalize: make version FK non-null, rename program FK to legacy

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programs', '0009_populate_version_for_po_plo_assessment'),
    ]

    operations = [
        # ── ProgramObjective: finalize ──
        # Make version non-null
        migrations.AlterField(
            model_name='programobjective',
            name='version',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='objectives',
                to='programs.trainingprogramversion',
                verbose_name='Phiên bản CTĐT',
            ),
        ),
        # Make program legacy (nullable, SET_NULL)
        migrations.AlterField(
            model_name='programobjective',
            name='program',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='objectives_legacy',
                to='programs.trainingprogram',
                verbose_name='Chương trình (Legacy)',
            ),
        ),
        # New unique_together
        migrations.AlterUniqueTogether(
            name='programobjective',
            unique_together={('version', 'code')},
        ),

        # ── ProgramLearningOutcome: finalize ──
        migrations.AlterField(
            model_name='programlearningoutcome',
            name='version',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='plos',
                to='programs.trainingprogramversion',
                verbose_name='Phiên bản CTĐT',
            ),
        ),
        migrations.AlterField(
            model_name='programlearningoutcome',
            name='program',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='plos_legacy',
                to='programs.trainingprogram',
                verbose_name='Chương trình (Legacy)',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='programlearningoutcome',
            unique_together={('version', 'code')},
        ),

        # ── PLOAssessmentPlan: finalize ──
        migrations.AlterField(
            model_name='ploassessmentplan',
            name='version',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='assessment_plans',
                to='programs.trainingprogramversion',
                verbose_name='Phiên bản CTĐT',
            ),
        ),
        migrations.AlterField(
            model_name='ploassessmentplan',
            name='program',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assessment_plans_legacy',
                to='programs.trainingprogram',
                verbose_name='Chương trình (Legacy)',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='ploassessmentplan',
            unique_together={('version', 'pi')},
        ),

        # ── Update indexes for PLOAssessmentPlan ──
        migrations.AddIndex(
            model_name='ploassessmentplan',
            index=models.Index(fields=['version'], name='programs_pl_version_idx_v2'),
        ),
    ]
