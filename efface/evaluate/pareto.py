"""Pareto frontier selection for removal against preservation.

Adapted from ``watermarks-remover`` (MIT).
"""

from __future__ import annotations

from collections.abc import Sequence


def pareto_frontier(
    points: Sequence[tuple[float, float]],
    *,
    maximize: tuple[bool, bool] = (True, True),
) -> list[int]:
    """Indices of points not dominated on both axes.

    A point dominates another when it is at least as good on both axes and
    strictly better on one. Duplicate points are all kept.
    """
    if not points:
        return []
    sign = (1.0 if maximize[0] else -1.0, 1.0 if maximize[1] else -1.0)
    scaled = [(sign[0] * x, sign[1] * y) for x, y in points]
    keep: list[int] = []
    for i, (xi, yi) in enumerate(scaled):
        dominated = False
        for j, (xj, yj) in enumerate(scaled):
            if i == j:
                continue
            if xj >= xi and yj >= yi and (xj > xi or yj > yi):
                dominated = True
                break
        if not dominated:
            keep.append(i)
    return keep
