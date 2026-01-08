# CCProxy Configuration

LiteLLM proxy with CCProxy hooks for intelligent routing and token management across multiple LLM providers.

## Features

- **Multi-Provider Support**: Claude (via OAuth), OpenAI, and Gemini models through a single endpoint
- **OAuth Integration**: Use Claude Pro subscription without additional API costs
- **Smart Token Management**: Automatic max_tokens adjustment for different models
- **Intelligent Routing**: Dynamic model selection and fallbacks
- **One-Command Installation**: Complete setup with a single installer script

## Installation

### Prerequisites

- [uv](https://docs.astral.sh/uv/) package manager (recommended)
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Or Python 3.10+ (fallback, but `uv` required for ccproxy installation)


### Quick Start

The installer handles everything:
- Installs `claude-ccproxy` tool
- Deploys configuration files to `~/.ccproxy/`
- Installs custom hooks package
- Sets up LiteLLM with proxy support

**From GitHub:**
```bash
uv run https://raw.githubusercontent.com/yourusername/yourrepo/main/install.py
```

**From local directory:**
```bash
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
