# EFFACE — Plan to publish

Plan for turning the current draft into a preprint that would clear the empirical-track review of 2026-11-21, then posting it on arXiv. Every actionable item is a checkbox.

**Target:** arXiv preprint whose claims, estimand, and artifact would survive that review. Venue conversion stays a follow-on (D1).
**Window:** five weeks, full-time, starting 2026-11-17. The accept-bar work below is inserted at the start of Week 2, before any attack is scored.
**Hardware:** this Mac (Apple Silicon, MPS).
**API budget:** more than $500 for hosted attackers.
**Scheme:** MarkLLM SynthID reimplementation.
**Human ratings:** dropped.
**Accept bar:** §3a. A posted PDF with empty result cells, or with claims ahead of the code, fails that bar.

---

## 1. Starting point

As of 2026-11-21, after Week 1 and the three-pass search write-up:

- The paper, preregistration, package skeleton, configs, statistics, strategy parser, and tests exist. Tactic modules, the MarkLLM generation and detection adapters, chain execution, and the three-pass search do not. `efface/attacks/` is the `Attack` protocol. `efface/chains/` is empty. `efface/search/` parses strategies.
- Result tables, the frontier figure, the findings paragraph, and the affiliation are still `\ph{}` placeholders. The conclusion already speaks of a measured frontier.
- `configs/search.yaml` records beam width, depth, floor, tolerance, split, and α. The headroom margin, the order screen of 57 pairs, and pass 3 live in the paper and in `PREREGISTRATION.md`.
- The preregistration was frozen on 2026-11-17 and revised on 2026-11-21. `PREREGISTRATION.sha256` matches the revised file.
- Appendix D marks downloadable data, pinned models, and the result-to-command table as done. Those items are still ahead of the tree.
- A full read of the draft against the code, on an empirical-track bar, is a reject until §3a holds. The protocol is the part worth publishing.
- Only `tectonic` is installed locally. `make tectonic` is the working build path. `paper/main.pdf` is gitignored.

## 2. Decisions locked

| ID | Decision | Consequence |
| --- | --- | --- |
| D1 | Publish on arXiv first, then submit to a venue | Plan stops at a posted preprint; venue conversion is a follow-on |
| D2 | Use the MarkLLM SynthID reimplementation | Title, abstract, §6, §9, README, and citations must stop claiming the Google reference implementation |
| D3 | Drop human ratings | Edits across abstract, §2, §7, §9, Appendix A, README |
| D4 | Full design as the target, with a tier ladder | Scope is fixed after the Week 1 throughput measurement |
| D5 | One Mac with MPS; more than $500 in API budget | Generation and metric scoring are the schedule risk, not the API spend |

## 3. Findings that force paper changes

These are contradictions or false claims in the current draft. Each becomes a task below.

| # | Finding | Where |
| --- | --- | --- |
| F1 | Table 1 says G1 runs the "SynthID-Text reference implementation", but §6 says detection uses "the SynthID scheme implementation in MarkLLM". MarkLLM's SynthID is a research reimplementation with different keying, and Google retired text-watermark detection on its API in August 2026 | `paper/sections/06-experimental-setup.tex` Table 1 vs Oracle paragraph; `README.md` lines 199-206, 380 |
| F2 | The G2 hosted row cannot carry a SynthID scheme: hosted models expose no logits, and the vendor detector no longer exists | `paper/sections/06-experimental-setup.tex`; `README.md` experiment table |
| F3 | The paper promises human ratings that will not exist | abstract; §2; §7 "Human ratings"; §9; Appendix A; README metrics and scope |
| F4 | The 12-tactic catalogue has no implementation; the reusable harness in `watermarks-remover` provides 7 tactics (`paraphrase`, `backtranslate`, `structural`, `humanize`, `chunk`, `mlm`, `code`) | `paper/sections/04-attack-catalogue.tex`; `README.md` catalogue |
| F5 | Four preservation metrics in the paper (BERTScore, COMET, BLEURT, MAUVE) are absent from the reusable harness, which has embedding similarity, lexical divergence, length drift, number/URL survival, and a human-likeness score | §7; `README.md` metrics |
| F6 | `Masked-LM infilling` is attributed to `sand` (Zhang et al., the impossibility paper) in both the paper and README; the attribution needs checking | Table 1; README catalogue |
| F7 | The objective constrains every document (`\forall x`) and then says it is enforced in expectation with a tolerance | `paper/sections/03-problem.tex` |
| F8 | Table 1 marks residual TPR with a down arrow, while the caption explains that a higher TPR means the detector still finds the mark | `paper/sections/07-results.tex` |
| F9 | The checklist names evaluation code as `eval/`; the planned layout is `efface/evaluate/` | `paper/appendix/d-checklist.tex`; `README.md` |
| F10 | `paper/README.md` references a `figures/` directory that does not exist | `paper/README.md` |
| F11 | `CITATION.cff` has `affiliation: "TODO"` and an author affiliation placeholder remains in `main.tex` | `CITATION.cff`; `paper/main.tex` |
| F12 | `make` cannot run on this machine; only `make tectonic` works | `paper/Makefile` |
| F13 | "Cross-lingual generation" is never defined operationally | §3, §4, Appendix A |
| F14 | The title says "Optimal", but the method is a pruned beam search over a subset of 1,884 chains | title; `README.md` subtitle already says "most effective" |
| F15 | Removal is "every key fails" in Eq. 2, `removed_from_pvalues`, and the preregistration, and "the generating key" in §6. The power calculation counts 480 held-out documents as independent | `03-problem.tex`; `06-experimental-setup.tex`; `efface/evaluate/stats.py`; `PREREGISTRATION.md` |
| F16 | The objective constrains a per-document score, and the composite averages in MAUVE, which is a divergence between two sets. BLEURT joins only at Tier B, so τ = 0.80 is a different constraint per tier | `03-problem.tex`; `07-results.tex`; `docs/decisions.md` D6 |
| F17 | The catalogue's Source column names DIPPER, the self-information rewrite attack, Three Bricks, and He et al. The planned runner is a DeepSeek Flash prompt, or local `roberta-large` for infilling | `04-attack-catalogue.tex`; `02-related-work.tex` |
| F18 | The additive screen \(S(p)+S(t)-1\) skips the interactions the chain study exists to measure. Instruction and discourse paraphrase enter depth 2 only through a beam of width 8 | `05-combination-search.tex` |
| F19 | The 1% FPR threshold is the empirical quantile of 100 negatives. D10's parametric null is the operating point that can be estimated stably | `06-experimental-setup.tex`; `docs/decisions.md` D10 |
| F20 | No unattacked detection rate is required before an attack table. On 1.3B and 1.5B models at 150–400 tokens, a high removal rate can be a weak mark | `06-experimental-setup.tex`; `09-limitations-ethics.tex` |
| F21 | Related work misses the closest 2025–2026 neighbours: SynGuard's SynthID-Text attack suite (arXiv:2508.20228), Diaa et al. adaptive paraphrasers (ICML 2025, arXiv:2410.02440), and cross-lingual summarization removal (arXiv:2510.24789) | `02-related-work.tex` |
| F22 | `PREREGISTRATION.sha256` was recomputed after the 2026-11-21 deviation, so the hash attests to the revised protocol | `PREREGISTRATION.sha256` |

