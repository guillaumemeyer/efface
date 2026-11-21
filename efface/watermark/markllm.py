"""MarkLLM SynthID generation adapter.

The backend is loaded lazily: importing this module costs nothing, and the
MarkLLM checkout, torch, and the model weights are touched only when a
generation request arrives. That keeps the test suite and the CLI importable
on a machine without the stack installed.

See `docs/perf.md` for the two MarkLLM behaviours this adapter works around:
the SynthID logits processor requires ``top_k <= 0``, and generation is
sampled with ``top_p`` only.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any, Protocol

from efface.watermark.base import GeneratedDocument, GenerationRequest

# MarkLLM's SynthID config carries a fixed 30-entry key array and hashes every
# generation with all of it. Per-document keys are therefore key *arrays*
# derived from one master seed and the key id; the derivation is recorded with
# the document so the detector can rebuild the same array.
KEY_LENGTH = 30
KEY_DERIVATION = "sha256('<seed>:<key>:<index>') mod <table_size>"


def derive_keys(
    *,
    seed: int,
    key: int,
    length: int = KEY_LENGTH,
    table_size: int = 65536,
) -> list[int]:
    """Deterministic key array for one (seed, key id) pair."""
    if length < 1:
        raise ValueError("length must be positive")
    if table_size < 2:
        raise ValueError("table_size must be at least 2")
    return [
        int.from_bytes(hashlib.sha256(f"{seed}:{key}:{index}".encode()).digest()[:8], "big")
        % table_size
        for index in range(length)
    ]


class Backend(Protocol):
    """Anything that can turn a prompt into watermarked text under a key."""

    def generate(self, prompt: str, *, key: int, seed: int, request: GenerationRequest) -> str: ...

    def metadata(self) -> dict[str, Any]: ...


class MarkLLMBackend:
    """Load one open-weight model with the MarkLLM SynthID scheme."""

    def __init__(
        self,
        *,
        markllm_dir: str | Path,
        model: str,
        revision: str | None = None,
        device: str | None = None,
        key_seed: int = 20261117,
        table_size: int = 65536,
    ) -> None:
        self.markllm_dir = Path(markllm_dir).expanduser().resolve()
        self.model = model
        self.revision = revision
        self.device = device
        self.key_seed = key_seed
        self.table_size = table_size
        self._loaded = False
        self._by_key: dict[int, Any] = {}
        self._tokenizer: Any = None
        self._device: str | None = None

    def _load(self) -> None:
        if self._loaded:
            return
        scheme_file = self.markllm_dir / "watermark" / "synthid" / "synthid.py"
        if not scheme_file.exists():
            raise FileNotFoundError(f"MarkLLM checkout not found at {self.markllm_dir}")
        sys.path.insert(0, str(self.markllm_dir))

        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from utils.transformers_config import TransformersConfig
        from watermark.synthid.synthid import SynthID

        self._device = self.device or ("mps" if torch.backends.mps.is_available() else "cpu")
        self._tokenizer = AutoTokenizer.from_pretrained(self.model, revision=self.revision)
        model = AutoModelForCausalLM.from_pretrained(self.model, revision=self.revision)
        model.to(self._device)
        model.eval()

        config = TransformersConfig(
            model=model,
            tokenizer=self._tokenizer,
            device=self._device,
            max_new_tokens=400,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
        self._config_class = TransformersConfig
        self._transformers_config = config
        self._synthid_class = SynthID
        self._synthid_path = str(self.markllm_dir / "config" / "SynthID.json")
        self._torch = torch
        self._loaded = True

    def _scheme_for(self, key: int) -> Any:
        """One SynthID instance per key array; the model is shared."""
        scheme = self._by_key.get(key)
        if scheme is None:
            keys = derive_keys(
                seed=self.key_seed, key=key, table_size=self.table_size
            )
            scheme = self._synthid_class(self._synthid_path, self._transformers_config, keys=keys)
            self._by_key[key] = scheme
        return scheme

    def generate(
        self, prompt: str, *, key: int, seed: int, request: GenerationRequest
    ) -> str:
        self._load()
        scheme = self._scheme_for(key)
        config = scheme.config
        config.max_new_tokens = request.max_new_tokens
        config.temperature = request.temperature
        config.top_p = request.top_p
        self._torch.manual_seed(seed)
        if self._device == "mps":
            self._torch.mps.manual_seed(seed)
        return scheme.generate_watermarked_text(prompt)

    def metadata(self) -> dict[str, Any]:
        return {
            "kind": "markllm-synthid",
            "markllm_dir": str(self.markllm_dir),
            "model": self.model,
            "revision": self.revision,
            "device": self._device or self.device,
            "key_seed": self.key_seed,
            "key_length": KEY_LENGTH,
            "key_table_size": self.table_size,
            "key_derivation": KEY_DERIVATION,
        }


class WatermarkGenerator:
    """`Generator` protocol implementation over a backend."""

    def __init__(self, backend: Backend) -> None:
        self.backend = backend

    def generate(self, request: GenerationRequest) -> GeneratedDocument:
        text = self.backend.generate(
            request.prompt, key=request.key, seed=request.seed, request=request
        )
        return GeneratedDocument(request=request, text=text)

    def metadata(self) -> dict[str, Any]:
        return self.backend.metadata()
