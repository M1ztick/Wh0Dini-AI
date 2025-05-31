# Wh0Dini-AI Development Makefile

.PHONY: help install dev test format lint clean run setup

help: ## Show this help message
	@echo "Wh0Dini-AI Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Run initial project setup
	@echo "🚀 Setting up Wh0Dini-AI development environment..."
	./setup.sh

install: ## Install dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	pip install black isort flake8 mypy pytest-cov

dev: ## Install development dependencies
	@echo "🔧 Installing development dependencies..."
	pip install black isort flake8 mypy pytest-cov pre-commit

run: ## Run the FastAPI server
	@echo "🚀 Starting Wh0Dini-AI server..."
	python main.py

test: ## Run tests with coverage
	@echo "🧪 Running tests..."
	pytest -v --cov=. --cov-report=html --cov-report=term

test-quick: ## Run tests without coverage
	@echo "⚡ Running quick tests..."
	pytest -v

format: ## Format code with black and isort
	@echo "🎨 Formatting code..."
	black .
	isort .

lint: ## Run linting checks
	@echo "🔍 Running linting checks..."
	flake8 .
	black --check .
	isort --check-only .

type-check: ## Run type checking with mypy
	@echo "🔍 Running type checking..."
	mypy . --ignore-missing-imports

clean: ## Clean up cache files
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/

check: ## Run all checks (format, lint, type-check, test)
	@echo "✅ Running all checks..."
	make format
	make lint
	make type-check
	make test

docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t wh0dini-ai .

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker run -p 8000:8000 wh0dini-ai

env-check: ## Check environment variables
	@echo "🔍 Checking environment setup..."
	@python -c "import os; print('OpenAI API Key:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"

logs: ## Show application logs
	@echo "📋 Showing logs..."
	tail -f logs/*.log 2>/dev/null || echo "No log files found"
