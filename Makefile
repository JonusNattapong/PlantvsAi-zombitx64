.PHONY: setup install test lint format clean docs server help

# Variables
PYTHON := python
PIP := pip
PYTEST := pytest
FLAKE8 := flake8
BLACK := black
ISORT := isort
VENV_NAME := venv
DOCS_DIR := docs
SRC_DIR := src
TESTS_DIR := tests

help:
	@echo "Available commands:"
	@echo "  make setup       - สร้างสภาพแวดล้อมเสมือนและติดตั้ง dependencies"
	@echo "  make install     - ติดตั้ง dependencies เท่านั้น"
	@echo "  make dev-install - ติดตั้ง dependencies รวมถึงชุดพัฒนา"
	@echo "  make test        - รันการทดสอบทั้งหมด"
	@echo "  make lint        - ตรวจสอบรูปแบบโค้ด"
	@echo "  make format      - จัดรูปแบบโค้ดอัตโนมัติ"
	@echo "  make clean       - ลบไฟล์ชั่วคราวและ caches"
	@echo "  make docs        - สร้างเอกสาร"
	@echo "  make server      - รันเซิร์ฟเวอร์"

setup:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "Installing dependencies..."
	$(VENV_NAME)/bin/$(PIP) install -r requirements.txt
	$(VENV_NAME)/bin/$(PIP) install -r requirements-dev.txt
	@echo "Setup complete!"
	@echo "Activate your virtual environment with: source $(VENV_NAME)/bin/activate (Linux/Mac) or $(VENV_NAME)\\Scripts\\activate (Windows)"

install:
	$(PIP) install -r requirements.txt

dev-install:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

test:
	$(PYTEST) $(TESTS_DIR) -v

lint:
	$(FLAKE8) $(SRC_DIR)
	$(FLAKE8) $(TESTS_DIR)

format:
	$(BLACK) $(SRC_DIR)
	$(BLACK) $(TESTS_DIR)
	$(ISORT) $(SRC_DIR)
	$(ISORT) $(TESTS_DIR)

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf $(SRC_DIR)/**/__pycache__
	rm -rf $(TESTS_DIR)/**/__pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	@echo "Cleanup complete!"

docs:
	@echo "Building documentation..."
	cd $(DOCS_DIR) && make html
	@echo "Documentation built in $(DOCS_DIR)/_build/html/"

server:
	$(PYTHON) app.py 