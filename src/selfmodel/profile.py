"""
Profile: Parametrization for self-model instances.

A Profile defines a specific configuration of the self-model:
- Who (name, persona)
- How (model tier, version)

Profiles enable:
- Multiple people: jacob, sarah, etc.
- Multiple personas: jacob-scholar, jacob-engineer
- Multiple configurations: heavy (expensive, thorough) vs light (cheap, fast)
- Versioning: v1, v2, etc.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Self
import re


@dataclass(frozen=True)
class Profile:
    """
    A parametrized profile for a self-model instance.

    The flat key format is: {name}[-{persona}]-{tier}-{version}

    Examples:
        - jacob-heavy-v1
        - jacob-scholar-heavy-v1
        - jacob-light-v2
        - sarah-engineer-light-v1
    """
    name: str
    tier: str = "light"
    version: str = "v1"
    persona: str | None = None

    def __post_init__(self):
        # Validate components don't contain hyphens
        for component in [self.name, self.tier, self.version]:
            if "-" in component:
                raise ValueError(f"Profile components cannot contain hyphens: {component}")
        if self.persona and "-" in self.persona:
            raise ValueError(f"Persona cannot contain hyphens: {self.persona}")

    @property
    def key(self) -> str:
        """
        Flat string key for this profile.

        Format: {name}[-{persona}]-{tier}-{version}
        """
        parts = [self.name]
        if self.persona:
            parts.append(self.persona)
        parts.extend([self.tier, self.version])
        return "-".join(parts)

    @classmethod
    def parse(cls, key: str) -> Self:
        """
        Parse a flat key back into a Profile.

        Handles both formats:
        - name-tier-version (3 parts, no persona)
        - name-persona-tier-version (4 parts, with persona)
        """
        parts = key.split("-")

        if len(parts) == 3:
            return cls(name=parts[0], tier=parts[1], version=parts[2])
        elif len(parts) == 4:
            return cls(name=parts[0], persona=parts[1], tier=parts[2], version=parts[3])
        else:
            raise ValueError(
                f"Invalid profile key: {key}. "
                f"Expected format: name-tier-version or name-persona-tier-version"
            )

    def state_dir(self, base: Path | str = "state") -> Path:
        """
        Get the state directory for this profile.

        Returns: base/key (e.g., state/jacob-scholar-heavy-v1/)
        """
        return Path(base) / self.key

    def with_tier(self, tier: str) -> Self:
        """Return a copy with a different tier."""
        return Profile(
            name=self.name,
            persona=self.persona,
            tier=tier,
            version=self.version,
        )

    def with_version(self, version: str) -> Self:
        """Return a copy with a different version."""
        return Profile(
            name=self.name,
            persona=self.persona,
            tier=self.tier,
            version=version,
        )

    def with_persona(self, persona: str | None) -> Self:
        """Return a copy with a different persona."""
        return Profile(
            name=self.name,
            persona=persona,
            tier=self.tier,
            version=self.version,
        )

    def __str__(self) -> str:
        return self.key

    def __repr__(self) -> str:
        return f"Profile({self.key!r})"


# Preset profiles for common configurations
PRESETS = {
    "default": Profile(name="default", tier="light", version="v1"),
    "heavy": Profile(name="default", tier="heavy", version="v1"),
}


def get_preset(name: str) -> Profile:
    """Get a preset profile by name."""
    if name in PRESETS:
        return PRESETS[name]
    raise ValueError(f"Unknown preset: {name}. Available: {list(PRESETS.keys())}")
