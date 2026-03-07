# Spec: CTĐT Core

## Models

### TrainingProgram
```python
class ProgramStatus(models.TextChoices):
    DRAFT = "DRAFT", "Bản nháp"
    SUBMITTED = "SUBMITTED", "Đã nộp"
    KHOA_REVIEWING = "KHOA_REVIEWING", "Khoa đang xét duyệt"
    KHOA_APPROVED = "KHOA_APPROVED", "Khoa đã duyệt"
    PDT_REVIEWING = "PDT_REVIEWING", "Phòng ĐT đang xét duyệt"
    PDT_APPROVED = "PDT_APPROVED", "Phòng ĐT đã duyệt"
    BGH_REVIEWING = "BGH_REVIEWING", "BGH đang xét duyệt"
    PUBLISHED = "PUBLISHED", "Đã công bố"
    REVISION_REQUIRED = "REVISION_REQUIRED", "Cần chỉnh sửa"

class EducationLevel(models.TextChoices):
    DAI_HOC = "DAI_HOC", "Đại học"
    THAC_SI = "THAC_SI", "Thạc sĩ"
    TIEN_SI = "TIEN_SI", "Tiến sĩ"

class TrainingProgram(UUIDModel, TimeStampedModel):
    # Thông tin chung (Table 1 in sample file)
    program_name_vi = CharField(max_length=300)          # "Ngôn ngữ Trung Quốc"
    program_name_en = CharField(max_length=300, blank=True)  # "Chinese Language"
    program_code = CharField(max_length=20, unique=True)     # "7220204"
    degree_name = CharField(max_length=200)                  # "Cử nhân Ngôn ngữ Trung Quốc"
    education_level = CharField(choices=EducationLevel)
    managing_department = ForeignKey(Department)              # Khoa quản lý
    
    # Tín chỉ & thời gian
    total_credits = PositiveIntegerField()                   # 125
    training_duration = CharField(max_length=50)             # "4 năm"
    
    # Văn bản pháp lý
    decision_number = CharField(max_length=100, blank=True)
    decision_date = DateField(null=True, blank=True)
    issuing_institution = CharField(max_length=200, default="Trường Đại học Công nghệ TP.HCM")
    
    # Nội dung mô tả
    general_objective = TextField(blank=True)                # Mục tiêu chung
    admission_requirements = TextField(blank=True)
    graduation_requirements = TextField(blank=True)
    career_opportunities = TextField(blank=True)             # Vị trí việc làm
    further_education = TextField(blank=True)                # Khả năng học tập nâng cao
    teaching_methodology = TextField(blank=True)             # Phương pháp giảng dạy
    assessment_methodology = TextField(blank=True)           # Phương pháp đánh giá
    implementation_guide = TextField(blank=True)             # Hướng dẫn thực hiện
    
    # Status & versioning
    status = CharField(choices=ProgramStatus, default='DRAFT')
    version = PositiveIntegerField(default=1)
    
    # Tracking
    created_by = ForeignKey(User, related_name='created_programs')
    last_modified_by = ForeignKey(User, null=True, related_name='modified_programs')
```

### ProgramObjective (PO)
```python
class ProgramObjective(UUIDModel, TimeStampedModel):
    program = ForeignKey(TrainingProgram, related_name='objectives')
    code = CharField(max_length=10)            # "PO1", "PO2"
    description = TextField()                   # Full description
    order_index = PositiveIntegerField()
    
    class Meta:
        unique_together = ['program', 'code']
        ordering = ['order_index']
```

### ProgramLearningOutcome (PLO)
```python
class ProgramLearningOutcome(UUIDModel, TimeStampedModel):
    program = ForeignKey(TrainingProgram, related_name='plos')
    code = CharField(max_length=10)            # "PLO1", "PLO2"
    description = TextField()
    competency_level = DecimalField(max_digits=3, decimal_places=1)  # Bloom 0.0-6.0
    competency_label = CharField(max_length=50)   # "Thành thạo", "Đạt yêu cầu"
    order_index = PositiveIntegerField()
    
    # M2M with PO
    objectives = ManyToManyField(ProgramObjective, through='PLOPOMapping', blank=True)
    
    class Meta:
        unique_together = ['program', 'code']
        ordering = ['order_index']
```

