"""Configuration loading.

Configs are YAML files under ``configs/``. A run refuses to start without a
configuration, and every result records the configuration path and its hash.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


def load(path: str | Path) -> dict[str, Any]:
    """Load one YAML mapping and reject empty or non-mapping files."""
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{config_path} must contain a YAML mapping")
    return data


def loads(text: str) -> dict[str, Any]:
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("configuration must be a YAML mapping")
    return data


def digest(path: str | Path) -> str:
    """SHA-256 of a config file, for the run manifest."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_all(directory: str | Path) -> dict[str, dict[str, Any]]:
    config_dir = Path(directory)
    return {path.stem: load(path) for path in sorted(config_dir.glob("*.yaml"))}
