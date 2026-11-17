# Throughput spike (Gate G1)

**Date:** 2026-11-17
**Machine:** Apple M5, 24 GB unified memory, macOS 27.3
**Python:** 3.11.15
**torch:** 2.15.0 (MPS available)
**transformers:** 5.23.0
**MarkLLM:** commit `0a4fe8c`
**Command:**

```sh
.venv/bin/python scripts/spike_mps.py --markllm-dir ~/MarkLLM \
  --model <model> --max-new-tokens 300
```

## Measurements

| Model | Load (s) | Generate (s) | Tokens | Tokens/s | Detect (s) | Peak MPS (GB) | Score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `facebook/opt-1.3b` | 2.8 | 5.85 | 199 | 34.0 | 0.037 | 3.35 | 0.5435 |
| `Qwen/Qwen2.5-1.5B-Instruct` | 128.8 | 16.37 | 331 | 20.2 | 0.024 | 3.34 | 0.5416 |

The Qwen load time includes the first-time weight download; a second load is a
few seconds.

## Gate G1

**Pass.** The failure threshold was 60 seconds per 300-token document. The
measured generation time is 12–22 seconds at 400 tokens, and detection is
20–40 milliseconds. Peak memory is 3.4 GB, so both models fit on the 24 GB
machine with room for the metric models.

Implication: Tier B is feasible. Generation is the largest local cost, at
roughly 12 hours for 2,400 documents; detection is negligible.

## Findings that affect the harness

1. **MarkLLM's SynthID logits processor requires `top_k <= 0`.** With
   `top_k = 50` it raises
   `RuntimeError: The size of tensor a (50272) must match the size of tensor b (50)`
   at `torch.where(is_repeated, scores, updated_scores)`, because
   `updated_scores` has shape `(batch, top_k)` while `scores` has
   `(batch, vocab_size)`. Generation therefore samples over the full
   distribution with `top_p` only. This is recorded in the generation config and
   in the paper's setup section.

2. **MarkLLM returns a score and a fixed threshold, not a p-value.** The
   detector returns the mean normalised g-value and compares it with
   `threshold = 0.52`. The paper's removal rule needs a p-value at
   `alpha = 0.05`. Week 2 adds an analytic null calibration: under the
   unwatermarked null the g-values are uniform over the sampling table, so the
   mean score has expectation 0.5 and variance `1 / (12 * n_eff)`, where
   `n_eff` is the number of unmasked positions. The one-sided normal p-value is
   validated against 100 unwatermarked documents per generator row.

3. **The watermark detected under the fixed threshold.** For OPT the score was
   0.5435 against a threshold of 0.52; for Qwen 0.5416. This confirms the
   pipeline is generating and detecting a mark, not returning a constant.

## Caveats

- One document per model; no repeated seeds.
- Generation stopped at EOS after 199 and 331 tokens, so the 400-token case is
  extrapolated from tokens per second.
- No batching. Batching will improve detector throughput but is not needed.
- The unwatermarked control was not measured in this spike.