### PLOPOMapping (Ma trận PO-PLO)
```python
class PLOPOMapping(models.Model):
    plo = ForeignKey(ProgramLearningOutcome, on_delete=CASCADE)
    po = ForeignKey(ProgramObjective, on_delete=CASCADE)
    
    class Meta:
        unique_together = ['plo', 'po']
```

### PerformanceIndicator (PI)
```python
class PerformanceIndicator(UUIDModel, TimeStampedModel):
    plo = ForeignKey(ProgramLearningOutcome, related_name='performance_indicators')
    code = CharField(max_length=20)            # "PI.1.1", "PI.1.2"
    description = TextField()
    order_index = PositiveIntegerField()
    
    class Meta:
        unique_together = ['plo', 'code']
        ordering = ['order_index']
```

### KnowledgeBlock (Khối kiến thức)
```python
class KnowledgeBlock(UUIDModel, TimeStampedModel):
    program = ForeignKey(TrainingProgram, related_name='knowledge_blocks')
    name = CharField(max_length=200)           # "Kiến thức giáo dục đại cương"
    parent = ForeignKey('self', null=True, blank=True, related_name='children')
    total_credits = PositiveIntegerField(default=0)
    required_credits = PositiveIntegerField(default=0)
    elective_credits = PositiveIntegerField(default=0)
    percentage = DecimalField(max_digits=5, decimal_places=1, null=True)  # "35.2%"
    order_index = PositiveIntegerField()
    
    class Meta:
        ordering = ['order_index']
```

## API Endpoints

```
# Training Programs
GET    /api/v1/programs/                             # List (filter: status, department, level)
POST   /api/v1/programs/                             # Create
GET    /api/v1/programs/{id}/                         # Detail (includes POs, PLOs summary)
PUT    /api/v1/programs/{id}/                         # Update
DELETE /api/v1/programs/{id}/                         # Soft delete (DRAFT only)

# Program Objectives (PO) - nested under program
GET    /api/v1/programs/{id}/objectives/              # List POs
POST   /api/v1/programs/{id}/objectives/              # Create PO
PUT    /api/v1/programs/{id}/objectives/{po_id}/      # Update PO
DELETE /api/v1/programs/{id}/objectives/{po_id}/      # Delete PO
POST   /api/v1/programs/{id}/objectives/reorder/      # Reorder POs

# Program Learning Outcomes (PLO) - nested under program
GET    /api/v1/programs/{id}/plos/                    # List PLOs
POST   /api/v1/programs/{id}/plos/                    # Create PLO
PUT    /api/v1/programs/{id}/plos/{plo_id}/           # Update PLO
DELETE /api/v1/programs/{id}/plos/{plo_id}/           # Delete PLO
POST   /api/v1/programs/{id}/plos/reorder/            # Reorder PLOs

# PO-PLO Matrix
GET    /api/v1/programs/{id}/po-plo-matrix/           # Get matrix
PUT    /api/v1/programs/{id}/po-plo-matrix/           # Bulk update matrix

# Performance Indicators (PI) - nested under PLO
GET    /api/v1/programs/{id}/plos/{plo_id}/pis/       # List PIs
POST   /api/v1/programs/{id}/plos/{plo_id}/pis/       # Create PI
PUT    /api/v1/programs/{id}/plos/{plo_id}/pis/{pi_id}/  # Update PI
DELETE /api/v1/programs/{id}/plos/{plo_id}/pis/{pi_id}/  # Delete PI

# Knowledge Blocks - nested under program
GET    /api/v1/programs/{id}/knowledge-blocks/        # List (tree)
POST   /api/v1/programs/{id}/knowledge-blocks/        # Create
PUT    /api/v1/programs/{id}/knowledge-blocks/{kb_id}/ # Update
DELETE /api/v1/programs/{id}/knowledge-blocks/{kb_id}/ # Delete
```

## Business Rules
1. TrainingProgram.program_code must be unique
2. PLO must reference at least 1 PO
3. PO/PLO codes must be sequential within a program (PO1, PO2... / PLO1, PLO2...)
4. competency_level must be between 0.0 and 6.0
5. KnowledgeBlock.total_credits = required_credits + elective_credits
6. Only DRAFT and REVISION_REQUIRED status allows editing
7. Delete only allowed for DRAFT status
