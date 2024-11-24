.PHONY: help install dev-install lint test clean build up down logs shell migrate

help:
	@echo "Available commands:"
	@echo "install      - Install production dependencies"
	@echo "dev-install - Install development dependencies"
	@echo "lint        - Run code quality checks"
	@echo "test        - Run tests"
	@echo "clean       - Clean up build artifacts"
	@echo "build       - Build Docker images"
	@echo "up          - Start Docker containers"
	@echo "down        - Stop Docker containers"
	@echo "logs        - View Docker container logs"
	@echo "shell       - Open shell in web container"
	@echo "migrate     - Run database migrations"

install:
	poetry install --no-dev

dev-install:
	poetry install

lint:
	poetry run black .
	poetry run isort .
	poetry run flake8
	poetry run mypy src

test:
	poetry run pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec web /bin/bash

migrate:
	docker-compose exec web poetry run alembic upgrade head
