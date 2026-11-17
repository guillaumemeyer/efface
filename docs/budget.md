# Compute and API budget

Derived from the measured throughput in `docs/perf.md` and the preregistered
design in `PREREGISTRATION.md`. All figures are planning estimates, not results.

## Corpus size

| Item | Count |
| --- | --- |
| Generators | 2 |
| Domains | 4 |
| Prompts per domain | 100 |
| Keys per prompt | 3 |
| Watermarked documents | 2,400 |
| Search-split documents | 1,440 (60%) |
| Held-out documents | 960 (40%) |
| Unwatermarked calibration documents | 200 (100 per generator) |

## Generation

Measured rates: 34 tokens/s (OPT) and 20 tokens/s (Qwen). Assume 440 tokens per
document.

| Row | Documents | Seconds each | Hours |
| --- | --- | --- | --- |
| G1 OPT-1.3b | 1,200 | 12.9 | 4.3 |
| G2 Qwen2.5-1.5B | 1,200 | 21.8 | 7.3 |
| Calibration, unwatermarked | 200 | 15.0 | 0.8 |
| **Total** | 2,600 | | **12.4** |

## Detection

Detector cost is 0.02–0.04 s per document. Search nodes are 12 singles, 96 pairs
(beam 8 × 12), and 96 triples (beam 8 × 12), for 204 nodes per generator.

| Item | Passes | Hours |
| --- | --- | --- |
| Search nodes × search-split documents | 204 × 1,440 | 2.4 |
| Held-out top chains and singles | ~22 × 960 | 0.2 |
| **Total** | | **2.6** |

## Attack API

A node application is one attacker call per document, because prefix caching
reuses the output of every prefix. Nodes per generator: 204. Search-split
documents per generator: 720; held-out documents per generator: 480.

| Item | Count |
| --- | --- |
| Search node applications, both generators | 204 × 720 × 2 = 293,760 |
| Held-out applications for reported chains | ~22 × 480 × 2 = 21,120 |
| Total node applications | ~315,000 |
| Average input tokens | 500 |
| Average output tokens | 400 |
| Calls per node, average (multi-hop and cross-lingual use 2–3) | 1.5 |
| Effective calls | ~470,000 |

At a cheap attacker priced at $0.15 per million input tokens and $0.60 per
million output tokens, one call costs about $0.00032, so the sweep is about
$150. A model three times more expensive puts it near $450, inside the cap. A
model ten times more expensive would exceed it.

**Plan:** use the cheap model for the search and the parameter sweeps; reserve a
stronger model for the regeneration row and for the final held-out pass. Cap at
$600 in `configs/search.yaml`, with a per-run dry-run estimate and a stop rule.

## Metric scoring

| Metric | Pairs | Rate (pairs/s) | Hours |
| --- | --- | --- | --- |
| BERTScore | 300,000 | 50 | 1.7 |
| COMET | 300,000 | 10 | 8.3 |
| BLEURT (Tier B) | 300,000 | 20 | 4.2 |
| MAUVE | per chain | — | 0.5 |
| **Total** | | | **14.7** |

Scores are computed once per (document, node) pair and cached; the held-out
pass reuses them.

## Engineering and writing

| Item | Hours |
| --- | --- |
| Harness, tactics, metrics, search, reports | 55–65 |
| Paper, references, artifact, arXiv | 30–35 |

## Pessimistic case

If attacker calls cost 3× the estimate, API spend reaches about $450, which
stays inside the cap. If a stronger model is used throughout, the cap binds:
reduce beam width from 8 to 5, which cuts depth-3 nodes from 96 to 60, and
evaluate metrics on a 50% subsample of the search split. Both are recorded as
deviations before the main sweep.

## Total

| Resource | Estimate |
| --- | --- |
| Local compute | 30 hours |
| API spend | $150–$600 |
| Engineering and writing | 85–100 hours |
