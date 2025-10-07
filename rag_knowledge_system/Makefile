# ================================
# RAG Knowledge System - Makefile
# ================================
#
# Professional automation for the RAG Knowledge System project
# Using uv for ultra-fast Python package management
#
# Usage:
#   make help          - Show this help message
#   make install       - Install the project and dependencies
#   make dev           - Install development dependencies
#   make test          - Run all tests
#   make lint          - Run code quality checks
#   make format        - Format code with black and isort
#   make clean         - Clean up build artifacts
#   make docker        - Build and run with Docker
#

# ================================
# CONFIGURATION
# ================================

.PHONY: help install dev test lint format clean docker run-api run-streamlit
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Project configuration
PROJECT_NAME := rag-knowledge-system
PYTHON_VERSION := 3.11
UV := $(shell which uv)
DOCKER := $(shell which docker)
DOCKER_COMPOSE := $(shell which docker-compose)

# Directories
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs
DATA_DIR := data
LOGS_DIR := logs
CONFIG_DIR := config

# ================================
# HELP
# ================================

help: ## Show this help message
	@echo "$(BLUE)RAG Knowledge System - Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(install|dev|setup)"
	@echo ""
	@echo "$(GREEN)Development Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(test|lint|format|check)"
	@echo ""
	@echo "$(GREEN)Execution Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(run|serve|start)"
	@echo ""
	@echo "$(GREEN)Data Pipeline Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(scrape|process|embed|index)"
	@echo ""
	@echo "$(GREEN)Docker Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(docker|compose)"
	@echo ""
	@echo "$(GREEN)Utility Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(clean|logs|backup|migrate)"

# ================================
# SETUP COMMANDS
# ================================

check-uv: ## Check if uv is installed
	@if [ -z "$(UV)" ]; then \
		echo "$(RED)Error: uv is not installed. Please install it first:$(NC)"; \
		echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ uv is installed: $(UV)$(NC)"

install: check-uv ## Install project dependencies using uv
	@echo "$(BLUE)Installing RAG Knowledge System...$(NC)"
	$(UV) sync
	@echo "$(GREEN)✓ Installation complete$(NC)"

dev: check-uv ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(UV) sync --extra dev
	$(UV) run pre-commit install
	@echo "$(GREEN)✓ Development environment ready$(NC)"

setup-spacy: ## Download spaCy language models
	@echo "$(BLUE)Downloading spaCy language models...$(NC)"
	$(UV) run python -m spacy download en_core_web_sm
	$(UV) run python -m spacy download es_core_news_sm
	@echo "$(GREEN)✓ spaCy models installed$(NC)"

setup-nltk: ## Download NLTK data
	@echo "$(BLUE)Downloading NLTK data...$(NC)"
	$(UV) run python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
	@echo "$(GREEN)✓ NLTK data installed$(NC)"

setup: install dev setup-spacy setup-nltk ## Complete project setup
	@echo "$(GREEN)✓ Project setup complete!$(NC)"

# ================================
# DEVELOPMENT COMMANDS
# ================================

test: ## Run all tests with coverage
	@echo "$(BLUE)Running tests...$(NC)"
	$(UV) run pytest

test-unit: ## Run only unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(UV) run pytest tests/unit -v

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(UV) run pytest tests/integration -v

test-e2e: ## Run end-to-end tests
	@echo "$(BLUE)Running E2E tests...$(NC)"
	$(UV) run pytest tests/e2e -v

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	$(UV) run pytest-watch

lint: ## Run code quality checks
	@echo "$(BLUE)Running code quality checks...$(NC)"
	$(UV) run ruff check $(SRC_DIR) $(TEST_DIR)
	$(UV) run mypy $(SRC_DIR)
	@echo "$(GREEN)✓ Code quality checks passed$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	$(UV) run black $(SRC_DIR) $(TEST_DIR)
	$(UV) run isort $(SRC_DIR) $(TEST_DIR)
	$(UV) run ruff check --fix $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✓ Code formatted$(NC)"

check: format lint test ## Run format, lint, and test

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	$(UV) run bandit -r $(SRC_DIR)
	@echo "$(GREEN)✓ Security checks passed$(NC)"

# ================================
# EXECUTION COMMANDS
# ================================

run-api: ## Start the FastAPI server
	@echo "$(BLUE)Starting FastAPI server...$(NC)"
	$(UV) run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

