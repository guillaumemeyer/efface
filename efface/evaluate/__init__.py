"""Evaluation primitives: rates, intervals, splits, frontier, cost."""

from efface.evaluate.stats import (
    Rate,
    auroc,
    clustered_rate,
    detection_check_pass,
    holm,
    is_removed,
    normal_quantile,
    paired_bootstrap_diff,
    removal_rate,
    tpr_at_fpr,
    tpr_at_fpr_parametric,
    wilson_interval,
)

__all__ = [
    "Rate",
    "auroc",
    "clustered_rate",
    "detection_check_pass",
    "holm",
    "is_removed",
    "normal_quantile",
    "paired_bootstrap_diff",
    "removal_rate",
    "tpr_at_fpr",
    "tpr_at_fpr_parametric",
    "wilson_interval",
]
