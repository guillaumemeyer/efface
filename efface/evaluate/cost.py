"""Cost accounting for hosted attack calls.

Prices are per million tokens and are supplied by configuration, never
hard-coded, so a provider change is a config change with a recorded date.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


def estimate_tokens(text: str, *, chars_per_token: float = 4.0) -> int:
    """Rough token count for planning; real counts come from the provider response."""
    if chars_per_token <= 0:
        raise ValueError("chars_per_token must be positive")
    return max(1, round(len(text) / chars_per_token))


@dataclass(frozen=True)
class Price:
    """USD per million tokens."""

    input_per_mtok: float
    output_per_mtok: float

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("token counts must be non-negative")
        return (
            input_tokens * self.input_per_mtok + output_tokens * self.output_per_mtok
        ) / 1_000_000.0


@dataclass(frozen=True)
class Usage:
    calls: int
    input_tokens: int
    output_tokens: int
    usd: float


def summarize(records: Iterable[dict]) -> Usage:
    """Sum ``calls``, ``input_tokens``, ``output_tokens``, and ``usd`` records."""
    calls = input_tokens = output_tokens = 0
    usd = 0.0
    for record in records:
        calls += int(record.get("calls", 1))
        input_tokens += int(record.get("input_tokens", 0))
        output_tokens += int(record.get("output_tokens", 0))
        usd += float(record.get("usd", 0.0))
    return Usage(calls=calls, input_tokens=input_tokens, output_tokens=output_tokens, usd=usd)
