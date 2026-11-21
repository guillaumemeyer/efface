# Preregistration

**Study:** EFFACE — finding the most effective meaning-preserving removal tactic,
or ordered chain of up to three tactics, against a SynthID-class text watermark.

**Frozen:** 2026-11-17, before any experimental result exists.

**Detector:** MarkLLM SynthID reimplementation, same configuration at generation
and detection. This is a research reimplementation with its own keying; the
study makes no claim about the production SynthID-Text detector.

**Hash:** recorded in `PREREGISTRATION.sha256`, committed with this file.

## Frozen bytes

The 2026-11-17 freeze is preserved at git commit `818ccf9`, blob
`d33c2f119a444db7a5bdc7753ecfd016d150a632`, with SHA-256
`c4b6c25326ba45c560edbd7d30bb5025f1b04c142e5b1b0d995fb8bd1b6ac688`.

That digest stays fixed. Every later change is an entry in §9, and
`PREREGISTRATION.sha256` continues to describe the working copy. A deviation
never replaces the frozen digest, because a hash that follows the edit attests
to the revised protocol rather than to the freeze.

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
| Watermark keys per prompt | 3, drawn once and fixed |
| Documents | One per prompt per key; each is scored under its own key |
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

**Primary:** held-out per-document removal rate at α = 0.05. A document is
generated under one key and scored under that key; it counts as removed when
the detector fails to reject the unwatermarked null at α = 0.05. The three
documents that share a prompt are repeated measurements of that prompt, so
intervals and paired comparisons resample prompts, not documents. Power is
stated at the number of prompts.

A prompt-level summary that requires all three keys to miss is reported as a
secondary table. It is not the headline number.

**Secondary:**

- Residual TPR at 1% FPR, computed on the pooled attacked set against the
  parametric unwatermarked null.
- Composite preservation score \(S\), each reported preservation metric, and
  the fraction of documents below τ.
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
| BLEURT | Reference-based learned judgement, `(s + 1) / 2` clipped to `[0, 1]`, Tier B, reported only |
| MAUVE | Distributional distance between attacked and unattacked sets, `[0, 1]`, reported only |
| Length ratio | Attacked tokens divided by source tokens, reported only |
| Composite \(S\) | Unweighted mean of BERTScore-F1 and COMET |

Only \(S\) selects the chain and defines the floor τ. BLEURT, MAUVE, and length
ratio are reported on the same documents and do not enter the constraint or the
recommendation, so a tier change cannot move which chain wins. The fraction of
documents with \(S < \tau\) is reported for every recommended chain.

## 5. Decision rule

1. Drop any chain whose mean \(S\) falls below τ − ε.
2. Drop any chain whose removal rate does not exceed its best prefix by more
   than the minimum detectable difference.
3. Among admissible chains, choose the one with the highest removal rate on the
   search split. Break ties by the higher \(S\), then by the shorter chain.
4. Report the chosen chain on the held-out split. The headline number is the
   held-out number.

A chain that only works at maximum intensity is reported with its intensity; it
is not merged with a moderate-intensity chain.

## 6. Statistical treatment

- Removal rates use 95% Wilson intervals on the document count and a
  prompt-clustered bootstrap interval. The prompt-clustered interval is the
  reported interval; the document-level Wilson interval is reported beside it.
- Chain comparisons on the same documents use a paired bootstrap with 10,000
  resamples and a fixed seed, resampling prompts.
- Holm correction is applied within each depth to the family of comparisons
  between a chain and its best prefix.
- Descriptive tables report unadjusted values; the text says which comparisons
  survive correction.
- The minimum detectable difference is 0.05 absolute removal rate. The pilot
  checks whether the prompt count gives at least 80% power at that effect
  size; if not, the shortfall is reported.
- The corpus operating point uses the parametric null in §6: the detector
  statistic is standardised against the unwatermarked null, and TPR at 1% FPR
  is read from that null rather than from the empirical quantile of a small
  negative set. The empirical quantile is reported as a calibration diagnostic.

## 6a. Predeclared detection check

Before any attack table is built, each generator row is checked on at least 200
watermarked documents of at least 150 tokens:

- the observed detection rate at α = 0.05 is at least 0.80, and
- its Wilson lower bound is at least 0.70.

The bounds are fixed here, before the measurement. A row that misses them is
reported as a detection result, the attack sweep for that row stops, and the
paper makes no removal or robustness claim from it.

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
- The attack sweep stops if any generator row fails the detection check in §6a.

## 9. Deviations

Any change to this file after the freeze is recorded here with a date, the
reason, and the affected results.

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-17 | Named the search and ablation attackers; added the second-attacker ablation as a secondary outcome | Design clarification before any removal result; no outcome definition changed |
| 2026-11-21 | One removal unit: each document is scored under the key that generated it, and intervals, bootstrap, and power are prompt-clustered. A prompt-level all-keys-miss table is secondary | Eq. 2, `removed_from_pvalues`, §6, and the power paragraph described different units. The primary outcome, floor, split, and decision rule are unchanged |
| 2026-11-21 | The selecting composite \(S\) is the mean of BERTScore-F1 and clipped COMET. BLEURT, MAUVE, and length ratio are reported beside it | MAUVE is a between-set divergence with no per-document value, and BLEURT exists only at Tier B, so the old composite was a different constraint per tier. τ, the split, and the decision rule are unchanged |
| 2026-11-21 | §6a predeclares a detection check before any attack table: observed TPR at α = 0.05 of at least 0.80 and a Wilson lower bound of at least 0.70 on at least 200 documents per generator row. Both operating points use the parametric null | A removal rate is uninterpretable when the unattacked mark is weak on these models, and 100 negatives do not pin a 1% FPR threshold. No outcome definition changed |
| 2026-11-21 | Detector null: the per-g-value variance is 1/4, not 1/12, and reported p-values use a normal null fitted to unwatermarked documents, with the fit recorded in every score | The g-values are Bernoulli(1/2), and a 60-document G1 pilot measured a null mean of 0.4978 and a variance scale of 0.0871 against the analytic 0.5 and 0.25 (holdout false-positive rate 0.000 analytic, 0.033 fitted). The per-document α, the floor, the split, and the outcome definitions are unchanged |
| 2026-11-21 | Each key id is a 30-entry SynthID key array derived as `sha256("<key_seed>:<key>:<index>") mod 65536`, with `key_seed = 20261117` fixed in `configs/` and recorded in every manifest | MarkLLM keys SynthID from a fixed 30-entry array and applies the whole array per generation, so a per-document key is an array. The three keys per prompt, the split, and the outcome definitions are unchanged |
| 2026-11-21 | The search records a false-skip audit and an off-beam audit | The additive headroom rule and the beam of width 8 are budget rules; their error is measured rather than assumed. Floor, split, and decision rule are unchanged |
| 2026-11-21 | Chain search is three passes. Pass 1 maps every swept intensity and sets each tactic's operating intensity (highest removal among levels with preservation at least τ − ε). Pass 2 is a beam of width 8: four slots by removal, two by preservation, two by the family of the final step. Extensions are skipped when predicted preservation S(p)+S(t)−1 is below τ − 0.10, and a screen of 57 pairs is not extended when it misses the 0.05 margin. Pass 3 tries the next stronger swept intensity on the top five chains and the best single, and keeps it only when preservation stays admissible and removal rises by at least 0.05. Every evaluated chain is still scored on the full search split | The crossed intensity grid has 18,278 cells. The passes search the preservation boundary and drop regions a measured prefix or a measured pair shows cannot win. Floor, split, primary outcome, and decision rule are unchanged |