## 3a. Accept bar from the 2026-11-21 review

The preprint is acceptable when every row below is true of the posted PDF and the tagged tree. Until then the manuscript stays a protocol, and the abstract, conclusion, and checklist say so.

| ID | Condition | Where it is locked |
| --- | --- | --- |
| B1 | One removal unit. A document is generated under one key and scored under that key. Three keys are three documents that share a prompt. Stochastic repetitions are averaged. Intervals and the paired bootstrap cluster by prompt. Power is stated at the number of prompts. | R1, before any attack score |
| B2 | One document-level composite selects the chain: the unweighted mean of BERTScore-F1 and clipped COMET. MAUVE, BLEURT, and length ratio are reported on the same split and do not enter τ. Tier A and Tier B never select under different composites. | R2, before metrics are coded |
| B3 | Every sentence in the abstract, findings paragraph, conclusion, and checklist is true of a table, a figure, or a path that exists. Placeholders are gone because the cells were filled, or because the sentence was deleted. | Week 4 claims audit |
| B4 | Each catalogue row names the system that runs. Published relatives are labelled as relatives. The paper lists the attacks the search leaves out. | R5, Week 2 |
| B5 | The three passes run from `configs/search.yaml`. The search log lists every evaluated chain and every skipped extension. A sampled false-skip rate and a sampled off-beam gap are in the paper. | W2.9, W3.11, W3.12 |
| B6 | Unattacked detection at α = 0.05 is reported before any attack table. The preregistered floor on that rate is met, or the sweep stops and the paper draws no robustness conclusion. Both operating points use D10's normal null. | G2b, before W3.2 |
| B7 | Section 2 cites SynGuard, Diaa et al., and the cross-lingual summarization attack, and states the remaining gap: non-adaptive ordered chains under a frozen document-level floor, on this reimplementation. | W2.14 |
| B8 | The 2026-11-17 preregistration bytes keep their own digest. Later deviations append to the log and do not replace that digest. | W2.0 |

Recommended locks, to be written into `docs/decisions.md` and `PREREGISTRATION.md` as dated deviations before the first scored attack. No removal result exists yet, so these are still pre-result changes.

| ID | Lock |
| --- | --- |
| R1 | Primary bit: \(p_{k^\star}(x) > 0.05\), where \(k^\star\) is the key used to generate \(x\). Prompt-level "all three keys miss" may be a secondary table. It is not the headline N. |
| R2 | Selecting score \(S\) = mean of BERTScore-F1 and COMET clipped to \([0,1]\). Amend D6. Report the fraction of documents with \(S < \tau\). |
| R3 | Unattacked true-positive rate at α = 0.05, on documents of at least 150 tokens, at least 200 per generator, must have a Wilson lower bound of at least 0.70. A miss stops the attack sweep. Write the bound into the preregistration before measuring it. |
| R4 | False-skip audit: run 30 extensions the headroom rule refused, or 10% of refusals, whichever is smaller. Report how often the measured chain was admissible. Off-beam audit: run 20 admissible depth-1 tactics' best unseen pairs. Report the removal gap to the selected pair. |
| R5 | Rename the catalogue column to "Closest published relative". State the operational difference in §4. Add an "attacks this search does not run" paragraph: adaptive paraphrasers, cross-lingual summarization, copy-paste mixing. |
| R6 | Corpus operating point uses the parametric null from D10 at both the per-document test and TPR at 1% FPR. The empirical quantile of the calibration set is a diagnostic. Grow that set if the null is over-dispersed; 100 negatives do not set the threshold. |

