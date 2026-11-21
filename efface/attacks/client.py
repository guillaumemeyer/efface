"""OpenAI-compatible chat client for the model-backed tactics.

No third-party HTTP dependency: the request is one JSON POST. The provider's
snapshot and endpoint are recorded in the run manifest by the caller; this
class only carries the model id and sampling settings.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class OpenAICompatibleChat:
    base_url: str
    api_key: str
    model: str
    temperature: float = 0.9
    timeout: float = 120.0
    system: str | None = None
    retries: int = 3

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")

    @classmethod
    def from_env(
        cls, *, base_url_env: str, api_key_env: str, model: str, **kwargs
    ) -> OpenAICompatibleChat:
        base_url = os.environ.get(base_url_env)
        api_key = os.environ.get(api_key_env)
        if not base_url or not api_key:
            raise RuntimeError(f"{base_url_env} and {api_key_env} must be set")
        return cls(base_url=base_url, api_key=api_key, model=model, **kwargs)

    def complete(self, prompt: str, *, seed: int = 0) -> str:
        messages = []
        if self.system:
            messages.append({"role": "system", "content": self.system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "seed": seed,
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        last_error: Exception | None = None
        for _ in range(self.retries):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
            except (urllib.error.URLError, KeyError, json.JSONDecodeError) as error:
                last_error = error
        raise RuntimeError(f"chat completion failed after {self.retries} attempts") from last_error
