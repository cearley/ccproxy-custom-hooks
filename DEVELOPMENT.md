## Development Setup

### 1. Install Dependencies

```bash
# Install ruff for linting and formatting
pip install ruff

# Optional: Install pre-commit for automatic checks
pip install pre-commit
pre-commit install
```

### 2. Code Quality Tools

We use **Ruff** for both linting and formatting. It's fast, comprehensive, and configured in `ruff.toml`.

#### Quick Commands (via Makefile)

```bash
# Show available commands
make help

# Format code
make format

# Run linter
make lint

# Check both lint and format
make check

# Clean build artifacts
make clean
```

#### Direct Ruff Commands

```bash
# Format all Python files
ruff format .

# Lint and auto-fix issues
ruff check --fix .

# Check without fixing
ruff check .
```

### 3. Pre-commit Hooks (Recommended)

Pre-commit hooks automatically run checks before each git commit:

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

The hooks will:
- Format code with Ruff
- Fix linting issues automatically
- Check YAML syntax
- Remove trailing whitespace
- Detect private keys


### 4. Testing Your Changes

```bash
# Test installation locally
make test

# Or directly
python3 install.py

# Test with custom directory
CCPROXY_CONFIG_DIR=/tmp/test python3 install.py
```

## Common Tasks

### Adding a New Template File

1. Add file to `templates/` directory
2. Update `install.py` to copy the new file
3. Update README.md if needed
4. Test the installation

### Modifying the Installer

1. Edit `install.py`
2. Run `make format` to format code
3. Run `make lint` to check for issues
4. Test with `make test`

### Updating Dependencies

Update the PEP 723 metadata in `install.py`:

```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["package-name"]
# ///
```

### Bumping Version

Version is managed in a single location:

**`templates/ccproxy-custom-hooks/custom_hooks.py`**
```python
__version__ = "0.1.0"  # Update this line only
```

The version automatically propagates to:
- `pyproject.toml` (via dynamic versioning)
- `install.py` (extracted at runtime)
- `~/.ccproxy/ccproxy-custom-hooks/VERSION` file (written during installation)

## Release Process

Follow these steps to create a new release:

### 1. Update Version

Edit the version in `templates/ccproxy-custom-hooks/custom_hooks.py`:

```python
__version__ = "0.2.0"  # Bump to new version
```

The version automatically propagates to:
- `pyproject.toml` (via dynamic versioning)
- `install.py` (extracted at runtime)
- `~/.ccproxy/ccproxy-custom-hooks/VERSION` file (written during installation)

### 2. Update CHANGELOG.md

Move unreleased changes to a new version section:

```markdown
## [0.2.0] - 2026-01-XX

### Added
- New feature description

### Changed
- Changed behavior description

### Fixed
- Bug fix description
```

Update the comparison links at the bottom:

```markdown
[Unreleased]: https://github.com/cearley/ccproxy-custom-hooks/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/cearley/ccproxy-custom-hooks/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/cearley/ccproxy-custom-hooks/releases/tag/v0.1.0
```

### 3. Run Tests

Ensure code quality and test installation:

```bash
make format
make lint
make test
```

### 4. Commit Changes

```bash
git add templates/ccproxy-custom-hooks/custom_hooks.py CHANGELOG.md
git commit -m "Bump version to 0.2.0"
```

### 5. Create and Push Tags

**Option A: Interactive (recommended for first time):**
```bash
make release VERSION=0.2.0
# Follow prompts, then manually push
```

**Option B: Automated:**
```bash
make tag-release VERSION=0.2.0
# Creates tags and pushes automatically
```

### 6. Create GitHub Release

1. Go to https://github.com/cearley/ccproxy-custom-hooks/releases/new
2. Select tag: `v0.2.0`
3. Title: `v0.2.0`
4. Copy relevant section from CHANGELOG.md into description
5. Publish release

### Version Tag Strategy

- **Version tags** (v0.1.0, v0.2.0): Permanent, never moved
- **Latest tag**: Moving pointer, force-updated with each release
- Users wanting stability: pin to version tags
- Users wanting latest: use `latest` tag

### Semantic Versioning Guidelines

- **Major (x.0.0)**: Breaking changes to hook APIs or configuration format
- **Minor (0.x.0)**: New features, new hooks, backward-compatible changes
- **Patch (0.0.x)**: Bug fixes, documentation updates, minor improvements
