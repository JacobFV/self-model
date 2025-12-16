"""
Tests for the LLM module.
"""

import pytest
from pydantic import BaseModel

from selfmodel.llm import (
    LLMConfig,
    LLMTier,
    LLMRouter,
    MockProvider,
    DEFAULT_TIERS,
    MOCK_TIERS,
)
from selfmodel.llm.providers import Message, LLMResult
from selfmodel.llm.config import MOCK_TIERS


class TestLLMConfig:
    def test_create_config(self):
        config = LLMConfig(
            provider="anthropic",
            model="claude-3-5-haiku-20241022",
            tier=LLMTier.LIGHT,
        )
        assert config.provider == "anthropic"
        assert config.tier == LLMTier.LIGHT

    def test_default_tiers(self):
        assert LLMTier.HEAVY in DEFAULT_TIERS
        assert LLMTier.LIGHT in DEFAULT_TIERS
        assert LLMTier.MICRO in DEFAULT_TIERS

        # Heavy should be more expensive than light
        heavy = DEFAULT_TIERS[LLMTier.HEAVY]
        light = DEFAULT_TIERS[LLMTier.LIGHT]
        assert heavy.cost_per_1k > light.cost_per_1k

    def test_cost_per_1k(self):
        config = LLMConfig(
            provider="test",
            model="test",
            tier=LLMTier.LIGHT,
            cost_per_1k_input=0.001,
            cost_per_1k_output=0.003,
        )
        assert config.cost_per_1k == 0.002


class TestMockProvider:
    @pytest.mark.asyncio
    async def test_basic_completion(self):
        provider = MockProvider()
        config = LLMConfig(
            provider="mock",
            model="mock",
            tier=LLMTier.LIGHT,
        )

        result = await provider.complete(
            messages=[Message("user", "Hello")],
            config=config,
        )

        assert result.content is not None
        assert result.input_tokens > 0
        assert len(provider.calls) == 1

    @pytest.mark.asyncio
    async def test_canned_responses(self):
        provider = MockProvider(responses={
            "weather": '{"condition": "sunny"}',
            "time": '{"hour": 12}',
        })
        config = LLMConfig(provider="mock", model="mock", tier=LLMTier.LIGHT)

        result = await provider.complete(
            messages=[Message("user", "What is the weather?")],
            config=config,
        )
        assert "sunny" in result.content

        result = await provider.complete(
            messages=[Message("user", "What time is it?")],
            config=config,
        )
        assert "12" in result.content

    @pytest.mark.asyncio
    async def test_structured_output(self):
        class TestModel(BaseModel):
            value: int = 42
            name: str = "test"

        provider = MockProvider()
        config = LLMConfig(provider="mock", model="mock", tier=LLMTier.LIGHT)

        result = await provider.complete(
            messages=[Message("user", "Generate data")],
            config=config,
            response_model=TestModel,
        )

        # Should generate valid JSON for the model
        parsed = TestModel.model_validate_json(result.content)
        assert parsed.value == 42


class TestLLMRouter:
    @pytest.fixture
    def router(self):
        """Create a router with mock provider."""
        mock = MockProvider()
        return LLMRouter(
            tiers=MOCK_TIERS,
            providers={"mock": mock},
        )

    @pytest.mark.asyncio
    async def test_basic_completion(self, router: LLMRouter):
        response = await router.complete(
            tier=LLMTier.LIGHT,
            messages=[Message("user", "Hello")],
        )

        assert response.content is not None
        assert response.tier == LLMTier.LIGHT
        assert response.model == "mock"

    @pytest.mark.asyncio
    async def test_tier_as_string(self, router: LLMRouter):
        response = await router.complete(
            tier="light",
            messages=[Message("user", "Hello")],
        )
        assert response.tier == LLMTier.LIGHT

    @pytest.mark.asyncio
    async def test_messages_as_dicts(self, router: LLMRouter):
        response = await router.complete(
            tier=LLMTier.LIGHT,
            messages=[
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Hello"},
            ],
        )
        assert response.content is not None

    @pytest.mark.asyncio
    async def test_system_message(self, router: LLMRouter):
        response = await router.complete(
            tier=LLMTier.LIGHT,
            messages=[Message("user", "Hello")],
            system="You are a pirate.",
        )
        assert response.content is not None

    @pytest.mark.asyncio
    async def test_usage_tracking(self, router: LLMRouter):
        await router.complete(tier=LLMTier.LIGHT, messages=[Message("user", "1")])
        await router.complete(tier=LLMTier.LIGHT, messages=[Message("user", "2")])
        await router.complete(tier=LLMTier.HEAVY, messages=[Message("user", "3")])

        assert router.usage.total_calls == 3
        assert router.usage.calls_by_tier[LLMTier.LIGHT] == 2
        assert router.usage.calls_by_tier[LLMTier.HEAVY] == 1

    @pytest.mark.asyncio
    async def test_usage_summary(self, router: LLMRouter):
        await router.complete(tier=LLMTier.LIGHT, messages=[Message("user", "test")])

        summary = router.get_usage_summary()
        assert summary["total_calls"] == 1
        assert "light" in summary["calls_by_tier"]

    @pytest.mark.asyncio
    async def test_reset_usage(self, router: LLMRouter):
        await router.complete(tier=LLMTier.LIGHT, messages=[Message("user", "test")])
        assert router.usage.total_calls == 1

        router.reset_usage()
        assert router.usage.total_calls == 0

    @pytest.mark.asyncio
    async def test_structured_output(self, router: LLMRouter):
        class Answer(BaseModel):
            value: int = 42

        response = await router.complete(
            tier=LLMTier.LIGHT,
            messages=[Message("user", "What is 2+2?")],
            response_model=Answer,
        )

        assert response.parsed is not None
        assert response.parsed.value == 42

    @pytest.mark.asyncio
    async def test_complete_parsed(self, router: LLMRouter):
        class Answer(BaseModel):
            value: int = 42
            name: str = "answer"

        result = await router.complete_parsed(
            tier=LLMTier.LIGHT,
            messages=[Message("user", "Give me an answer")],
            response_model=Answer,
        )

        assert isinstance(result, Answer)
        assert result.value == 42

    @pytest.mark.asyncio
    async def test_unknown_tier_raises(self, router: LLMRouter):
        with pytest.raises(ValueError, match="not a valid"):
            await router.complete(
                tier="nonexistent",
                messages=[Message("user", "test")],
            )


class TestMessage:
    def test_create_message(self):
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