## 4. Scope ladder and gates

The full design is the target. Scope drops in the order listed if a gate fails.

| Tier | Generator rows | Domains | Prompts per domain | Search | Selecting \(S\) | Reported beside \(S\) |
| --- | --- | --- | --- | --- | --- | --- |
| A (must ship) | 1 | News, long-form QA | 60 | Singles, depth 2, beam 8 | BERTScore, COMET | MAUVE, length ratio, achieved edit rate |
| B (target) | 2 | All four | 100 | Singles, depth 3, three-pass search | Same \(S\) as Tier A | Add BLEURT. BLEURT does not move the recommendation |
| C (stretch) | 2 | All four | 150 | Depth 3, beam 16 | Same \(S\) | Same columns, tighter audits |

**G1, end of Week 1:** passed on 2026-11-17. Generation is 12–22 seconds per 400-token document on MPS, detection is 0.02–0.04 seconds, and peak memory is 3.4 GB. Tier B is feasible. Details in `docs/perf.md`.

**G2, end of Week 2:** pilot run on 20 documents and 3 tactics. If per-chain cost exceeds the budget model by more than 2×, cut beam width and prompts before the main sweep. R1–R6 are already written into the preregistration. A pilot that scored attacks under the old all-keys bit or under a MAUVE composite is discarded and rerun.

**G2b, before any attack table:** unattacked detection meets R3 on each generator row that will appear in §7. A miss stops W3.2. The paper then reports the detection curve and draws no robustness conclusion from removal rates.

**G3, end of Week 3:** singles and depth-2 results exist, the control row matches the unattacked detection rate within the minimum detectable difference, and the false-skip sample has been scored. If depth 3 has no survivor, the preprint reports singles and pairs and says so in the abstract.

## 5. Phase plan

### Week 1 — decisions, skeleton, measurement (2026-11-17 to 11-23)

- [x] **W1.1** Write `docs/decisions.md`: scheme framing, G2 replacement, dropped tactics, metric set, tier choice. Done when: one page, linked from README.
- [x] **W1.2** Resolve F1/F2: rename G1 to "opt-1.3b with the MarkLLM SynthID reimplementation"; replace G2 with a second open-weight model or delete the row. Done when: tables in `06-experimental-setup.tex` and README agree.
- [x] **W1.3** Write `PREREGISTRATION.md`: τ, beam width, split seed, minimum detectable difference, prompt counts, metric definitions, decision rule. Done when: committed before any result exists, with a timestamp.
- [x] **W1.4** Create the package skeleton: `pyproject.toml`, `efface/{watermark,attacks,chains,detect,evaluate,search}`, `configs/`, `scripts/`, `tests/`. Done when: `pip install -e ".[dev]"` succeeds.
- [x] **W1.5** Port reusable code from `watermarks-remover` (MIT) with attribution: strategy parser, holdout split, AUROC, Pareto, cost accounting, report renderer. Done when: code runs under the new package name; NOTICE added.
- [x] **W1.6** MPS spike: load opt-1.3b through MarkLLM, generate and detect one 300-token document under one key, record wall clock and peak memory. Done when: timing table in `docs/perf.md`; G1 decided.
- [x] **W1.7** Cost model: tokens per attack call, calls per chain, metric cost, API price, total estimate. Done when: `docs/budget.md` with a pessimistic case.
- [x] **W1.8** Paper edits for D2 and D3: remove human ratings, correct the detector claims, retitle. Done when: draft compiles; `grep -rn 'human rating'` returns nothing.
- [x] **W1.9** Build check: `make tectonic` from a clean copy of `paper/`. Done when: PDF builds with no missing references.

**Gate G1: pass. Decision recorded in `docs/decisions.md`.**

### Week 2 — estimand, harness, tactics, pilot (11-24 to 11-30)

W2.0 blocks W2.1. Attack scores computed before R1–R6 are in the preregistration are discarded.

