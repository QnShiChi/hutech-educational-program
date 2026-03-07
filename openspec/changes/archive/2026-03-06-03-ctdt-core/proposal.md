# Proposal: CTĐT Core Module

## Summary
Xây dựng models, API cho quản lý Chương trình đào tạo — bao gồm thông tin chung, mục tiêu đào tạo (PO), chuẩn đầu ra (PLO), chỉ số đo lường (PI), và khối kiến thức.

## What's Changing
- Models: TrainingProgram, ProgramObjective, ProgramLearningOutcome, PerformanceIndicator, KnowledgeBlock
- CRUD APIs cho tất cả entities
- Status management cho CTĐT (DRAFT → PUBLISHED)
- Filter, search, pagination

## What's NOT Changing
- Course management (change 04)
- Matrices (change 05)
- Approval workflow (change 06)
