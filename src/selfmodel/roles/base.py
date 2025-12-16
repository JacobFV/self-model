"""
Base Role class for the self-model.

Roles are specialized LLM agents that update specific nodes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, TypeVar, Generic
from pydantic import BaseModel

from ..llm import LLMRouter, LLMTier
from ..llm.providers import Message
from ..store import StateStore
from ..events import EventBus, Event, EventType


T = TypeVar("T", bound=BaseModel)


@dataclass
class RoleResult:
    """Result from a role execution."""
    success: bool
    updates: dict[str, Any] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)
    error: str | None = None


class Role(ABC):
    """
    Base class for roles that update state nodes.

    A Role is responsible for:
    1. Reading relevant state from the store
    2. Constructing prompts for the LLM
    3. Parsing LLM responses into state updates
    4. Writing updates back to the store

    Subclasses must implement:
    - name: The role's identifier
    - default_tier: Which LLM tier to use by default
    - reads: List of nodes this role reads from
    - writes: List of nodes this role writes to
    - execute(): The main execution logic
    """

    # Override in subclasses
    name: str = "base"
    description: str = "Base role"
    default_tier: LLMTier = LLMTier.LIGHT

    # Nodes this role interacts with
    reads: list[str] = []
    writes: list[str] = []

    def __init__(
        self,
        router: LLMRouter,
        store: StateStore,
        bus: EventBus | None = None,
        tier: LLMTier | None = None,
    ):
        """
        Initialize a role.

        Args:
            router: LLM router for making completions
            store: State store for reading/writing nodes
            bus: Optional event bus for publishing updates
            tier: Override the default LLM tier
        """
        self.router = router
        self.store = store
        self.bus = bus
        self.tier = tier or self.default_tier

    @abstractmethod
    async def execute(self, **kwargs) -> RoleResult:
        """
        Execute the role's main function.

        Returns:
            RoleResult with success status and any updates made
        """
        pass

    async def _complete(
        self,
        messages: list[Message] | list[dict],
        response_model: type[T] | None = None,
        system: str | None = None,
        tier: LLMTier | None = None,
    ) -> T | str:
        """
        Make an LLM completion.

        Args:
            messages: Chat messages
            response_model: Optional Pydantic model for structured output
            system: Optional system message
            tier: Override tier for this call

        Returns:
            Parsed model if response_model provided, else raw content
        """
        tier = tier or self.tier

        if response_model:
            return await self.router.complete_parsed(
                tier=tier,
                messages=messages,
                response_model=response_model,
                system=system,
            )
        else:
            response = await self.router.complete(
                tier=tier,
                messages=messages,
                system=system,
            )
            return response.content

    async def _emit(self, node: str, data: dict | None = None) -> None:
        """Emit a node update event."""
        if self.bus:
            await self.bus.publish(Event(
                type=EventType.NODE_UPDATED,
                source=node,
                data=data or {},
            ))

    def _get_system_prompt(self) -> str:
        """Get the system prompt for this role."""
        return f"""You are the {self.name} role in a cognitive self-model system.

{self.description}

You update these nodes: {', '.join(self.writes)}
You read from these nodes: {', '.join(self.reads)}

Always respond with valid JSON matching the requested schema.
Be precise and avoid speculation beyond the evidence.
"""

    def _read_node(self, node: str) -> Any:
        """Read a node's current value."""
        accessor = getattr(self.store, node)
        return accessor.value

    async def _write_node(self, node: str, value: BaseModel) -> None:
        """Write a value to a node."""
        accessor = getattr(self.store, node)
        accessor.append(value)
        await self._emit(node, {"role": self.name})
