"""
LLM provider implementations.

Each provider handles the actual API calls for a specific service.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import json
import os

from pydantic import BaseModel

from .config import LLMConfig


@dataclass
class Message:
    """A chat message."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResult:
    """Result from an LLM call."""
    content: str
    input_tokens: int
    output_tokens: int
    model: str
    raw_response: Any = None


class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        config: LLMConfig,
        response_model: type[BaseModel] | None = None,
    ) -> LLMResult:
        """
        Send a completion request.

        Args:
            messages: Chat messages
            config: LLM configuration
            response_model: Optional Pydantic model for structured output

        Returns:
            LLMResult with generated content
        """
        pass

    def _format_structured_prompt(
        self,
        messages: list[Message],
        response_model: type[BaseModel],
    ) -> list[Message]:
        """Add JSON schema instructions to messages."""
        schema = response_model.model_json_schema()
        schema_str = json.dumps(schema, indent=2)

        instruction = f"""
Respond with a JSON object matching this schema:
```json
{schema_str}
```
Output ONLY valid JSON, no other text."""

        # Append to last user message or add new one
        new_messages = list(messages)
        if new_messages and new_messages[-1].role == "user":
            new_messages[-1] = Message(
                role="user",
                content=new_messages[-1].content + "\n\n" + instruction
            )
        else:
            new_messages.append(Message(role="user", content=instruction))

        return new_messages


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

    async def complete(
        self,
        messages: list[Message],
        config: LLMConfig,
        response_model: type[BaseModel] | None = None,
    ) -> LLMResult:
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package required: pip install anthropic")

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        client = anthropic.AsyncAnthropic(api_key=self.api_key)

        # Separate system message from others
        system = None
        chat_messages = []
        for msg in messages:
            if msg.role == "system":
                system = msg.content
            else:
                chat_messages.append({"role": msg.role, "content": msg.content})

        # Add structured output instructions if needed
        if response_model:
            chat_messages = [
                {"role": m.role, "content": m.content}
                for m in self._format_structured_prompt(
                    [Message(m["role"], m["content"]) for m in chat_messages],
                    response_model
                )
            ]

        kwargs = {
            "model": config.model,
            "max_tokens": config.max_tokens,
            "messages": chat_messages,
        }
        if system:
            kwargs["system"] = system
        if config.temperature is not None:
            kwargs["temperature"] = config.temperature

        response = await client.messages.create(**kwargs)

        content = response.content[0].text if response.content else ""

        return LLMResult(
            content=content,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model=response.model,
            raw_response=response,
        )


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

    async def complete(
        self,
        messages: list[Message],
        config: LLMConfig,
        response_model: type[BaseModel] | None = None,
    ) -> LLMResult:
        try:
            import openai
        except ImportError:
            raise ImportError("openai package required: pip install openai")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")

        client = openai.AsyncOpenAI(api_key=self.api_key)

        chat_messages = [{"role": m.role, "content": m.content} for m in messages]

        # Add structured output instructions if needed
        if response_model:
            chat_messages = [
                {"role": m.role, "content": m.content}
                for m in self._format_structured_prompt(
                    [Message(m["role"], m["content"]) for m in chat_messages],
                    response_model
                )
            ]

        response = await client.chat.completions.create(
            model=config.model,
            messages=chat_messages,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )

        content = response.choices[0].message.content or ""

        return LLMResult(
            content=content,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
            model=response.model,
            raw_response=response,
        )


class OllamaProvider(LLMProvider):
    """Ollama local model provider."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    async def complete(
        self,
        messages: list[Message],
        config: LLMConfig,
        response_model: type[BaseModel] | None = None,
    ) -> LLMResult:
        try:
            import httpx
        except ImportError:
            raise ImportError("httpx package required: pip install httpx")

        chat_messages = [{"role": m.role, "content": m.content} for m in messages]

        if response_model:
            chat_messages = [
                {"role": m.role, "content": m.content}
                for m in self._format_structured_prompt(
                    [Message(m["role"], m["content"]) for m in chat_messages],
                    response_model
                )
            ]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": config.model,
                    "messages": chat_messages,
                    "stream": False,
                    "options": {
                        "num_predict": config.max_tokens,
                        "temperature": config.temperature,
                    },
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()

        content = data.get("message", {}).get("content", "")

        return LLMResult(
            content=content,
            input_tokens=data.get("prompt_eval_count", 0),
            output_tokens=data.get("eval_count", 0),
            model=config.model,
            raw_response=data,
        )


class MockProvider(LLMProvider):
    """Mock provider for testing."""

    def __init__(self, responses: dict[str, str] | None = None):
        self.responses = responses or {}
        self.calls: list[tuple[list[Message], LLMConfig]] = []

    async def complete(
        self,
        messages: list[Message],
        config: LLMConfig,
        response_model: type[BaseModel] | None = None,
    ) -> LLMResult:
        self.calls.append((messages, config))

        # Check for canned response
        if messages:
            last_content = messages[-1].content
            for key, response in self.responses.items():
                if key in last_content:
                    content = response
                    break
            else:
                content = '{"status": "mock response"}'
        else:
            content = '{"status": "mock response"}'

        # If response_model, try to generate valid JSON
        if response_model:
            try:
                # Try to create a default instance
                instance = response_model()
                content = instance.model_dump_json()
            except:
                pass

        return LLMResult(
            content=content,
            input_tokens=100,
            output_tokens=50,
            model="mock",
        )


# Provider registry
_providers: dict[str, type[LLMProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
    "mock": MockProvider,
}


def get_provider(name: str, **kwargs) -> LLMProvider:
    """Get a provider instance by name."""
    if name not in _providers:
        raise ValueError(f"Unknown provider: {name}. Available: {list(_providers.keys())}")
    return _providers[name](**kwargs)


def register_provider(name: str, provider_class: type[LLMProvider]) -> None:
    """Register a custom provider."""
    _providers[name] = provider_class
