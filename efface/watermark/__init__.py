"""Watermark generation: records, the MarkLLM adapter, and the corpus runner."""

from efface.watermark.base import GeneratedDocument, GenerationRequest, Generator
from efface.watermark.markllm import MarkLLMBackend, WatermarkGenerator
from efface.watermark.records import (
    build_manifest,
    document_id,
    read_jsonl,
    record_for,
    requests_for_row,
    write_jsonl,
)
from efface.watermark.runner import generate_corpus

__all__ = [
    "GeneratedDocument",
    "GenerationRequest",
    "Generator",
    "MarkLLMBackend",
    "WatermarkGenerator",
    "build_manifest",
    "document_id",
    "generate_corpus",
    "read_jsonl",
    "record_for",
    "requests_for_row",
    "write_jsonl",
]
