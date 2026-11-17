"""Removal and detection statistics.

Definitions used throughout the paper:

- A document is removed when the detector fails to reject the unwatermarked
  null under every watermark key at level ``alpha``.
- The removal rate is the mean of that indicator, with a Wilson interval.
- The residual true-positive rate is measured on attacked watermarked documents
  at a threshold calibrated to a fixed false-positive rate on unwatermarked
  documents. Higher values mean the mark is still detectable.

Adapted from ``watermarks-remover`` (MIT): rank-based AUROC with tie handling.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass

Z95 = 1.959963984540054


def wilson_interval(successes: int, n: int, z: float = Z95) -> tuple[float, float]:
    """Two-sided Wilson score interval for a binomial proportion."""
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= successes <= n:
        raise ValueError("successes must lie in [0, n]")
    p = successes / n
    denominator = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / denominator
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denominator
    low = max(0.0, centre - half)
    high = min(1.0, centre + half)
    # Floating point leaves the boundary a hair short of 0 or 1.
    if low < 1e-12:
        low = 0.0
    if high > 1.0 - 1e-12:
        high = 1.0
    return low, high


@dataclass(frozen=True)
class Rate:
    """A proportion with a confidence interval."""

    value: float
    low: float
    high: float
    n: int


def removal_rate(removed: Sequence[bool], z: float = Z95) -> Rate:
    """Fraction of documents whose mark was removed, with a Wilson interval."""
    n = len(removed)
    if n == 0:
        raise ValueError("removed must not be empty")
    k = sum(1 for flag in removed if flag)
    low, high = wilson_interval(k, n, z)
    return Rate(value=k / n, low=low, high=high, n=n)


def removed_from_pvalues(pvalues: Sequence[float], alpha: float = 0.05) -> bool:
    """True when every key fails to reject the null, i.e. no key detects the mark."""
    if not pvalues:
        raise ValueError("at least one key is required")
    return min(pvalues) > alpha


def _average_ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        average = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = average
        i = j + 1
    return ranks


def auroc(positives: Sequence[float], negatives: Sequence[float]) -> float:
    """Area under the ROC curve for scores where higher means more positive.

    Ties between a positive and a negative count as half a correct ranking.
    """
    if not positives or not negatives:
        raise ValueError("both classes must be non-empty")
    values = list(positives) + list(negatives)
    ranks = _average_ranks(values)
    n_pos = len(positives)
    n_neg = len(negatives)
    rank_sum = sum(ranks[:n_pos])
    return (rank_sum - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)


def tpr_at_fpr(
    positives: Sequence[float], negatives: Sequence[float], fpr: float = 0.01
) -> float:
    """True-positive rate at a threshold whose empirical FPR does not exceed ``fpr``.

    With fewer than ``1 / fpr`` negatives no positive threshold reaches the
    target, so the function returns 0.0 rather than inventing a threshold.
    """
    if not positives or not negatives:
        raise ValueError("both classes must be non-empty")
    if not 0.0 < fpr < 1.0:
        raise ValueError("fpr must lie in (0, 1)")
    ordered = sorted(negatives)
    allowed = math.floor(fpr * len(ordered))
    if allowed == 0:
        threshold = math.nextafter(ordered[-1], math.inf)
    else:
        threshold = ordered[len(ordered) - allowed]
    return sum(1 for score in positives if score >= threshold) / len(positives)


def paired_bootstrap_diff(
    a: Sequence[float],
    b: Sequence[float],
    *,
    n_resamples: int = 10_000,
    seed: int = 0,
    confidence: float = 0.95,
) -> tuple[float, float, float, float]:
    """Paired bootstrap for mean(a) - mean(b).

    Returns ``(observed, low, high, p_value)``. The p-value is two-sided and
    uses the percentile bootstrap with a one-count correction.
    """
    if len(a) != len(b) or not a:
        raise ValueError("a and b must have the same non-zero length")
    diffs = [float(x) - float(y) for x, y in zip(a, b, strict=True)]
    n = len(diffs)
    rng = random.Random(seed)
    samples = []
    for _ in range(n_resamples):
        total = 0.0
        for _ in range(n):
            total += diffs[rng.randrange(n)]
        samples.append(total / n)
    samples.sort()
    alpha = (1.0 - confidence) / 2.0
    low = samples[int(alpha * n_resamples)]
    high = samples[min(n_resamples - 1, int((1.0 - alpha) * n_resamples))]
    below = sum(1 for value in samples if value <= 0.0)
    above = sum(1 for value in samples if value >= 0.0)
    p_value = min(1.0, 2.0 * min(below + 1, above + 1) / (n_resamples + 1))
    return sum(diffs) / n, low, high, p_value


def holm(pvalues: Sequence[float]) -> list[float]:
    """Holm step-down adjusted p-values, order preserved."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, index in enumerate(order):
        value = min(1.0, (m - rank) * pvalues[index])
        running = max(running, value)
        adjusted[index] = running
    return adjusted
