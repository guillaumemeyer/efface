"""Detection: the MarkLLM mean detector and its null-calibrated p-value."""

from efface.detect.base import Detector, DetectorScore
from efface.detect.markllm import (
    MarkLLMDetector,
    NullModel,
    mean_score,
    normal_critical_value,
    pvalue_from_score,
    record_score,
)

__all__ = [
    "Detector",
    "DetectorScore",
    "MarkLLMDetector",
    "NullModel",
    "mean_score",
    "normal_critical_value",
    "pvalue_from_score",
    "record_score",
]
