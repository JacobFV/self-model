"""
LLM Router: Routes requests to appropriate models by tier.

The router handles:
- Tier-based model selection
- Usage tracking and cost estimation
- Structured output parsing
- Fallback handling
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import TypeVar
import json

from pydantic import BaseModel

from .config import LLMConfig, LLMTier, DEFAULT_TIERS
from .providers import LLMProvider, Message, LLMResult, get_provider


T = TypeVar("T", bound=BaseModel)


@dataclass
class UsageStats:
    """Track LLM usage statistics."""
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_calls: int = 0
    total_cost: float = 0.0
    calls_by_tier: dict[LLMTier, int] = field(default_factory=dict)
    tokens_by_tier: dict[LLMTier, int] = field(default_factory=dict)

    def record(self, tier: LLMTier, config: LLMConfig, result: LLMResult) -> None:
        """Record a completed call."""
        self.total_input_tokens += result.input_tokens
        self.total_output_tokens += result.output_tokens
        self.total_calls += 1

        # Calculate cost
        input_cost = (result.input_tokens / 1000) * config.cost_per_1k_input
        output_cost = (result.output_tokens / 1000) * config.cost_per_1k_output
        self.total_cost += input_cost + output_cost

        # Track by tier
        self.calls_by_tier[tier] = self.calls_by_tier.get(tier, 0) + 1
        total_tokens = result.input_tokens + result.output_tokens
        self.tokens_by_tier[tier] = self.tokens_by_tier.get(tier, 0) + total_tokens


@dataclass
class LLMResponse:
    """Response from the router."""
    content: str
    tier: LLMTier
    model: str
    input_tokens: int
    output_tokens: int
    parsed: BaseModel | None = None
    raw_result: LLMResult | None = None


class LLMRouter:
    """
    Routes LLM requests to appropriate models based on tier.

    Features:
    - Tier-based routing (micro, light, heavy)
    - Usage tracking and cost estimation
    - Structured output parsing with Pydantic
    - Provider abstraction

    Example:
        router = LLMRouter()

        # Simple completion
        response = await router.complete(
            tier=LLMTier.LIGHT,
            messages=[Message("user", "What is 2+2?")]
        )
        print(response.content)

        # Structured output
        class Answer(BaseModel):
            value: int
            explanation: str

        response = await router.complete(
            tier=LLMTier.LIGHT,
            messages=[Message("user", "What is 2+2?")],
            response_model=Answer,
        )
        print(response.parsed.value)  # 4
    """

    def __init__(
        self,
        tiers: dict[LLMTier, LLMConfig] | None = None,
        providers: dict[str, LLMProvider] | None = None,
    ):
        """
        Initialize the router.

        Args:
            tiers: Tier configurations (defaults to DEFAULT_TIERS)
            providers: Provider instances (created on demand if not provided)
        """
        self.tiers = tiers or dict(DEFAULT_TIERS)
        self._providers = providers or {}
        self.usage = UsageStats()

    def _get_provider(self, config: LLMConfig) -> LLMProvider:
        """Get or create a provider for a config."""
        if config.provider not in self._providers:
            self._providers[config.provider] = get_provider(config.provider)
        return self._providers[config.provider]

    async def complete(
        self,
        tier: LLMTier | str,
        messages: list[Message] | list[dict],
        response_model: type[T] | None = None,
        system: str | None = None,
    ) -> LLMResponse:
        """
        Send a completion request.

        Args:
            tier: Which tier to use (micro, light, heavy)
            messages: Chat messages (Message objects or dicts)
            response_model: Optional Pydantic model for structured output
            system: Optional system message to prepend

        Returns:
            LLMResponse with content and optional parsed model
        """
        # Normalize tier
        if isinstance(tier, str):
            tier = LLMTier(tier)

        # Get config
        if tier not in self.tiers:
            raise ValueError(f"Unknown tier: {tier}. Available: {list(self.tiers.keys())}")
        config = self.tiers[tier]

        # Normalize messages
        normalized_messages: list[Message] = []

        if system:
            normalized_messages.append(Message(role="system", content=system))

        for msg in messages:
            if isinstance(msg, Message):
                normalized_messages.append(msg)
            elif isinstance(msg, dict):
                normalized_messages.append(Message(
                    role=msg["role"],
                    content=msg["content"]
                ))
            else:
                raise ValueError(f"Invalid message type: {type(msg)}")

        # Get provider and make request
        provider = self._get_provider(config)
        result = await provider.complete(
            messages=normalized_messages,
            config=config,
            response_model=response_model,
        )

        # Record usage
        self.usage.record(tier, config, result)

        # Parse structured output if requested
        parsed = None
        if response_model:
            try:
                # Try to extract JSON from response
                content = result.content.strip()
                # Handle markdown code blocks
                if content.startswith("```"):
                    lines = content.split("\n")
                    content = "\n".join(lines[1:-1])
                parsed = response_model.model_validate_json(content)
            except Exception as e:
                # Return unparsed - caller can handle
                pass

        return LLMResponse(
            content=result.content,
            tier=tier,
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            parsed=parsed,
            raw_result=result,
        )

    async def complete_parsed(
        self,
        tier: LLMTier | str,
        messages: list[Message] | list[dict],
        response_model: type[T],
        system: str | None = None,
        retries: int = 2,
    ) -> T:
        """
        Send a completion request and return parsed model.

        Like complete() but raises if parsing fails.

        Args:
            tier: Which tier to use
            messages: Chat messages
            response_model: Pydantic model for structured output
            system: Optional system message
            retries: Number of retries on parse failure

        Returns:
            Parsed Pydantic model instance

        Raises:
            ValueError: If parsing fails after retries
        """
        last_error = None

        for attempt in range(retries + 1):
            response = await self.complete(
                tier=tier,
                messages=messages,
                response_model=response_model,
                system=system,
            )

            if response.parsed is not None:
                return response.parsed

            last_error = f"Failed to parse response: {response.content[:200]}"

            # Add hint for retry
            if attempt < retries:
                messages = list(messages)
                messages.append(Message(
                    role="assistant",
                    content=response.content
                ))
                messages.append(Message(
                    role="user",
                    content="That response was not valid JSON. Please try again with valid JSON only."
                ))

        raise ValueError(last_error)

    def get_usage_summary(self) -> dict:
        """Get usage statistics summary."""
        return {
            "total_calls": self.usage.total_calls,
            "total_tokens": self.usage.total_input_tokens + self.usage.total_output_tokens,
            "total_cost": round(self.usage.total_cost, 4),
            "calls_by_tier": {t.value: c for t, c in self.usage.calls_by_tier.items()},
            "tokens_by_tier": {t.value: c for t, c in self.usage.tokens_by_tier.items()},
        }

    def reset_usage(self) -> None:
        """Reset usage statistics."""
        self.usage = UsageStats()
