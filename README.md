# CCProxy Custom Hooks

Custom hooks for [CCProxy](https://github.com/starbased-co/ccproxy) that enable [Claude Code](https://claude.com/claude-code) to work seamlessly with multiple AI model providers through [LiteLLM](https://docs.litellm.ai).

## What It Does

Solves two key compatibility issues when using Claude Code with non-Claude models:

1. **Max Tokens Adjustment** - Claude Code sends `max_tokens=21333` by default, exceeding most models' limits (GPT-4o: 4,096, GPT-4o-mini: 16,384)
2. **Tool Filtering** - Claude Code sends ~11.5K tokens of tool definitions, which can overflow smaller model contexts (e.g., gpt-3.5-turbo's 16K total)

The hooks automatically adjust request parameters based on target model capabilities.

## Installation

**Prerequisites:** [uv](https://docs.astral.sh/uv/) package manager (or Python 3.10+)

```bash
# Latest release
uv run https://raw.githubusercontent.com/cearley/ccproxy-custom-hooks/v0.1.2/install.py

# From local directory
git clone https://github.com/cearley/ccproxy-custom-hooks.git
cd ccproxy-custom-hooks
uv run install.py
```

**What gets installed:**
- Custom hooks package to `~/.ccproxy/ccproxy-custom-hooks/`
- Example config files: `config.example.yaml` and `ccproxy.example.yaml`
- CCProxy tool (if not already installed)

**First install:**
- Creates working configs (`config.yaml`, `ccproxy.yaml`) from examples
- Installs custom hooks package
- Installs `claude-ccproxy` tool if needed

**Upgrades:**
- Updates `.example` files and custom hooks package
- Preserves your `config.yaml` and `ccproxy.yaml`
- Compare configs: `diff ~/.ccproxy/config.yaml ~/.ccproxy/config.example.yaml`

**Custom directory:**
```bash
CCPROXY_CONFIG_DIR=/custom/path uv run install.py
```

## Configuration

The included `.example` files demonstrate how to:
- Configure hooks in the processing pipeline
- Set up multiple model providers (Claude, OpenAI, Gemini, GitHub Copilot)
- Define model-specific parameter limits

**To customize:**
1. Edit `~/.ccproxy/config.yaml` or `~/.ccproxy/ccproxy.yaml`
2. Restart: `ccproxy restart`

**Note:** The `.example` files are reference documentation - edit the actual config files, not the examples.

## Usage

```bash
# Start CCProxy
ccproxy start --detach

# Use with Claude Code
export ANTHROPIC_BASE_URL="http://localhost:4000"

# Or use ccproxy wrapper
ccproxy run claude -p "Your prompt"
ccproxy run claude --model gpt-4o-mini -p "Your prompt"
ccproxy run claude --model gemini-flash-latest -p "Your prompt"

# Check status
ccproxy status
ccproxy logs -f
```

## Custom Hooks

Located in `ccproxy-custom-hooks/custom_hooks.py`:

**max_tokens_adjuster** - Adjusts `max_tokens` based on model capabilities
```yaml
- hook: custom_hooks.max_tokens_adjuster
  params:
    safety_margin: 100  # Buffer tokens
    model_limits:       # Override LiteLLM's defaults
      "gpt-4o": 4096
      "gemini-2.5-flash": 8192
```

**tool_filter** - Removes tools for small-context models
```yaml
- hook: custom_hooks.tool_filter
  params:
    models_without_tools:
      - "gpt-3.5-turbo"
```

## File Structure

```
ccproxy-custom-hooks/
├── ccproxy.example.yaml    # Hook pipeline configuration example
├── config.example.yaml     # Model routing configuration example
├── ccproxy-custom-hooks/   # Custom hooks package
│   ├── custom_hooks.py     # Hook implementations
│   └── pyproject.toml      # Package metadata
└── install.py              # Installer
```

## Version Check

```bash
cat ~/.ccproxy/ccproxy-custom-hooks/VERSION
```

## Further Reading

- [CCProxy Documentation](https://github.com/starbased-co/ccproxy)
- [LiteLLM Documentation](https://docs.litellm.ai)
- [Claude Code](https://claude.com/claude-code)
