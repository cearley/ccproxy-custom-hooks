# CCProxy Custom Hooks

## Architecture

[CCProxy](https://github.com/starbased-co/ccproxy) ([LiteLLM](https://docs.litellm.ai)-based proxy for [Claude Code](https://claude.com/claude-code)) custom hooks installer.

Includes ccproxy.yaml and config.yaml (litellm) configurations and custom hooks for:
- max tokens adjustment based on model context window
- tool filtering based on model capabilities

## Installation

Use the standalone installer (installs everything):

```bash
# From local directory
uv run install.py

# Or with Python
python3 install.py

# Custom directory
CCPROXY_CONFIG_DIR=/custom/path uv run install.py
```

The installer automatically:
- Installs claude-ccproxy tool with LiteLLM
- Deploys configuration files to ~/.ccproxy/ or custom directory
- Installs custom hooks package

## Key Files

Template files in repository:
- `config.example.yaml` - LiteLLM model routing configuration template
- `ccproxy.example.yaml` - Hook configurations template
- `ccproxy-custom-hooks/` - Custom hooks Python package

Deployed files in `~/.ccproxy/` (or custom directory):
- `config.yaml` - Your active LiteLLM configuration (preserved on upgrade)
- `ccproxy.yaml` - Your active hook configuration (preserved on upgrade)
- `config.example.yaml` - Latest template reference (updated on upgrade)
- `ccproxy.example.yaml` - Latest template reference (updated on upgrade)
- `ccproxy-custom-hooks/` - Custom hooks Python package (replaced on upgrade)

## CCProxy Commands

```bash
# Start the proxy server
ccproxy start --detach

# Check proxy status
ccproxy status

# View proxy logs
ccproxy logs [-f]

# Stop the proxy server
ccproxy stop

# Check installed custom hooks version
cat ~/.ccproxy/ccproxy-custom-hooks/VERSION
```

## Usage with Claude Code

Configure Claude Code to use CCProxy:

```bash
# Set environment variables (add to your shell profile)
export ANTHROPIC_BASE_URL="http://localhost:4000"

# Or use ccproxy's wrapper
ccproxy run claude -p "Your prompt"
ccproxy run claude --model <model-name> -p "Your prompt"
```

**Important:** OAuth tokens from Claude Code are restricted to Claude Code only. Direct API requests with the OAuth token will be rejected by Anthropic.

## Configuration Updates

To modify your configuration:

1. Edit `~/.ccproxy/config.yaml` or `~/.ccproxy/ccproxy.yaml` directly
2. Restart ccproxy: `ccproxy restart`

**Upgrading to a new version:**

```bash
# Re-run installer (preserves your configs)
python3 install.py

# Compare changes
diff ~/.ccproxy/config.yaml ~/.ccproxy/config.example.yaml

# Merge any new settings as needed

# Restart ccproxy
ccproxy restart
```

**Note:** `.example` files are templates - edit the actual config files, not the examples.

## Release Management

### Creating a New Release

The project uses semantic versioning with git tags for releases.

**Quick Release:**
```bash
# 1. Update version and CHANGELOG
vim ccproxy-custom-hooks/custom_hooks.py  # Bump __version__
vim CHANGELOG.md  # Add release notes

# 2. Test and commit
make check
git commit -am "Bump version to 0.2.0"

# 3. Create and push tags
make tag-release VERSION=0.2.0

# 4. Create GitHub release (copy CHANGELOG section)
# Visit: https://github.com/cearley/ccproxy-custom-hooks/releases/new
```

**Detailed process documented in DEVELOPMENT.md**

### Version Strategy

- **Version source**: `ccproxy-custom-hooks/custom_hooks.py` (`__version__` variable)
- **Git tags**: `v0.1.0`, `v0.2.0`, etc. (permanent)
- **Latest tag**: Moving pointer to most recent release
- **CHANGELOG**: Maintained in `CHANGELOG.md` following keepachangelog.com format

### Installation from Releases

**Latest release:**
```bash
uv run https://raw.githubusercontent.com/cearley/ccproxy-custom-hooks/latest/install.py
```

**Specific version:**
```bash
uv run https://raw.githubusercontent.com/cearley/ccproxy-custom-hooks/v0.1.0/install.py
```
