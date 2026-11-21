"""Removal and detection statistics.

Definitions used throughout the paper:

- A document is generated under one key and scored under that key. It is
  removed when the detector fails to reject the unwatermarked null at level
  ``alpha``.
- The removal rate is the document mean, with a prompt-clustered bootstrap
  interval and a document-level Wilson interval beside it.
- The residual true-positive rate is measured on attacked watermarked documents
  at a threshold read from the parametric unwatermarked null at a fixed
  false-positive rate. Higher values mean the mark is still detectable.

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


def is_removed(pvalue: float, alpha: float = 0.05) -> bool:
    """True when the detector fails to reject the null under the generating key.

    A document carries one key, the key used to generate it, so removal is a
    single test. Requiring every key to miss is a prompt-level summary and
    lives beside this bit, not in it.
    """
    if not 0.0 <= pvalue <= 1.0:
        raise ValueError("pvalue must lie in [0, 1]")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")
    return pvalue > alpha


def clustered_rate(
    removed: Sequence[bool],
    clusters: Sequence[str],
    *,
    n_resamples: int = 10_000,
    seed: int = 0,
    confidence: float = 0.95,
) -> Rate:
    """Removal rate with a prompt-clustered bootstrap interval.

    The three documents that share a prompt are repeated measurements of that
    prompt, so resampling documents would understate the interval. Clusters
    are resampled whole, and the point estimate stays the document mean.
    """
    if len(removed) != len(clusters):
        raise ValueError("removed and clusters must have the same length")
    if not removed:
        raise ValueError("removed must not be empty")
    by_cluster: dict[str, list[bool]] = {}
    for flag, cluster in zip(removed, clusters, strict=True):
        by_cluster.setdefault(cluster, []).append(flag)
    names = sorted(by_cluster)
    rng = random.Random(seed)
    estimates = []
    for _ in range(n_resamples):
        total = 0
        count = 0
        for _ in names:
            members = by_cluster[names[rng.randrange(len(names))]]
            total += sum(1 for flag in members if flag)
            count += len(members)
        estimates.append(total / count)
    estimates.sort()
    alpha = (1.0 - confidence) / 2.0
    low = estimates[int(alpha * n_resamples)]
    high = estimates[min(n_resamples - 1, int((1.0 - alpha) * n_resamples))]
    value = sum(1 for flag in removed if flag) / len(removed)
    return Rate(value=value, low=low, high=high, n=len(removed))


def normal_quantile(p: float) -> float:
    """Inverse standard normal CDF, for the parametric null threshold."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must lie in (0, 1)")
    # Acklam's rational approximation; absolute error below 1.15e-9.
    a = (-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00)
    b = (-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00)
    plow, phigh = 0.02425, 1.0 - 0.02425
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
        )
    if p > phigh:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
        )
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (
        ((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0
    )


def tpr_at_fpr_parametric(
    positives: Sequence[float],
    negatives: Sequence[float],
    fpr: float = 0.01,
) -> float:
    """TPR at a false-positive rate set by the normal null.

    ``negatives`` are the calibration documents, used to estimate the null mean
    and standard deviation. The 1% threshold is the matching normal quantile of
    that null, which is far more stable than an empirical quantile of a small
    calibration set. Scores are oriented so that higher means more watermarked.
    """
    if not positives or not negatives:
        raise ValueError("both classes must be non-empty")
    if not 0.0 < fpr < 1.0:
        raise ValueError("fpr must lie in (0, 1)")
    n = len(negatives)
    mean = sum(negatives) / n
    variance = sum((value - mean) ** 2 for value in negatives) / (n - 1)
    if variance <= 0.0:
        raise ValueError("negatives must vary to calibrate a null")
    threshold = mean + normal_quantile(1.0 - fpr) * math.sqrt(variance)
    return sum(1 for score in positives if score >= threshold) / len(positives)


def detection_check_pass(
    detected: Sequence[bool],
    *,
    observed_floor: float = 0.80,
    lower_bound_floor: float = 0.70,
) -> bool:
    """Predeclared gate from preregistration §6a.

    The observed detection rate and its Wilson lower bound must both clear
    their floors before an attack table is built for a generator row.
    """
    if not detected:
        raise ValueError("detected must not be empty")
    matched = sum(1 for flag in detected if flag)
    rate = matched / len(detected)
    low, _ = wilson_interval(matched, len(detected))
    return rate >= observed_floor and low >= lower_bound_floor


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
