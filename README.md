# LiteLLM Proxy with CCProxy

LiteLLM proxy server with CCProxy hooks for routing and token management.

## Status

✅ **Working Configuration** - CCProxy is successfully running and routing requests to:
- Claude models (via OAuth/Claude Pro subscription)
- OpenAI models (via API key)
- Gemini models (via API key)

CCProxy is installed directly and running on localhost:4000.

## Quick Start

### Using Direct CCProxy Installation

```bash

# Start ccproxy
ccproxy start --detach

# Check status
ccproxy status

# View logs
ccproxy logs [-f]

# Stop ccproxy
ccproxy stop
```

### Using Docker Compose (Alternative)

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

## Services

- **CCProxy/LiteLLM**: http://localhost:4000
- **PostgreSQL**: localhost:5432
- **Prometheus**: http://localhost:9090

## Configuration

- `.env` - API keys and credentials
- `config.yaml` - LiteLLM model configurations
- `ccproxy.yaml` - CCProxy hooks and routing rules

## Available Models

- `default` - Claude Sonnet 4.5
- `think` - Claude Opus 4.5
- `background` - Claude 3.5 Haiku
- GitHub Copilot models
- OpenAI GPT models
- Gemini models

## Usage

Point your application to `http://localhost:4000` with the master key from `.env`:

```bash
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="<YOUR_MASTER_KEY>"
```

## Testing the Proxy

### Health Check

```bash
curl http://localhost:4000/health/liveliness
# Returns: "I'm alive!"
```

### List Models

```bash
curl http://localhost:4000/v1/models \
  -H "Authorization: Bearer <YOUR_MASTER_KEY>"
```

### Chat Completion (with working model)

```bash
cat > /tmp/test.json << 'EOF'
{
  "model": "gemini/gemini-flash-latest",
  "messages": [{"role": "user", "content": "Say hello"}],
  "max_tokens": 100
}
EOF

curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_MASTER_KEY>" \
  -d @/tmp/test.json
```

### Using Claude CLI (Expected per ccproxy README)

```bash
ANTHROPIC_BASE_URL="http://localhost:4000" \
ANTHROPIC_AUTH_TOKEN="<YOUR_MASTER_KEY>" \
claude -p "Say hello"
```

**Note**: Replace `<YOUR_MASTER_KEY>` with your actual `LITELLM_MASTER_KEY` from `.env`

## CCProxy Configuration

CCProxy hooks enabled:
- `forward_oauth` - OAuth token forwarding for Claude.ai Pro
- `model_router` - Dynamic model routing
- `rule_evaluator` - Request evaluation rules

Available Claude model aliases:
- `default` / `claude-sonnet-4-5-20250929` → Claude Sonnet 4.5
- `think` / `claude-opus-4-5-20251101` → Claude Opus 4.5
- `background` / `claude-haiku-4-5-20251001` / `claude-3-5-haiku-20241022` → Claude Haiku

## How to Use Different Models from Claude Code

CCProxy provides access to multiple LLM providers through a single endpoint, allowing you to use Claude (via OAuth), OpenAI, and Gemini models interchangeably.

### Available Models

**Claude Models (via Claude Pro OAuth subscription):**
- `default` or `claude-sonnet-4-5-20250929` - Claude Sonnet 4.5
- `think` or `claude-opus-4-5-20251101` - Claude Opus 4.5
- `background` or `claude-3-haiku-20240307` - Claude 3 Haiku

**OpenAI Models (via API key):**
- `gpt-4o` - GPT-4 Omni
- `gpt-4o-mini` - GPT-4 Omni Mini
- `gpt-3.5-turbo` - GPT-3.5 Turbo

**Gemini Models (via API key):**
- `gemini-2.0-flash-exp` - Gemini 2.0 Flash (experimental)
- `gemini-flash-latest` - Gemini Flash (latest stable)

### Method 1: Using ccproxy CLI Wrapper

```bash
# Source environment variables first
source /Users/craig/.litellm/.env

# Start ccproxy (if not already running)
cd /Users/craig/.ccproxy && ccproxy start

# Use Claude models (OAuth - no additional cost)
ccproxy run claude -p "Say hello"
ccproxy run claude -m think -p "Complex reasoning task"
ccproxy run claude -m background -p "Simple task"

# Use OpenAI models
ccproxy run claude -m gpt-4o-mini -p "Your prompt here"
ccproxy run claude -m gpt-4o -p "Your prompt here"

# Use Gemini models
ccproxy run claude -m gemini-flash-latest -p "Your prompt here"
ccproxy run claude -m gemini-2.0-flash-exp -p "Your prompt here"
```

### Method 2: Direct API Calls

```bash
# Using Claude model with OAuth
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_MASTER_KEY>" \
  -d '{
    "model": "default",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'

# Using Gemini model
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_MASTER_KEY>" \
  -d '{
    "model": "gemini-flash-latest",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'

# Using OpenAI model
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_MASTER_KEY>" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'
```

### Method 3: From Claude Code CLI

Configure Claude Code to use ccproxy as its backend:

```bash
# Set environment variables (add to your shell profile)
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="<YOUR_MASTER_KEY>"

# Now Claude Code will route through ccproxy
claude -p "Your prompt here"

# To use a specific model, you'll need to specify it in API calls
# or use the ccproxy wrapper shown in Method 1
```

### Benefits of This Setup

✅ **Claude Models**: Use your Claude Pro OAuth subscription (no additional API costs)
✅ **Cost Tracking**: All requests logged to PostgreSQL database via LiteLLM
✅ **Intelligent Routing**: LiteLLM handles retries, fallbacks, and load balancing
✅ **Multi-Provider**: Switch between Claude, OpenAI, and Gemini without changing code
✅ **Observability**: Prometheus metrics available at http://localhost:9090

### Model Selection Guidelines

- **Use `default` (Sonnet)**: General-purpose tasks, balanced speed/quality
- **Use `think` (Opus)**: Complex reasoning, creative writing, hard problems
- **Use `background` (Haiku)**: Simple tasks, quick responses, high volume
- **Use `gpt-4o-mini`**: Cost-effective alternative to Claude models
- **Use `gemini-flash-latest`**: Fast responses, good for simple queries

## Working Configuration Notes

### Current Setup (Verified Working)

This configuration uses **ccproxy installed directly** (not Docker Compose):

- **Installation**: CCProxy CLI installed via pip/uv
- **Running on**: `localhost:4000`
- **Configuration Directory**: `/Users/craig/.ccproxy/`

### Key Configuration Files

1. **ccproxy.yaml**: Hook configurations in `/Users/craig/.ccproxy/`
   - `forward_oauth`: Routes Claude requests through OAuth
   - `model_router`: Dynamic model selection and routing
   - `rule_evaluator`: Request validation and rule enforcement

2. **config.yaml**: LiteLLM model definitions
   - Claude model aliases (default, think, background)
   - OpenAI model configurations
   - Gemini model configurations

### Confirmed Working Features

✅ Claude models via OAuth (no API costs with Pro subscription)
✅ OpenAI models via API key
✅ Gemini models via API key
✅ Model routing and aliasing
✅ Claude Code CLI integration
