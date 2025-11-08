.PHONY: help setup start-backend start-frontend start-services stop-services test clean

help: ## Show this help message
	@echo "DevStandup AI Development Commands"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial project setup
	@echo "🚀 Setting up DevStandup AI..."
	@./run-local.sh

start-services: ## Start Docker services (DynamoDB)
	@echo "📦 Starting Docker services..."
	@docker-compose up -d

stop-services: ## Stop Docker services
	@echo "🛑 Stopping Docker services..."
	@docker-compose down

start-backend: ## Start backend server
	@echo "🐍 Starting backend server..."
	@cd backend && python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

start-frontend: ## Start frontend development server
	@echo "⚛️ Starting frontend server..."
	@cd frontend && npm run dev

test-backend: ## Run backend tests
	@echo "🧪 Running backend tests..."
	@cd backend && python -m pytest tests/ -v

test-frontend: ## Run frontend tests
	@echo "🧪 Running frontend tests..."
	@cd frontend && npm test

test: test-backend test-frontend ## Run all tests

build: ## Build Docker images
	@echo "🏗️ Building Docker images..."
	@docker-compose build

clean: ## Clean up generated files
	@echo "🧹 Cleaning up..."
	@cd backend && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@cd backend && find . -name "*.pyc" -delete 2>/dev/null || true
	@cd frontend && rm -rf dist/ 2>/dev/null || true
	@docker-compose down --volumes --remove-orphans 2>/dev/null || true

logs: ## View Docker logs
	@docker-compose logs -f

status: ## Check service status
	@echo "📊 Service Status:"
	@docker-compose ps
	@echo ""
	@echo "🌐 URLs:"
	@echo "Frontend: http://localhost:5173"
	@echo "Backend:  http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

dev: start-services ## Start full development environment
	@echo "🚀 Starting development environment..."
	@echo "Open two terminals and run:"
	@echo "Terminal 1: make start-backend"
	@echo "Terminal 2: make start-frontend"