.PHONY: help install install-dev test test-cov lint format type-check pre-commit docker-build docker-up docker-down docker-logs clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync --python 3.13

install-dev: ## Install all dependencies including dev tools
	uv sync --python 3.13 --all-extras

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage report
	uv run pytest --cov=src --cov-report=html --cov-report=term

lint: ## Run linting checks
	uv run ruff check .

format: ## Format code with ruff
	uv run ruff format .

format-check: ## Check code formatting without making changes
	uv run ruff format --check .

type-check: ## Run type checking with mypy
	uv run mypy src/

pre-commit: ## Run all pre-commit hooks
	uv run pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	uv run pre-commit install

docker-build: ## Build Docker image
	docker compose build

docker-up: ## Start Docker containers
	docker compose up -d

docker-up-logs: ## Start Docker containers with logs
	docker compose up

docker-down: ## Stop Docker containers
	docker compose down

docker-logs: ## Show Docker container logs
	docker compose logs -f

docker-shell: ## Open shell in running container
	docker compose exec app /bin/bash

docker-clean: ## Remove Docker containers and volumes
	docker compose down -v

clean: ## Clean up generated files
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-all: clean docker-clean ## Clean everything including Docker

setup: install-dev pre-commit-install ## Complete initial setup
	@echo "✅ Setup complete! Run 'source .venv/bin/activate' to activate the virtual environment"
