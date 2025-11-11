"""
Anthropic (Claude) Integration
===============================

Full implementation of Anthropic API client for code generation.
"""

from typing import List, Dict, Any, Optional
import base64
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base import BaseLLMClient


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API client with full implementation"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")

        self.api_key = api_key
        self.model = model or "claude-3-opus-20240229"
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None

    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate completion using Claude API"""
        if not self.client:
            raise ValueError("Anthropic client not initialized. Provide an API key.")

        try:
            response = self.client.messages.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")

    def complete_with_vision(
        self,
        messages: List[Dict[str, Any]],
        images: List[bytes],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate completion with vision"""
        if not self.client:
            raise ValueError("Anthropic client not initialized. Provide an API key.")

        try:
            # Convert images to base64
            image_contents = []
            for img_bytes in images:
                b64_image = base64.b64encode(img_bytes).decode('utf-8')
                image_contents.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": b64_image
                    }
                })

            # Add images to the last message
            if messages:
                last_message = messages[-1].copy()
                if isinstance(last_message["content"], str):
                    last_message["content"] = [
                        {"type": "text", "text": last_message["content"]},
                        *image_contents
                    ]
                messages = messages[:-1] + [last_message]

            response = self.client.messages.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic Vision API error: {str(e)}")

    def stream_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """Stream completion tokens as they're generated"""
        if not self.client:
            raise ValueError("Anthropic client not initialized. Provide an API key.")

        try:
            with self.client.messages.stream(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise RuntimeError(f"Anthropic streaming error: {str(e)}")
