"""Masked-language-model infilling.

Operational difference from the self-information rewrite attack: that policy
masks the highest-self-information tokens; this implementation masks a seeded
sample of word positions, which is the weaker variant because it spends the
edit budget at random. One position is masked and filled per call, so the model
always sees exactly one ``<mask>``.
"""

from __future__ import annotations

import random
from typing import Protocol, runtime_checkable

from efface.attacks.base import register


@runtime_checkable
class Filler(Protocol):
    """Fill texts that contain a single ``<mask>``."""

    def fill(self, texts: list[str]) -> list[str]: ...


class RobertaFiller:
    """`roberta-large` masked-LM filler, loaded on first use."""

    def __init__(self, model: str = "roberta-large", device: str | None = None) -> None:
        self.model_name = model
        self.device = device
        self._pipeline = None

    def _load(self) -> None:
        if self._pipeline is not None:
            return
        from transformers import pipeline

        self._pipeline = pipeline(
            "fill-mask", model=self.model_name, device=self.device, top_k=1
        )

    def fill(self, texts: list[str]) -> list[str]:
        self._load()
        return [self._pipeline(text)[0]["sequence"] for text in texts]


@register
class MaskedLMInfill:
    """Mask a fraction of word positions and let a masked LM fill them."""

    name = "mlm_infill"
    default_intensity = 0.15

    def __init__(self, filler: Filler) -> None:
        self.filler = filler

    def apply(self, text: str, *, intensity: float = 0.15, seed: int = 0) -> str:
        words = text.split()
        if len(words) < 2:
            return text
        rng = random.Random(seed)
        count = max(1, round(len(words) * intensity))
        positions = sorted(rng.sample(range(len(words)), min(count, len(words))))

        current = text
        for position in positions:
            current_words = current.split()
            if position >= len(current_words):
                continue
            masked = list(current_words)
            masked[position] = "<mask>"
            filled = self.filler.fill([" ".join(masked)])
            if filled:
                current = filled[0]
        return current
