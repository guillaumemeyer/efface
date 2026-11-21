"""MarkLLM SynthID detection adapter.

The score is MarkLLM's mean detector: the mean of the g-values that survive
the end-of-text and context-repetition masks. Each g-value is a fair coin under
the unwatermarked null, so the score has mean 1/2 and variance ``1/(4 n_eff)``
where ``n_eff`` is the number of unmasked positions times the depth. Using
1/12 in place of 1/4 is the variance of a uniform draw, and it would make the
p-value too small by a constant factor.

The detector rebuilds the key array from the record's key id and the manifest's
``key_seed``. Detecting a text under a different array measures a different
mark.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any

from efface.detect.base import DetectorScore
from efface.evaluate.stats import normal_quantile
from efface.watermark.markllm import MarkLLMBackend


def mean_score(g_values: list[list[list[float]]], mask: list[list[float]]) -> tuple[float, int]:
    """MarkLLM's mean-detector score and the number of g-values behind it."""
    if len(g_values) != len(mask):
        raise ValueError("g_values and mask must agree on batch size")
    total = 0.0
    n_eff = 0
    for document, document_mask in zip(g_values, mask, strict=True):
        if len(document) != len(document_mask):
            raise ValueError("g_values and mask must agree on sequence length")
        for position, position_mask in zip(document, document_mask, strict=True):
            if position_mask == 0:
                continue
            total += sum(position)
            n_eff += len(position)
    if n_eff == 0:
        raise ValueError("no unmasked g-values; the text is too short")
    return total / n_eff, n_eff


@dataclass(frozen=True)
class NullModel:
    """Normal null for the mean score.

    The analytic model centres the score at 1/2 with variance ``0.25/n_eff``,
    because each g-value is Bernoulli(1/2). Empirically the centre sits a
    little below 1/2 and the between-document variance is smaller than that
    model predicts, so the harness fits the centre and the variance scale to a
    set of unwatermarked documents and records the fit with every result.
    """

    mean: float
    variance_scale: float
    n_documents: int = 0
    source: str = "analytic"

    @classmethod
    def analytic(cls) -> NullModel:
        return cls(mean=0.5, variance_scale=0.25, source="analytic")

    @classmethod
    def fit(cls, samples: list[tuple[float, int]]) -> NullModel:
        """Method of moments on ``(score, n_eff)`` pairs.

        The mean is unweighted across documents. The scale solves
        ``var(score) = scale / n_eff`` in the least-squares sense.
        """
        if len(samples) < 2:
            raise ValueError("fitting a null needs at least two documents")
        scores = [score for score, _ in samples]
        mean = sum(scores) / len(scores)
        numerator = sum((score - mean) ** 2 for score in scores)
        denominator = sum(1.0 / n_eff for _, n_eff in samples)
        if denominator <= 0.0:
            raise ValueError("n_eff must be positive")
        return cls(
            mean=mean,
            variance_scale=numerator / denominator,
            n_documents=len(samples),
            source="empirical",
        )

    def pvalue(self, score: float, n_eff: int) -> float:
        if n_eff < 1:
            raise ValueError("n_eff must be positive")
        if not 0.0 <= score <= 1.0:
            raise ValueError("score must lie in [0, 1]")
        variance = self.variance_scale / n_eff
        if variance <= 0.0:
            raise ValueError("variance scale must be positive")
        z = (score - self.mean) / math.sqrt(variance)
        return 0.5 * math.erfc(z / math.sqrt(2.0))

    def to_dict(self) -> dict[str, Any]:
        return {
            "mean": self.mean,
            "variance_scale": self.variance_scale,
            "n_documents": self.n_documents,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NullModel:
        return cls(
            mean=float(data["mean"]),
            variance_scale=float(data["variance_scale"]),
            n_documents=int(data.get("n_documents", 0)),
            source=str(data.get("source", "empirical")),
        )


def pvalue_from_score(score: float, n_eff: int, null: NullModel | None = None) -> float:
    """One-sided normal p-value for 'the mark is present'.

    Small values mean the score sits high in the unwatermarked null. The
    default is the analytic null; a calibrated ``NullModel`` is preferred for
    any reported result.
    """
    return (null or NullModel.analytic()).pvalue(score, n_eff)


class MarkLLMDetector:
    """Score documents with the scheme and key array that generated them."""

    NAME = "markllm-synthid-mean"

    def __init__(self, backend: MarkLLMBackend, null: NullModel | None = None) -> None:
        self.backend = backend
        self.null = null or NullModel.analytic()

    def _g_values_and_mask(self, text: str, key: int) -> tuple[list, list]:
        scheme = self.backend.scheme_for(key)
        processor = scheme.logits_processor
        tokenizer = scheme.config.generation_tokenizer
        encoded = tokenizer(text, return_tensors="pt", add_special_tokens=False)["input_ids"]
        encoded = encoded.to(scheme.config.device)

        g_values = processor.compute_g_values(encoded)
        eos_mask = processor.compute_eos_token_mask(
            input_ids=encoded, eos_token_id=tokenizer.eos_token_id
        )[:, processor.ngram_len - 1 :]

        if scheme.config.watermark_mode == "non-distortionary":
            repetition_mask = processor.compute_context_repetition_mask(input_ids=encoded)
            combined_mask = repetition_mask * eos_mask
        else:
            combined_mask = eos_mask

        return g_values.cpu().tolist(), combined_mask.cpu().tolist()

    def score(self, text: str, key: int) -> DetectorScore:
        g_values, mask = self._g_values_and_mask(text, key)
        score, n_eff = mean_score(g_values, mask)
        return DetectorScore(
            pvalue=self.null.pvalue(score, n_eff),
            score=score,
            key=key,
            detector=self.NAME,
            n_eff=n_eff,
            metadata={"threshold": self._threshold(key), "null": self.null.to_dict()},
        )

    def _threshold(self, key: int) -> float:
        return float(self.backend.scheme_for(key).config.threshold)

    def score_many(self, documents: Iterable[tuple[str, int]]) -> Iterator[DetectorScore]:
        """Batch mode: one score per ``(text, key)`` pair, in order."""
        for text, key in documents:
            yield self.score(text, key)


def record_score(record: dict[str, Any], detector: MarkLLMDetector) -> DetectorScore:
    """Score a generation record under its own key."""
    return detector.score(record["text"], int(record["key"]))


def normal_critical_value(alpha: float = 0.05) -> float:
    """Z at which the one-sided test rejects; kept here for callers that
    compare scores rather than p-values."""
    return normal_quantile(1.0 - alpha)
