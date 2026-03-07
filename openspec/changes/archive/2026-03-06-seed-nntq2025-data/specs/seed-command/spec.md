## ADDED Requirements

### Requirement: Seed command creates complete NNTQ2025 program data

The system SHALL provide a Django management command `seed_nntq2025` that creates a complete TrainingProgram "Ngôn ngữ Trung Quốc" (NNTQ2025) with all related entities from the Word document.

#### Scenario: First-time seed creates all data

- **WHEN** user runs `python manage.py seed_nntq2025`
- **THEN** system creates 1 TrainingProgram (code="NNTQ2025"), 1 Department ("Khoa Ngoại ngữ"), 4 POs, 7 PLOs, PO-PLO mappings, KnowledgeBlocks, Courses, ProgramCourses, PIs, CoursePLOContributions, and PLOAssessmentPlans

#### Scenario: Command is idempotent - skips existing

- **WHEN** user runs `python manage.py seed_nntq2025` and NNTQ2025 already exists
- **THEN** system prints a message that program already exists and exits without changes

#### Scenario: Flush option deletes and recreates

- **WHEN** user runs `python manage.py seed_nntq2025 --flush`
- **THEN** system deletes existing NNTQ2025 program (cascade) and recreates all data from scratch

#### Scenario: Atomic transaction on failure

- **WHEN** seed command encounters an error during creation
- **THEN** system rolls back all changes (no partial data left in database)

### Requirement: Seed command creates correct program metadata

The system SHALL create the TrainingProgram with correct metadata extracted from the document.

#### Scenario: Program fields populated correctly

- **WHEN** seed command runs successfully
- **THEN** TrainingProgram has program_code="NNTQ2025", program_name_vi="Ngôn ngữ Trung Quốc", program_name_en="Chinese Language", education_level="DAI_HOC", total_credits=125, training_duration="4 năm", status="PUBLISHED"

### Requirement: Seed command creates PO and PLO data

The system SHALL create 4 POs and 7 PLOs with descriptions and PO-PLO mappings.

#### Scenario: POs created with correct descriptions

- **WHEN** seed command runs successfully
- **THEN** 4 ProgramObjective records exist: PO1 (Kiến thức), PO2 (Kỹ năng ngôn ngữ), PO3 (Kỹ năng chuyên ngành), PO4 (Kỹ năng mềm và thái độ)

#### Scenario: PLOs created with competency levels

- **WHEN** seed command runs successfully
- **THEN** 7 ProgramLearningOutcome records exist (PLO1-PLO7) with correct descriptions and competency_level values

#### Scenario: PO-PLO mappings created

- **WHEN** seed command runs successfully
- **THEN** PLOPOMapping records link each PLO to its corresponding POs as specified in the document

### Requirement: Seed command creates course structure

The system SHALL create courses, knowledge blocks, and program-course associations.

#### Scenario: Knowledge blocks created with hierarchy

- **WHEN** seed command runs successfully
- **THEN** KnowledgeBlock records exist for "Kiến thức giáo dục đại cương" (44 credits) and "Kiến thức giáo dục chuyên nghiệp" (81 credits) with child blocks

#### Scenario: Courses created with correct data

- **WHEN** seed command runs successfully
- **THEN** Course records exist with code, name_vi, total_credits for all courses in the program

#### Scenario: Courses assigned to semesters

- **WHEN** seed command runs successfully
- **THEN** ProgramCourse records link courses to the program with semester assignments (1-8)

### Requirement: Seed command outputs progress

The system SHALL print progress information during execution.

#### Scenario: Progress output shown

- **WHEN** seed command runs
- **THEN** system prints counts of created entities (e.g., "Created 4 POs, 7 PLOs, 60 Courses...")