- [x] **W2.0** Lock the accept bar. Done 2026-11-21, before any attack result exists:
  - [x] Frozen 2026-11-17 bytes pinned at `818ccf9`, blob `d33c2f1`, digest `c4b6c253…`. New deviations append to §9.
  - [x] R1–R6 written into `PREREGISTRATION.md` (§§3–7, §6a, §9) and `docs/decisions.md` (D6, D7, D10, D12).
  - [x] Eq. 2 is the generating-key bit. `is_removed` replaces `removed_from_pvalues`. `clustered_rate`, `tpr_at_fpr_parametric`, and `detection_check_pass` implement the unit, the null, and the gate. §6 power is stated in prompts.
  - [x] `S` is BERTScore + COMET in §7 and D6. BLEURT, MAUVE, and length ratio are reported columns. The COMET call is stated.
  - [x] Headroom margin, 57-pair screen, pass 3, and the R3 bound are in `configs/search.yaml`.
  - [x] Conclusion, checklist, README, and the abstract describe the protocol. Tests 50 passed, smoke 9 checks, lint clean, `tectonic` builds.
- [x] **W2.1** Generation adapter: one document per prompt per key, fixed seeds, revision pinned. Done 2026-11-21: `python -m efface.cli generate` wrote three records for one prompt, each carrying its key id, the MarkLLM commit, and the key derivation. A derived key scored 0.5559 against the 0.52 threshold. Per-document key arrays are D13.
- [x] **W2.2** Detector adapter: per-key p-value, score, batch mode, MarkLLM commit recorded. Done 2026-11-21: `efface score` writes score, `n_eff`, p-value, the null used, and the `removed` flag. The stored fixture reproduces its p-value for the fitted G1 null. Calibration found the analytic null mis-centred (G1 mean 0.4978, scale 0.0871 against 0.5 and 0.25), so D10 now fits the null from unwatermarked documents. `docs/detector-calibration.md`.
- [x] **W2.3** Attack interface: `apply(text, intensity, seed) -> text`, one module per tactic. Done 2026-11-21: `Attack` protocol and registry; all 13 tactics registered; `factory.build` injects the chat model or filler; an unknown name raises `KeyError` and the CLI exits 2.
- [x] **W2.4** Implement the 12 tactics, reusing the rewrite, humanize, and MLM passes. Done 2026-11-21: model-backed tactics in `attacks/model.py`, rules in `attacks/local.py`, infilling in `attacks/mlm.py`; each has a test, and `docs/attack-catalogue.md` records the operational difference from its closest relative.
- [x] **W2.5** Build the five missing tactics: synonym substitution, random edits, typo/noise, regeneration, cross-lingual generation. Done 2026-11-21: all five exist. The catalogue in code, README, and paper matches one-to-one, and the paper and README now say "closest relative". A real `typo_noise` pass changed all three documents end to end.
- [x] **W2.6** Chain executor with prefix caching. Done 2026-11-21: `ChainExecutor` resumes from the longest cached prefix; keys hash document id, seed, source digest, and prefix. A CLI run of a depth-2 chain then its depth-3 extension reported `resumed_at 2` on all three documents and wrote one new cache entry per document. Memory and disk caches, with tests for seed, source, and persistence.
- [x] **W2.7** Metrics under R2. Done 2026-11-21: `evaluate/preservation.py` makes BERTScore and COMET the only inputs to \(S\); `composite` raises on MAUVE or a missing metric, and a test pins that. Ten-pair fixture scored end to end (aggregate \(S\) = 0.905) with stored values in `tests/fixtures/metrics/expected.json` and a gated reproduction test. Four dependency defects fixed: `comet` vs `unbabel-comet`, the Hugging Face model id, a COMET/torch DataLoader conflict, and `pkg_resources`. `docs/metric-calibration.md`.
- [ ] **W2.8** Removal statistics under R1 and R6: Wilson interval clustered by prompt, TPR at 1% FPR from the parametric null, paired bootstrap clustered by prompt. Done when: tests against hand-computed values, including a prompt with three keys.
- [ ] **W2.9** Three-pass search as specified in §5 and `configs/search.yaml`: intensity map, diverse beam, headroom skip, 57-pair screen, shortlist intensity pass. Log every evaluated chain and every skipped extension with the rule that skipped it. Done when: the log is machine-readable and a fixture search matches a hand-computed beam.
- [ ] **W2.10** Prompt sets: source, licence, download manifest, checksums, fixed split. Done when: `data/manifest.json`; split hash in the preregistration.
- [ ] **W2.11** Pilot: 20 documents, 3 tactics, all metrics, end to end. Done when: `results/pilot/report.md`; G2 decided.
- [ ] **W2.12** Smoke run under two minutes. Done when: `make smoke` passes in CI.
- [ ] **W2.13** Unattacked detection curve per generator: at least 200 watermarked documents of at least 150 tokens, plus an unwatermarked calibration set large enough to check the normal null. Done when: TPR at α = 0.05, empirical FPR, and the Wilson lower bound are in `results/detection/`. G2b is decided from that file.
- [ ] **W2.14** Related work for B7. Cite SynGuard (arXiv:2508.20228), Diaa, Aremu, and Lukas (ICML 2025, arXiv:2410.02440), and cross-lingual summarization removal (arXiv:2510.24789). State the gap as non-adaptive ordered chains under a frozen document-level floor on this reimplementation. Add the "attacks this search does not run" paragraph (adaptive paraphrasers, cross-lingual summarization, copy-paste mixing). Done when: those three papers are in `refs.bib` and §2.
- [ ] **W2.15** Clear `provisional_until_w2_1` on the Qwen row once generation and detection succeed under the same config as G1. Done when: `configs/generators.yaml` has no provisional flag.

