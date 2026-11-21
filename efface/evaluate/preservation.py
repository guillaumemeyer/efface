"""Preservation metrics and the selecting composite.

Two metrics select the chain: BERTScore-F1 and COMET. Their unweighted mean is
``S``, the score the floor τ constrains (preregistration R2). BLEURT, MAUVE,
length ratio, and achieved edit rate are reported beside ``S`` and never enter
the constraint, so adding a tier cannot move which chain wins.

MAUVE is a divergence between two sets, so it has no per-document value and
cannot appear in ``S``. ``composite`` rejects it, and a test pins that.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

SELECTING = ("bertscore", "comet")
REPORTED_ONLY = ("bleurt", "mauve", "length_ratio", "edit_rate")


class Metric(Protocol):
    name: str

    def score(self, pairs: Sequence[tuple[str, str]]) -> list[float]:
        """One value per (source, candidate) pair."""


def composite(scores: dict[str, float]) -> float:
    """The selecting composite ``S``: mean of BERTScore and COMET.

    Raises when a metric outside the selecting pair is supplied, because a
    composite that quietly averaged in MAUVE or BLEURT would change the floor.
    """
    if set(scores) != set(SELECTING):
        extra = sorted(set(scores) - set(SELECTING))
        missing = sorted(set(SELECTING) - set(scores))
        raise ValueError(f"composite takes exactly {SELECTING}; extra={extra} missing={missing}")
    values = [float(scores[name]) for name in SELECTING]
    for name, value in zip(SELECTING, values, strict=True):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must lie in [0, 1], got {value}")
    return sum(values) / len(values)


def length_ratio(source: str, candidate: str) -> float:
    """Candidate tokens over source tokens, by whitespace."""
    source_tokens = len(source.split())
    if source_tokens == 0:
        raise ValueError("source must have at least one token")
    return len(candidate.split()) / source_tokens


@dataclass
class PreservationReport:
    """``S`` plus the reported columns, for one document."""

    source_id: str
    composite: float
    reported: dict[str, float] = field(default_factory=dict)

    def below_floor(self, tau: float) -> bool:
        return self.composite < tau


class BertScore:
    name = "bertscore"

    def __init__(self, model: str = "roberta-large", device: str | None = None) -> None:
        self.model = model
        self.device = device
        self._scorer: Callable | None = None

    def _load(self) -> Callable:
        if self._scorer is None:
            from bert_score import score

            self._scorer = score
        return self._scorer

    def score(self, pairs: Sequence[tuple[str, str]]) -> list[float]:
        scorer = self._load()
        sources = [source for source, _ in pairs]
        candidates = [candidate for _, candidate in pairs]
        _, _, f1 = scorer(
            candidates, sources, model_type=self.model, device=self.device, verbose=False
        )
        return [float(value) for value in f1]


class Comet:
    name = "comet"

    def __init__(
        self, model: str = "Unbabel/wmt22-comet-da", device: str | None = None
    ) -> None:
        self.model = model
        self.device = device
        self._model: Any = None

    def _load(self) -> Any:
        if self._model is None:
            from comet import download_model, load_from_checkpoint

            path = download_model(self.model)
            self._model = load_from_checkpoint(path)
        return self._model

    def score(self, pairs: Sequence[tuple[str, str]]) -> list[float]:
        model = self._load()
        data = [
            {"src": source, "mt": candidate, "ref": source}
            for source, candidate in pairs
        ]
        # num_workers=1 avoids a COMET 2.2.7 / torch 2.x conflict: at gpus=0 it
        # passes multiprocessing_context="fork" with num_workers=0 on a Mac,
        # which torch rejects.
        output = model.predict(
            data, batch_size=8, gpus=0, progress_bar=False, num_workers=1
        )
        # COMET returns roughly [-1, 1]; clip to the composite's range.
        return [min(1.0, max(0.0, float(value))) for value in output.scores]


class Bleurt:
    name = "bleurt"

    def __init__(self, model: str = "BLEURT-20", device: str | None = None) -> None:
        self.model = model
        self.device = device
        self._scorer: Any = None

    def _load(self) -> Any:
        if self._scorer is None:
            from bleurt import score as bleurt_score

            self._scorer = bleurt_score.BleurtScorer(self.model)
        return self._scorer

    def score(self, pairs: Sequence[tuple[str, str]]) -> list[float]:
        scorer = self._load()
        references = [source for source, _ in pairs]
        candidates = [candidate for _, candidate in pairs]
        raw = scorer.score(references=references, candidates=candidates)
        # (s + 1) / 2, clipped: BLEURT is not bounded, so clipping is explicit.
        return [min(1.0, max(0.0, (float(value) + 1.0) / 2.0)) for value in raw]


def score_pairs(
    pairs: Sequence[tuple[str, str]],
    *,
    metrics: Sequence[Metric] | None = None,
    tau: float | None = None,
) -> list[PreservationReport]:
    """Score each pair with the selecting metrics and the reported columns.

    ``pairs`` are ``(source, candidate)``, with the source document as the
    watermarked original. Pass only the metrics this tier runs.
    """
    if metrics is None:
        metrics = (BertScore(), Comet())
    names = {metric.name for metric in metrics}
    unknown = names - set(SELECTING) - set(REPORTED_ONLY)
    if unknown:
        raise ValueError(f"unknown metric names: {sorted(unknown)}")

    columns: dict[str, list[float]] = {}
    for metric in metrics:
        columns[metric.name] = metric.score(pairs)
    columns.setdefault("length_ratio", [length_ratio(s, c) for s, c in pairs])

    reports = []
    for index, _pair in enumerate(pairs):
        selecting = {name: columns[name][index] for name in SELECTING if name in columns}
        if set(selecting) != set(SELECTING):
            raise ValueError(
                f"the floor needs {SELECTING}; got {sorted(selecting)}"
            )
        reported = {
            name: columns[name][index]
            for name in REPORTED_ONLY
            if name in columns
        }
        s_value = composite(selecting)
        reports.append(
            PreservationReport(
                source_id=str(index),
                composite=s_value,
                reported=reported,
            )
        )
    return reports


def aggregate(reports: Sequence[PreservationReport]) -> dict[str, float]:
    """Mean ``S`` and mean of each reported column, for one chain."""
    if not reports:
        raise ValueError("reports must not be empty")
    summary = {"S": sum(r.composite for r in reports) / len(reports)}
    names = {name for report in reports for name in report.reported}
    for name in sorted(names):
        values = [report.reported[name] for report in reports if name in report.reported]
        summary[name] = sum(values) / len(values)
    return summary


def below_floor_fraction(reports: Sequence[PreservationReport], tau: float) -> float:
    if not reports:
        raise ValueError("reports must not be empty")
    return sum(1 for report in reports if report.below_floor(tau)) / len(reports)
