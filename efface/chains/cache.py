"""Prefix caches for the chain executor.

A cache maps a prefix key to the text that prefix produced. Because every
tactic is deterministic given its seed, the text after steps ``1..k`` is a
function of the source text, the seed, and the k-step prefix, so a longer chain
can reuse every shorter one it shares.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Protocol


class Cache(Protocol):
    def get(self, key: str) -> str | None: ...

    def put(self, key: str, text: str) -> None: ...


def cache_key(*, doc_id: str, seed: int, source_digest: str, prefix: str) -> str:
    """Key for one (document, seed, prefix) triple.

    ``source_digest`` keeps two different source texts with the same id apart;
    ``doc_id`` namespaces records that share a source.
    """
    material = f"{doc_id}\x1f{seed}\x1f{source_digest}\x1f{prefix}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]


class MemoryCache:
    """Process-local cache. Cheap and enough for one run."""

    def __init__(self) -> None:
        self._entries: dict[str, str] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> str | None:
        text = self._entries.get(key)
        if text is None:
            self.misses += 1
        else:
            self.hits += 1
        return text

    def put(self, key: str, text: str) -> None:
        self._entries[key] = text

    def __len__(self) -> int:
        return len(self._entries)


class DiskCache:
    """One file per key under a directory, so a rerun skips paid calls."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.hits = 0
        self.misses = 0

    def _path(self, key: str) -> Path:
        return self.directory / f"{key}.json"

    def get(self, key: str) -> str | None:
        path = self._path(key)
        if not path.exists():
            self.misses += 1
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self.misses += 1
            return None
        self.hits += 1
        return data.get("text")

    def put(self, key: str, text: str) -> None:
        self._path(key).write_text(
            json.dumps({"text": text}, ensure_ascii=False), encoding="utf-8"
        )

    def __iter__(self) -> Iterator[Path]:
        return self.directory.glob("*.json")
