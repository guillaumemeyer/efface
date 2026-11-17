"""Ordered attack strategies.

A strategy is a comma-separated list of ``tactic@intensity`` steps, applied
left to right. Chains are limited to three steps, which is the search depth in
the paper. Intensities are normalised to ``(0, 1]``.

Adapted from ``watermarks-remover`` (MIT).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeAlias

Step: TypeAlias = tuple[str, float]
Strategy: TypeAlias = tuple[Step, ...]

REMOVAL_TACTICS: tuple[str, ...] = (
    "instruction_paraphrase",
    "discourse_paraphrase",
    "mlm_infill",
    "style_normalisation",
    "document_rewrite",
    "backtranslate_single",
    "backtranslate_multi",
    "crosslingual_generation",
    "synonym_substitution",
    "random_edits",
    "typo_noise",
    "regeneration",
)

CONTROL_TACTIC = "unicode_scrub"
ALL_TACTICS: tuple[str, ...] = REMOVAL_TACTICS + (CONTROL_TACTIC,)

DEFAULT_MAX_STEPS = 3


def parse_strategy(
    spec: str, *, max_steps: int = DEFAULT_MAX_STEPS, allow_control: bool = False
) -> Strategy:
    """Parse ``"tactic@0.6,tactic@1.0"`` into an ordered tuple of steps."""
    if not spec or not spec.strip():
        raise ValueError("strategy must be a non-empty list of tactic@intensity steps")
    if max_steps < 1:
        raise ValueError("max_steps must be positive")
    steps: list[Step] = []
    for raw in spec.split(","):
        item = raw.strip()
        if not item:
            raise ValueError("empty strategy step")
        if "@" not in item:
            raise ValueError(f"bad strategy step {item!r}; expected tactic@intensity")
        tactic, raw_level = item.rsplit("@", 1)
        tactic = tactic.strip()
        if tactic not in ALL_TACTICS:
            raise ValueError(f"unknown tactic {tactic!r}")
        if tactic == CONTROL_TACTIC and not allow_control:
            raise ValueError("unicode_scrub is a control row and is not chainable")
        try:
            level = float(raw_level)
        except ValueError:
            raise ValueError(f"bad intensity in step {item!r}") from None
        if not 0.0 < level <= 1.0:
            raise ValueError(f"intensity must lie in (0, 1], got {level} in {item!r}")
        steps.append((tactic, level))
    if len(steps) > max_steps:
        raise ValueError(f"strategy has {len(steps)} steps; the maximum is {max_steps}")
    return tuple(steps)


def normalize_strategy(steps: Sequence[Step]) -> Strategy:
    """Round intensities so that equivalent strategies share a cache key."""
    return tuple((tactic, round(float(level), 4)) for tactic, level in steps)


def strategy_slug(steps: Sequence[Step]) -> str:
    """Filesystem-safe name, for example ``instruction_paraphrase@0.6+typo_noise@0.2``."""
    return "+".join(f"{tactic}@{level:g}" for tactic, level in steps)


def strategy_key(steps: Sequence[Step]) -> Strategy:
    """Hashable, normalised identity of a strategy."""
    return normalize_strategy(steps)
