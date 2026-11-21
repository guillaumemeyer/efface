# Decision record

Status: provisional. The defaults from `PLAN.md` §15 are adopted so that Week 1
can proceed. Any change after 2026-11-23 is recorded here with a date and a
reason.

## D1 — Publication order

arXiv preprint first. A venue submission follows once the preprint is posted.
No venue template work is in scope for the five-week plan.

## D2 — Detector and scheme

The study uses the **MarkLLM SynthID reimplementation**, not the
`google-deepmind/synthid-text` reference implementation.

- MarkLLM implements the SynthID sampling-bias scheme with its own keying.
- Google retired SynthID text-watermark detection on its API in August 2026, so
  no vendor tier exists to verify against.
- Every claim in the paper is therefore about the MarkLLM scheme configuration,
  at the recorded commit, and not about the production SynthID-Text detector.
- Pinned commit: `0a4fe8c642b31b8a8c4993615b1c70a0c300d918`.

The MarkLLM commit is recorded in every run manifest. Its SynthID logits
processor requires `top_k <= 0`; with a positive `top_k` it returns a tensor of
the wrong width. Generation therefore uses `top_p` only.

## D3 — Human ratings dropped

No human evaluation. Preservation rests on BERTScore, COMET, MAUVE, and length
ratio at Tier A, with BLEURT added at Tier B. The limitations section says this
plainly. No ethics approval is needed because no human subjects are involved.

## D4 — Generator rows

| Row | Model | Scheme | Rationale |
| --- | --- | --- | --- |
| G1 | `facebook/opt-1.3b` | MarkLLM SynthID | Default model of the MarkLLM SynthID configuration; fits on MPS |
| G2 | `Qwen/Qwen2.5-1.5B-Instruct` | MarkLLM SynthID, same config | Second family, Apache-2.0, comparable size |

The hosted row is removed. A hosted model exposes no logits, so the
sampling-time scheme cannot be applied to it, and the vendor detector no longer
exists.

G2 is confirmed: `Qwen/Qwen2.5-1.5B-Instruct` generated and detected under the
same MarkLLM SynthID config in the Week 1 spike (`docs/perf.md`).

## D5 — Attack catalogue

Twelve removal tactics plus one control. No tactic is dropped at this stage.
The five tactics absent from `watermarks-remover` are implemented in Week 2.

**Cross-lingual generation** is defined operationally as follows, so that it is
a transformation of an existing document rather than a generation task:

1. Translate the source document into the pivot language.
2. Ask the attacker model to rewrite the translated document in the pivot
   language, preserving its claims.
3. Translate the result back into English.

This differs from single-pivot back-translation because step 2 generates new
wording in the pivot instead of translating the source word for word.

## D6 — Metrics and composite

| Metric | Role | Normalisation |
| --- | --- | --- |
| BERTScore-F1 | Selects: half of \(S\) | Already in `[0, 1]` |
| COMET | Selects: half of \(S\) | Clip to `[0, 1]` |
| BLEURT | Reported at Tier B | `(s + 1) / 2`, clipped to `[0, 1]` |
| MAUVE | Reported | Already in `[0, 1]`; a set divergence, so no per-document value |
| Length ratio | Reported | Attacked tokens over source tokens |

The selecting composite is \(S = \tfrac{1}{2}(\text{BERTScore-F1} + \text{COMET})\).
Only \(S\) defines τ and chooses the chain. BLEURT, MAUVE, and length ratio are
reported beside \(S\) and never enter the constraint, so the recommendation
does not move when a tier adds BLEURT. COMET is called with the source
document on the source side, the attacked document as the hypothesis, and the
watermarked source as the reference. The fraction of documents with \(S < \tau\)
is reported for every recommended chain.

## D7 — Preregistered settings

