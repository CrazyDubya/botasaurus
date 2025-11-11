"""
LLM Integrations
================

Support for multiple LLM providers (OpenAI, Anthropic, local models).
"""

from typing import Optional
from .base import BaseLLMClient


def get_llm_client(
    provider: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> BaseLLMClient:
    """
    Factory function to get appropriate LLM client.

    Args:
        provider: Provider name ("openai", "anthropic", "local")
        api_key: API key for the provider
        model: Specific model to use

    Returns:
        Initialized LLM client
    """
    if provider == "openai":
        from .openai import OpenAIClient
        return OpenAIClient(api_key=api_key, model=model)
    elif provider == "anthropic":
        from .anthropic import AnthropicClient
        return AnthropicClient(api_key=api_key, model=model)
    elif provider == "local":
        from .local_models import LocalModelClient
        return LocalModelClient(model=model)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


__all__ = ["get_llm_client", "BaseLLMClient"]
