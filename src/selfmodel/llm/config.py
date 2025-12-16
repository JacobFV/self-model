"""
LLM configuration and tier definitions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class LLMTier(str, Enum):
    """
    Cost/capability tiers for LLM routing.

    - MICRO: Fastest, cheapest, for high-frequency simple tasks
    - LIGHT: Balanced cost/capability for routine updates
    - HEAVY: Most capable, for complex reasoning and rare updates
    """
    MICRO = "micro"
    LIGHT = "light"
    HEAVY = "heavy"


@dataclass(frozen=True)
class LLMConfig:
    """
    Configuration for a specific LLM.

    Attributes:
        provider: The provider name ("anthropic", "openai", "ollama", "mock")
        model: The model identifier
        tier: Which tier this config is for
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        cost_per_1k_input: Cost per 1000 input tokens (for tracking)
        cost_per_1k_output: Cost per 1000 output tokens (for tracking)
    """
    provider: str
    model: str
    tier: LLMTier
    max_tokens: int = 4096
    temperature: float = 0.7
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0

    @property
    def cost_per_1k(self) -> float:
        """Average cost per 1k tokens (rough estimate)."""
        return (self.cost_per_1k_input + self.cost_per_1k_output) / 2


# Default tier configurations
DEFAULT_TIERS: dict[LLMTier, LLMConfig] = {
    LLMTier.HEAVY: LLMConfig(
        provider="anthropic",
        model="claude-sonnet-4-20250514",
        tier=LLMTier.HEAVY,
        max_tokens=8192,
        temperature=0.7,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
    ),
    LLMTier.LIGHT: LLMConfig(
        provider="anthropic",
        model="claude-3-5-haiku-20241022",
        tier=LLMTier.LIGHT,
        max_tokens=4096,
        temperature=0.7,
        cost_per_1k_input=0.0008,
        cost_per_1k_output=0.004,
    ),
    LLMTier.MICRO: LLMConfig(
        provider="ollama",
        model="llama3.2:3b",
        tier=LLMTier.MICRO,
        max_tokens=2048,
        temperature=0.7,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
    ),
}


# Alternative configurations for different setups
OPENAI_TIERS: dict[LLMTier, LLMConfig] = {
    LLMTier.HEAVY: LLMConfig(
        provider="openai",
        model="gpt-4o",
        tier=LLMTier.HEAVY,
        max_tokens=8192,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015,
    ),
    LLMTier.LIGHT: LLMConfig(
        provider="openai",
        model="gpt-4o-mini",
        tier=LLMTier.LIGHT,
        max_tokens=4096,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
    ),
    LLMTier.MICRO: LLMConfig(
        provider="ollama",
        model="llama3.2:3b",
        tier=LLMTier.MICRO,
        max_tokens=2048,
    ),
}


# Mock configuration for testing
MOCK_TIERS: dict[LLMTier, LLMConfig] = {
    tier: LLMConfig(
        provider="mock",
        model="mock",
        tier=tier,
        max_tokens=4096,
    )
    for tier in LLMTier
}