| Setting | Value |
| --- | --- |
| Semantic floor τ | 0.80 on the composite |
| Floor tolerance ε | 0.02 |
| Minimum detectable difference | 0.05 absolute removal rate |
| Beam width B | 8 |
| Maximum chain depth | 3 |
| Search/holdout split | 60/40 by document, seed 20261117 |
| Prompts per domain | 100 at Tier B |
| Watermark keys per prompt | 3 |
| Documents | One per prompt per key, each scored under its generating key |
| Intervals and bootstrap | Prompt-clustered |
| Stochastic repetitions | 3 seeds per document |
| Minimum document length | 150 tokens |
| Per-document α | 0.05 |
| Corpus operating point | TPR at 1% FPR |
| Multiplicity | Holm within each depth |

τ is revised at most once, after the Week 2 pilot and before the main sweep. A
revision is recorded in `PREREGISTRATION.md` as a dated deviation.

On 2026-11-21 the chain search was refined into the three passes in
`paper/sections/05-combination-search.tex`: operating intensities from the
depth-1 map, a diverse beam, a headroom skip, an order screen of 57 pairs, and
a one-step intensity adjustment on the shortlist. The floor, the beam width,
the split, and the decision rule are unchanged. The deviation is recorded in
`PREREGISTRATION.md`.

## D8 — Prompt sources

Self-authored prompts for news writing, long-form question answering, and
creative writing, generated from a documented template and a public topic list.
The MarkMyWords tasks are loaded from the upstream release; prompts are
redistributed only if that project's licence allows it, otherwise the manifest
records the loader and checksum.

Self-authored prompts trade comparability for licence clarity. The limitations
section states this.

## D9 — Code release

The full attack catalogue and harness are released under MIT with a
responsible-use notice. The release ships no service and no vendor integration.

## D10 — Detector p-values

MarkLLM returns a mean normalised g-value and compares it with a fixed
threshold of 0.52. The paper's removal rule is defined at `alpha = 0.05`, so the
harness derives a p-value rather than reusing that threshold.

Under the unwatermarked null, the g-values are uniform over the sampling table,
so the normalised mean score has expectation 0.5 and variance
`1 / (12 * n_eff)`, where `n_eff` is the number of unmasked positions. The
harness reports the one-sided normal p-value and validates its calibration on
100 unwatermarked documents per generator row. If the empirical null is
over-dispersed, the variance is estimated from that calibration set instead and
the change is recorded here.

Both operating points use that null. The per-document removal test takes its
critical value from the normal null, and the corpus TPR at 1% FPR takes its
threshold from the same distribution. The empirical 1% quantile of the
calibration set is reported as a diagnostic; 100 negatives cannot pin a 1%
threshold. The calibration set grows when the null is over-dispersed.

**Detection check before any attack table (added 2026-11-21).** On at least 200
watermarked documents of at least 150 tokens per generator row, the observed
detection rate at α = 0.05 must be at least 0.80 and its Wilson lower bound at
least 0.70. A row that misses stops its attack sweep.

## D11 — Attacker models

| Role | Search sweep | Second-attacker ablation |
| --- | --- | --- |
| Paraphrase and style | DeepSeek Flash | Claude Sonnet |
| Translation | DeepSeek Flash | Claude Sonnet |
| Synonym candidates | DeepSeek Flash | Claude Sonnet |
| Regeneration | DeepSeek Flash | Claude Sonnet |
| Masked-LM infilling | local `roberta-large` | local `roberta-large` |

Rules:

- **One attacker per chain.** Every step of a chain uses the same model, so a
  chain's result is attributable to the tactic sequence rather than to a model
  switch inside the sequence.
- **Search with the cheap model.** DeepSeek Flash keeps the search and the
  intensity sweep inside the API cap.
- **Confirm with the strong model.** The top five chains, the best single
  tactic, and the Unicode control are re-run end to end on the held-out split
  with Claude Sonnet. The paper reports the rank correlation and the largest
  removal delta.
- **Opus is not used.** The capability gap from Flash to Sonnet is the
  informative contrast; Opus adds cost with little extra signal. A single Opus
  run on the best chain remains an optional upper bound.
