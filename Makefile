# Phony targets
.PHONY: all clean help install reinstall test

# Variables (consider using environment variables for flexibility)
PYTHON := $(shell which python3)  # Get path to Python 3 (adjust if needed)
PIP := venv/bin/pip  # Use pip from virtual environment

# Targets

all: clean install test  # Install and run tests by default

help:
	@echo "Available targets:"
	@echo "  clean  	- Remove build artifacts"
	@echo "  venv   	- Create a virtual environment"
	@echo "  help   	- Print this help message"
	@echo "  install 	- Install the nfa-broker library"
	@echo "  uninstall 	- Uninstall the nfa-broker library"
	@echo "  reinstall 	- Uninstall and reinstall the library"
	@echo "  test    	- Run tests for the nfa-broker library"

clean:
	# Remove build artifacts (consider using more specific commands)
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete -type d

venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv venv
	@echo "Virtual environment created in venv."

install:
	@$(PIP) install -e .

uninstall:
	@$(PIP) uninstall -y nfa-broker

reinstall: uninstall install

test: install
	@echo "Running tests..."
	pytest tests
