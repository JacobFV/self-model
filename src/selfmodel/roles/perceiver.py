"""
Perceiver role: Updates context_now from inputs.

The Perceiver is responsible for:
- Processing raw sensory/lifelog inputs
- Extracting structured context information
- Identifying relevant people, tasks, constraints

Runs in the instant loop (~100ms - 1s).
"""

from pydantic import BaseModel, Field

from ..llm import LLMTier
from ..llm.providers import Message
from ..models import ContextNow
from .base import Role, RoleResult


class PerceptionInput(BaseModel):
    """Input for the perceiver."""
    raw_input: str
    input_source: str = "manual"  # "manual", "lifelog", "sensor", "api"
    timestamp: str | None = None


class Perceiver(Role):
    """
    Updates context_now from raw inputs.

    The Perceiver extracts structured context from unstructured input:
    - Location and environment
    - People present
    - Current task and constraints
    - Time pressure and stakes
    """

    name = "perceiver"
    description = "Processes raw inputs into structured context."
    default_tier = LLMTier.MICRO  # Fast, cheap, runs frequently

    reads = ["context_now"]
    writes = ["context_now"]

    async def execute(
        self,
        input_data: PerceptionInput | str | None = None,
        **kwargs,
    ) -> RoleResult:
        """
        Process input and update context_now.

        Args:
            input_data: Raw input to process (string or PerceptionInput)

        Returns:
            RoleResult with updated context
        """
        # Normalize input
        if input_data is None:
            return RoleResult(
                success=False,
                error="No input provided",
            )

        if isinstance(input_data, str):
            input_data = PerceptionInput(raw_input=input_data)

        # Get current context for continuity
        current = self._read_node("context_now")

        # Build prompt
        context_str = ""
        if current:
            context_str = f"""
Previous context:
- Location: {current.location}
- Task: {current.current_task}
- People: {', '.join(current.people_present) if current.people_present else 'none'}
"""

        messages = [
            Message(
                role="user",
                content=f"""Process this input and extract structured context.

{context_str}

New input ({input_data.input_source}):
{input_data.raw_input}

Extract:
1. Location/environment changes
2. People present or mentioned
3. Current task/activity
4. Time pressure (0-1)
5. Social setting (alone/intimate/small_group/professional/public)
6. Any constraints or relevant context

Respond with JSON matching the ContextNow schema."""
            )
        ]

        # Get structured response
        try:
            new_context = await self._complete(
                messages=messages,
                response_model=ContextNow,
                system=self._get_system_prompt(),
            )

            # Preserve raw input
            new_context.raw_input = input_data.raw_input
            new_context.input_source = input_data.input_source

            # Write update
            await self._write_node("context_now", new_context)

            return RoleResult(
                success=True,
                updates={"context_now": new_context.model_dump()},
                messages=[f"Updated context: {new_context.current_task or 'no task'}"],
            )

        except Exception as e:
            return RoleResult(
                success=False,
                error=str(e),
            )

    async def process_stream(
        self,
        inputs: list[str],
        source: str = "stream",
    ) -> list[RoleResult]:
        """
        Process multiple inputs in sequence.

        Useful for batch processing lifelog entries.
        """
        results = []
        for raw_input in inputs:
            result = await self.execute(
                input_data=PerceptionInput(
                    raw_input=raw_input,
                    input_source=source,
                )
            )
            results.append(result)
        return results
