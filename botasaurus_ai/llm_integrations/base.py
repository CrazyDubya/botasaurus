"""
Base LLM Client Interface
==========================

Abstract base class for all LLM integrations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseLLMClient(ABC):
    """Base class for LLM clients"""

    @abstractmethod
    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Generate a completion from messages.

        Args:
            messages: List of message dicts with "role" and "content"
            temperature: Sampling temperature (0.0 - 2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters

        Returns:
            Generated text completion
        """
        pass

    @abstractmethod
    def complete_with_vision(
        self,
        messages: List[Dict[str, Any]],
        images: List[bytes],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Generate a completion with image inputs.

        Args:
            messages: List of message dicts
            images: List of image bytes
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Provider-specific parameters

        Returns:
            Generated text completion
        """
        pass

    @abstractmethod
    def stream_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        Stream completion tokens as they're generated.

        Args:
            messages: List of message dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Provider-specific parameters

        Yields:
            Completion tokens as they arrive
        """
        pass
