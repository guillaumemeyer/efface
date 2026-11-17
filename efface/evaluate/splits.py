"""Deterministic document splits.

A split is a function of the document id and a seed, so the same corpus always
produces the same search and held-out sets. Documents are never split across
folds: every key and every attack of a document stays on one side.

Adapted from ``watermarks-remover`` (MIT), which split by sorted document id.
This version hashes the id with a seed so that the split does not correlate
with corpus order.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Sequence
from typing import TypeVar

T = TypeVar("T")


def _digest(value: str, seed: int) -> str:
    return hashlib.sha256(f"{seed}:{value}".encode()).hexdigest()


def split_documents(
    doc_ids: Iterable[str], *, fraction: float = 0.6, seed: int = 20261117
) -> tuple[list[str], list[str]]:
    """Split document ids into ``(search, holdout)``.

    ``fraction`` is the share assigned to search. Both lists are sorted by the
    hash of the id, so the result is deterministic and independent of input
    order.
    """
    if not 0.0 < fraction < 1.0:
        raise ValueError("fraction must lie in (0, 1)")
    unique = sorted(set(doc_ids), key=lambda doc: _digest(doc, seed))
    if not unique:
        return [], []
    if len(unique) == 1:
        return unique, []
    n_search = round(len(unique) * fraction)
    n_search = max(1, min(len(unique) - 1, n_search))
    return unique[:n_search], unique[n_search:]


def split_records(
    records: Sequence[T],
    *,
    key,
    fraction: float = 0.6,
    seed: int = 20261117,
) -> tuple[list[T], list[T]]:
    """Split records by a key function, keeping every record of a document together."""
    ids = [key(record) for record in records]
    search_list, holdout_list = split_documents(ids, fraction=fraction, seed=seed)
    search_ids, holdout_ids = set(search_list), set(holdout_list)
    search = [record for record in records if key(record) in search_ids]
    holdout = [record for record in records if key(record) in holdout_ids]
    return search, holdout
