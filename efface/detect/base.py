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
    pvalue: float
    score: float
    key: int
    detector: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Detector(Protocol):
    def score(self, text: str, key: int) -> DetectorScore: ...
