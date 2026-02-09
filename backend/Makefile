.PHONY: help install test run build deploy clean

help:
	@echo "CloudOptima - Development Commands"
	@echo "install   - Install dependencies"
	@echo "test      - Run tests with coverage"
	@echo "run       - Start development server"
	@echo "build     - Build Docker image"
	@echo "deploy    - Deploy to local Docker"
	@echo "clean     - Clean temporary files"

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v --cov=. --cov-report=html

run:
	python app.py

build:
	docker build -t cloudoptima:latest .

deploy:
	docker-compose up -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov