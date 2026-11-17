# EFFACE — Plan to publish

Plan for turning the current paper draft into a posted arXiv preprint. Every actionable item is a checkbox.

**Target:** arXiv preprint first, peer-reviewed venue later.
**Window:** five weeks, full-time, starting 2026-11-17.
**Hardware:** this Mac (Apple Silicon, MPS).
**API budget:** more than $500 for hosted attackers.
**Scheme:** MarkLLM SynthID reimplementation.
**Human ratings:** dropped.

---

## 1. Starting point

- The repository contains the paper only: `paper/` with 17 pages, about 6,500 words, and **83 `\ph{}` placeholders**.
- No package, `pyproject.toml`, `configs/`, `data/`, `scripts/`, `tests/`, `results/`, or `figures/` exists.
- One commit (`cc51532`), one uncommitted change (`.gitignore`).
- `refs.bib` has 18 entries; every entry is cited at least once.
- Only `tectonic` is installed locally. `latexmk`, `pdflatex`, and `bibtex` are absent, so `make` fails and `make tectonic` is the working build path.
- `paper/main.pdf` exists locally and is gitignored.

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

## 4. Scope ladder and gates

The full design is the target. Scope drops in the order listed if a gate fails.

| Tier | Generator rows | Domains | Prompts per domain | Search | Metrics |
| --- | --- | --- | --- | --- | --- |
| A (must ship) | 1 | News, long-form QA | 60 | Singles, depth 2, beam 8 | BERTScore, COMET, MAUVE, length ratio |
| B (target) | 2 | All four | 100 | Singles, depth 3, beam 8 | Add BLEURT |
| C (stretch) | 2 | All four | 150 | Depth 3, beam 16, intensity sweep at depth 1 | Full set plus per-key sensitivity |

**G1, end of Week 1:** passed on 2026-11-17. Generation is 12–22 seconds per 400-token document on MPS, detection is 0.02–0.04 seconds, and peak memory is 3.4 GB. Tier B is feasible. Details in `docs/perf.md`.

**G2, end of Week 2:** pilot run on 20 documents and 3 tactics. If per-chain cost exceeds the budget model by more than 2×, cut beam width and prompts before the main sweep.

**G3, end of Week 3:** singles and depth-2 results exist and the control row behaves. If not, ship a preprint that reports single tactics and pairs only, with the claims narrowed.

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

### Week 2 — harness, tactics, pilot (11-24 to 11-30)

- [ ] **W2.1** Generation adapter: prompt to watermarked document, 3 keys, fixed seeds, revision pinned. Done when: `python -m efface.cli generate` writes a JSON record.
- [ ] **W2.2** Detector adapter: per-key p-value, score, batch mode, MarkLLM commit recorded. Done when: unit test on a fixture reproduces a stored p-value.
- [ ] **W2.3** Attack interface: `apply(text, intensity, seed) -> text`, one module per tactic. Done when: all tactics share the interface; unknown tactic fails loudly.
- [ ] **W2.4** Implement the 12 tactics, reusing `paraphrase`, `backtranslate`, `structural`, `humanize`, `chunk`, `mlm`. Done when: each tactic has a test and a recorded example.
- [ ] **W2.5** Build the five missing tactics: synonym substitution, random edits, typo/noise, regeneration, cross-lingual generation (or drop it with a written reason). Done when: catalogue table matches the code one-to-one.
- [ ] **W2.6** Chain executor with prefix caching: reuse the output of every evaluated prefix; cache key includes seeds. Done when: depth-3 extension does not recompute depth-2 work.
- [ ] **W2.7** Metrics: BERTScore, COMET, BLEURT, MAUVE adapters; normalisation to `[0,1]`; composite; length ratio. Done when: metric values reproduce on a 10-pair fixture.
- [ ] **W2.8** Removal statistics: Wilson interval, TPR at 1% FPR, paired bootstrap. Done when: tests against hand-computed values.
- [ ] **W2.9** Beam search: extend, prune, log every dropped chain with its reason. Done when: search log is machine-readable.
- [ ] **W2.10** Prompt sets: source, licence, download manifest, checksums, fixed split. Done when: `data/manifest.json`; split hash in the preregistration.
- [ ] **W2.11** Pilot: 20 documents, 3 tactics, all metrics, end to end. Done when: `results/pilot/report.md`; G2 decided.
- [ ] **W2.12** Smoke run under two minutes. Done when: `make smoke` passes in CI.