**Gate G2 decision recorded. Gate G2b recorded before Week 3 attack tables.**

### Week 3 — main runs (12-01 to 12-07)

- [ ] **W3.1** Generate the corpus: one document per prompt per key, both generator rows, discarded documents counted. Done when: corpus manifest with counts and hashes, and each record stores its generating key.
- [ ] **W3.2** Singles at operating intensity, plus the control row. Starts only after G2b passes. Done when: `tab:singles` data file exists, and the control removal rate is within 0.05 of one minus the unattacked detection rate.
- [ ] **W3.3** Intensity sweep at depth 1. Done when: intensity table exists.
- [ ] **W3.4** Depth-2 beam search on the search split. Done when: ranked chain list with search-split metrics.
- [ ] **W3.5** Depth-3 beam search on the search split. Done when: ranked chain list, with the marginal gain over each best prefix.
- [ ] **W3.6** Held-out evaluation of the top chains, both splits reported. Done when: held-out file separate from the search file.
- [ ] **W3.7** Per-domain and per-length-bucket results. Done when: data files for `tab:perdomain` and `tab:length`.
- [ ] **W3.8** τ sensitivity at τ ± 0.05. Done when: data file for `tab:tau`.
- [ ] **W3.9** Cost and runtime log: wall clock, API spend, GPU hours. Done when: `results/runlog.json`.
- [ ] **W3.10** Second-attacker ablation: re-run the top five chains, the best single tactic, and the control with Claude Sonnet on the held-out split; report rank correlation and the maximum removal delta. Done when: `tab:ablation` data file exists.
- [ ] **W3.11** False-skip audit (R4) on the headroom rule. Done when: the paper reports the sample size, the predicted \(S\), the measured \(S\), and the fraction that were admissible.
- [ ] **W3.12** Off-beam audit (R4). Done when: the paper reports the removal gap between the selected pair and the best sampled pair the beam did not extend.

**Gate G3 decision recorded.**

### Week 4 — analysis, figures, writing (12-08 to 12-14)

- [ ] **W4.1** Generate all LaTeX tables from result files; no manual transcription. Done when: `make tables` rewrites the `.tex` fragments.
- [ ] **W4.2** Pareto frontier figure as vector PDF, colourblind-safe, floor drawn. Done when: `paper/figures/frontier.pdf` exists.
- [ ] **W4.3** Fill every `\ph{}` placeholder from a result file, or delete the sentence. `grep -rn '\\ph{' paper` is empty. Done when: zero placeholders, and no empty cell was replaced with a qualitative claim.
- [ ] **W4.4** Rewrite abstract, introduction findings, discussion, and conclusion from the held-out tables. The conclusion describes a frontier only after `fig:pareto` exists. Quantitative agreement with DIPPER, He et al., or MarkMyWords is stated only where scheme, length, detector, and attacker match; otherwise the sentence stays directional. Done when: numbers match the tables exactly.
- [ ] **W4.5** Order-effect analysis: same pair in both orders. Done when: one table or paragraph with the measured asymmetry.
- [ ] **W4.6** Selection-bias and multiplicity treatment: paired bootstrap, Holm or BH, holdout emphasis. Done when: statement in §7 and §5.
- [ ] **W4.7** Failure cases: documents that passed the floor but changed a fact, number, or attribution. Done when: Appendix C list with examples.
- [ ] **W4.8** Limitations updated for the reimplementation detector and the dropped human study. Done when: §9 reads consistently.
- [ ] **W4.9** Claims audit: every sentence in the abstract, introduction, conclusion, and checklist traced to a table, a figure, or a path in the tagged tree. Done when: `docs/claims.md` lists each sentence and its source. A sentence with no source is deleted.
- [ ] **W4.10** External-validity paragraph in §9: generators are 1.3B and 1.5B, 400 tokens, MarkLLM keying. The unattacked detection curve is the precondition for reading removal rates. Done when: §9 states the measured unattacked TPR next to that limit.

### Week 5 — integrity, artifact, submission (12-15 to 12-21)

- [ ] **W5.1** Verify every bibliography entry against Crossref, DBLP, or arXiv; add missing venues and fix author lists. Done when: `refs.bib` matches the record; verification log kept.
- [ ] **W5.2** Re-read §2 against the held-out ranking. The novelty sentence stays inside B7. Done when: the paragraph cites SynGuard, Diaa et al., and the cross-lingual summarization attack, and it describes what this search adds.
- [ ] **W5.3** Fix F6 (masked-LM attribution) and every other defect in §8. Done when: defect table closed.
- [ ] **W5.4** Consistency pass: British spelling, terminology, table and figure references, numbers repeated in text. Done when: read-through notes closed.
- [ ] **W5.5** Plagiarism and self-similarity check on the full text. Done when: report kept outside the repo.
- [ ] **W5.6** Artifact release: tagged `v1.0.0`, Zenodo DOI, archive of configs and result JSON, reproduction commands. Done when: DOI resolves; README command table runnable.
- [ ] **W5.7** README rewrite: real numbers, real runtimes, status badges, citation block with the arXiv ID. Done when: README has no `TODO`.
- [ ] **W5.8** Responsible disclosure: notify MarkLLM maintainers and the relevant SynthID team at least ten days before posting. Done when: disclosure log in `docs/`.
- [ ] **W5.9** arXiv source flattening, clean build with `tectonic`, metadata, categories, licence, comments. Done when: tarball builds in an empty directory.
- [ ] **W5.10** Submit to arXiv; monitor moderation; fix any build rejection. Done when: preprint announced.

