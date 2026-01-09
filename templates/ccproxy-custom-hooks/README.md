# CCProxy Custom Hooks

Custom hooks for extending ccproxy functionality.

## Available Hooks

### `max_tokens_adjuster`

Adjusts `max_tokens` for models with lower limits than Claude models.

#### The Problem

Claude Code sends `max_tokens=21333` optimized for Claude models (64k output tokens), but many models have lower limits:

- **GPT-4o**: 4,096 max output tokens
- **GPT-4o-mini**: 16,384 max output tokens
- **Gemini**: Varying limits

Without adjustment, you'll get errors like:
```
max_tokens is too large: 21333. This model supports at most 4096 completion tokens
```

#### Why Not Just Set max_tokens in config.yaml?

LiteLLM supports static `max_tokens` configuration:

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      max_tokens: 4096  # Static limit
```

However, this doesn't work with CCProxy because:

1. **Client Override**: Request parameters from Claude Code override static config values
2. **Dynamic Routing**: The actual model isn't known until after routing:
   ```
   Request: "default" → [routing] → Could be gpt-4o or claude-sonnet-4-5-20250929
   ```
   Static config can't adapt per-request
3. **Timing**: Must adjust AFTER routing completes to know which model's limits to apply

#### How the Hook Works

```
Claude Code (max_tokens=21333)
    ↓
[rule_evaluator] → classifies request type
    ↓
[model_router] → routes "default" to "gpt-4o"
    ↓
[max_tokens_adjuster] → detects gpt-4o limit (4096), adjusts to 3996
    ↓
LiteLLM → sends request with safe max_tokens
```

The hook:
1. Detects the routed model from metadata
2. Looks up the model's limit using `litellm.get_max_tokens()`
3. Applies a safety margin (default 100 tokens)
4. Adjusts only if the client's value exceeds the limit

Note: Only `max_tokens` (output length) is modified. System prompts, messages, and other parameters are unchanged.

#### Verification

Test the hook with different models:

```bash
ccproxy start --detach
ccproxy run claude --model gpt-4o -p "Say hello"
ccproxy run claude --model default -p "Say hello"
```

Check logs for adjustments:
```bash
tail -100 ~/.ccproxy/litellm.log | grep "Adjusted max_tokens"
# Output: Adjusted max_tokens for gpt-4o: 21333 → 3996
```

### `tool_filter`

Removes tool definitions for models with small context windows.

#### The Problem

Claude Code sends extensive tool definitions (~11,585 tokens) with every request. Some models like `gpt-3.5-turbo` have small context windows (16,385 tokens total) where tools would consume most of the available space, leaving little room for your actual conversation.

#### How It Works

For specified models, the hook removes all tool definitions from the request. The model will only generate text responses (no tool calls), but can still process your full conversation.

Configure in `ccproxy.yaml`:
```yaml
hooks:
  - hook: custom_hooks.tool_filter
    params:
      models_without_tools:
        - "gpt-3.5-turbo"
```
