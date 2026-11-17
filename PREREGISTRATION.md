# Preregistration

**Study:** EFFACE — finding the most effective meaning-preserving removal tactic,
or ordered chain of up to three tactics, against a SynthID-class text watermark.

**Frozen:** 2026-11-17, before any experimental result exists.

**Detector:** MarkLLM SynthID reimplementation, same configuration at generation
and detection. This is a research reimplementation with its own keying; the
study makes no claim about the production SynthID-Text detector.

**Hash:** recorded in `PREREGISTRATION.sha256`, committed with this file.

## 1. Hypotheses

- **H1.** Single tactics differ in removal rate by more than the minimum
  detectable difference (0.05) at the same semantic floor.
- **H2.** The best ordered pair removes more than the best single tactic by at
  least 0.05 absolute removal rate on the held-out split.
- **H3.** The best ordered triple improves on its best prefix by less than 0.05
  absolute removal rate, so the third step buys little removal for its semantic
  cost.
- **H4.** Order matters: for at least one pair, the two orders differ by more
  than 0.05 absolute removal rate.

H3 and H4 are exploratory if the pilot forces Tier A (no depth 3).

## 2. Design

| Factor | Value |
| --- | --- |
| Generators | `facebook/opt-1.3b` (G1); `Qwen/Qwen2.5-1.5B-Instruct` (G2) |
| Scheme | MarkLLM SynthID, same configuration for both rows |
| Domains | News writing, long-form QA, creative writing, MarkMyWords tasks |
| Prompts per domain | 100 |
| Watermark keys per document | 3, drawn once and fixed |
| Documents | One per prompt per key |
| Minimum length | 150 tokens; shorter documents are excluded and counted |
| Search split | 60% of documents, hash of document id with seed 20261117 |
| Held-out split | 40% of documents, untouched during search |
| Attack catalogue | 12 tactics plus a Unicode-scrub control |
| Chain depth | 1 to 3, ordered, repeats allowed |
| Intensities | Default per tactic in the main sweep; depth-1 intensity sweep |
| Search attacker | DeepSeek Flash, one model per chain |
| Ablation attacker | Claude Sonnet on the top five chains, the best single tactic, and the control |
| Stochastic repetitions | 3 seeds per document; the mean is scored |

## 3. Outcomes

**Primary:** held-out per-document removal rate at α = 0.05. A document counts
as removed when the mark fails to be detected under every one of its three keys.

**Secondary:**

- Residual TPR at 1% FPR, computed on the pooled attacked set against an
  unwatermarked null set.
- Composite preservation score and each per-metric value.
- Length ratio.
- Removal and preservation by domain and by length bucket.
- Removal at τ − 0.05 and τ + 0.05.
- Marginal removal of each chain over its best prefix.
- Rank stability across the two attackers: Spearman correlation over the ablated
  rows and the largest absolute removal change.

## 4. Metrics

| Metric | Definition |
| --- | --- |
| BERTScore-F1 | Reference-based similarity to the source, `[0, 1]` |
| COMET | Reference-based adequacy and fluency, clipped to `[0, 1]` |
| BLEURT | Reference-based learned judgement, `(s + 1) / 2` clipped to `[0, 1]`, Tier B only |
| MAUVE | Distributional distance between attacked and unattacked sets, `[0, 1]` |
| Composite | Unweighted mean of the metrics available at the tier |
| Length ratio | Attacked tokens divided by source tokens |

The composite is computed per tier. Tier A and Tier B composites are not
compared.

## 5. Decision rule

1. Drop any chain whose mean composite falls below τ − ε.
2. Drop any chain whose removal rate does not exceed its best prefix by more
   than the minimum detectable difference.
3. Among admissible chains, choose the one with the highest removal rate on the
   search split. Break ties by the higher composite, then by the shorter chain.
4. Report the chosen chain on the held-out split. The headline number is the
   held-out number.

A chain that only works at maximum intensity is reported with its intensity; it
is not merged with a moderate-intensity chain.

## 6. Statistical treatment

- Removal rates use 95% Wilson intervals.
- Chain comparisons on the same documents use a paired bootstrap with 10,000
  resamples and a fixed seed.
- Holm correction is applied within each depth to the family of comparisons
  between a chain and its best prefix.
- Descriptive tables report unadjusted values; the text says which comparisons
  survive correction.
- The minimum detectable difference is 0.05 absolute removal rate. The pilot
  checks whether the document count gives at least 80% power at that effect
  size; if not, the shortfall is reported.

## 7. Exclusions and failures

- Documents below 150 tokens are excluded before any attack and counted.
- A failed API call is retried up to three times with exponential backoff. A
  document that still fails is excluded and counted by tactic.
- A document whose attacked text is empty or shorter than 50 tokens is treated
  as a failure of that tactic, not as a removal.
- No document is dropped after seeing its detector score.

## 8. Stopping rules

- Search stops at depth 3.
- Search stops earlier if no chain survives pruning.
- A run stops if projected API spend exceeds the configured cap. The partial
  result is written and the run is marked incomplete.

## 9. Deviations

Any change to this file after the freeze is recorded here with a date, the
reason, and the affected results.

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-17 | Named the search and ablation attackers; added the second-attacker ablation as a secondary outcome | Design clarification before any removal result; no outcome definition changed |
