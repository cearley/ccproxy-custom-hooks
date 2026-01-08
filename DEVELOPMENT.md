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
