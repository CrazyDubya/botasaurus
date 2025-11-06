"""
OpenAI Integration
==================

Full implementation of OpenAI API client for code generation.
"""

from typing import List, Dict, Any, Optional
import base64
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .base import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """OpenAI API client with full implementation"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

        self.api_key = api_key
        self.model = model or "gpt-4"
        self.client = openai.OpenAI(api_key=api_key) if api_key else None

    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate completion using OpenAI API"""
        if not self.client:
            raise ValueError("OpenAI client not initialized. Provide an API key.")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    def complete_with_vision(
        self,
        messages: List[Dict[str, Any]],
        images: List[bytes],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate completion with vision (GPT-4V)"""
        if not self.client:
            raise ValueError("OpenAI client not initialized. Provide an API key.")

        try:
            # Convert images to base64
            image_contents = []
            for img_bytes in images:
                b64_image = base64.b64encode(img_bytes).decode('utf-8')
                image_contents.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{b64_image}"
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

            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI Vision API error: {str(e)}")

    def stream_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """Stream completion tokens as they're generated"""
        if not self.client:
            raise ValueError("OpenAI client not initialized. Provide an API key.")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise RuntimeError(f"OpenAI streaming error: {str(e)}")
