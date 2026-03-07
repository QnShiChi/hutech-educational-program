# Design: Project Setup

## Cookiecutter Django Options
```
project_name: HUTECH Program
project_slug: hutech_program
description: Training Program Management System for HUTECH University
author_name: HUTECH IT Team
domain_name: program.hutech.edu.vn
email: it@hutech.edu.vn
version: 0.1.0
timezone: Asia/Ho_Chi_Minh
use_whitenoise: y
use_celery: y
use_mailpit: y
use_sentry: n (add later)
use_docker: y
postgresql_version: 16
cloud_provider: None
mail_service: Other SMTP
use_async: n
use_drf: y
frontend_pipeline: None (we'll add React separately)
ci_tool: Github
keep_local_envs_in_vcs: y
```

## Project Structure
```
hutech_program/
├── .envs/                          # Environment files (from cookiecutter)
│   ├── .local/
│   │   ├── .django
│   │   └── .postgres
│   └── .production/
├── config/                         # Django config
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py
│   ├── api_router.py              # DRF router
│   ├── celery_app.py
│   └── wsgi.py
├── hutech_program/                 # Main Django apps
│   ├── users/                     # Custom User (from cookiecutter, extended)
│   ├── rbac/                      # NEW: Roles, Permissions, Departments
│   ├── programs/                  # NEW: CTĐT, PLO, PO, Courses, Matrices
│   ├── workflows/                 # NEW: Approval, Versioning, AuditLog
│   ├── imports/                   # NEW: Word file parsing
│   ├── notifications/             # NEW: In-app notifications
│   └── common/                    # NEW: Shared base models, mixins, utils
├── frontend/                      # NEW: React app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   ├── types/
│   │   └── utils/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── openspec/                      # Spec files
├── requirements/                  # Python deps (from cookiecutter)
├── compose/                       # Docker configs (from cookiecutter)
├── CLAUDE.md
├── docker-compose.local.yml
└── manage.py
```

## Custom User Model Extension
Cookiecutter Django generates `users/` app with AbstractUser. We extend:

```python
# hutech_program/users/models.py (extended)
class User(AbstractUser):
    # Cookiecutter fields: name (CharField)
    # Our additions:
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True,
                                    verbose_name="Mã nhân viên")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    department = models.ForeignKey('rbac.Department', on_delete=models.SET_NULL, 
                                   null=True, blank=True, verbose_name="Đơn vị")
    is_active = models.BooleanField(default=True)
```

## Frontend Setup
```bash
cd frontend/
npm create vite@latest . -- --template react-ts
npm install antd @ant-design/icons
npm install tailwindcss @tailwindcss/vite
npm install axios @tanstack/react-query zustand
npm install react-router-dom
npm install -D @types/react-router-dom
```

## Docker Compose Addition
Add React dev server to `docker-compose.local.yml`:
```yaml
frontend:
  build:
    context: .
    dockerfile: ./compose/local/frontend/Dockerfile
  volumes:
    - ./frontend:/app
    - /app/node_modules
  ports:
    - "5173:5173"
  command: npm run dev -- --host 0.0.0.0
```

## Django Additional Packages
Add to `requirements/local.txt`:
```
django-filter==24.3
drf-spectacular==0.27.2
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.4.0
```
