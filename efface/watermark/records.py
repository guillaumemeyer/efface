"""Generation records and run manifests.

One record is one document: one prompt under one key. The record carries the
key that generated it, because that is the key the detector must use
(preregistration R1). Every record also carries the manifest of the run that
produced it, so a result can be traced to a config, a commit, and a model
revision.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from efface import __version__
from efface.watermark.base import GeneratedDocument, GenerationRequest


def document_id(prompt_id: str, key: int) -> str:
    """Stable id for one prompt under one key."""
    return f"{prompt_id}-k{key}"


def _git_sha(path: Path | None = None) -> str | None:
    """Commit of the repository at ``path``, or None outside git."""
    command = ["git", "-C", str(path or Path.cwd()), "rev-parse", "HEAD"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def build_manifest(
    *,
    config_path: str | Path | None = None,
    config_digest: str | None = None,
    markllm_dir: str | Path | None = None,
    model_revision: str | None = None,
    backend_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Everything a reader needs to reconstruct how a record was produced."""
    resolved_markllm = Path(markllm_dir).expanduser() if markllm_dir else None
    return {
        "efface_version": __version__,
        "efface_sha": _git_sha(),
        "markllm_dir": str(resolved_markllm) if resolved_markllm else None,
        "markllm_sha": _git_sha(resolved_markllm) if resolved_markllm else None,
        "model_revision": model_revision,
        "config_path": str(config_path) if config_path else None,
        "config_digest": config_digest,
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "backend": backend_metadata or {},
    }


def record_for(
    document: GeneratedDocument,
    *,
    manifest: dict[str, Any],
    prompt_id: str,
    seed: int,
) -> dict[str, Any]:
    """Serialise one generated document.

    ``key`` is the watermark key. Detection reads this field, so a record
    cannot be scored under a different key without editing it.
    """
    request = document.request
    return {
        "doc_id": request.doc_id,
        "prompt_id": prompt_id,
        "domain": request.domain,
        "key": request.key,
        "model": request.model,
        "family": request.metadata.get("family"),
        "scheme": request.scheme,
        "seed": seed,
        "decoding": {
            "max_new_tokens": request.max_new_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
        },
        "text": document.text,
        "unwatermarked_text": document.unwatermarked_text,
        "manifest": manifest,
    }


def write_jsonl(records: Iterable[dict[str, Any]], path: str | Path) -> int:
    """Write records as JSON Lines; return the count."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with target.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def read_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def requests_for_row(
    *,
    prompt_id: str,
    prompt: str,
    domain: str,
    row: dict[str, Any],
    seed: int = 0,
) -> list[GenerationRequest]:
    """One request per key in the row, each with its own document id."""
    return [
        GenerationRequest(
            doc_id=document_id(prompt_id, key),
            prompt=prompt,
            key=key,
            model=row["model"],
            scheme=row["scheme"],
            max_new_tokens=int(row.get("max_new_tokens", 400)),
            temperature=float(row.get("temperature", 0.7)),
            top_p=float(row.get("top_p", 0.9)),
            seed=seed,
            domain=domain,
            metadata={"family": row.get("family")},
        )
        for key in row["keys"]
    ]
