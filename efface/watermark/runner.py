"""Corpus generation: prompts crossed with keys, one record per document."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from efface.config import digest
from efface.watermark.base import Generator
from efface.watermark.records import (
    build_manifest,
    record_for,
    requests_for_row,
)


def generate_corpus(
    *,
    prompts: Iterable[dict[str, Any]],
    row: dict[str, Any],
    generator: Generator,
    config_path: str | Path | None = None,
    markllm_dir: str | Path | None = None,
    model_revision: str | None = None,
    seed: int = 0,
) -> Iterator[dict[str, Any]]:
    """Yield one record per prompt per key.

    ``row`` is a generator row from `configs/generators.yaml`. The record's
    ``key`` is the generation key and the detection key.
    """
    manifest = build_manifest(
        config_path=config_path,
        config_digest=digest(config_path) if config_path else None,
        markllm_dir=markllm_dir,
        model_revision=model_revision,
        backend_metadata=getattr(generator, "metadata", lambda: {})(),
    )
    for prompt in prompts:
        for request in requests_for_row(
            prompt_id=str(prompt["prompt_id"]),
            prompt=str(prompt["prompt"]),
            domain=str(prompt.get("domain", "")),
            row=row,
            seed=seed,
        ):
            document = generator.generate(request)
            yield record_for(
                document,
                manifest=manifest,
                prompt_id=str(prompt["prompt_id"]),
                seed=seed,
            )
