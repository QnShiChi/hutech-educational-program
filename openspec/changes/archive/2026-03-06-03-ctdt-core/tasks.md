# Tasks: 03 - CTĐT Core Module

## 1. Models

- [x] 1.1 Create TrainingProgram model with all fields from spec
- [x] 1.2 Create ProgramObjective model
- [x] 1.3 Create ProgramLearningOutcome model
- [x] 1.4 Create PLOPOMapping model
- [x] 1.5 Create PerformanceIndicator model
- [x] 1.6 Create KnowledgeBlock model (self-referencing tree)
- [x] 1.7 Run makemigrations + migrate
- [x] 1.8 Register in Django Admin with inline editing

## 2. Serializers

- [x] 2.1 TrainingProgramListSerializer (summary for list view)
- [x] 2.2 TrainingProgramDetailSerializer (full detail with nested POs, PLOs)
- [x] 2.3 TrainingProgramCreateUpdateSerializer (validation logic)
- [x] 2.4 ProgramObjectiveSerializer
- [x] 2.5 PLOSerializer (with PO mapping)
- [x] 2.6 PerformanceIndicatorSerializer
- [x] 2.7 KnowledgeBlockSerializer (tree)
- [x] 2.8 POPLOMatrixSerializer (bulk read/write)

## 3. ViewSets & APIs

- [x] 3.1 TrainingProgramViewSet (CRUD + filter/search)
- [x] 3.2 ProgramObjectiveViewSet (nested under program)
- [x] 3.3 PLOViewSet (nested under program, with reorder)
- [x] 3.4 POPLOMatrixView (GET/PUT for bulk matrix)
- [x] 3.5 PerformanceIndicatorViewSet (nested under PLO)
- [x] 3.6 KnowledgeBlockViewSet (nested under program, tree)
- [x] 3.7 Wire up URL routing in api_router.py

## 4. Business Logic

- [x] 4.1 Status validation: only edit in DRAFT/REVISION_REQUIRED
- [x] 4.2 Auto-calculate KnowledgeBlock totals
- [x] 4.3 Validate PLO-PO mapping (each PLO needs ≥1 PO)
- [x] 4.4 Sequential code validation (PO1, PO2... / PLO1, PLO2...)
- [x] 4.5 Department scope: apply DepartmentScopedPermission

## 5. Tests

- [x] 5.1 Factories for all models (factory_boy)
- [x] 5.2 Test TrainingProgram CRUD
- [x] 5.3 Test PO/PLO CRUD + reorder
- [x] 5.4 Test PO-PLO matrix bulk update
- [x] 5.5 Test PI CRUD
- [x] 5.6 Test KnowledgeBlock tree
- [x] 5.7 Test status-based edit restrictions
- [x] 5.8 Test department-scoped access
