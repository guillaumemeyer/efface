# Attack catalogue

Thirteen rows: twelve removal tactics in four families and one control. Each row
has one interface, `apply(text, *, intensity, seed) -> str`, one module, and one
intensity unit. The Source column in the paper names the **closest published
relative**; this file states what runs.

| Tactic | Module | Intensity unit | Closest published relative | Operational difference |
| --- | --- | --- | --- | --- |
| `instruction_paraphrase` | `attacks/model.py` | target rewrite ratio | Kirchenbauer et al. 2024 reliability study | One prompted rewrite of the whole passage, not the reliability study's machine paraphraser |
| `discourse_paraphrase` | `attacks/model.py` | target rewrite ratio | DIPPER (Krishna et al. 2023) | A prompt that permits reordering; DIPPER's 11B discourse paraphraser is not executed |
| `mlm_infill` | `attacks/mlm.py` | fraction of word positions | self-information rewrite (Cheng et al. 2025) | Masks a seeded sample of positions; the published policy masks the highest-self-information tokens |
| `style_normalisation` | `attacks/local.py` | rule set (always full) | MarkMyWords style perturbation | Fixed deterministic rules over quotes, dashes, filler, and stock transitions |
| `document_rewrite` | `attacks/model.py` | rewrite strength | DIPPER (Krishna et al. 2023) | Whole-passage rewrite from a prompt; no chunk-level paraphrase model |
| `backtranslate_single` | `attacks/model.py` | pivot count (French) | MarkMyWords translation perturbation | One model translates both legs, so translator errors can compound |
| `backtranslate_multi` | `attacks/model.py` | pivot chain (French, German) | He et al. 2024 cross-lingual study | Two pivots then back, all through one model |
| `crosslingual_generation` | `attacks/model.py` | pivot count (French) | He et al. 2024 cross-lingual study | Translate, rewrite in the pivot, translate back; the rewrite is prompted rather than a second model family |
| `synonym_substitution` | `attacks/model.py` | fraction of content words | Three Bricks (Fernandez et al. 2023) | Candidates come from a prompted model, applied to seeded distinct word types |
| `random_edits` | `attacks/local.py` | fraction of word positions | MarkMyWords random perturbation | Swap, insert, or delete with equal probability from a seeded RNG |
| `typo_noise` | `attacks/local.py` | character error rate | MarkMyWords character perturbation | Transpose, delete, or neighbour-replace at a per-character rate |
| `regeneration` | `attacks/model.py` | full generation | He et al. 2024 regeneration study | The model is asked to restate the passage's claims in a new passage; no separate model family or prompt oracle |
| `unicode_scrub` (control) | `attacks/local.py` | scrub all invisible characters | MarkMyWords invisible-character probe | Removes Unicode `Cf` characters and normalises exotic spaces |

## Determinism

The local rows are deterministic given `seed`: `random_edits` and `typo_noise`
draw from `random.Random(seed)`, and the rule rows have no randomness. The model
rows pass `seed` to the provider; providers do not guarantee determinism, so
every record stores the seed and the model snapshot, and the achieved edit rate
is measured rather than assumed.

## Attributed code

The style rules follow the deterministic subset of `humanize_pass.py` in
`watermarks-remover` (MIT). The prompt structure follows its rewrite passes.
Attribution is recorded in `NOTICE`.

## What is not in the catalogue

Adaptive paraphrasers trained against the detector (Diaa, Aremu, and Lukas,
ICML 2025), cross-lingual summarization removal, and copy-paste mixing. The
first two are stronger attacks that the non-adaptive search does not attempt;
the third is a dilution attack that the length controls partly cover. The paper
lists them in §2.
