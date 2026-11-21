"""Apply an ordered chain with prefix reuse.

Each step conditions on the previous output, so the text after a prefix is a
deterministic function of the source, the seed, and the prefix. A depth-3 chain
therefore shares its depth-2 work with every chain that starts the same way.
The executor looks for the longest cached prefix, applies only the steps after
it, and stores the prefixes it computes.
"""

from __future__ import annotations

import difflib
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from efface.chains.cache import Cache, MemoryCache, cache_key, text_digest
from efface.search.strategy import Step, strategy_slug

AttackFactory = Callable[[str], Any]


def edit_rate(before: str, after: str) -> float:
    """Fraction of characters changed, as ``1 - similarity``."""
    if not before and not after:
        return 0.0
    return 1.0 - difflib.SequenceMatcher(a=before, b=after, autojunk=False).ratio()


@dataclass
class StepResult:
    tactic: str
    intensity: float
    edit_rate: float


@dataclass
class ChainResult:
    text: str
    source: str
    resumed_at: int
    steps: list[StepResult] = field(default_factory=list)

    @property
    def evaluated(self) -> int:
        return len(self.steps)

    @property
    def cache_hits(self) -> int:
        return self.resumed_at


class ChainExecutor:
    """Run ordered steps over a document, reusing cached prefixes."""

    def __init__(
        self,
        build_attack: AttackFactory,
        *,
        cache: Cache | None = None,
        seed: int = 0,
        max_depth: int = 3,
    ) -> None:
        self.build_attack = build_attack
        self.cache = cache or MemoryCache()
        self.seed = seed
        self.max_depth = max_depth
        self._attacks: dict[str, Any] = {}

    def _attack(self, tactic: str):
        attack = self._attacks.get(tactic)
        if attack is None:
            attack = self.build_attack(tactic)
            self._attacks[tactic] = attack
        return attack

    def _key(self, doc_id: str, digest: str, prefix: Sequence[Step]) -> str:
        return cache_key(
            doc_id=doc_id,
            seed=self.seed,
            source_digest=digest,
            prefix=strategy_slug(prefix),
        )

    def run(self, text: str, steps: Sequence[Step], *, doc_id: str = "") -> ChainResult:
        if len(steps) > self.max_depth:
            raise ValueError(f"chain has {len(steps)} steps; the maximum is {self.max_depth}")
        source = text
        digest = text_digest(source)

        # Longest cached prefix wins; length 0 is the untouched source.
        start = 0
        current = source
        for length in range(len(steps), 0, -1):
            cached = self.cache.get(self._key(doc_id, digest, steps[:length]))
            if cached is not None:
                current = cached
                start = length
                break

        results: list[StepResult] = []
        for index in range(start, len(steps)):
            tactic, level = steps[index]
            output = self._attack(tactic).apply(current, intensity=level, seed=self.seed)
            results.append(
                StepResult(tactic=tactic, intensity=level, edit_rate=edit_rate(current, output))
            )
            current = output
            self.cache.put(self._key(doc_id, digest, steps[: index + 1]), current)

        return ChainResult(text=current, source=source, resumed_at=start, steps=results)