run-streamlit: ## Start Streamlit interface
	@echo "$(BLUE)Starting Streamlit interface...$(NC)"
	$(UV) run streamlit run src/chatbot/interface/streamlit_app.py --server.port 8501

run-celery: ## Start Celery worker
	@echo "$(BLUE)Starting Celery worker...$(NC)"
	$(UV) run celery -A src.core.celery_app worker --loglevel=info

run-celery-beat: ## Start Celery scheduler
	@echo "$(BLUE)Starting Celery beat scheduler...$(NC)"
	$(UV) run celery -A src.core.celery_app beat --loglevel=info

run-redis: ## Start Redis server (if installed locally)
	@echo "$(BLUE)Starting Redis server...$(NC)"
	redis-server

serve: ## Start all services using Docker Compose
	@echo "$(BLUE)Starting all services...$(NC)"
	$(DOCKER_COMPOSE) up -d

# ================================
# DATA PIPELINE COMMANDS
# ================================

scrape: ## Run web scraping
	@echo "$(BLUE)Starting web scraping...$(NC)"
	$(UV) run scrapy crawl company_spider -s JOBDIR=jobs/company_spider-1

scrape-list: ## List available spiders
	@echo "$(BLUE)Available spiders:$(NC)"
	$(UV) run scrapy list

process-data: ## Process raw scraped data
	@echo "$(BLUE)Processing scraped data...$(NC)"
	$(UV) run python -m src.data_processing.pipeline

generate-embeddings: ## Generate embeddings from processed data
	@echo "$(BLUE)Generating embeddings...$(NC)"
	$(UV) run python -m src.data_processing.embeddings.generator

index-data: ## Index data into vector database
	@echo "$(BLUE)Indexing data into vector database...$(NC)"
	$(UV) run python -m src.vector_store.indexer

pipeline: scrape process-data generate-embeddings index-data ## Run complete data pipeline
	@echo "$(GREEN)✓ Complete data pipeline executed$(NC)"

# ================================
# DOCKER COMMANDS
# ================================

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	$(DOCKER) build -t $(PROJECT_NAME):latest .
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-run: docker-build ## Run application with Docker
	@echo "$(BLUE)Running application with Docker...$(NC)"
	$(DOCKER) run -p 8000:8000 -p 8501:8501 --env-file .env $(PROJECT_NAME):latest

compose-up: ## Start services with Docker Compose
	@echo "$(BLUE)Starting services with Docker Compose...$(NC)"
	$(DOCKER_COMPOSE) up -d

compose-down: ## Stop Docker Compose services
	@echo "$(BLUE)Stopping Docker Compose services...$(NC)"
	$(DOCKER_COMPOSE) down

compose-logs: ## View Docker Compose logs
	$(DOCKER_COMPOSE) logs -f

docker-clean: ## Clean Docker artifacts
	@echo "$(BLUE)Cleaning Docker artifacts...$(NC)"
	$(DOCKER) system prune -a -f
	$(DOCKER) volume prune -f

# ================================
# DATABASE COMMANDS
# ================================

migrate-up: ## Run database migrations up
	@echo "$(BLUE)Running database migrations...$(NC)"
	$(UV) run alembic upgrade head
	@echo "$(GREEN)✓ Database migrations applied$(NC)"

migrate-down: ## Rollback last migration
	@echo "$(BLUE)Rolling back last migration...$(NC)"
	$(UV) run alembic downgrade -1

migrate-create: ## Create new migration (usage: make migrate-create MESSAGE="description")
	@echo "$(BLUE)Creating new migration...$(NC)"
	$(UV) run alembic revision --autogenerate -m "$(MESSAGE)"

db-reset: ## Reset database (DESTRUCTIVE)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(UV) run python scripts/setup/reset_db.py; \
		echo "$(GREEN)✓ Database reset$(NC)"; \
	fi

# ================================
# MONITORING COMMANDS
# ================================

