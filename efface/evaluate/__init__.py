"""Evaluation primitives: rates, intervals, splits, frontier, cost."""

from efface.evaluate.stats import (
    Rate,
    auroc,
    holm,
    paired_bootstrap_diff,
    removal_rate,
    removed_from_pvalues,
    tpr_at_fpr,
    wilson_interval,
)

__all__ = [
    "Rate",
    "auroc",
    "holm",
    "paired_bootstrap_diff",
    "removal_rate",
    "removed_from_pvalues",
    "tpr_at_fpr",
    "wilson_interval",
]