- **Pin snapshots.** The provider model identifier and snapshot date are
  recorded in every run manifest. The config carries the family name until
  W2.1 confirms the exact snapshot.

Estimated ablation cost: 7 rows over the held-out split is about 6,700
document-attacks, roughly $45–$60 at Sonnet 5.5 list prices after the tokenizer
allowance. Details in `docs/budget.md`.

## D12 — Estimand locks before the first attack score

Added 2026-11-21, before any removal result exists. These supersede the earlier
wording of D6 and D7 where the two differ, and they change no collected number
because none has been collected.

| ID | Lock |
| --- | --- |
| R1 | A document is generated under one key and scored under that key. It is removed when that p-value exceeds 0.05. Three keys produce three documents that share a prompt; intervals and the paired bootstrap resample prompts, and power is stated in prompts. All-three-keys-miss is a secondary table |
| R2 | \(S\), the selecting composite, is the mean of BERTScore-F1 and clipped COMET (D6). BLEURT, MAUVE, and length ratio are reported and stay out of τ |
| R3 | The detection check in D10 gates every attack table |
| R4 | The headroom rule and the beam are budget rules whose error is measured: 30 skipped extensions or 10% of refusals, whichever is smaller, plus 20 off-beam pairs. Both rates enter §5 and §7 |
| R5 | Catalogue rows name the closest published relative in the Source column and state their operational difference. Adaptive paraphrasers, cross-lingual summarization removal, and copy-paste mixing are listed as attacks the search does not run |
| R6 | Both operating points use the parametric null from D10; the empirical 1% quantile is a diagnostic |

## Gate G1

**Pass**, 2026-11-17. Measured on the M5: 12–22 seconds per 400-token
document, 0.02–0.04 seconds per detection, 3.4 GB peak. Tier B is feasible.
Details in `docs/perf.md`.

## Ethics decisions (E1–E6)

Recorded in `docs/ethics.md` on 2026-11-17.

| ID | Decision | Consequence |
| --- | --- | --- |
| E1 | Proceed with the DeepSeek hosted API for the search, with mitigations | No attacked documents are published; training opt-out; dedicated account; open-weight attacker is the fallback |
| E2 | MAUVE stays in the metric set as an optional GPLv3 extra, invoked as a subprocess | `mauve-text` is out of the `metrics` extra; the MIT core does not import it |
| E3 | Disclosure floor of ten days before posting | Follow up after five business days; grant up to 90 days if a maintainer asks |
| E4 | Disclose the author's separate removal tool in the paper and README | Competing interest stated; EFFACE itself ships no service |
| E5 | Load MarkMyWords task text; do not redistribute it | The bundled text is third-party content; the manifest records the loader and checksums |
| E6 | Release code, configs, and aggregate results only | No attacked corpus, model weights, or hosted endpoint |

## Open items

| ID | Item | Owner | Due |
| --- | --- | --- | --- |
| O1 | ~~Confirm `Qwen/Qwen2.5-1.5B-Instruct` runs under MarkLLM SynthID~~ — done in W1.6 | — | 2026-11-17 |
| O2 | Author affiliation for `main.tex` and `CITATION.cff` | Author | 2026-12-01 |
| O3 | ~~Record MarkLLM commit and model revisions~~ — commit `0a4fe8c`; HF revisions recorded in W2.1 | W2.1 | 2026-11-24 |
| O4 | ~~Confirm both providers and their terms of service~~ — done; see `docs/ethics.md` §4 | — | 2026-11-17 |
| O5 | Validate the normal-approximation p-value on 100 unwatermarked documents per row | W2.2 | 2026-11-24 |
| O6 | Pin exact attacker snapshots and list prices in `configs/attackers.yaml` — current: `deepseek-flash` (V4.1-Flash-1017) and `claude-sonnet-5-5` | W2.1 | 2026-11-24 |