logs: ## View application logs
	@echo "$(BLUE)Viewing application logs...$(NC)"
	tail -f $(LOGS_DIR)/*.log

logs-scraping: ## View scraping logs
	tail -f $(LOGS_DIR)/scrapy.log

logs-api: ## View API logs
	tail -f $(LOGS_DIR)/api.log

logs-clear: ## Clear all logs
	@echo "$(BLUE)Clearing logs...$(NC)"
	find $(LOGS_DIR) -name "*.log" -delete
	@echo "$(GREEN)✓ Logs cleared$(NC)"

monitor: ## Start monitoring dashboard
	@echo "$(BLUE)Starting monitoring dashboard...$(NC)"
	$(UV) run python -m src.core.monitoring.dashboard

# ================================
# UTILITY COMMANDS
# ================================

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	@echo "$(GREEN)✓ Cleaned$(NC)"

clean-data: ## Clean data directories (CAREFUL!)
	@echo "$(RED)WARNING: This will delete all scraped and processed data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf $(DATA_DIR)/raw/*; \
		rm -rf $(DATA_DIR)/processed/*; \
		rm -rf $(DATA_DIR)/embeddings/*; \
		echo "$(GREEN)✓ Data directories cleaned$(NC)"; \
	fi

backup-data: ## Backup data directory
	@echo "$(BLUE)Backing up data...$(NC)"
	tar -czf backups/data-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz $(DATA_DIR)/
	@echo "$(GREEN)✓ Data backed up$(NC)"

env-example: ## Create .env file from .env.example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ Created .env file from .env.example$(NC)"; \
		echo "$(YELLOW)Don't forget to update the values in .env$(NC)"; \
	else \
		echo "$(YELLOW).env file already exists$(NC)"; \
	fi

version: ## Show version information
	@echo "$(BLUE)RAG Knowledge System Version Information$(NC)"
	@echo "Project: $(PROJECT_NAME)"
	@echo "Python: $(shell python --version)"
	@echo "uv: $(shell $(UV) --version)"
	@if [ -n "$(DOCKER)" ]; then echo "Docker: $(shell $(DOCKER) --version)"; fi

health-check: ## Check system health
	@echo "$(BLUE)System Health Check$(NC)"
	@$(UV) run python scripts/health_check.py

# ================================
# CI/CD COMMANDS
# ================================

ci-install: check-uv ## Install for CI environment
	$(UV) sync --frozen

ci-test: ## Run tests in CI environment
	$(UV) run pytest --cov-report=xml --junitxml=junit.xml

ci-lint: ## Run linting for CI
	$(UV) run ruff check --output-format=github $(SRC_DIR) $(TEST_DIR)
	$(UV) run mypy $(SRC_DIR) --junit-xml mypy-report.xml

ci-security: ## Run security checks for CI
	$(UV) run bandit -r $(SRC_DIR) -f json -o bandit-report.json

ci-build: ## Build for CI
	$(UV) build

ci: ci-install ci-lint ci-security ci-test ci-build ## Run complete CI pipeline

# ================================
# DEVELOPMENT SHORTCUTS
# ================================

quick-start: env-example install ## Quick start for new developers
	@echo "$(GREEN)✓ Quick start complete!$(NC)"
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Update .env with your configuration"
	@echo "  2. Run 'make dev' to install development dependencies"
	@echo "  3. Run 'make run-api' to start the API server"
	@echo "  4. Run 'make run-streamlit' to start the web interface"

demo: ## Run demo with sample data
	@echo "$(BLUE)Running demo with sample data...$(NC)"
	$(UV) run python scripts/demo.py
	@echo "$(GREEN)✓ Demo complete$(NC)"

# ================================
# NOTEBOOK COMMANDS
# ================================

notebook: ## Start Jupyter notebook server
	@echo "$(BLUE)Starting Jupyter notebook server...$(NC)"
	$(UV) run jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser

lab: ## Start JupyterLab server
	@echo "$(BLUE)Starting JupyterLab server...$(NC)"
	$(UV) run jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

# ================================
# PERFORMANCE COMMANDS
# ================================

benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running performance benchmarks...$(NC)"
	$(UV) run python scripts/benchmarks.py

profile: ## Profile application performance
	@echo "$(BLUE)Profiling application...$(NC)"
	$(UV) run python -m cProfile -o profile.stats scripts/profile_app.py
	$(UV) run python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

# ================================
# ERROR HANDLING
# ================================

.ONESHELL:
check-env:
	@if [ ! -f .env ]; then \
		echo "$(RED)Error: .env file not found$(NC)"; \
		echo "Run 'make env-example' to create one"; \
		exit 1; \
	fi