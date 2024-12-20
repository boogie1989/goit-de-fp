# Variables
ENV_DIR = venv
PYTHON = python3.11
REQUIREMENTS = requirements.txt
TASK_1_MAIN = task_1/main.py
TASK_2_MAIN = task_2/main.py

# Default target
all: create_env install_deps

# Create virtual environment
create_env:
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(ENV_DIR)
	@echo "Virtual environment created in $(ENV_DIR)"

# Install dependencies
install_deps: create_env
	@echo "Installing dependencies..."
	@$(ENV_DIR)/bin/pip install --upgrade pip
	@$(ENV_DIR)/bin/pip install -r $(REQUIREMENTS)
	@echo "Dependencies installed."

# Run Task 1
run_task_1:
	@echo "Running Task 1..."
	@PYTHONPATH=$$(pwd) $(ENV_DIR)/bin/python $(TASK_1_MAIN)

# Run Task 2
run_task_2:
	@echo "Running Task 2..."
	@PYTHONPATH=$$(pwd) $(ENV_DIR)/bin/python $(TASK_2_MAIN)

# Clean the virtual environment
clean:
	@echo "Cleaning up..."
	@rm -rf $(ENV_DIR)
	@echo "Virtual environment removed."

# Help message
help:
	@echo "Makefile commands:"
	@echo "  make all          - Create virtual environment and install dependencies."
	@echo "  make create_env   - Create a virtual environment."
	@echo "  make install_deps - Install dependencies from requirements.txt."
	@echo "  make run_task_1   - Run the main application for Task 1."
	@echo "  make run_task_2   - Run the main application for Task 2."
	@echo "  make clean        - Remove the virtual environment."
	@echo "  make help         - Show this help message."
