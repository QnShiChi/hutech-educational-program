# Proposal: Project Setup with Cookiecutter Django

## Summary
Khởi tạo project HUTECH Program sử dụng Cookiecutter Django template, cấu hình cho PostgreSQL, Redis, Celery, Docker Compose. Setup frontend React/Vite/TypeScript trong cùng monorepo.

## Motivation
Cookiecutter Django cung cấp production-ready boilerplate: user model, Docker, Celery, mail, settings phân tách (local/production), security headers, etc. Tiết kiệm 2-3 ngày setup thủ công.

## What's Changing
- Tạo Django project từ cookiecutter-django template
- Cấu hình custom User model (thêm employee_id, phone, department FK)
- Setup React frontend với Vite + TypeScript + Ant Design
- Docker Compose cho development (postgres, redis, mailpit, django, celery, react)
- CLAUDE.md + OpenSpec structure

## What's NOT Changing
- Không implement business logic
- Không tạo API endpoints (chỉ health check)
- Không custom UI (chỉ scaffold)
