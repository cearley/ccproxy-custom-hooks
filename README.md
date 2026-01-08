# CCProxy Custom Hooks Project

This is a configuration and custom hooks installer for [ccproxy](https://github.com/starbased-co/ccproxy), a [LiteLLM](https://docs.litellm.ai)-based proxy server that enables [Claude Code](https://claude.com/claude-code) to route requests through multiple AI model providers.

## Core Purpose

The project solves two key problems when using Claude Code with non-Claude models:

1. **Max Tokens Adjustment:** Claude Code sends max_tokens=21333 by default, which exceeds the output limits of many models (e.g., GPT-4o: 4,096 tokens, GPT-4o-mini: 16,384 tokens)
2. **Tool Filtering:** Claude Code sends ~11.5K tokens of tool definitions, which can exceed the context windows of smaller models like gpt-3.5-turbo (16K tokens total)

## Architecture

### Three-Layer System:

1. **Installer** ([install.py](install.py)): Standalone Python script that:
  - Installs the [claude-ccproxy](https://github.com/starbased-co/ccproxy) tool with LiteLLM
  - Deploys configuration files to ~/.ccproxy/
  - Installs the custom hooks Python package
2. **Configuration Templates** (in [templates/](templates/)):
  - [config.yaml](templates/config.yaml): LiteLLM model routing configuration with Claude (OAuth), OpenAI, Gemini, and GitHub Copilot models
  - [ccproxy.yaml](templates/ccproxy.yaml): Hook pipeline configuration defining how requests are processed
  - [ccproxy-custom-hooks/](templates/ccproxy-custom-hooks/): Python package with custom hooks
3. **Custom Hooks** ([custom_hooks.py](templates/ccproxy-custom-hooks/custom_hooks.py)):
  - **max_tokens_adjuster**: Dynamically adjusts max_tokens based on model capabilities
  - **tool_filter**: Removes tools for models that can't fit them in their context window

### Key Features

- **One-command installation**: `uv run install.py` handles everything
- **Multi-provider support**: Claude (OAuth), OpenAI, Gemini, GitHub Copilot
- **OAuth forwarding**: Uses Claude Code's OAuth tokens for free Claude access
- **Intelligent routing**: Aliases like `default`, `think`, `background` map to appropriate Claude models
- **Drop-in replacement**: Set `ANTHROPIC_BASE_URL=http://localhost:4000` and Claude Code routes through the proxy

### Workflow

1. User runs installer → configs deployed to ~/.ccproxy/
2. User starts CCProxy → LiteLLM proxy runs on localhost:4000
3. Claude Code makes requests → CCProxy intercepts and processes through hook pipeline:
  - Rule evaluation
  - Model routing
  - Max tokens adjustment (custom)
  - Tool filtering (custom)
  - OAuth forwarding
4. Request forwarded to appropriate provider

### File Structure

```ultree
/templates/
  ├── ccproxy.yaml          # Hook pipeline config
  ├── config.yaml           # Model routing config
  └── cproxy-custom-hooks/  # Custom hooks package
      ├── custom_hooks.py   # Hook implementations
      ├── pyproject.toml    # Package metadata
      └── README.md         # Hook documentation
install.py                  # Standalone installer
```

The project is currently in development with several test scripts and configuration files for testing different scenarios (OAuth, max tokens, etc.).

## Installation

### Prerequisites

- [uv](https://docs.astral.sh/uv/) package manager (recommended)
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Or Python 3.10+ (fallback, but `uv` required for ccproxy installation)


### Quick Start

The installer handles everything:
- Installs `claude-ccproxy` tool with LiteLLM
- Deploys configuration files to `~/.ccproxy/` or custom directory
- Installs custom hooks package

**From GitHub:**
```bash
uv run https://raw.githubusercontent.com/cearley/ccproxy-custom-hooks/main/install.py
```

**From local directory:**
```bash
git clone https://github.com/cearley/ccproxy-custom-hooks.git
cd ccproxy-custom-hooks
uv run install.py
# Or: python3 install.py
```

**Custom installation directory:**
```bash
CCPROXY_CONFIG_DIR=/custom/path uv run install.py
```

*Development Note:* The installer is idempotent - safe to run multiple times:

**From local directory:**
```bash
# Edit files in templates/
# Re-run installer
uv run install.py
# Or: python3 install.py

# Restart ccproxy
ccproxy restart
```

**Note:** Re-running overwrites deployed files in `~/.ccproxy/`. Edit templates, not deployed files.

### Start CCProxy

```bash
ccproxy start --detach  # Start in background
ccproxy status          # Check status
ccproxy logs -f         # View logs
ccproxy stop            # Stop server
```

### Check Version

```bash
# Check installed custom hooks version
cat ~/.ccproxy/ccproxy-custom-hooks/VERSION

# Or check from custom directory
cat $CCPROXY_CONFIG_DIR/ccproxy-custom-hooks/VERSION
```

## Usage

### Using CCProxy CLI Wrapper for Claude Code

With ccproxy running, use the `ccproxy run claude` command to access Claude models via OAuth:

```bash
# Start ccproxy first
ccproxy start --detach

# Use Claude models (OAuth - no additional cost)
ccproxy run claude -p "Say hello"
ccproxy run claude --model think -p "Complex reasoning task"
ccproxy run claude --model background -p "Simple task"

# Use OpenAI models
ccproxy run claude --model gpt-4o-mini -p "Your prompt here"
# Use Gemini models
ccproxy run claude --model gemini-flash-latest -p "Your prompt here"
```

**Important:** OAuth tokens from Claude Code are restricted to Claude Code only. Direct API requests with OAuth tokens (see below) will be rejected by Anthropic.

### Using Direct API Calls

With ccproxy running you can send requests directly to the LiteLLM proxy endpoint:

```bash
# Chat completion
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_MASTER_KEY>" \
  -d '{
    "model": "default",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'

# List available models
curl http://localhost:4000/v1/models \
  -H "Authorization: Bearer <YOUR_MASTER_KEY>"
```

**Important:** Because Claude Code OAuth tokens are restricted, you cannot send direct API requests to Anthropic provided models using those tokens. You will need to obtain an API key from Anthropic for direct API access to their models, and set `api_key` accordingly in your LiteLLM configuration for those models.

## Testing

### Health Check

```bash
curl http://localhost:4000/health/liveliness
# Returns: "I'm alive!"
```

### Test with different models

```bash
# Test Claude (OAuth)
ccproxy run claude -p "What is 2+2?"

# Test Gemini
ccproxy run claude -m gemini-flash-latest -p "What is 2+2?"

# Test OpenAI
ccproxy run claude -m gpt-4o-mini -p "What is 2+2?"
```

## Model Selection Guidelines

- **`default` (Sonnet)**: General-purpose tasks, balanced speed/quality
- **`think` (Opus)**: Complex reasoning, creative writing, hard problems
- **`background` (Haiku)**: Simple tasks, quick responses, high volume
- **`gpt-4o-mini`**: Cost-effective alternative to Claude models
- **`gemini-flash-latest`**: Fast responses, good for simple queries

## Environment Variables

- `CCPROXY_CONFIG_DIR`: Custom configuration directory (default: `~/.ccproxy/`)
- `ANTHROPIC_BASE_URL`: Set to `http://localhost:4000` to route Claude Code through ccproxy
- `ANTHROPIC_AUTH_TOKEN`: Your LiteLLM master key for authentication

## Further Reading

- [CCProxy Main README](https://github.com/starbased-co/ccproxy)
- [LiteLLM Documentation](https://docs.litellm.ai)
- [Claude Code Documentation](https://claude.com/claude-code)