**Gate G2 decision recorded.**

### Week 3 — main runs (12-01 to 12-07)

- [ ] **W3.1** Generate the corpus: every prompt under 3 keys, both generator rows, discarded documents counted. Done when: corpus manifest with counts and hashes.
- [ ] **W3.2** Singles at default intensity, plus the control row. Done when: `tab:singles` data file exists.
- [ ] **W3.3** Intensity sweep at depth 1. Done when: intensity table exists.
- [ ] **W3.4** Depth-2 beam search on the search split. Done when: ranked chain list with search-split metrics.
- [ ] **W3.5** Depth-3 beam search on the search split. Done when: ranked chain list, with the marginal gain over each best prefix.
- [ ] **W3.6** Held-out evaluation of the top chains, both splits reported. Done when: held-out file separate from the search file.
- [ ] **W3.7** Per-domain and per-length-bucket results. Done when: data files for `tab:perdomain` and `tab:length`.
- [ ] **W3.8** τ sensitivity at τ ± 0.05. Done when: data file for `tab:tau`.
- [ ] **W3.9** Cost and runtime log: wall clock, API spend, GPU hours. Done when: `results/runlog.json`.
- [ ] **W3.10** Second-attacker ablation: re-run the top five chains, the best single tactic, and the control with Claude Sonnet on the held-out split; report rank correlation and the maximum removal delta. Done when: `tab:ablation` data file exists.

**Gate G3 decision recorded.**

### Week 4 — analysis, figures, writing (12-08 to 12-14)

- [ ] **W4.1** Generate all LaTeX tables from result files; no manual transcription. Done when: `make tables` rewrites the `.tex` fragments.
- [ ] **W4.2** Pareto frontier figure as vector PDF, colourblind-safe, floor drawn. Done when: `paper/figures/frontier.pdf` exists.
- [ ] **W4.3** Fill every `\ph{}` placeholder; `grep -rn '\\ph{' paper` is empty. Done when: zero placeholders.
- [ ] **W4.4** Rewrite abstract, introduction findings, discussion, conclusion with the measured numbers. Done when: numbers match the tables exactly.
- [ ] **W4.5** Order-effect analysis: same pair in both orders. Done when: one table or paragraph with the measured asymmetry.
- [ ] **W4.6** Selection-bias and multiplicity treatment: paired bootstrap, Holm or BH, holdout emphasis. Done when: statement in §7 and §5.
- [ ] **W4.7** Failure cases: documents that passed the floor but changed a fact, number, or attribution. Done when: Appendix C list with examples.
- [ ] **W4.8** Limitations updated for the reimplementation detector and the dropped human study. Done when: §9 reads consistently.
- [ ] **W4.9** Claims audit: every sentence in abstract and introduction traced to a table or figure. Done when: audit checklist in `docs/claims.md`.

### Week 5 — integrity, artifact, submission (12-15 to 12-21)

