# Step 1: Add new fields to Version + rename verbose_names on Program + add training_mode
# Does NOT remove any fields from Program (that happens in 0013 after data copy)

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programs', '0010_finalize_version_fk'),
        ('rbac', '0002_auditlog_permission_role_rolepermission_userrole_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='ploassessmentplan',
            name='programs_pl_program_609a0c_idx',
        ),
        migrations.RenameIndex(
            model_name='ploassessmentplan',
            new_name='programs_pl_version_1b3678_idx',
            old_name='programs_pl_version_idx_v2',
        ),
        # ── Add training_mode to TrainingProgram ──
        migrations.AddField(
            model_name='trainingprogram',
            name='training_mode',
            field=models.CharField(choices=[('CHINH_QUY', 'Chính quy'), ('TAI_CHUC', 'Tại chức'), ('TU_XA', 'Từ xa')], default='CHINH_QUY', max_length=20, verbose_name='Hình thức đào tạo'),
        ),
        # ── Add content fields to TrainingProgramVersion ──
        migrations.AddField(
            model_name='trainingprogramversion',
            name='admission_criteria',
            field=models.TextField(blank=True, verbose_name='Tiêu chí tuyển sinh'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='admission_requirements',
            field=models.TextField(blank=True, verbose_name='Chuẩn đầu vào'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='admission_target',
            field=models.TextField(blank=True, verbose_name='Đối tượng tuyển sinh'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='assessment_methodology',
            field=models.TextField(blank=True, verbose_name='Thang điểm đánh giá và cách thức đánh giá'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='career_opportunities',
            field=models.TextField(blank=True, verbose_name='Vị trí việc làm'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='decision_date',
            field=models.DateField(blank=True, null=True, verbose_name='Ngày quyết định'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='decision_number',
            field=models.CharField(blank=True, max_length=100, verbose_name='Số quyết định'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='description_update_period',
            field=models.TextField(blank=True, verbose_name='Thời gian cập nhật bản mô tả CTĐT'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='further_education',
            field=models.TextField(blank=True, verbose_name='Học tập nâng cao trình độ'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='general_objective',
            field=models.TextField(blank=True, verbose_name='Mục tiêu chung'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='graduation_requirements',
            field=models.TextField(blank=True, verbose_name='Điều kiện tốt nghiệp'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='implementation_guide',
            field=models.TextField(blank=True, verbose_name='Hướng dẫn thực hiện'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='reference_programs',
            field=models.TextField(blank=True, verbose_name='Chương trình tham khảo khi xây dựng'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='teaching_methodology',
            field=models.TextField(blank=True, verbose_name='Phương pháp giảng dạy'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='total_credits',
            field=models.PositiveIntegerField(default=0, verbose_name='Số tín chỉ'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='training_duration',
            field=models.CharField(default='4 năm', max_length=50, verbose_name='Thời gian đào tạo'),
        ),
        migrations.AddField(
            model_name='trainingprogramversion',
            name='training_process',
            field=models.TextField(blank=True, verbose_name='Quy trình đào tạo'),
        ),
        # ── Rename verbose_names on TrainingProgram ──
        migrations.AlterField(
            model_name='trainingprogram',
            name='degree_name',
            field=models.CharField(max_length=200, verbose_name='Tên gọi văn bằng'),
        ),
        migrations.AlterField(
            model_name='trainingprogram',
            name='issuing_institution',
            field=models.CharField(default='Trường Đại học Công nghệ TP.HCM', max_length=200, verbose_name='Trường cấp bằng'),
        ),
        migrations.AlterField(
            model_name='trainingprogram',
            name='managing_department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='training_programs', to='rbac.department', verbose_name='Đơn vị quản lý'),
        ),
        migrations.AlterField(
            model_name='trainingprogram',
            name='program_code',
            field=models.CharField(max_length=20, unique=True, verbose_name='Mã ngành'),
        ),
        migrations.AlterField(
            model_name='trainingprogram',
            name='program_name_en',
            field=models.CharField(blank=True, max_length=300, verbose_name='Tên ngành đào tạo (EN)'),
        ),
        migrations.AlterField(
            model_name='trainingprogram',
            name='program_name_vi',
            field=models.CharField(max_length=300, verbose_name='Tên ngành đào tạo (VN)'),
        ),
    ]