## 6. Paper rebuild checklist

- [ ] **`main.tex`** — Real affiliation; final title; remove draft date; ORCID if available.
- [ ] **`00-abstract.tex`** — Remove human ratings; fill document and chain counts; state the detector precisely; headline finding.
- [ ] **`01-introduction.tex`** — Remove "alongside human ratings"; fill the three counts; write the findings paragraph; qualify the contribution as "a beam search over a bounded space".
- [ ] **`02-related-work.tex`** — Remove the human-rating sentence; add 2025–2026 removal work; state the novelty narrowly.
- [ ] **`03-problem.tex`** — Mean constraint plus a reported per-document violation rate. Primary removal bit is the generating key (R1). TPR@1%FPR uses the parametric null (R6). Prompt clustering is stated next to the interval.
- [ ] **`04-attack-catalogue.tex`** — One row per implemented module. Column name "Closest published relative". Operational difference for DIPPER, the self-information infill policy, Three Bricks, and He et al. Intensity units, plus a pointer to the achieved-edit-rate column. Cross-lingual generation matches D5.
- [ ] **`05-combination-search.tex`** — Beam width, prefix caching, pruning margins, chains evaluated, chains skipped, false-skip rate, off-beam gap. The additive screen is described as a budget rule whose error is measured.
- [ ] **`06-experimental-setup.tex`** — G1 = opt-1.3b with MarkLLM SynthID; G2 replaced or removed; five attacker models; four data rows; decoding settings; minimum length; repetitions; hardware, wall clock, and cost shares.
- [ ] **`07-results.tex`** — Fill singles, pairs, triples, per-domain, and the frontier from generated tables. State which \(S\) selected the chain. Report MAUVE, BLEURT, length ratio, and achieved edit rate beside \(S\). Include the unattacked detection rate in the singles table or directly above it.
- [ ] **`08-discussion.tex`** — Fill composition value, order effects, literature comparison, turning point; remove the human check.
- [ ] **`09-limitations-ethics.tex`** — Remove the human sample; add the reimplementation caveat; fill length and model-drift fields; keep the disclosure promise.
- [ ] **`10-conclusion.tex`** — Describe a frontier only after the figure exists. Match the held-out recommendation and its cost in \(S\).
- [ ] **`appendix/a-prompts.tex`** — Delete the rating protocol; keep the attack prompts; add the regeneration prompt.
- [ ] **`appendix/b-hyperparameters.tex`** — Fill all 13 rows, search settings, detector settings.
- [ ] **`appendix/c-per-domain.tex`** — Fill length buckets, τ sensitivity, failure cases.
- [ ] **`appendix/d-checklist.tex`** — Fix the `eval/` path; make every "yes" true or change it; fill data link, runtime, infrastructure.
- [ ] **`paper/README.md`** — Remove the missing `figures/` reference; document `make tectonic` as the default.
- [ ] **`README.md`** — Rewrite status, setup, catalogue, experiment tables, results, reproduction table, checklist, citations.
- [ ] **`CITATION.cff`** — Affiliation, arXiv ID, DOI, version 1.0.0, release date.

## 7. Placeholder inventory

| File | Count | What it needs |
| --- | --- | --- |
| `sections/07-results.tex` | 30 | τ value and justification, 13 × 5 single-tactic cells, 2 × 5 chain rows, figure, 4 × 2 per-domain cells |
| `sections/06-experimental-setup.tex` | 15 | 2 generator rows, 5 attacker models, 4 data rows, decoding settings, minimum length, repetitions, hardware, wall clock, 2 cost shares |
| `appendix/b-hyperparameters.tex` | 14 | 13 tactic defaults and swept values, plus search settings |
| `appendix/c-per-domain.tex` | 7 | 3 length buckets, 3 τ rows, failure-case list |
| `sections/08-discussion.tex` | 4 | Composition value, order asymmetry, literature comparison, turning point |
| `appendix/d-checklist.tex` | 4 | Data link, runtime, infrastructure, code path |
| `sections/05-combination-search.tex` | 3 | Document count, intensity count, top-chain count |
| `sections/09-limitations-ethics.tex` | 2 | Length bucket, hosted model and month |
| `sections/01-introduction.tex` | 2 | Document and chain counts |
| `sections/00-abstract.tex` | 1 | Headline finding, plus two counts |
| `appendix/a-prompts.tex` | 1 | Raters (deleted with D3) |
| `main.tex` | 1 | Affiliation |

## 8. Known defects to close

