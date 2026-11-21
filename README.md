# EFFACE

**Finding the most effective meaning-preserving tactic, or chain of up to three, against SynthID-Text watermarks.**

[![Status: draft](https://img.shields.io/badge/status-draft-orange)](#status)
[![arXiv: pending](https://img.shields.io/badge/arXiv-pending-lightgrey)](#citation)
[![Paper: CC BY 4.0](https://img.shields.io/badge/paper-CC%20BY%204.0-lightgrey)](LICENSE-paper)
[![Code: MIT](https://img.shields.io/badge/code-MIT-blue)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](#setup)

This repository holds the paper and the code for **EFFACE**, a study of how much of a SynthID-Text-style watermark survives a given amount of meaning-preserving rewrite. The question is a constrained one: among the known removal tactics, and among ordered compositions of up to three of them, which achieves the highest removal rate without dropping below a fixed semantic-preservation floor?

## Status

> **Draft, preprint in preparation.** The paper source is in [`paper/`](paper/). Every number in the paper and in this README is a `TODO` placeholder until the runs land. At this commit the paper is a protocol: it specifies the estimand, the search, and the detection gate, and it reports no removal result. The code interface shown below is the planned one. Results will be replaced with held-out numbers, and a DOI will be added to the citation block.

Working documents: [`PLAN.md`](PLAN.md) for the task list, [`docs/decisions.md`](docs/decisions.md) for the locked design choices, and [`PREREGISTRATION.md`](PREREGISTRATION.md) for the frozen analysis protocol.

## Abstract

Text watermarking schemes of the SynthID-Text class embed a statistical signal in the sampling process, so the mark lives in the choice of tokens. Prior work measures how well such marks survive individual transformations: paraphrasing, back-translation, token substitution, regeneration. Each study picks its own operating point, and few report what the transformation costs in meaning. This paper poses the joint question. Given a semantic floor, which single transformation, or which ordered chain of at most three, removes the watermark most reliably? We formalise the problem as a constrained search over an attack catalogue, measure removal against a same-config detector at a per-document threshold and at a corpus-level true-positive rate, and measure preservation with complementary automatic metrics, reported per metric and as a fixed composite. We release the catalogue, the search procedure, and the evaluation harness.

## The paper

| Item | Location |
| --- | --- |
| LaTeX source | [`paper/main.tex`](paper/main.tex) |
| Build instructions | [`paper/README.md`](paper/README.md) |
| Bibliography | [`paper/refs.bib`](paper/refs.bib) |
| Compiled PDF | `paper/main.pdf`, produced by `make -C paper`; not tracked |

Section map:

| § | Title | File |
| --- | --- | --- |
| 1 | Introduction | [`paper/sections/01-introduction.tex`](paper/sections/01-introduction.tex) |
| 2 | Related work | [`paper/sections/02-related-work.tex`](paper/sections/02-related-work.tex) |
| 3 | Problem formulation | [`paper/sections/03-problem.tex`](paper/sections/03-problem.tex) |
| 4 | Attack catalogue | [`paper/sections/04-attack-catalogue.tex`](paper/sections/04-attack-catalogue.tex) |
| 5 | Searching over chains | [`paper/sections/05-combination-search.tex`](paper/sections/05-combination-search.tex) |
| 6 | Experimental setup | [`paper/sections/06-experimental-setup.tex`](paper/sections/06-experimental-setup.tex) |
| 7 | Results | [`paper/sections/07-results.tex`](paper/sections/07-results.tex) |
| 8 | Discussion | [`paper/sections/08-discussion.tex`](paper/sections/08-discussion.tex) |
| 9 | Limitations and ethics | [`paper/sections/09-limitations-ethics.tex`](paper/sections/09-limitations-ethics.tex) |
| 10 | Conclusion | [`paper/sections/10-conclusion.tex`](paper/sections/10-conclusion.tex) |
| A–D | Prompts, hyperparameters, extra results, checklist | [`paper/appendix/`](paper/appendix/) |

To build the PDF you need a TeX distribution with `latexmk`:

```sh
make -C paper
```

## Scope

The object of study is a **statistical, sampling-time text watermark** of the SynthID-Text class, detected from the token sequence alone. The study covers:

- removal tactics that change the token stream: paraphrase, back-translation, token edits, regeneration;
- ordered chains of up to three such tactics;
- removal measured at a per-document threshold and at a corpus operating point;
- preservation measured with embedding similarity, learned quality metrics, and distributional distance.

Out of scope:

- file metadata and C2PA manifests, which carry provenance outside the text;
- image, audio, and video watermarks;
- invisible-Unicode and other edit-based text carriers, which appear only as a control row;
- watermark stealing, forgery, and spoofing, which are a different threat model.

## Contributions

1. **A catalogue.** Twelve removal tactics in four families, plus one control, each defined operationally, traced to the paper that introduced or evaluated it, and implemented behind one interface.
2. **A search.** Ordered chains of up to three tactics, scored against a semantic floor fixed in advance, with pruning that keeps the evaluation budget bounded and a held-out split that keeps the headline number honest.
3. **A frontier.** Removal and preservation measured on the same documents across generators and domains, reported at two operating points, with the marginal value of the third step made explicit.

These are the paper's claims. They become findings once the runs in [`paper/sections/07-results.tex`](paper/sections/07-results.tex) are filled in.

## Repository layout

```text
efface/
├── README.md                  this file
├── LICENSE                    MIT, for code
├── LICENSE-paper              CC BY 4.0, for the paper text
├── CITATION.cff               machine-readable citation metadata
├── paper/                     LaTeX source of the paper (present)
│   ├── main.tex
│   ├── sections/
│   ├── appendix/
│   ├── refs.bib
│   └── Makefile
├── efface/                    Python package (planned)
│   ├── watermark/             generation through the MarkLLM SynthID reimplementation
│   ├── attacks/               one module per tactic in the catalogue
│   ├── chains/                composition, ordering, intensity
│   ├── detect/                MarkLLM adapter and scoring
│   ├── evaluate/              removal, preservation, intervals
│   ├── search/                beam search, pruning, split handling
│   └── cli.py                 command-line entry points
├── configs/                   generators, attackers, tactics, search, metrics
├── data/                      prompt sets and download manifests
├── scripts/                   thin wrappers for the commands in this README
├── results/                   generated reports; not tracked
└── tests/                     unit tests and a smoke run
```

Directories marked *planned* do not exist yet.

## Setup

> Not runnable yet. The package, `pyproject.toml`, and `configs/` land with the first code release. The commands below describe the intended workflow so that the reproduction table has a stable target.

Requirements: Python 3.11 or newer, a MarkLLM checkout for the detector, and API keys for the hosted models you configure. Preservation metrics need the `metrics` extra (`uv pip install -e ".[metrics]"`), which pulls BERTScore and `unbabel-comet`; the first run downloads `roberta-large` and a COMET checkpoint. See [`docs/metric-calibration.md`](docs/metric-calibration.md).

```sh
git clone https://github.com/guillaumemeyer/efface.git
cd efface
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Install the detector:

```sh
git clone https://github.com/THU-BPM/MarkLLM.git ~/MarkLLM
export MARKLLM_DIR="$HOME/MarkLLM"
```

Configure the models. Keys live in the environment; `.env` is ignored by git.

| Variable | Purpose |
| --- | --- |
| `DEEPSEEK_API_KEY` | Search attacker: paraphrase, translation, synonyms, regeneration |
| `DEEPSEEK_BASE_URL` | DeepSeek OpenAI-compatible endpoint |
| `ANTHROPIC_API_KEY` | Ablation attacker (Claude Sonnet) |
| `MARKLLM_DIR` | Path to the MarkLLM checkout used as the detector |
| `EFFACE_RESULTS_DIR` | Where run reports are written; defaults to `results/` |

Every model identifier and version is pinned in `configs/`. A run whose config does not record the model version is rejected, so that a hosted-model change cannot silently alter a result.

## Quickstart

The three commands below are the planned interface. They are listed here so the reproduction table has a stable target.

```sh
# 1. Generate watermarked documents: one per prompt per key
python -m efface.cli generate --config configs/generators.yaml \
  --row g1 --prompts data/prompts.jsonl --limit 1 --output results/docs.jsonl

# 2. Apply one tactic, or an ordered chain, to every document
python -m efface.cli attack --tactic typo_noise --intensity 0.05 --input results/docs.jsonl
python -m efface.cli attack --strategy "typo_noise@0.05,random_edits@0.1" \
  --input results/docs.jsonl --output results/attacked.jsonl
```

The chain executor caches the text after every prefix under `--cache-dir`
(default `results/cache`), keyed by document, seed, and prefix. A depth-3
extension of a depth-2 chain therefore skips the first two steps, and a rerun
reuses paid model calls. Each record's `chain` lists the steps that ran, with
their measured character edit rate, and `resumed_at` says how many prefixes came
from the cache.

# 3. Score removal under each document's generating key
python -m efface.cli score --input results/docs.jsonl \
  --null results/null-g1.json --output results/scores.jsonl
```

`score` writes one record per document with the detector score, `n_eff`, the p-value, the null that produced it, the `removed` flag at α = 0.05, and the manifest inherited from generation. The same records feed the tables in the paper.

## Attack catalogue

The catalogue is the unit of comparison. Each tactic has one interface, one intensity parameter, and one implementation. Semantic cost is the expected loss of fidelity at the intensity used in the main sweep.

The Source column names the closest published relative. The executed system is a prompted rewrite, a local masked-LM filler, or a deterministic rule set; [`docs/attack-catalogue.md`](docs/attack-catalogue.md) gives the operational difference per row.

| Tactic | Family | What it changes | Semantic cost | Closest relative | Implementation |
| --- | --- | --- | --- | --- | --- |
| Instruction paraphrase | Paraphrase | Sentence wording, kept close to the source | Low | Kirchenbauer et al. 2024 | `efface/attacks/model.py` |
| Discourse paraphrase | Paraphrase | Paragraph structure, sentence boundaries, wording | Medium | Krishna et al. 2023 | `efface/attacks/model.py` |
| Masked-LM infilling | Paraphrase | Individual spans, local context only | Low | Cheng et al. 2025 | `efface/attacks/mlm.py` |
| Style normalisation | Paraphrase | Contractions, casing, punctuation, filler, stock transitions | Low | Piet et al. 2025 | `efface/attacks/local.py` |
| Document rewrite | Paraphrase | Whole document, fresh context per chunk | High | Krishna et al. 2023 | `efface/attacks/model.py` |
| Single-pivot back-translation | Back-translation | Token stream, through one pivot language | Medium | Piet et al. 2025 | `efface/attacks/model.py` |
| Multi-hop back-translation | Back-translation | Token stream, through two or more pivots | High | He et al. 2024 | `efface/attacks/model.py` |
| Cross-lingual generation | Back-translation | Response generated in the pivot, then translated back | High | He et al. 2024 | `efface/attacks/model.py` |
| Synonym substitution | Token edits | A fraction of content words | Low | Fernandez et al. 2023 | `efface/attacks/model.py` |
| Random word edits | Token edits | Swap, insert, or delete at random positions | Low | Piet et al. 2025 | `efface/attacks/local.py` |
| Typo and noise injection | Token edits | Character-level noise and misspellings | Low | Piet et al. 2025 | `efface/attacks/local.py` |
| Non-origin regeneration | Regeneration | The entire token stream, from a different model family | High | He et al. 2024 | `efface/attacks/model.py` |
| Unicode scrub | Control | Invisible and zero-width characters only | None | Piet et al. 2025 | `efface/attacks/local.py` |

The control row exists to separate two channels. A sampling-time mark is not carried by invisible characters, so the scrub should leave its detection score unchanged; if it does not, the measurement is picking up something other than the statistical signal.

Two properties of the catalogue matter for the results. First, the families differ in how much of the token stream they replace, which is why a fixed semantic floor ranks them differently from a fixed edit budget. Second, every tactic that calls a model uses a model from a family different from the generator, so the attacker cannot reintroduce the generator's own mark.

## Combining tactics

A chain is an ordered tuple of up to three tactics, applied left to right. Order is part of the chain: paraphrase then back-translate yields a different document from back-translate then paraphrase, because each step conditions on the previous output.

With 12 tactics and depth at most three, the ordered space has 12 + 144 + 1,728 = **1,884 chains** at one intensity. Seven tactics have three intensity levels and five have one, so the crossed grid has 26 + 26² + 26³ = **18,278 cells**. The objective only needs the cells that sit on the preservation floor. EFFACE searches that surface in three passes:

1. Map every tactic at each swept intensity. The operating intensity is the admissible level with the highest removal.
2. Extend a diverse beam of width 8 (four slots by removal, two by preservation headroom, two by the family of the last step). Skip an extension whose predicted preservation is below τ − 0.10, and do not extend an order screen of 57 pairs that misses the 0.05 removal margin. Drop a measured chain that misses the semantic floor or that same margin against its best prefix.
3. On the top five chains and the best single, try the next stronger swept intensity and keep it only when the chain stays admissible and removal rises by at least 0.05.

Choose on the search split, report on the held-out split. Every evaluated chain is scored on the full search split.

The paper reports beam width, pruning margins, and the number of chains actually evaluated, so that the search cost is auditable. It also reports the marginal removal bought by the third step, since a pair that captures most of the achievable removal is the honest recommendation.

## Experimental protocol

Generators and schemes:

| Row | Model | Scheme | Sampling distribution available |
| --- | --- | --- | --- |
| G1 | `facebook/opt-1.3b` | MarkLLM SynthID reimplementation | Yes |
| G2 | `Qwen/Qwen2.5-1.5B-Instruct` | MarkLLM SynthID reimplementation | Yes |

Both rows are open-weight models, so the sampling distribution is available and the same SynthID reimplementation applies to each. MarkLLM's SynthID is a research reimplementation with its own keying. Google retired text-watermark detection on its API in August 2026, so the study has no vendor tier and makes no claim about production SynthID-Text detection.

Attackers, all from families other than the generator's:

| Role | Model | Used by |
| --- | --- | --- |
| Paraphrase and style | DeepSeek Flash | Instruction paraphrase, discourse paraphrase, style normalisation, document rewrite |
| Translation | DeepSeek Flash | All back-translation tactics |
| Masked infilling | `roberta-large` (local) | Masked-LM infilling |
| Synonym candidates | DeepSeek Flash | Synonym substitution |
| Regeneration | DeepSeek Flash | Non-origin regeneration |
| Second-attacker ablation | Claude Sonnet | Top five chains, best single, control |

One attacker is used per chain, so a chain's result is not confounded by a model switch inside the chain. The search runs on DeepSeek Flash. The top five chains, the best single tactic, and the control are re-run end to end with Claude Sonnet on the held-out split, and the paper reports the rank correlation and the largest removal change.

Data:

| Domain | Source | Prompts | Target length |
| --- | --- | --- | --- |
| News writing | TODO | TODO | TODO |
| Long-form question answering | TODO | TODO | TODO |
| Creative writing | TODO | TODO | TODO |
| MarkMyWords tasks | Piet et al. 2025 | TODO | TODO |

Fixed settings: TODO temperature, top-p, and maximum length per generator; three watermark keys per prompt, with each document scored under its generating key; a fixed seed list per stochastic tactic; documents below a minimum length discarded and counted. All of these live in `configs/` and are restated in Appendix B of the paper.

## Metrics and decision rule

Removal:

- **Per-document removal rate** at `α = 0.05`: the fraction of documents where the same-config detector fails to reject the unwatermarked null under the key that generated the document, with a 95% prompt-clustered bootstrap interval and a document-level Wilson interval beside it.
- **TPR at 1% FPR**: the corpus-level true-positive rate of the detector at a false-positive rate read from the parametric unwatermarked null, computed over the pooled attacked and unattacked sets.
- **Detection check**: before any attack table, each generator row must show a detection rate of at least 0.80 at `α = 0.05`, with a Wilson lower bound of at least 0.70, on at least 200 documents.

Preservation:

- **BERTScore-F1** for embedding-level similarity to the source;
- **COMET** for adequacy and fluency against the source;
- **BLEURT** as a second learned judgement;
- **MAUVE** for distributional closeness between attacked and unattacked sets;
- **Length ratio**, because a tactic that shortens a document can inflate similarity scores.

The selecting preservation score `S` is the unweighted mean of BERTScore-F1 and COMET, normalised to `[0, 1]`. BLEURT, MAUVE, and length ratio are reported on the same documents and stay out of the constraint, so a tier change cannot move which chain wins. Per-metric values are reported so the composite can be reweighted. The semantic floor `τ` is fixed before the search and reported with every recommendation, along with results at `τ ± 0.05` and the fraction of documents below the floor.

## Results

All cells below are placeholders. They mirror the paper's tables by label and will be filled from `results/` once the sweep completes.

**Table 1 — single tactics** (`paper` label `tab:singles`):

| Tactic | Removal rate ↑ | TPR@1%FPR ↓ | BERTScore ↑ | COMET ↑ | Length ratio |
| --- | --- | --- | --- | --- | --- |
| Instruction paraphrase | TODO | TODO | TODO | TODO | TODO |
| Discourse paraphrase | TODO | TODO | TODO | TODO | TODO |
| Masked-LM infilling | TODO | TODO | TODO | TODO | TODO |
| Style normalisation | TODO | TODO | TODO | TODO | TODO |
| Document rewrite | TODO | TODO | TODO | TODO | TODO |
| Single-pivot back-translation | TODO | TODO | TODO | TODO | TODO |
| Multi-hop back-translation | TODO | TODO | TODO | TODO | TODO |
| Cross-lingual generation | TODO | TODO | TODO | TODO | TODO |
| Synonym substitution | TODO | TODO | TODO | TODO | TODO |
| Random word edits | TODO | TODO | TODO | TODO | TODO |
| Typo and noise injection | TODO | TODO | TODO | TODO | TODO |
| Non-origin regeneration | TODO | TODO | TODO | TODO | TODO |
| Unicode scrub (control) | TODO | TODO | TODO | TODO | TODO |

**Table 2 — best ordered pairs** (`tab:pairs`), **Table 3 — best ordered triples** (`tab:triples`), **Table 4 — per domain** (`tab:perdomain`), **Figure 1 — removal vs preservation frontier** (`fig:pareto`): see [`paper/sections/07-results.tex`](paper/sections/07-results.tex).

The recommendation the paper will make is the frontier point with the highest removal among chains at or above `τ`, chosen on the search split and reported on the held-out split.

## Reproducing the paper

Each row names the paper label, the command that produces it, and the expected runtime. Commands are planned; runtimes are placeholders until the code lands.

| Paper label | What it produces | Command | Runtime |
| --- | --- | --- | --- |
| `tab:singles` | Single-tactic table | `python -m efface.cli run --config configs/experiments/singles.yaml` | TODO |
| `tab:pairs` | Best ordered pairs | `python -m efface.cli search --depth 2 --beam TODO` | TODO |
| `tab:triples` | Best ordered triples | `python -m efface.cli search --depth 3 --beam TODO` | TODO |
| `tab:perdomain` | Per-domain recommendation | `python -m efface.cli report --by domain` | TODO |
| `fig:pareto` | Frontier figure | `python -m efface.cli report --figure pareto` | TODO |
| `tab:length` | Results by length bucket | `python -m efface.cli report --by length` | TODO |
| `tab:tau` | Sensitivity to the floor | `python -m efface.cli report --tau-grid 0.05` | TODO |
| `tab:ablation` | Second-attacker ablation | `python -m efface.cli report --ablation` | TODO |

A smoke run that takes under two minutes and exercises one tactic on one prompt set:

```sh
python -m efface.cli smoke --config configs/experiments/smoke.yaml
```

## Reproducibility checklist

Answers to the Machine Learning Reproducibility Checklist v2.0 (Pineau et al., 2021), matching Appendix D of the paper.

| Item | Status |
| --- | --- |
| Mathematical setting and algorithm described | Yes — paper §3 |
| Assumptions stated | Yes — paper §3, §9 |
| Complexity analysis (time, space, sample size) | Partial — per-tactic wall clock in §6; sample-size analysis TODO |
| Dataset statistics and splits | Yes — paper Table 3 |
| Excluded data and preprocessing described | Yes — paper §6 |
| Dataset downloadable | TODO — manifest in `data/` |
| Dependencies specified | TODO — `pyproject.toml` with pins, first code release |
| Evaluation code | TODO — `efface/evaluate/` |
| Pretrained models named and versioned | TODO — `configs/` |
| README maps each result to a command | Partial — reproduction table above; commands planned |
| Hyperparameter ranges and selection method | Yes — paper Appendix B |
| Number of evaluation runs | Yes — paper §6 |
| Statistic definitions | Yes — paper §7.1 and this README |
| Central tendency and variation | Yes — Wilson intervals for rates, mean and SD elsewhere |
| Runtime or energy cost | TODO |
| Computing infrastructure | TODO |

## Limitations

- **The detector is a same-config oracle.** It is configured with the scheme parameters and key family used at generation, which makes the study reproducible and bounds it. A vendor detector may aggregate differently, and nothing here certifies what a deployed checker reports.
- **Semantic metrics are proxies.** They miss some factual corruptions and can be gamed by a tactic that keeps the opening intact. A specific failure mode is best read from the per-metric table rather than the composite.
- **No human evaluation.** A human rating study was out of scope, so preservation rests on the automatic metrics; their blind spots are a limitation of the preservation claim.
- **Composition compounds loss.** A chain at the floor on average can still fail on individual documents; the per-document distribution is reported alongside the mean.
- **Length effects.** Detector power grows with tokens, and removal rates do not transfer to short passages.
- **Model drift.** Hosted models change without notice; a committed record of model identifiers and dates is the only mitigation.
- **Language coverage.** The evaluation is English-centric, while watermark strength is known to vary across languages.
- **Ceiling on guarantees.** Impossibility results rule out a scheme-independent guarantee; EFFACE measures what a named detector reports at a named operating point.

## Responsible use

The work measures the robustness of a deployed provenance mark. That measurement is what scheme designers and standards bodies need in order to decide how much rewriting a mark should survive. The removal targets are model-generated documents; prompts come from self-authored sets and public benchmark tasks. No third-party document is attacked. EFFACE ships no service and no hosted endpoint, and reports results at the level of tactic classes and frontiers. The author maintains [`watermarks-remover`](https://github.com/guillaumemeyer/watermarks-remover), a separate MIT tool that removes provenance marks from content its users own; EFFACE reuses its strategy parser and statistics code. That tool is a competing interest and is disclosed here. Findings are shared with the maintainers of the implementation under test and, as a courtesy, with the SynthID and Claude watermark teams at least ten days before posting. The compliance record, including the provider-terms review, is in [`docs/ethics.md`](docs/ethics.md).

## Citation

Machine-readable metadata is in [`CITATION.cff`](CITATION.cff); GitHub renders a "Cite this repository" panel from it. Until the preprint is announced:

```bibtex
@article{efface2026,
  title   = {{EFFACE}: Finding the Most Effective Meaning-Preserving Attack Chain against {SynthID-Text-Class} Watermarks},
  author  = {Meyer, Guillaume},
  journal = {arXiv preprint arXiv:TODO},
  year    = {2026},
  note    = {Preprint in preparation}
}
```

## References

### Watermarking schemes

- Dathathri, S., See, A., et al. *Scalable watermarking for identifying large language model outputs.* Nature 634, 818–823 (2024). [doi:10.1038/s41586-024-08025-4](https://doi.org/10.1038/s41586-024-08025-4)
- Kirchenbauer, J., Geiping, J., Wen, Y., Katz, J., Miers, I., Goldstein, T. *A Watermark for Large Language Models.* ICML 2023. [arXiv:2301.10226](https://arxiv.org/abs/2301.10226)
- Kuditipudi, R., Thickstun, J., Hashimoto, T., Liang, P. *Robust Distortion-free Watermarks for Language Models.* TMLR (2024). [arXiv:2307.15593](https://arxiv.org/abs/2307.15593)
- Christ, M., Gunn, S., Zamir, O. *Undetectable Watermarks for Language Models.* COLT 2024. [arXiv:2306.09194](https://arxiv.org/abs/2306.09194)
- Fernandez, P., Couairon, G., Jégou, H., Douze, M., Furon, T. *Three Bricks to Consolidate Watermarks for Large Language Models.* 2023. [arXiv:2308.00113](https://arxiv.org/abs/2308.00113)

### Removal attacks and robustness

- Kirchenbauer, J., Geiping, J., Wen, Y., Shu, M., Saifullah, K., Kong, K., Fernando, K., Saha, A., Goldblum, M., Goldstein, T. *On the Reliability of Watermarks for Large Language Models.* ICLR 2024. [arXiv:2306.04634](https://arxiv.org/abs/2306.04634)
- Krishna, K., Song, Y., Karpinska, M., Wieting, J., Iyyer, M. *Paraphrasing evades detectors of AI-generated text, but retrieval is an effective defense.* NeurIPS 2023. [arXiv:2303.13408](https://arxiv.org/abs/2303.13408)
- He, Z., Zhou, B., Hao, H., Liu, A., Wang, X., Tu, Z., Zhang, Z., Wang, R. *Can Watermarks Survive Translation? On the Cross-lingual Consistency of Text Watermark for Large Language Models.* ACL 2024. [arXiv:2402.14007](https://arxiv.org/abs/2402.14007)
- Piet, J., Sitawarin, C., Fang, V., Mu, N., Wagner, D. *Mark My Words: Analyzing and Evaluating Language Model Watermarks.* IEEE SaTML 2025. [arXiv:2312.00273](https://arxiv.org/abs/2312.00273)
- Zhang, H., Edelman, B. L., Francati, D., Venturi, D., Ateniese, G., Barak, B. *Watermarks in the Sand: Impossibility of Strong Watermarking for Generative Models.* ICML 2024. [arXiv:2311.04378](https://arxiv.org/abs/2311.04378)
- Cheng, Y., Guo, H., Li, Y., Sigal, L. *Revealing Weaknesses in Text Watermarking Through Self-Information Rewrite Attacks.* ICML 2025. [arXiv:2505.05190](https://arxiv.org/abs/2505.05190)
- Sadasivan, V. S., Kumar, A., Balasubramanian, S., Wang, W., Feizi, S. *Can AI-Generated Text be Reliably Detected?* TMLR (2024). [arXiv:2303.11156](https://arxiv.org/abs/2303.11156)
- Jovanović, N., Staab, R., Vechev, M. *Watermark Stealing in Large Language Models.* ICML 2024. [arXiv:2402.19361](https://arxiv.org/abs/2402.19361)

### Evaluation metrics

- Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., Artzi, Y. *BERTScore: Evaluating Text Generation with BERT.* ICLR 2020. [arXiv:1904.09675](https://arxiv.org/abs/1904.09675)
- Sellam, T., Das, D., Parikh, A. P. *BLEURT: Learning a Robust Metric for Text Generation.* ACL 2020. [arXiv:2005.01535](https://arxiv.org/abs/2005.01535)
- Rei, R., Stewart, C., Farinha, A. C., Lavie, A. *COMET: A Neural Framework for MT Evaluation.* EMNLP 2020. [arXiv:2009.12061](https://arxiv.org/abs/2009.12061)
- Pillutla, K., Swayamdipta, S., Zellers, R., Thickstun, J., Welleck, S., Choi, Y., Zettlemoyer, L. *MAUVE: Measuring the Gap Between Neural Text and Human Text using Divergence Frontiers.* NeurIPS 2021. [arXiv:2102.01454](https://arxiv.org/abs/2102.01454)

### Standards and checklists

- Pineau, J., Vincent-Lamarre, P., Sinha, K., Larivière, V., Beygelzimer, A., d'Alché-Buc, F., Fox, E., Larochelle, H. *Improving Reproducibility in Machine Learning Research.* JMLR 22(164), 2021. [Checklist v2.0](https://www.cs.mcgill.ca/~jpineau/ReproducibilityChecklist-v2.0.pdf)
- NeurIPS 2021 Paper Checklist. [neurips.cc](https://neurips.cc/Conferences/2021/PaperInformation/PaperChecklist)

## Materials and tooling

External projects the study depends on or compares against. Each is governed by its own license.

| Project | Role | Link |
| --- | --- | --- |
| MarkLLM | Reference schemes and the same-config detector | [THU-BPM/MarkLLM](https://github.com/THU-BPM/MarkLLM) |
| MarkMyWords | Benchmark tasks and tamper-resistance comparisons | [wagner-group/MarkMyWords](https://github.com/wagner-group/MarkMyWords) |
| DIPPER | Discourse-paraphrase method reference (not executed; the paraphrase family uses the attacker model) | [martiansideofthemoon/ai-detection-paraphrases](https://github.com/martiansideofthemoon/ai-detection-paraphrases) |
| Three Bricks | Token-substitution reference | [facebookresearch/three_bricks](https://github.com/facebookresearch/three_bricks) |
| Impossibility watermark | Quality-oracle random-walk attack implementation | [hlzhang109/impossibility-watermark](https://github.com/hlzhang109/impossibility-watermark) |
| Cross-lingual watermark project | Data and code for the pivot round-trip study | [cross-lingual-watermark.github.io](https://cross-lingual-watermark.github.io/) |

## License

Copyright © 2026 Guillaume Meyer.

Code is released under the [MIT License](LICENSE); the paper text and figures are released under [CC BY 4.0](LICENSE-paper).

MAUVE is GPLv3. It is isolated in the optional `metrics-gpl` extra and invoked as a separate process, so the core install remains MIT; see [`NOTICE`](NOTICE) and [`docs/ethics.md`](docs/ethics.md). `facebook/opt-1.3b` is used under the OPT-175B non-commercial research license; no weights or OPT-derived text are redistributed. MarkMyWords task text is third-party content and is not redistributed. Third-party material cited in the paper remains under its own license.

## Contact

Guillaume Meyer — [guillaume.meyer@outlook.com](mailto:guillaume.meyer@outlook.com). Open an issue for questions about the paper or the harness.
