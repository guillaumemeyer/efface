# Detector calibration

**Date:** 2026-11-21
**Row:** G1, `facebook/opt-1.3b`
**Scheme:** MarkLLM SynthID reimplementation, commit `0a4fe8c`
**Key:** id 3 (30-entry derived array, seed 20261117)

## What the score is

MarkLLM's mean detector returns the mean of the g-values that survive the
end-of-text and context-repetition masks. Each g-value is a fair coin under the
unwatermarked null, so the score has mean 1/2 and variance `1 / (4 n_eff)`,
where `n_eff` is the number of unmasked positions times the depth (30).

D10 originally recorded `1 / (12 n_eff)`. That is the variance of a continuous
uniform draw; the g-values here are binary. The constant was corrected before
any removal result existed.

## Pilot calibration

60 unwatermarked documents: three prompts (news, question answering, creative
writing) times 20 seeds, 120 new tokens, the row's decoding settings.

| Quantity | Value |
| --- | --- |
| Mean score | 0.4978 |
| SD of score | 0.0077 |
| `n_eff` range | 510 to 9,180 |
| Fitted null mean | 0.4978 |
| Fitted variance scale | 0.0871 |
| Documents in the fit | 60 |

The fitted model is `score ~ Normal(mean, variance_scale / n_eff)`.

## End-to-end check

Half the documents fit the null, the other half test it.

| Quantity | Analytic null (0.5, 0.25) | Fitted null |
| --- | --- | --- |
| Holdout z mean | −0.24 | −0.38 |
| Holdout z SD | 1.26 | 1.26 |
| Holdout fraction with p < 0.05 | 0.000 | 0.033 |

The analytic null puts the centre at 0.5 while the measured null mean is
0.4978, and it assumes a variance scale of 0.25 while the fit is 0.0871. The
fitted null puts the holdout false-positive rate near the nominal 5%. Its
holdout z SD of 1.26 means the variance is under-estimated on held-out
documents, so the test is slightly liberal; 30 holdout documents are too few to
settle that, and W2.13 repeats the check with at least 200 documents per row.

A first run of this calibration used a key array that never reached MarkLLM
(the scheme's constructor drops keyword overrides), so every "key" produced
identical scores. The numbers above come from the corrected adapter; key ids 3,
42, and 1234 now score 0.5674, 0.5394, and 0.5586 on the same prompt.

## Consequences

- Reported p-values use a fitted null loaded from `--null`. The analytic null
  remains the default when no calibration exists.
- The fit is recorded in every score record under
  `metadata.null`, together with the document count.
- The pilot uses 60 documents. The preregistration requires at least 200 per
  generator row before the detection gate is read (W2.13); the gate is not
  passed on this pilot.
- G2 has not been calibrated yet.

## Reproduce

```sh
python scripts/calibrate_null.py --row g1 --prompts <prompts.jsonl> \
  --seeds 20 --key 3 --output results/null-g1.json
```