- [x] **F1** — Make G1 say "MarkLLM SynthID reimplementation"; remove every claim about the Google reference implementation; add a §9 caveat.
- [x] **F2** — Replace G2 with a second open-weight model under the same scheme, or delete the row and adjust the count claims.
- [x] **F3** — Remove human ratings from abstract, §2, §7, §9, Appendix A, README.
- [ ] **F4** — Align the catalogue table with implemented modules. Label published systems as relatives (F17, R5).
- [ ] **F5** — BERTScore and COMET form \(S\). BLEURT, MAUVE, and length ratio are reported and stay out of τ (F16, R2).
- [x] **F6** — Verify the masked-LM infilling source; cite the introducing paper or the one that evaluated it.
- [x] **F7** — Formalise the constraint as an expectation with a reported violation rate.
- [x] **F8** — Rename the column "Residual TPR@1%FPR" and keep the down arrow.
- [x] **F9** — Name the evaluation package consistently (`efface/evaluate/`).
- [x] **F10** — Create `paper/figures/` with the generated PDF, or remove the reference.
- [ ] **F11** — Fill affiliation in `main.tex` and `CITATION.cff`.
- [x] **F12** — Add a `clean` target that does not need `latexmk`, and make `tectonic` the default.
- [x] **F13** — Define cross-lingual generation operationally or drop it.
- [x] **F14** — Retitle: "Most Effective" or "Best" instead of "Optimal"; say beam search in the abstract.
- [x] **F15** — One removal unit: generating key, prompt-clustered intervals, power at the number of prompts (R1).
- [x] **F16** — Document-level \(S\) without MAUVE. One composite for search and for the held-out recommendation (R2).
- [ ] **F17** — Catalogue column and §4 name the system that runs.
- [ ] **F18** — False-skip rate and off-beam gap reported (R4).
- [ ] **F19** — Both operating points use the parametric null. Empirical quantile is a diagnostic (R6).
- [ ] **F20** — G2b passed, and the unattacked TPR is printed next to the attack tables.
- [ ] **F21** — §2 cites SynGuard, Diaa et al., and cross-lingual summarization removal, and states the remaining gap (B7).
- [ ] **F22** — 2026-11-17 preregistration digest preserved. The 2026-11-21 and R1–R6 deviations are log entries.

## 9. Artifact and code release

- [ ] **A1** — `pyproject.toml` with pinned dependencies and an optional `metrics` extra. Done when: fresh install works on macOS and Linux.
- [ ] **A2** — `configs/` for generators, attackers, tactics, search, metrics. Done when: every run reads a config; no magic constants.
- [ ] **A3** — CLI: `generate`, `attack`, `score`, `run`, `search`, `report`, `smoke`. Done when: each README command runs.
- [ ] **A4** — Tests: unit for tactics, statistics, cache; one integration test on a small fixture. Done when: CI green.
- [ ] **A5** — CI: ruff, pytest, `make pdf`, placeholder check. Done when: pull request check runs.
- [ ] **A6** — Run manifest: git SHA, MarkLLM SHA, HF revisions, API model IDs and dates, seeds, timings, cost. Done when: every result file carries its manifest.
- [ ] **A7** — Results archive: JSON plus generated tables, under a versioned DOI. Done when: Zenodo record resolves.
- [ ] **A8** — Reproduction doc: one command per table and figure, with measured runtime. Done when: README table complete.
- [ ] **A9** — Dependency licences and third-party notices: MarkLLM (Apache-2.0), Hugging Face models, `watermarks-remover` (MIT). Done when: `NOTICE` file present.
- [ ] **A10** — Docker image or lockfile for the metric stack. Done when: optional, only if time allows.
- [ ] **A11** — One test binds Eq. 2, `removed_from_pvalues`, \(S\), and the preregistration constants (τ, ε, α, beam, split seed, R3 bound). Done when: editing any one of them without the others fails CI.

## 10. arXiv submission checklist

- [ ] Flatten `paper/` into a tarball with `main.tex`, `sections/`, `appendix/`, `refs.bib`, and `figures/`; leave out the PDF and build artefacts.
- [ ] Compile in an empty directory with `tectonic -X compile main.tex`; confirm the `.bbl` is generated and all references resolve.
- [ ] Confirm the PDF has no red `[TODO: …]` text.
- [ ] Choose categories: `cs.CL` primary, `cs.CR` cross-list.
- [ ] Metadata: final title, author, affiliation, abstract, comments ("17 pages, X figures, code at …"), licence CC BY 4.0 for the paper.
- [ ] Confirm arXiv endorsement is in place for a first submission in `cs.CL`; allow several days for moderation.
- [ ] Verify fonts are embedded, hyperlinks work, and the page count matches the claims in the text.
- [ ] After announcement: add the arXiv ID to `CITATION.cff` and README, tag the repository, update the badge.

## 11. Responsible use and compliance

- [ ] Check the terms of service of every hosted attacker model: some forbid producing content intended to evade provenance systems. Record the decision and the provider terms in `docs/ethics.md`.
- [ ] Notify MarkLLM maintainers and the SynthID team before posting; keep a dated log.
- [ ] Release attack code with a defensive framing and a documented intended use, consistent with §9 of the paper.
- [ ] No human subjects remain after D3, so no ethics approval is needed; state that the ratings were dropped and why.
- [ ] Keep prompts and generated documents to public benchmarks and self-authored prompts; record licences in `data/manifest.json`.

