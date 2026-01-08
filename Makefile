# Makefile for CCProxy Configuration

.PHONY: help lint format check install test clean release tag-release

help:
	@echo "Available commands:"
	@echo "  make lint         - Run linter (ruff check)"
	@echo "  make format       - Format code (ruff format)"
	@echo "  make check        - Run lint + format check"
	@echo "  make install      - Install configuration to ~/.ccproxy/"
	@echo "  make test         - Test installation to /tmp"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make release      - Create release (interactive, VERSION=x.y.z)"
	@echo "  make tag-release  - Create and push release tags (VERSION=x.y.z)"

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

release:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION not specified. Usage: make release VERSION=0.2.0"; \
		exit 1; \
	fi
	@echo "Creating release v$(VERSION)..."
	@echo ""
	@echo "Have you:"
	@echo "  1. Updated __version__ in custom_hooks.py?"
	@echo "  2. Updated CHANGELOG.md?"
	@echo "  3. Run 'make check' successfully?"
	@echo "  4. Committed all changes?"
	@echo ""
	@read -p "Continue with release? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo ""
	@echo "Creating tags..."
	git tag v$(VERSION)
	git tag -f latest
	@echo ""
	@echo "Tags created. Ready to push."
	@echo ""
	@echo "Next steps:"
	@echo "  1. git push origin main"
	@echo "  2. git push origin v$(VERSION)"
	@echo "  3. git push -f origin latest"
	@echo "  4. Create GitHub release at: https://github.com/cearley/ccproxy-custom-hooks/releases/new"
	@echo ""

tag-release:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION not specified. Usage: make tag-release VERSION=0.2.0"; \
		exit 1; \
	fi
	@echo "Creating and pushing tags for v$(VERSION)..."
	git tag v$(VERSION)
	git tag -f latest
	git push origin main
	git push origin v$(VERSION)
	git push -f origin latest
	@echo ""
	@echo "✓ Tags created and pushed!"
	@echo "Create GitHub release: https://github.com/cearley/ccproxy-custom-hooks/releases/new?tag=v$(VERSION)"
