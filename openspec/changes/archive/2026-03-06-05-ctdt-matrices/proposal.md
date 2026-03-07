# Proposal: HP-PLO-PI Matrix & Assessment Plan

## Summary
Implement ma trận đóng góp của học phần vào PLO (thông qua PI), và kế hoạch đánh giá PLO — hai thành phần phức tạp nhất về mặt dữ liệu trong CTĐT.

## Models

### CoursePLOContribution (Ma trận HP-PLO-PI)
```python
class CoursePLOContribution(models.Model):
    program_course = ForeignKey(ProgramCourse, related_name='plo_contributions')
    pi = ForeignKey(PerformanceIndicator, related_name='course_contributions')
    contribution_level = PositiveIntegerField(default=0)  # 0=None, 1=Low, 2=Medium, 3=High

    class Meta:
        unique_together = ['program_course', 'pi']
```

### PLOAssessmentPlan (Kế hoạch đánh giá PLO)
```python
class PLOAssessmentPlan(UUIDModel, TimeStampedModel):
    program = ForeignKey(TrainingProgram, related_name='assessment_plans')
    pi = ForeignKey(PerformanceIndicator, related_name='assessment_plans')
    contributing_courses_text = TextField(blank=True)       # "POS104 POS105 POS106..."
    sample_course = ForeignKey(Course, null=True)           # HP lấy mẫu
    direct_evidence = CharField(max_length=200)             # "Chuyên cần", "Báo cáo cuối kỳ"
    assessment_tool = CharField(max_length=200)             # "Điểm chuyên cần", "Rubric"
    expected_standard = CharField(max_length=200)           # "Tối thiểu 70% người học đáp ứng"
    assessment_schedule = CharField(max_length=100)         # "HK1 / năm 3"
    responsible_lecturer = CharField(max_length=200, blank=True)
    managing_unit = CharField(max_length=200, blank=True)
```

## API Endpoints
```
# HP-PLO-PI Matrix
GET  /api/v1/programs/{id}/course-plo-matrix/
     Response: {rows: [{course_id, course_code, name, contributions: {pi_id: level}}]}
PUT  /api/v1/programs/{id}/course-plo-matrix/
     Body: [{program_course_id, pi_id, contribution_level}, ...]

# PLO Assessment Plan
GET    /api/v1/programs/{id}/assessment-plans/
POST   /api/v1/programs/{id}/assessment-plans/
PUT    /api/v1/programs/{id}/assessment-plans/{ap_id}/
DELETE /api/v1/programs/{id}/assessment-plans/{ap_id}/
POST   /api/v1/programs/{id}/assessment-plans/bulk/     # Bulk create/update
```

## Business Rules
1. Mỗi PLO phải có ít nhất 1 HP đóng góp (level > 0) — warning, not error
2. Ma trận dimensions: rows = ProgramCourse count, cols = total PIs across all PLOs
3. API phải hỗ trợ bulk update (ma trận lớn ~70x21 = 1470 cells)
4. Matrix read API returns pivot format for frontend rendering