- [ ] **W5.1** Verify every bibliography entry against Crossref, DBLP, or arXiv; add missing venues and fix author lists. Done when: `refs.bib` matches the record; verification log kept.
- [ ] **W5.2** Update related work for 2025–2026 papers on watermark removal and chain search; re-check the "no prior chain search" claim. Done when: novelty paragraph cites the closest work.
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
- [ ] **`03-problem.tex`** — Replace `\forall x` with a mean constraint plus a reported violation rate; justify the all-keys removal rule; define TPR@1%FPR precisely.
- [ ] **`04-attack-catalogue.tex`** — One row per implemented tactic; fix the masked-LM source; define or drop cross-lingual generation; state intensity ranges.
- [ ] **`05-combination-search.tex`** — Replace "generation-free pass" with the real cost; state beam width, prefix caching, pruning margins, and the number of chains actually run.
- [ ] **`06-experimental-setup.tex`** — G1 = opt-1.3b with MarkLLM SynthID; G2 replaced or removed; five attacker models; four data rows; decoding settings; minimum length; repetitions; hardware, wall clock, and cost shares.
- [ ] **`07-results.tex`** — Delete the human-ratings paragraph; rename the residual TPR column; fill 13 singles; fill pairs, triples, per-domain; replace the figure placeholder; state τ and its sensitivity.
- [ ] **`08-discussion.tex`** — Fill composition value, order effects, literature comparison, turning point; remove the human check.
- [ ] **`09-limitations-ethics.tex`** — Remove the human sample; add the reimplementation caveat; fill length and model-drift fields; keep the disclosure promise.
- [ ] **`10-conclusion.tex`** — Match the narrower claims and the measured numbers.
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
- [ ] **F4** — Align the catalogue table with implemented modules; drop any tactic that cannot be implemented faithfully.
- [ ] **F5** — Add BERTScore, COMET, BLEURT (Tier B), MAUVE; state normalisation and the composite.
- [x] **F6** — Verify the masked-LM infilling source; cite the introducing paper or the one that evaluated it.
- [x] **F7** — Formalise the constraint as an expectation with a reported violation rate.
- [x] **F8** — Rename the column "Residual TPR@1%FPR" and keep the down arrow.
- [x] **F9** — Name the evaluation package consistently (`efface/evaluate/`).
- [x] **F10** — Create `paper/figures/` with the generated PDF, or remove the reference.
- [ ] **F11** — Fill affiliation in `main.tex` and `CITATION.cff`.
- [x] **F12** — Add a `clean` target that does not need `latexmk`, and make `tectonic` the default.
- [x] **F13** — Define cross-lingual generation operationally or drop it.
- [x] **F14** — Retitle: "Most Effective" or "Best" instead of "Optimal"; say beam search in the abstract.

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
| Engineering | 55–65 h | Port, five new tactics, four metrics, search, reports, tests |
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

## 14. Definition of done

The research is publishable when all of these hold:

- [ ] `grep -rn '\\ph{' paper` returns nothing.
- [ ] The paper builds from a clean tarball with `tectonic`.
- [ ] Every number in the paper is reproducible from a command in the README, and every table and figure is generated from a result file.
- [ ] The abstract names the detector as a MarkLLM reimplementation and makes no claim about production SynthID.
- [ ] The catalogue table and the code agree one-to-one.
- [ ] The preregistration is committed and dated before the results.
- [ ] The results archive, code, configs, seeds, and run manifests are public under a DOI.
- [ ] An independent reader has checked the claims against the tables.
- [ ] The disclosure log exists and the ten-day notice has elapsed.
- [ ] The arXiv metadata, licence, and categories are set.

## 15. Decisions still open

| ID | Question | Recommended default |
| --- | --- | --- |
| O1 | Replace G2 with a second open-weight model, or delete the row? | Second open-weight model from a different family, same MarkLLM scheme |
| O2 | Keep the word "Optimal" in the title? | No: "Most Effective" |
| O3 | Keep cross-lingual generation in the catalogue? | Only if it can be defined as an attack on an existing document; otherwise drop |
| O4 | Keep BLEURT, given the Mac's throughput? | Tier B only; drop first if a gate fails |
| O5 | Release the full attack code or the harness only? | Full code with a responsible-use notice, matching §9 |
| O6 | Which four prompt sources, and how many prompts each? | Public benchmark prompts with recorded licences; 100 per domain at Tier B |
