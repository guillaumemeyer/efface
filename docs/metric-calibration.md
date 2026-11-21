# Preservation metrics: stack and fixture

**Date:** 2026-11-21
**Selecting composite:** `S` = mean of BERTScore-F1 and COMET (preregistration R2)

## Stack

| Package | Version |
| --- | --- |
| `bert-score` | 0.3.13 |
| `unbabel-comet` | 2.2.7 |
| `sentence-transformers` | 5.7.0 |
| `torch` | 2.15.0 |
| `transformers` | 4.57.6 |
| `numpy` | 1.26.4 |

Models: `roberta-large` for BERTScore; `Unbabel/wmt22-comet-da` for COMET.

## Dependencies that needed fixing

- **`comet` is the wrong PyPI name.** It is an astronomy VOEvent broker. The
  translation metric is `unbabel-comet`, and its import name is still `comet`.
  The pin now names `unbabel-comet`.
- **COMET model ids are Hugging Face repo ids.** `wmt22-comet-da` resolves only
  through the legacy downloader; `Unbabel/wmt22-comet-da` is the current id.
- **COMET 2.2.7 and torch 2.x disagree on the DataLoader.** At `gpus=0` COMET
  passes `multiprocessing_context="fork"` on a Mac with `num_workers=0`, which
  torch rejects. The adapter passes `num_workers=1`.
- **`unbabel-comet` pins `torchmetrics` 0.10, which imports `pkg_resources`**,
  removed in `setuptools` 81+. The metrics extra pins `setuptools<81`.

## Ten-pair fixture

`tests/fixtures/metrics/pairs.json` holds ten source/candidate pairs across news,
question answering, creative writing, a typo case, and two long passages.
`tests/fixtures/metrics/expected.json` records the values from the run below.

| Pair | `S` | Length ratio |
| --- | --- | --- |
| news-1 | 0.9546 | 1.00 |
| news-2 | 0.9487 | 1.00 |
| qa-1 | 0.9094 | 1.00 |
| qa-2 | 0.8246 | 1.00 |
| creative-1 | 0.8731 | 1.00 |
| creative-2 | 0.9119 | 1.00 |
| typo-1 | 0.8329 | 1.00 |
| short-1 | 0.9411 | 1.20 |
| long-1 | 0.9201 | 1.04 |
| long-2 | 0.9339 | 1.19 |

Aggregate `S` = 0.905; no pair falls below τ = 0.80.

The typo pair scores 0.833 while changing three words. That is the composite
behaving as documented: character noise costs less than the edit looks like it
costs, which is why per-metric tables and failure cases are reported beside `S`.

## Reproduce

```sh
uv pip install -e ".[metrics]"
.venv/bin/python scripts/score_pairs.py --pairs tests/fixtures/metrics/pairs.json \
  --output results/metrics-fixture.json
EFFACE_METRICS=1 .venv/bin/python -m pytest tests/test_preservation_fixture.py
```

The fixture test is skipped unless `EFFACE_METRICS=1`, because the first run
downloads `roberta-large` and the COMET checkpoint (several GB).
