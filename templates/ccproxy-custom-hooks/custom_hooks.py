"""Custom hooks for ccproxy.

Hooks are loaded by ccproxy when specified in ccproxy.yaml under the 'hooks' section.
"""

import logging
from typing import Any

from litellm import get_max_tokens

logger = logging.getLogger(__name__)


def max_tokens_adjuster(
    data: dict[str, Any], user_api_key_dict: dict[str, Any], **kwargs: Any
) -> dict[str, Any]:
    """Adjust max_tokens for models with lower limits than Claude models.

    Claude Code sends max_tokens=21333 which exceeds limits for models like:
    - GPT-4o: 4,096 max completion tokens
    - GPT-4o-mini: 16,384 max completion tokens
    - Gemini: varying limits

    This hook:
    1. Detects the target model from routing metadata
    2. Looks up the model's max_output_tokens limit
    3. Applies a safety margin to avoid edge cases
    4. Adjusts max_tokens if it exceeds the limit

    Args:
        data: Request data from LiteLLM
        user_api_key_dict: User API key dictionary
        **kwargs: Additional keyword arguments including:
            - safety_margin: Optional safety margin (default: 100 tokens)
            - model_limits: Optional dict of model-specific limits

    Returns:
        Modified request data with adjusted max_tokens

    Example configuration in ccproxy.yaml:
        hooks:
          - hook: custom_hooks.max_tokens_adjuster
            params:
              safety_margin: 100
              model_limits:
                "gpt-4o": 4096
                "gpt-4o-mini": 16384
    """
    safety_margin = kwargs.get("safety_margin", 100)
    model_limits = kwargs.get("model_limits", {})

    metadata = data.get("metadata", {})
    routed_model = metadata.get("ccproxy_litellm_model")

    if not routed_model:
        return data

    current_max_tokens = data.get("max_tokens")

    if current_max_tokens is None:
        return data

    model_limit = model_limits.get(routed_model)

    if model_limit is None:
        try:
            # get_max_tokens returns the max OUTPUT tokens for the model
            model_limit = get_max_tokens(routed_model)
        except Exception as e:
            logger.debug(f"Could not get max_tokens for model {routed_model}: {e}")
            return data

    if model_limit is None:
        return data

    effective_limit = model_limit - safety_margin

    if current_max_tokens > effective_limit:
        original_max_tokens = current_max_tokens
        data["max_tokens"] = effective_limit

        logger.info(
            f"Adjusted max_tokens for model {routed_model}",
            extra={
                "event": "max_tokens_adjustment",
                "model": routed_model,
                "original_max_tokens": original_max_tokens,
                "adjusted_max_tokens": effective_limit,
                "model_limit": model_limit,
                "safety_margin": safety_margin,
            },
        )

    return data


def tool_filter(
    data: dict[str, Any], user_api_key_dict: dict[str, Any], **kwargs: Any
) -> dict[str, Any]:
    """Filter or remove tools for models with small context windows.

    Claude Code sends extensive tool definitions (~11,585 tokens) which exceed
    the context window limits of some models like gpt-3.5-turbo (16,385 tokens).

    This hook removes tools for specified models, allowing them to work but
    only with text generation (no tool-calling capabilities).

    Args:
        data: Request data from LiteLLM
        user_api_key_dict: User API key dictionary
        **kwargs: Additional keyword arguments including:
            - models_without_tools: List of models that should have tools removed

    Returns:
        Modified request data with tools removed for specified models

    Example configuration in ccproxy.yaml:
        hooks:
          - hook: custom_hooks.tool_filter
            params:
              models_without_tools:
                - "openai/gpt-3.5-turbo"
                - "gpt-3.5-turbo"
    """
    models_without_tools = kwargs.get("models_without_tools", [])

    metadata = data.get("metadata", {})
    routed_model = metadata.get("ccproxy_litellm_model")

    if not routed_model:
        return data

    if routed_model in models_without_tools:
        original_tools_count = len(data.get("tools", []))

        if original_tools_count > 0:
            data.pop("tools", None)
            data.pop("tool_choice", None)

            logger.info(
                f"Removed {original_tools_count} tools for model {routed_model}",
                extra={
                    "event": "tool_filtering",
                    "model": routed_model,
                    "tools_removed": original_tools_count,
                },
            )

    return data
