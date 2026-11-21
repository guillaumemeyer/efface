"""Detection interface.

The detector is a same-config oracle: it is configured with the scheme
parameters and key family used at generation. ``pvalue`` is the value of the
scheme's test under the unwatermarked null.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class DetectorScore:
    """One detection result.

    ``n_eff`` is the number of g-values that entered the mean: unmasked
    positions times the watermarking depth. Each g-value is Bernoulli(1/2)
    under the null, so the score has mean 1/2 and variance ``1/(4 n_eff)``.
    """

    pvalue: float
    score: float
    key: int
    detector: str
    n_eff: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class Detector(Protocol):
    def score(self, text: str, key: int) -> DetectorScore: ...