## 12. Budget and time

| Item | Estimate | Basis |
| --- | --- | --- |
| Generation, Tier B | 15–25 h wall clock | 2 models × 4 domains × 100 prompts × 3 keys at 20–40 s per document on MPS |
| Detection, search | 10–20 h | ~290 chains × 720 documents at 0.1–0.3 s per pass |
| Attack API | $150–$500 | ~200k calls at 300–600 tokens with a cheap model; prefix caching keeps this down |
| Metric scoring | 8–15 h | 200k pairs; BERTScore and COMET dominate |
| Engineering | 65–75 h | Port, five new tactics, document-level metrics, three-pass search, prompt-clustered statistics, tests |
| Detection gate and search audits | 8–12 h | 200+ unattacked documents per row, 30 false-skip extensions, 20 off-beam pairs |
| Writing and checks | 30–35 h | Placeholders, claims audit, references, artifact, arXiv |

Contingency: if G1 or G2 fails, cut prompts to 60 per domain and drop BLEURT and the second generator. That saves roughly 40% of the run time.

## 13. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| MarkLLM does not run on MPS | Generation becomes CPU-bound and infeasible | Test in Week 1; fall back to a rented GPU or Tier A with fewer prompts |
| Reimplementation keying differs from production | Results do not transfer to deployed SynthID | State it in the title, abstract, and §9; never claim production behaviour |
| Hosted attacker models change | Results not reproducible | Pin model IDs, record dates, prefer open-weight attackers where possible |
| API spend overrun | Runs stop mid-search | Per-run token cap, cache, dry-run estimate, stop rule |
| Selection bias from searching 1,884 chains | Inflated headline | Preregistered split, held-out report, paired bootstrap, multiplicity correction |
| Length gaming of semantic metrics | Preservation overstated | Length ratio, per-metric reporting, failure cases |
| Prompt licensing | Cannot release data | Use public benchmark prompts; record licence per source |
| arXiv moderation delay | Missed target date | Submit with a week of buffer; have the PDF and source ready earlier |
| Scope creep from the full design | Nothing ships | Tier ladder and gates G1–G3 |
| Attack scores land before R1–R6 | Headline uses the estimand the review rejected | W2.0 blocks W2.1. Scores from the old bit or the old composite are discarded |
| Unattacked detection is weak on these models | Removal rates do not support a robustness claim | G2b. The paper reports the curve and stops the sweep |
| Headroom rule hides the best chain | The reported frontier is an artifact of the predictor | R4 false-skip and off-beam samples are in §5 and §7 |
| Claims written ahead of result files | Abstract and checklist fail the accept bar | W4.9. Protocol wording stays until the files exist |

## 14. Definition of done

The preprint clears the 2026-11-21 bar when all of these hold:

- [ ] B1–B8 in §3a are true of the PDF and the tagged tree.
- [ ] `grep -rn '\\ph{' paper` returns nothing.
- [ ] The paper builds from a clean tarball with `tectonic`.
- [ ] Every number in the paper is reproducible from a command in the README, and every table and figure is generated from a result file.
- [ ] The abstract names the detector as a MarkLLM reimplementation and limits every removal claim to that detector at the recorded commit.
- [ ] The catalogue table and the code agree one-to-one, and each row's published relative is named as a relative.
- [ ] The 2026-11-17 preregistration digest is unchanged. R1–R6 and the three-pass deviation are dated log entries written before the result files.
- [ ] G2b passed, and the unattacked detection rate is printed with the attack tables.
- [ ] The false-skip rate and the off-beam gap are in the paper.
- [ ] The results archive, code, configs, seeds, and run manifests are public under a DOI.
- [ ] An independent reader has checked `docs/claims.md` against the tables.
- [ ] The disclosure log exists and the ten-day notice has elapsed.
- [ ] The arXiv metadata, licence, and categories are set.

## 15. Decisions still open

Resolved since this list was written: G2 is `Qwen/Qwen2.5-1.5B-Instruct` (D4). The title says "Most Effective" (F14). Cross-lingual generation is the three-step pivot rewrite (D5). Full code ships with the responsible-use notice (D9). Prompt sources are D8.

| ID | Question | Recommended default |
| --- | --- | --- |
| O4 | Where does BLEURT sit if Tier B is funded? | Reported column. It stays out of \(S\) so a tier change cannot move the selected chain. Drop the column first if the Mac runs out of time |
| O7 | Is the R3 bound 0.70 on the Wilson lower bound the right stop rule? | Yes. Write it down before W2.13. A weaker mark means the paper reports detectability, not removal |
| O8 | Sample sizes for R4 if the API cap binds? | 30 false-skip extensions and 20 off-beam pairs, paid for before any depth-3 extension beyond the beam |
| O6 | Prompt counts if G2 cuts scope? | 60 per domain, two domains, Tier A. \(S\) stays the R2 composite |
