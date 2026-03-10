# ============================================================================
# HUTECH Program - Makefile
# ============================================================================
COMPOSE_FILE := docker-compose.local.yml
DC := docker compose -f $(COMPOSE_FILE)
DJANGO_CONTAINER := hutech_program_local_django

.DEFAULT_GOAL := help

# ----------------------------------------------------------------------------
# 🐳  Docker
# ----------------------------------------------------------------------------
.PHONY: build up down restart prune ps logs

build: ## Build all Docker images
	$(DC) build

build-no-cache: ## Build images without cache
	$(DC) build --no-cache

up: ## Start all services in background
	$(DC) up -d --remove-orphans

down: ## Stop all services
	$(DC) down

restart: down up ## Restart all services

prune: ## Stop services and remove volumes (DESTRUCTIVE)
	$(DC) down -v --remove-orphans

ps: ## Show running containers
	$(DC) ps

logs: ## Tail all container logs
	$(DC) logs -f

logs-django: ## Tail Django logs
	$(DC) logs -f django

logs-celery: ## Tail Celery worker logs
	$(DC) logs -f celeryworker

logs-frontend: ## Tail frontend logs
	$(DC) logs -f frontend

# ----------------------------------------------------------------------------
# 🐍  Django Management
# ----------------------------------------------------------------------------
.PHONY: manage migrate makemigrations createsuperuser shell dbshell collectstatic seed

manage: ## Run Django manage.py – Usage: make manage cmd="showmigrations"
	$(DC) run --rm django python manage.py $(cmd)

migrate: ## Apply database migrations
	$(DC) run --rm django python manage.py migrate

makemigrations: ## Create new database migrations
	$(DC) run --rm django python manage.py makemigrations

createsuperuser: ## Create a Django superuser
	$(DC) run --rm django python manage.py createsuperuser

shell: ## Open Django shell_plus (or shell)
	$(DC) run --rm django python manage.py shell_plus 2>/dev/null || $(DC) run --rm django python manage.py shell

dbshell: ## Open database shell
	$(DC) run --rm django python manage.py dbshell

collectstatic: ## Collect static files
	$(DC) run --rm django python manage.py collectstatic --noinput

seed: ## Seed sample data
	$(DC) run --rm django python manage.py seed_nntq2025

showmigrations: ## Show migration status
	$(DC) run --rm django python manage.py showmigrations

# ----------------------------------------------------------------------------
# ✅  Quality & Testing
# ----------------------------------------------------------------------------
.PHONY: test test-v lint format typecheck

test: ## Run test suite
	$(DC) run --rm django pytest

test-v: ## Run tests with verbose output
	$(DC) run --rm django pytest -v

test-cov: ## Run tests with coverage report
	$(DC) run --rm django coverage run -m pytest && $(DC) run --rm django coverage report

lint: ## Lint Python code with ruff
	$(DC) run --rm django ruff check .

format: ## Format Python code with ruff
	$(DC) run --rm django ruff format .

typecheck: ## Run mypy type checking
	$(DC) run --rm django mypy hutech_program

# ----------------------------------------------------------------------------
# 🖥️  Interactive Shells
# ----------------------------------------------------------------------------
.PHONY: bash bash-frontend

bash: ## Open a bash shell in Django container
	$(DC) exec django bash

bash-frontend: ## Open a bash shell in frontend container
	$(DC) exec frontend sh

# ----------------------------------------------------------------------------
# 🗄️  Database
# ----------------------------------------------------------------------------
.PHONY: db-backup db-restore db-reset

db-backup: ## Backup database
	$(DC) exec postgres backup

db-restore: ## Restore database – Usage: make db-restore file="backup_2026_03_07.sql.gz"
	$(DC) exec postgres restore $(file)

db-reset: ## Reset database (DESTRUCTIVE) – drops and recreates
	$(DC) run --rm django python manage.py flush --noinput

# ----------------------------------------------------------------------------
# 📦  Frontend
# ----------------------------------------------------------------------------
.PHONY: npm-install npm-build

npm-install: ## Install frontend dependencies
	$(DC) exec frontend npm install

npm-build: ## Build frontend for production
	$(DC) exec frontend npm run build

# ----------------------------------------------------------------------------
# 📚  Docs
# ----------------------------------------------------------------------------
.PHONY: docs

docs: ## Serve documentation locally
	docker compose -f docker-compose.docs.yml up

# ----------------------------------------------------------------------------
# 🧹  Cleanup
# ----------------------------------------------------------------------------
.PHONY: clean

clean: ## Remove Python cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# ----------------------------------------------------------------------------
# ❓  Help
# ----------------------------------------------------------------------------
.PHONY: help

help: ## Show this help message
	@echo ""
	@echo "  HUTECH Program – Available commands"
	@echo "  ──────────────────────────────────────"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
