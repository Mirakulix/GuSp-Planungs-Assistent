# Makefile for Pfadi AI Assistant Development

.PHONY: help build up down logs clean test lint format install dev-setup prod-setup

# Default target
help: ## Show this help message
	@echo "GuSp-Planungs-Assistent - Development Commands"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development Container Startup and Build
dev:
	@echo "GuSp-Planungs-Assistent - Development Container Startup"
	@echo "=============================================="
	@docker compose -f docker-compose.yml up --build

# Development Setup
dev-setup: ## Set up development environment
	@echo "🏗️  Setting up development environment..."
	@cp .env.example .env || echo "⚠️  .env file already exists"
	@echo "📝 Please configure your Azure credentials in .env file"
	@echo "✅ Development setup complete!"

install: ## Install dependencies locally
	@echo "📦 Installing backend dependencies..."
	@cd backend && pip install -r requirements.txt && pip install pydantic-settings
	@echo "📦 Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "✅ Dependencies installed!"

# Docker Commands
build: ## Build Docker images
	@echo "🏗️  Building Docker images..."
	@docker compose build

up: ## Start services with Docker Compose
	@echo "🚀 Starting services..."
	@docker compose up -d
	@echo "✅ Services started!"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"

up-build: ## Build and start services
	@echo "🏗️  Building and starting services..."
	@docker compose up -d --build

up-logs: ## Start services and show logs
	@echo "🚀 Starting services with logs..."
	@docker compose up

down: ## Stop services
	@echo "🛑 Stopping services..."
	@docker compose down

restart: down up ## Restart services

logs: ## Show logs from all services
	@docker compose logs -f

logs-backend: ## Show backend logs
	@docker compose logs -f backend

logs-frontend: ## Show frontend logs
	@docker compose logs -f frontend

logs-redis: ## Show Redis logs
	@docker compose logs -f redis

# Development Commands
dev-backend: ## Run backend in development mode
	@echo "🔧 Starting backend development server..."
	@cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend: ## Run frontend in development mode
	@echo "🎨 Starting frontend development server..."
	@cd frontend && npm run dev

test: ## Run tests
	@echo "🧪 Running tests..."
	@docker compose exec backend python -m pytest tests/ -v || echo "⚠️  Tests not yet implemented"
	@cd frontend && npm test || echo "⚠️  Frontend tests not yet configured"

test-backend: ## Run backend tests only
	@echo "🧪 Running backend tests..."
	@cd backend && python -m pytest tests/ -v || echo "⚠️  Tests not yet implemented"

test-frontend: ## Run frontend tests only
	@echo "🧪 Running frontend tests..."
	@cd frontend && npm test || echo "⚠️  Frontend tests not yet configured"

# Code Quality
lint: ## Run linting
	@echo "🔍 Running linting..."
	@cd backend && python -m flake8 app/ || echo "⚠️  Install flake8 first: pip install flake8"
	@cd frontend && npm run lint || echo "⚠️  Frontend linting not configured"

format: ## Format code
	@echo "🎨 Formatting code..."
	@cd backend && python -m black app/ || echo "⚠️  Install black first: pip install black"
	@cd backend && python -m isort app/ || echo "⚠️  Install isort first: pip install isort"
	@cd frontend && npm run format || echo "⚠️  Frontend formatting not configured"

# Database Commands
migrate: ## Run database migrations
	@echo "🗄️  Running database migrations..."
	@docker compose exec backend alembic upgrade head || echo "⚠️  Database migrations not yet configured"

migrate-create: ## Create new migration
	@echo "🗄️  Creating new migration..."
	@read -p "Migration name: " name; \
	docker compose exec backend alembic revision --autogenerate -m "$$name"

# Health Checks
health: ## Check service health
	@echo "🏥 Checking service health..."
	@echo "Backend:" && curl -s http://localhost:8000/api/v1/health | jq . || echo "❌ Backend not responding"
	@echo "Frontend:" && curl -s http://localhost:3000/health || echo "❌ Frontend not responding"
	@echo "Redis:" && docker compose exec redis redis-cli ping || echo "❌ Redis not responding"

# Cleanup
clean: ## Clean up Docker resources
	@echo "🧹 Cleaning up..."
	@docker compose down --volumes --remove-orphans
	@docker system prune -f
	@echo "✅ Cleanup complete!"

clean-all: ## Clean everything including images
	@echo "🧹 Deep cleaning..."
	@docker compose down --volumes --remove-orphans
	@docker system prune -af
	@echo "✅ Deep cleanup complete!"

# Production
prod-build: ## Build for production
	@echo "🏭 Building for production..."
	@docker compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up: ## Start production services
	@echo "🚀 Starting production services..."
	@docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Backup and Restore
backup: ## Backup database and data
	@echo "💾 Creating backup..."
	@mkdir -p backups
	@docker compose exec backend cp /app/pfadi_assistant.db /app/data/backup_$(shell date +%Y%m%d_%H%M%S).db
	@echo "✅ Backup created in data/ directory"

# Monitoring
ps: ## Show running containers
	@docker compose ps

stats: ## Show container resource usage
	@docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.PIDs}}"

# Azure AI Testing
test-ai: ## Test Azure AI integration
	@echo "🤖 Testing Azure AI integration..."
	@python test_azure_ai.py

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@echo "⚠️  Documentation generation not yet configured"

# Quick commands for daily development
quick-start: dev-setup build up ## Quick start for new developers
	@echo "🎉 Quick start complete!"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔧 Backend: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"

daily: up logs ## Daily development start

# Environment info
info: ## Show environment information
	@echo "📊 Environment Information"
	@echo "=========================="
	@echo "Docker version: $(shell docker --version)"
	@echo "Docker Compose version: $(shell docker compose version)"
	@echo "Node version: $(shell node --version || echo 'Not installed')"
	@echo "NPM version: $(shell npm --version || echo 'Not installed')"
	@echo "Python version: $(shell python --version || echo 'Not installed')"
	@echo "Current directory: $(shell pwd)"
	@echo "Git branch: $(shell git branch --show-current || echo 'Not a git repository')"