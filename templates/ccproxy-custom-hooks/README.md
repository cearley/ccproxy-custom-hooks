# CCProxy Custom Hooks

This package provides custom hooks for extending ccproxy functionality.

## What Are Hooks?

Hooks process requests at different stages in the ccproxy pipeline. They can inspect, modify, or enhance requests before they're sent to LLM providers.

## Available Hooks In This Package

### `max_tokens_adjuster`

Automatically adjusts `max_tokens` for models with lower output limits than Claude models.

#### The Problem

Claude Code sends `max_tokens=21333` with every request, optimized for Claude models:

```json
{
  "messages": [...],     // Your system prompt + conversation (INPUT)
  "max_tokens": 21333    // Maximum response length (OUTPUT)
}
```

**Model Limits:**
- **Claude models**: Support up to 64k output tokens → `max_tokens=21333` works fine ✅
- **GPT-4o**: Only supports 4,096 output tokens → `max_tokens=21333` fails ❌
- **GPT-4o-mini**: Only supports 16,384 output tokens → `max_tokens=21333` fails ❌
- **Gemini models**: Varying limits → May fail ❌

**Error you'll see without this hook:**
```
max_tokens is too large: 21333. This model supports at most 4096 completion tokens
```

#### What the Hook Does

When a request is routed to a model like GPT-4o, the hook:

1. **Detects the target model**: `gpt-4o`
2. **Looks up its limit**: `4096 max output tokens`
3. **Applies safety margin**: `4096 - 100 = 3996`
4. **Adjusts the request**: Changes `max_tokens` from `21333` to `3996`

```
Before hook: max_tokens=21333 → Error ❌
After hook:  max_tokens=3996  → Success ✅
```

#### What the Hook Does NOT Do

The hook **does NOT truncate or modify your input**:

- ✅ **System prompt**: Completely unchanged
- ✅ **Messages**: All your conversation history stays the same
- ✅ **All other parameters**: Tools, temperature, etc. remain unchanged

The `max_tokens` parameter only controls the **maximum OUTPUT length** (the model's response), not the input. Your system prompt and all messages go through exactly as Claude Code sent them.

#### Why This Matters

This allows Claude Code to work seamlessly with non-Claude models without:
- ❌ Truncating your system prompt
- ❌ Losing any input context
- ❌ Modifying your conversation history

It simply ensures the model doesn't try to generate a response longer than it's capable of.

#### How It Works

**Request Flow:**
```
Claude Code → ccproxy → [rule_evaluator] → [model_router] → [max_tokens_adjuster] → LiteLLM → Provider
```

The hook runs **after routing** so it knows which model the request is going to, then adjusts `max_tokens` based on that model's capabilities.

**Example:**
```
1. Claude Code sends:
   model: "default"
   max_tokens: 21333

2. model_router changes:
   model: "gpt-4o"
   max_tokens: 21333  (still unchanged)

3. max_tokens_adjuster detects gpt-4o and changes:
   model: "gpt-4o"
   max_tokens: 3996  (adjusted to fit model limit)

4. Request sent to OpenAI with safe max_tokens ✅
```

#### Fallback Mechanism

This implementation uses a **two-layer approach**:

1. **Primary (Intelligent)**: The `max_tokens_adjuster` hook dynamically adjusts based on model capabilities
2. **Fallback (Safety Net)**: The `drop_params: true` setting catches any failures

This ensures maximum reliability while maintaining transparency through logging.

#### Testing

After installation, test with different models:

```bash
# Start ccproxy
ccproxy start --detach

# Test with GPT-4o (should work now)
ccproxy run claude --model gpt-4o -p "Say hello"

# Test with Claude (should work as before)
ccproxy run claude --model default -p "Say hello"

# Stop ccproxy
ccproxy stop
```

Check logs to see adjustments:
```bash
tail -100 ~/.ccproxy/litellm.log | grep "Adjusted max_tokens"
```

You should see entries like:
```
Adjusted max_tokens for gpt-4o: 32000 → 3996
```
