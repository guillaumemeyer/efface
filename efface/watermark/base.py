"""Generation interface.

A generator turns a prompt into a watermarked document under one key. The
request records every setting that affects the output, so a run manifest can be
reconstructed from it alone.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class GenerationRequest:
    doc_id: str
    prompt: str
    key: int
    model: str
    scheme: str
    max_new_tokens: int = 400
    temperature: float = 0.7
    top_p: float = 0.9
    seed: int = 0
    domain: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GeneratedDocument:
    request: GenerationRequest
    text: str
    unwatermarked_text: str | None = None



class Generator(Protocol):
    def generate(self, request: GenerationRequest) -> GeneratedDocument: ...
