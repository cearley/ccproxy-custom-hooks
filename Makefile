# Makefile for CCProxy Configuration

.PHONY: help lint format check install test clean

help:
	@echo "Available commands:"
	@echo "  make lint      - Run linter (ruff check)"
	@echo "  make format    - Format code (ruff format)"
	@echo "  make check     - Run lint + format check"
	@echo "  make install   - Install configuration to ~/.ccproxy/"
	@echo "  make test      - Test installation to /tmp"
	@echo "  make clean     - Remove build artifacts"

lint:
	@echo "Running ruff linter..."
	ruff check .

format:
	@echo "Formatting code with ruff..."
	ruff format .

check: lint
	@echo "Checking formatting..."
	ruff format --check .

install:
	@echo "Installing configuration..."
	python3 install.py

test:
	@echo "Testing installation to /tmp/ccproxy-test..."
	CCPROXY_CONFIG_DIR=/tmp/ccproxy-test python3 install.py

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"
