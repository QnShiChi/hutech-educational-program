# Tasks: 01 - Project Setup

## 1. Django Project Initialization

- [x] 1.1 Run cookiecutter-django with options from design.md
- [x] 1.2 Verify project boots: `docker compose -f docker-compose.local.yml up`
- [x] 1.3 Run migrations, create superuser
- [x] 1.4 Verify DRF browsable API at `/api/`

## 2. Extend User Model

- [x] 2.1 Add UUID pk, employee_id, phone fields to User model
- [x] 2.2 Create migration (before first migrate if possible, else reset)
- [x] 2.3 Update UserAdmin to show new fields
- [x] 2.4 Update User serializer and API

## 3. Create App Skeletons

- [x] 3.1 `python manage.py startapp rbac` → move to `hutech_program/rbac/`
- [x] 3.2 `python manage.py startapp programs` → move to `hutech_program/programs/`
- [x] 3.3 `python manage.py startapp workflows` → move to `hutech_program/workflows/`
- [x] 3.4 `python manage.py startapp imports` → move to `hutech_program/imports/`
- [x] 3.5 `python manage.py startapp notifications` → move to `hutech_program/notifications/`
- [x] 3.6 Create `hutech_program/common/` with base models (TimeStampedModel, UUIDModel)
- [x] 3.7 Register all apps in INSTALLED_APPS

## 4. Install Additional Dependencies

- [x] 4.1 Add django-filter, drf-spectacular, simplejwt, cors-headers to requirements
- [x] 4.2 Configure drf-spectacular in settings (title, description, version)
- [x] 4.3 Configure SimpleJWT settings (access: 60min, refresh: 7 days)
- [x] 4.4 Configure CORS for frontend dev server (localhost:5173)
- [x] 4.5 Add JWT auth endpoints: /api/v1/auth/token/, /api/v1/auth/token/refresh/

## 5. Frontend Scaffold

- [x] 5.1 Create Vite React-TS project in `frontend/`
- [x] 5.2 Install antd, tailwind, axios, tanstack-query, zustand, react-router-dom
- [x] 5.3 Configure Tailwind + Ant Design theme
- [x] 5.4 Create base layout: Sidebar + Header + Content area
- [x] 5.5 Setup API client (axios instance with JWT interceptor)
- [x] 5.6 Setup React Router with placeholder pages
- [x] 5.7 Create auth store (Zustand) for login state

## 6. Docker & Dev Environment

- [x] 6.1 Add frontend Dockerfile for dev
- [x] 6.2 Add frontend service to docker-compose.local.yml
- [x] 6.3 Verify full stack boots: Django + Postgres + Redis + Celery + Frontend
- [x] 6.4 Add OpenSpec folder structure + CLAUDE.md

## 7. Verification

- [x] 7.1 Django admin accessible at localhost:8000/admin/
- [x] 7.2 DRF schema at localhost:8000/api/schema/
- [x] 7.3 Swagger UI at localhost:8000/api/docs/
- [x] 7.4 Frontend dev server at localhost:5173
- [x] 7.5 JWT login/refresh works
- [x] 7.6 All tests pass: `pytest`
