"""Attack interface shared by every tactic.

Each tactic is one module with one public class that satisfies ``Attack``. The
runner knows nothing about prompt templates or provider clients; it only calls
``apply`` and records the seed.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Attack(Protocol):
    name: str
    default_intensity: float

    def apply(self, text: str, *, intensity: float = 1.0, seed: int = 0) -> str:
        """Return the transformed text. Must be deterministic given the seed."""
        ...


_REGISTRY: dict[str, type[Attack]] = {}


def register(cls: type[Attack]) -> type[Attack]:
    """Class decorator that adds a tactic to the registry."""
    name = getattr(cls, "name", None)
    if not name:
        raise ValueError("an attack class must define a non-empty name")
    if name in _REGISTRY:
        raise ValueError(f"attack {name!r} is already registered")
    _REGISTRY[name] = cls
    return cls


def get(name: str) -> type[Attack]:
    try:
        return _REGISTRY[name]
    except KeyError:
        available = ", ".join(sorted(_REGISTRY)) or "none"
        raise KeyError(f"unknown attack {name!r}; registered: {available}") from None


def available() -> tuple[str, ...]:
    return tuple(sorted(_REGISTRY))
