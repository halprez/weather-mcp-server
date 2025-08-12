# Weather MCP Server - Makefile
# Provides convenient commands for development, testing, and deployment

.PHONY: help install build test run clean deploy stop logs health check lint format

# Default target
.DEFAULT_GOAL := help

# Colors for output
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
BLUE := \033[34m
RESET := \033[0m

# Project configuration
PROJECT_NAME := weather-mcp-server
PYTHON := python3
PIP := pip
DOCKER_COMPOSE := docker-compose
VENV_DIR := .venv

## Help - Show this help message
help:
	@echo "$(BLUE)Weather MCP Server - Available Commands$(RESET)"
	@echo "======================================"
	@echo ""
	@echo "$(GREEN)🚀 Quick Start:$(RESET)"
	@echo "  make install    - Install dependencies"
	@echo "  make build      - Build all Docker containers"
	@echo "  make run        - Run the application (HTTP server)"
	@echo "  make test       - Run all tests"
	@echo ""
	@echo "$(YELLOW)📦 Development:$(RESET)"
	@echo "  make install    - Install Python dependencies"
	@echo "  make lint       - Run code linting"
	@echo "  make format     - Format code with black"
	@echo "  make clean      - Clean up cache files and containers"
	@echo ""
	@echo "$(BLUE)🐳 Docker Operations:$(RESET)"
	@echo "  make build      - Build all Docker images"
	@echo "  make deploy     - Deploy full Docker stack"
	@echo "  make stop       - Stop all containers"
	@echo "  make logs       - Show container logs"
	@echo "  make health     - Check service health"
	@echo ""
	@echo "$(GREEN)🧪 Testing:$(RESET)"
	@echo "  make test       - Run all tests"
	@echo "  make test-unit  - Run unit tests only"
	@echo "  make test-integration - Run integration tests"
	@echo "  make check      - Run health checks and validation"

## Install - Set up development environment
install:
	@echo "$(GREEN)📦 Installing dependencies...$(RESET)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi
	@echo "Installing Python packages..."
	@$(VENV_DIR)/bin/pip install --upgrade pip
	@$(VENV_DIR)/bin/pip install -r requirements.txt
	@echo "$(GREEN)✅ Installation complete!$(RESET)"

## Build - Build all Docker containers
build:
	@echo "$(BLUE)🐳 Building Docker containers...$(RESET)"
	@echo "Building AIFS server container..."
	@docker build -f Dockerfile.aifs -t weather-mcp/aifs-server .
	@echo "Building MCP server container..."
	@docker build -f Dockerfile.mcp -t weather-mcp/mcp-server .
	@echo "$(GREEN)✅ All containers built successfully!$(RESET)"

## Run - Start the HTTP MCP server locally
run:
	@echo "$(GREEN)🌐 Starting Weather MCP HTTP Server...$(RESET)"
	@echo "Server will be available at http://localhost:8081"
	@echo "Press Ctrl+C to stop"
	@$(VENV_DIR)/bin/python weather_mcp/mcp_server.py

## Deploy - Deploy full Docker stack
deploy: build
	@echo "$(BLUE)🚀 Deploying full Docker stack...$(RESET)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Stack deployed! Services starting...$(RESET)"
	@echo "AIFS Server: http://localhost:8080"
	@echo "MCP Server: http://localhost:8081"
	@echo "Use 'make logs' to see service logs"
	@echo "Use 'make health' to check service status"

## Stop - Stop all containers
stop:
	@echo "$(YELLOW)🛑 Stopping all containers...$(RESET)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ All containers stopped$(RESET)"

## Logs - Show container logs
logs:
	@echo "$(BLUE)📋 Container logs:$(RESET)"
	@$(DOCKER_COMPOSE) logs -f

## Health - Check service health
health:
	@echo "$(BLUE)🏥 Checking service health...$(RESET)"
	@echo ""
	@echo "$(YELLOW)MCP Server Health:$(RESET)"
	@curl -s http://localhost:8081/health | jq . 2>/dev/null || curl -s http://localhost:8081/health || echo "❌ MCP server not responding"
	@echo ""
	@echo "$(YELLOW)AIFS Server Health:$(RESET)"
	@curl -s http://localhost:8080/health | jq . 2>/dev/null || curl -s http://localhost:8080/health || echo "❌ AIFS server not responding"
	@echo ""
	@echo "$(YELLOW)Docker Services:$(RESET)"
	@$(DOCKER_COMPOSE) ps

## Test - Run all tests
test: install
	@echo "$(GREEN)🧪 Running all tests...$(RESET)"
	@echo ""
	@echo "$(YELLOW)Running unit tests:$(RESET)"
	@$(VENV_DIR)/bin/pytest tests/ -v --tb=short
	@echo ""
	@echo "$(YELLOW)Running application tests:$(RESET)"
	@$(VENV_DIR)/bin/python weather_mcp/mcp_server.py test
	@echo "$(GREEN)✅ All tests completed!$(RESET)"

## Test Unit - Run unit tests only
test-unit: install
	@echo "$(GREEN)🧪 Running unit tests...$(RESET)"
	@$(VENV_DIR)/bin/pytest tests/test_*.py -v

## Test Integration - Run integration tests
test-integration: install
	@echo "$(GREEN)🧪 Running integration tests...$(RESET)"
	@$(VENV_DIR)/bin/pytest tests/test_integration.py -v
	@$(VENV_DIR)/bin/python tests/test_deployment.py

## Check - Run health checks and validation
check:
	@echo "$(BLUE)🔍 Running system checks...$(RESET)"
	@echo ""
	@echo "$(YELLOW)Python environment:$(RESET)"
	@$(VENV_DIR)/bin/python --version
	@echo ""
	@echo "$(YELLOW)Docker status:$(RESET)"
	@docker --version
	@docker-compose --version
	@echo ""
	@echo "$(YELLOW)Project structure:$(RESET)"
	@test -f weather_mcp/mcp_server.py && echo "✅ MCP server found" || echo "❌ MCP server missing"
	@test -f requirements.txt && echo "✅ Requirements found" || echo "❌ Requirements missing"
	@test -f docker-compose.yml && echo "✅ Docker compose found" || echo "❌ Docker compose missing"
	@echo ""
	@echo "$(YELLOW)Available tools:$(RESET)"
	@timeout 10s $(VENV_DIR)/bin/python -c "from weather_mcp.mcp_server import WeatherMCPServer; import asyncio; server = WeatherMCPServer(); result = asyncio.run(server.list_tools()); print(f'✅ {len(result[\"tools\"])} tools available')" 2>/dev/null || echo "❌ Could not load tools"

## Lint - Run code linting
lint: install
	@echo "$(YELLOW)🔍 Running code linting...$(RESET)"
	@$(VENV_DIR)/bin/python -m isort --check-only weather_mcp/ tests/ || echo "❌ Import sorting issues found"
	@$(VENV_DIR)/bin/python -m black --check weather_mcp/ tests/ || echo "❌ Code formatting issues found"
	@echo "$(GREEN)✅ Linting complete$(RESET)"

## Format - Format code with black and isort
format: install
	@echo "$(YELLOW)🎨 Formatting code...$(RESET)"
	@$(VENV_DIR)/bin/python -m isort weather_mcp/ tests/
	@$(VENV_DIR)/bin/python -m black weather_mcp/ tests/
	@echo "$(GREEN)✅ Code formatted$(RESET)"

## Clean - Clean up cache files and containers
clean:
	@echo "$(YELLOW)🧹 Cleaning up...$(RESET)"
	@echo "Removing Python cache files..."
	@find . -type d -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -not -path "./.venv/*" -delete 2>/dev/null || true
	@echo "Stopping Docker containers..."
	@$(DOCKER_COMPOSE) down --remove-orphans 2>/dev/null || true
	@echo "Removing Docker containers and networks..."
	@docker system prune -f --filter "label=com.docker.compose.project=$(PROJECT_NAME)" 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete$(RESET)"

## Clean All - Deep clean including virtual environment
clean-all: clean
	@echo "$(RED)🧹 Deep cleaning (including virtual environment)...$(RESET)"
	@rm -rf $(VENV_DIR)
	@docker rmi weather-mcp/aifs-server weather-mcp/mcp-server 2>/dev/null || true
	@echo "$(GREEN)✅ Deep cleanup complete$(RESET)"

# Development shortcuts
dev: install run  ## Quick development setup
up: deploy        ## Alias for deploy
down: stop        ## Alias for stop
restart: stop deploy  ## Restart all services

# Emergency commands
emergency-stop:   ## Force stop all containers
	@echo "$(RED)🚨 Emergency stop - force killing containers...$(RESET)"
	@docker kill $$(docker ps -q --filter "label=com.docker.compose.project") 2>/dev/null || true
	@$(DOCKER_COMPOSE) down --remove-orphans

# Information commands
info:             ## Show project information
	@echo "$(BLUE)Weather MCP Server Project Information$(RESET)"
	@echo "======================================"
	@echo "Project: $(PROJECT_NAME)"
	@echo "Python: $$($(VENV_DIR)/bin/python --version 2>/dev/null || echo 'Not installed')"
	@echo "Docker: $$(docker --version 2>/dev/null || echo 'Not installed')"
	@echo ""
	@echo "$(YELLOW)Services:$(RESET)"
	@echo "• MCP HTTP Server: http://localhost:8081"
	@echo "• AIFS Server: http://localhost:8080"
	@echo "• Redis Cache: localhost:6379"
	@echo ""
	@echo "$(YELLOW)Useful URLs:$(RESET)"
	@echo "• MCP Health: http://localhost:8081/health"
	@echo "• AIFS Health: http://localhost:8080/health"
	@echo "• MCP Tools: http://localhost:8081/tools"