# Proposal: Course Management (Quản lý Học phần)

## Summary
Quản lý danh mục học phần (Course) dùng chung cho nhiều CTĐT, và quản lý quan hệ học phần trong từng CTĐT cụ thể (ProgramCourse) bao gồm điều kiện tiên quyết, phân nhóm, kế hoạch giảng dạy.

## Models

### Course (Master — dùng chung nhiều CTĐT)
```python
class Course(UUIDModel, TimeStampedModel):
    code = CharField(max_length=20, unique=True)         # "POS104", "CHN107"
    name_vi = CharField(max_length=300)                  # "Triết học Mác - Lênin"
    name_en = CharField(max_length=300, blank=True)
    total_credits = PositiveIntegerField()               # 3
    theory_credits = PositiveIntegerField(default=0)
    practice_credits = PositiveIntegerField(default=0)
    project_credits = PositiveIntegerField(default=0)
    internship_credits = PositiveIntegerField(default=0)
    total_hours = PositiveIntegerField(null=True)
    theory_hours = PositiveIntegerField(default=0)
    practice_hours = PositiveIntegerField(default=0)
    managing_department = ForeignKey(Department)
    description = TextField(blank=True)                  # Mô tả tóm tắt (< 150 từ)
    course_group = ForeignKey('CourseGroup', null=True, blank=True)
    is_active = BooleanField(default=True)
```

### CourseGroup
```python
class CourseGroup(UUIDModel, TimeStampedModel):
    name = CharField(max_length=100, unique=True)        # "Kỹ thuật", "Kinh tế"
    description = TextField(blank=True)
```

### ProgramCourse (HP trong 1 CTĐT cụ thể)
```python
class ProgramCourse(UUIDModel, TimeStampedModel):
    program = ForeignKey(TrainingProgram, related_name='program_courses')
    course = ForeignKey(Course, related_name='program_courses')
    knowledge_block = ForeignKey(KnowledgeBlock)
    order_number = CharField(max_length=10)              # "I.01", "II.03"
    is_required = BooleanField(default=True)             # Bắt buộc / Tự chọn
    semester = PositiveIntegerField(null=True)            # HK khuyến nghị (1-8)
    batch = CharField(max_length=1, blank=True)          # "A" hoặc "B" phân đợt
    software_required = CharField(max_length=200, blank=True)
    notes = TextField(blank=True)

    class Meta:
        unique_together = ['program', 'course']
```

### CoursePrerequisite
```python
class PrerequisiteType(models.TextChoices):
    PREREQUISITE = "PREREQUISITE", "Học trước"
    COREQUISITE = "COREQUISITE", "Song hành"

class CoursePrerequisite(models.Model):
    program_course = ForeignKey(ProgramCourse, related_name='prerequisites')
    prerequisite_course = ForeignKey(Course)
    type = CharField(choices=PrerequisiteType)

    class Meta:
        unique_together = ['program_course', 'prerequisite_course']
```

### SemesterPlan
```python
class SemesterPlan(UUIDModel):
    program = ForeignKey(TrainingProgram, related_name='semester_plans')
    semester_number = PositiveIntegerField()              # 1-8
    program_course = ForeignKey(ProgramCourse)
    order_index = PositiveIntegerField()

    class Meta:
        unique_together = ['program', 'program_course']
        ordering = ['semester_number', 'order_index']
```

## API Endpoints
```
# Master Courses
GET/POST   /api/v1/courses/
GET/PUT/DEL /api/v1/courses/{id}/
GET        /api/v1/courses/{id}/programs/         # Which CTDTs use this course
GET/POST   /api/v1/course-groups/

# Program Courses (nested under CTDT)
GET/POST   /api/v1/programs/{id}/courses/
PUT/DEL    /api/v1/programs/{id}/courses/{pc_id}/
POST       /api/v1/programs/{id}/courses/bulk/    # Bulk add courses
GET/PUT    /api/v1/programs/{id}/prerequisites/    # All prerequisites

# Semester Plan
GET/PUT    /api/v1/programs/{id}/semester-plan/    # Full 8-semester plan
```

## Business Rules
1. Course.code must be unique globally
2. total_credits = theory + practice + project + internship
3. Prerequisite course must be in earlier semester than current
4. Cannot delete Course if used by any CTDT with status != DRAFT
5. When Course is edited → create notification for all related CTDTs
