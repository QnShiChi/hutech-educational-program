# HUTECH Program V1

> Hệ thống Quản lý Chương trình Đào tạo — HUTECH University

---

## 🚀 Hướng dẫn chạy ứng dụng (Local Development)

### Yêu cầu hệ thống

| Phần mềm           | Phiên bản                  |
| ------------------ | -------------------------- |
| **Docker Desktop** | ≥ 4.x (bắt buộc)           |
| **Docker Compose** | v2 (đi kèm Docker Desktop) |
| **Git**            | ≥ 2.x                      |
| **Make**           | có sẵn trên Linux/macOS    |

> **Lưu ý:** Toàn bộ ứng dụng chạy trong Docker containers — không cần cài Python hay Node.js trực tiếp trên máy.

### 1. Clone project

```bash
git clone <repo-url> hutech-program
cd hutech-program
```

### 2. Kiểm tra file cấu hình

Project đã có sẵn các file env tại `.envs/.local/`. Kiểm tra chúng tồn tại:

```
.envs/.local/.django    # Cấu hình Django, Redis, Celery
.envs/.local/.postgres  # Cấu hình PostgreSQL
```

### 3. Build images

```bash
make build
```

Lần đầu sẽ mất 3-5 phút để download base images và cài dependencies.

### 4. Khởi động tất cả services

```bash
make up
```

### 5. Chạy migrations & tạo tài khoản admin

```bash
make migrate
make createsuperuser
```

### 6. (Tùy chọn) Seed dữ liệu mẫu

```bash
make seed
```

### 7. Truy cập ứng dụng

| Dịch vụ          | URL                                          | Mô tả                           |
| ---------------- | -------------------------------------------- | ------------------------------- |
| **Frontend**     | http://localhost:5173                        | React + Ant Design              |
| **Backend API**  | http://localhost:8000/api/                   | Django REST Framework           |
| **API Docs**     | http://localhost:8000/api/schema/swagger-ui/ | Swagger UI                      |
| **Django Admin** | http://localhost:8000/admin/                 | Admin panel                     |
| **Mailpit**      | http://localhost:8025                        | Mail testing (xem email gửi đi) |
| **Flower**       | http://localhost:5555                        | Celery task monitor             |
| **PostgreSQL**   | localhost:5432                               | Dùng DataGrip/DBeaver kết nối   |

### Kiến trúc Docker Services

```
┌──────────────────────────────────────────────────┐
│                   Frontend :5173                 │
│               (React + Vite dev server)          │
└──────────────┬───────────────────────────────────┘
               │ proxy /api → :8000
┌──────────────▼───────────────────────────────────┐
│                   Django :8000                   │
│           (API + Admin + Static files)           │
└──────┬──────────┬────────────┬───────────────────┘
       │          │            │
┌──────▼──┐ ┌────▼────┐ ┌─────▼─────┐
│Postgres │ │  Redis  │ │  Mailpit  │
│  :5432  │ │  :6379  │ │   :8025   │
└─────────┘ └────┬────┘ └───────────┘
                 │
        ┌────────┼────────┐
   ┌────▼────┐ ┌─▼──────┐ ┌──▼───┐
   │ Celery  │ │ Celery │ │Flower│
   │ Worker  │ │  Beat  │ │:5555 │
   └─────────┘ └────────┘ └──────┘
```

---

## 🛠 Makefile Commands

Xem tất cả commands: `make help`

### Docker

```bash
make up               # Khởi động tất cả containers
make down             # Dừng tất cả containers
make restart          # Restart toàn bộ
make build            # Build lại images
make build-no-cache   # Build không dùng cache
make ps               # Xem trạng thái containers
make logs             # Xem logs tất cả services
make logs-django      # Xem logs Django
make logs-celery      # Xem logs Celery worker
make logs-frontend    # Xem logs Frontend
make prune            # Xóa containers + volumes (⚠️ mất data)
```

### Django

```bash
make migrate          # Chạy migrations
make makemigrations   # Tạo migration files mới
make createsuperuser  # Tạo tài khoản admin
make shell            # Mở Django shell
make dbshell          # Mở PostgreSQL shell
make showmigrations   # Xem trạng thái migrations
make collectstatic    # Thu thập static files
make seed             # Seed dữ liệu mẫu
make manage cmd="..."  # Chạy lệnh manage.py bất kỳ
```

### Testing & Code Quality

```bash
make test             # Chạy test suite
make test-v           # Tests với output chi tiết
make test-cov         # Tests với coverage report
make lint             # Kiểm tra code style (ruff)
make format           # Format code tự động (ruff)
make typecheck        # Kiểm tra types (mypy)
```

### Database

```bash
make db-backup        # Backup database
make db-reset         # Reset toàn bộ database (⚠️ mất data)
```

### Khác

```bash
make bash             # Vào shell container Django
make bash-frontend    # Vào shell container Frontend
make npm-install      # Cài lại npm packages
make clean            # Xóa cache Python (__pycache__, .pyc)
```

---

## 🔧 Xử lý sự cố thường gặp

### Container không start được

```bash
make logs-django   # Đọc log lỗi
make down          # Dừng hoàn toàn
make build         # Build lại
make up            # Khởi động lại
```

### Database bị lỗi / muốn làm sạch

```bash
make prune         # Xóa volumes (mất data)
make up            # Tạo lại containers
make migrate       # Chạy lại migrations
make createsuperuser
```

### Frontend không load hoặc lỗi module

```bash
make bash-frontend
npm ci             # Cài lại dependencies
exit
make restart
```

### Xem email gửi đi (reset password, notification)

Mở http://localhost:8025 — Mailpit sẽ bắt tất cả email trong môi trường local.

---

## 📋 OpenSpec Workflow (dành cho AI-assisted development)

<details>
<summary><strong>Xem hướng dẫn sử dụng với Claude Code</strong></summary>

### Chuẩn bị thêm

- Claude Code (CLI) — `npm install -g @anthropic-ai/claude-code`
- OpenSpec — `npm install -g @fission-ai/openspec`

### Thứ tự triển khai

| #   | Change            | Thời gian |
| --- | ----------------- | --------- |
| 01  | Project Setup     | 2 ngày    |
| 02  | RBAC Module       | 3 ngày    |
| 03  | CTĐT Core         | 3 ngày    |
| 04  | Course Management | 2 ngày    |
| 05  | Matrices          | 2 ngày    |
| 06  | Approval Workflow | 3 ngày    |
| 07  | Word Import       | 3 ngày    |
| 08  | Frontend Setup    | 2 ngày    |
| 09  | Frontend RBAC     | 2 ngày    |
| 10  | Frontend CTĐT     | 5-7 ngày  |

### Prompt Template cho Claude Code

```
Đọc file CLAUDE.md để hiểu project conventions.
Đọc openspec/changes/{XX-change-name}/proposal.md để hiểu yêu cầu.
Đọc openspec/changes/{XX-change-name}/design.md để hiểu thiết kế.
Đọc openspec/changes/{XX-change-name}/tasks.md để biết danh sách tasks.

Thực hiện từng task trong tasks.md theo thứ tự.
Sau mỗi task, đánh dấu [x] trong tasks.md.
Commit sau mỗi nhóm tasks hoàn thành.
```

### Tips

- Mỗi khi bắt đầu session mới, luôn bắt đầu bằng: `Đọc CLAUDE.md trước`
- Chia thành sessions nhỏ: Models → APIs → Tests → Integration
- Commit thường xuyên

</details>
