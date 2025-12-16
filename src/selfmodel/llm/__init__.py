"""
LLM abstraction layer for interchangeable models.

Provides:
- LLMConfig: Configuration for a specific model
- LLMRouter: Routes requests to appropriate models by tier
- Provider implementations: Anthropic, OpenAI, Ollama
"""

from .config import LLMConfig, LLMTier, DEFAULT_TIERS, MOCK_TIERS, OPENAI_TIERS
from .router import LLMRouter, LLMResponse
from .providers import get_provider, AnthropicProvider, OpenAIProvider, MockProvider

__all__ = [
    "LLMConfig",
    "LLMTier",
    "DEFAULT_TIERS",
    "MOCK_TIERS",
    "OPENAI_TIERS",
    "LLMRouter",
    "LLMResponse",
    "get_provider",
    "AnthropicProvider",
    "OpenAIProvider",
    "MockProvider",
]
