.PHONY: clean test type-check lint format install-dev help
.DEFAULT_GOAL := help
PYTHON = uv python
PACKAGE = elastica_mcp_server

# Help message
help:
	@echo "Elastica MCP Server Development Commands"
	@echo "========================================"
	@echo "make install-dev  - Install development dependencies using uv"
	@echo "make test         - Run pytest"
	@echo "make clean        - Remove Python cache files and directories"
	@echo "make type-check   - Run mypy for type checking"
	@echo "make lint         - Run ruff linter"
	@echo "make format       - Run formatters (ruff)"
	@echo "make all-checks   - Run linting, type-checking, and tests"
	@echo "make help         - Show this help message"

# Clean cache directories
clean:
	@echo "Cleaning Python cache files and directories..."
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	@echo "Clean complete!"

# Run tests using pytest
test:
	@echo "Running tests with pytest..."
	pytest tests

# Run mypy for type checking
type-check:
	@echo "Running mypy type checker..."
	$(PYTHON) -m mypy $(PACKAGE)

# Run ruff linter
lint:
	@echo "Running ruff linter..."
	$(PYTHON) -m ruff check $(PACKAGE) tests

# Run formatters
format:
	@echo "Running code formatters..."
	$(PYTHON) -m ruff format $(PACKAGE) tests
	$(PYTHON) -m ruff check --fix $(PACKAGE) tests

# Install development dependencies using uv
install-dev:
	uv sync --all-groups

# Run all checks
all-checks: lint type-check test
	@echo "All checks completed!"
