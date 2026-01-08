# CCProxy Configuration Project

## Architecture

Stand-alone CCProxy with LiteLLM model routing and OAuth hooks:
- Running on localhost:4000
- Configuration managed via install.py
- Custom hooks for max_tokens adjustment

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
- Installs claude-ccproxy tool
- Deploys configuration files to ~/.ccproxy/
- Installs custom hooks package
- Sets up LiteLLM with proxy support

## Key Files

Configuration files in `~/.ccproxy/` (or custom directory):
- `config.yaml` - LiteLLM model routing configuration
- `ccproxy.yaml` - Hook configurations (rule_evaluator, model_router, forward_oauth, max_tokens_adjuster)
- `ccproxy-custom-hooks/` - Custom hooks Python package

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

After editing template files:

```bash
# Re-run installer to update deployed files
python3 install.py

# Restart ccproxy
ccproxy restart
```
