import json

import pytest

from efface.cli import main
from efface.watermark import (
    GeneratedDocument,
    document_id,
    generate_corpus,
    read_jsonl,
    requests_for_row,
    write_jsonl,
)

ROW = {
    "model": "facebook/opt-1.3b",
    "family": "opt",
    "scheme": "markllm-synthid",
    "max_new_tokens": 32,
    "temperature": 0.7,
    "top_p": 0.9,
    "keys": [3, 42, 1234],
}

PROMPTS = [
    {"prompt_id": "news-0001", "domain": "news", "prompt": "Write a report."},
    {"prompt_id": "news-0002", "domain": "news", "prompt": "Write a second report."},
]


class FakeGenerator:
    """Deterministic stand-in for the MarkLLM adapter."""

    def __init__(self):
        self.seen = []

    def generate(self, request):
        self.seen.append((request.doc_id, request.key, request.seed))
        return GeneratedDocument(request=request, text=f"{request.prompt} k={request.key}")

    def metadata(self):
        return {"kind": "fake"}


def test_one_request_per_prompt_per_key():
    requests = requests_for_row(
        prompt_id="news-0001", prompt="p", domain="news", row=ROW
    )
    assert [r.key for r in requests] == [3, 42, 1234]
    assert len({r.doc_id for r in requests}) == 3
    assert requests[0].doc_id == document_id("news-0001", 3)


def test_corpus_has_one_record_per_document():
    generator = FakeGenerator()
    records = list(generate_corpus(prompts=PROMPTS, row=ROW, generator=generator))
    assert len(records) == 6
    assert len({record["doc_id"] for record in records}) == 6
    assert all(record["key"] in ROW["keys"] for record in records)
    assert len(generator.seen) == 6


def test_record_key_is_the_generation_key():
    records = list(generate_corpus(prompts=PROMPTS[:1], row=ROW, generator=FakeGenerator()))
    for record in records:
        assert record["doc_id"].endswith(f"-k{record['key']}")
        assert f"k={record['key']}" in record["text"]


def test_record_manifest_is_attached():
    records = list(generate_corpus(prompts=PROMPTS[:1], row=ROW, generator=FakeGenerator()))
    manifest = records[0]["manifest"]
    assert manifest["backend"] == {"kind": "fake"}
    assert manifest["efface_version"]
    assert manifest["created_at"]


def test_jsonl_round_trip(tmp_path):
    path = tmp_path / "docs.jsonl"
    records = list(generate_corpus(prompts=PROMPTS[:1], row=ROW, generator=FakeGenerator()))
    assert write_jsonl(records, path) == 3
    assert list(read_jsonl(path)) == records


def test_cli_generate_writes_records(tmp_path, monkeypatch):
    prompts = tmp_path / "prompts.jsonl"
    prompts.write_text("".join(json.dumps(p) + "\n" for p in PROMPTS), encoding="utf-8")
    output = tmp_path / "out.jsonl"

    monkeypatch.setattr("efface.cli._build_generator", lambda row, args: FakeGenerator())
    code = main(
        [
            "generate",
            "--config",
            "configs/generators.yaml",
            "--prompts",
            str(prompts),
            "--output",
            str(output),
            "--limit",
            "1",
        ]
    )
    assert code == 0
    records = list(read_jsonl(output))
    assert len(records) == 3
    assert {record["prompt_id"] for record in records} == {"news-0001"}


def test_cli_generate_needs_a_prompts_file(capsys):
    code = main(["generate", "--config", "configs/generators.yaml"])
    assert code == 2
    assert "--prompts" in capsys.readouterr().err


def test_cli_generate_rejects_unknown_row(tmp_path, capsys):
    prompts = tmp_path / "prompts.jsonl"
    prompts.write_text(json.dumps(PROMPTS[0]) + "\n", encoding="utf-8")
    code = main(
        [
            "generate",
            "--config",
            "configs/generators.yaml",
            "--prompts",
            str(prompts),
            "--row",
            "nope",
        ]
    )
    assert code == 2
    assert "unknown generator row" in capsys.readouterr().err


def test_derive_keys_is_deterministic_and_key_specific():
    from efface.watermark.markllm import derive_keys

    first = derive_keys(seed=7, key=3)
    assert first == derive_keys(seed=7, key=3)
    assert first != derive_keys(seed=7, key=42)
    assert first != derive_keys(seed=8, key=3)
    assert len(first) == 30
    assert all(0 <= value < 65536 for value in first)


def test_missing_markllm_checkout_fails_loudly(tmp_path):
    from efface.watermark.markllm import MarkLLMBackend

    backend = MarkLLMBackend(markllm_dir=tmp_path, model="m")
    with pytest.raises(FileNotFoundError):
        backend._load()
