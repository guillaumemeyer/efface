# Ethics and compliance record

**Status:** v1.0, approved 2026-11-17.
**Owner:** Guillaume Meyer.
**Scope:** the EFFACE study, its code, its data, and its release, as described in
`PLAN.md` and `PREREGISTRATION.md`.

This file is the record required by `PLAN.md` §11. It states what the study
does, which provider terms apply, which licences constrain the artifact, how
findings are disclosed, and which conflicts exist. It is a research record, not
legal advice. Terms change; the versions and retrieval dates below are part of
the record.

**Review triggers:**

- before the first hosted API call;
- at gates G2 and G3;
- before the artifact release and before the arXiv submission;
- after any provider updates its terms, privacy policy, or model line-up;
- after any change to the attack catalogue or the released artifact.

---

## 1. What the study does

EFFACE measures how well the MarkLLM SynthID reimplementation survives
meaning-preserving transformations. It generates documents with two open-weight
models (`facebook/opt-1.3b` and `Qwen/Qwen2.5-1.5B-Instruct`), applies twelve
removal tactics and one Unicode control, searches ordered chains of up to three
tactics, and reports removal and preservation on a held-out split.

The removal targets are model-generated documents. Prompts come from
self-authored sets and public benchmark tasks. No third-party document is
attacked. The study ships no service, no hosted endpoint, and no vendor
integration. It measures a named detector under a named configuration; it makes
no claim about production SynthID.

## 2. Intended use and dual-use assessment

**Intended use.** Measuring the robustness of a deployed provenance mechanism,
so that scheme designers, standards bodies, and auditors can see which tactic
classes a mark survives and where the preservation frontier turns. The same
measurement supports defence: it identifies the cheapest attack class that a
scheme must resist.

**The capability is already public.** MarkLLM ships text editors for word
deletion, synonym substitution, GPT paraphrasing, DIPPER paraphrasing, and a
random-walk attack. The removal literature cited in the paper describes
paraphrase, back-translation, and token edits. EFFACE adds an organised search
over ordered chains; it does not introduce a new removal primitive. Withholding
the harness would not remove the capability, and would remove the reproducibility
that makes the measurement useful.

**What is released (E6):**

- the MIT-licensed package, configs, tests, and search code;
- aggregate result files and generated tables;
- the paper's LaTeX source and figures.

**What is withheld:**

- the attacked document corpus;
- model weights and checkpoints;
- any hosted endpoint or service wrapper;
- a turnkey product or vendor-specific evasion recipe.

**Residual risk.** The paper ranks chains, which lowers the cost of finding an
effective sequence. The mitigations are the measurement framing, the withheld
corpus, the responsible-use notice, and the pre-publication notice in §7. The
repository carries a documented intended use; users must bring their own API
keys and their own content.

## 3. Legal and regulatory context

**EU AI Act, Article 50(2).** From 2026-08-02, providers of AI systems that
generate synthetic text must ensure outputs are marked in a machine-readable
format and detectable as artificially generated. The obligation is on providers.
Article 50(4) adds deployer disclosure duties for certain published content.
EFFACE evaluates a research reimplementation of one marking scheme; it does not
publish AI-generated text to inform the public, and it does not advise anyone to
remove a mark from content they do not own.

**Code of Practice on Transparency of AI-generated Content.** The Commission
and the AI Board assessed the code as adequate; about 190 organisations signed
by the end of July 2026, including Anthropic, Google, Meta, Microsoft, Mistral,
and OpenAI in Section 1. The code is a route to demonstrating compliance with
the Article 50 marking duty. EFFACE measures the robustness of a mechanism that
this code requires, which is the public-interest case for the work.

**GDPR and personal data.** The prompts contain no personal data. No data
subjects are involved, and no special-category data is processed. The only
personal-data flow is the author's account data to the API providers: DeepSeek
processes account data in the PRC, and Anthropic processes it under its
Commercial Terms and Data Processing Addendum. A dedicated API account with
minimal account data is used.

**Contract and platform terms.** The provider terms in §4 govern the hosted
calls. Removing a provenance mark from content the user does not own may breach
a platform's terms, a deployer duty, or consumer law; the study does not do
that, and the released notice says so.

**Export control and sanctions.** The author is in France. France is a supported
region for both providers, and no restricted-party or sanctioned-country issue
applies.

## 4. Provider terms assessment

### 4.1 DeepSeek — search and intensity sweep

**Documents reviewed (accessed 2026-11-17):**

| Document | Version | URL |
| --- | --- | --- |
| Terms of Use | Last updated 2026-03-27 | `https://cdn.deepseek.com/policies/en-UK/deepseek-terms-of-use.html` |
| Open Platform Terms of Service | Released 2026-04-22, effective 2026-04-29 | `https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html` |
| Privacy Policy | Last updated 2026-02-10 | `https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html` |

The English documents are translations, so wording may differ from the Chinese
originals. A native speaker should confirm the two conduct clauses below before
the first paid call. This is a residual risk, recorded rather than resolved.

**Clauses that matter:**

| Clause | Text or substance | Reading |
| --- | --- | --- |
| Terms of Use §4.2(3) | Inputs and outputs may be used for academic research | The study is an expressly contemplated use |
| Terms of Use §5.3 | "You shall not delete, alter, forge, conceal, or attempt to circumvent such labels" | The clause concerns labels DeepSeek adds to its own platform content; the study removes a mark from OPT/Qwen text and never touches a DeepSeek label |
| Terms of Use §3.1(2) | Published outputs must be clearly marked as AI-generated | The study publishes no outputs; if an example is ever published, it will carry that disclosure |
| Terms of Use §3.6(2) | No use for "dangerous purposes that may have serious harmful impacts on physical health, psychology, society, or the economy, or violate scientific and technological ethics" | Broad; the only clause that could be cited against the project; the study's purpose is defensive measurement, not deployment |
| Open Platform ToS §3.1 | Incorporates the Terms of Use | The same reading applies to API use |
| Open Platform ToS §4.2(3) | Academic research is a permitted use of inputs and outputs | Supports the study |
| Open Platform ToS §8.1 | End users must be told outputs are AI-generated | No end users; no publication |
| Privacy Policy | Data processed and stored in the PRC; inputs may be used to improve and train models; right to opt out; EU representative Prighter | No personal data is sent; training opt-out is enabled; the account is dedicated |

**Assessment.** No clause explicitly prohibits watermark-removal research. The
study does not remove DeepSeek's labels, does not publish outputs, has no end
users, and uses the API for the academic research expressly permitted by
§4.2(3). The residual ambiguity is §3.6(2). The decision is to proceed with the
mitigations below and to keep a fallback.

**Decision E1 — proceed, mitigated.**

- Publish no attacked documents. Aggregate metrics and generated tables only.
- If any example is ever published, label it as AI-generated and as attacked
  under a named detector.
- No personal, confidential, or third-party text is sent.
- Enable the training opt-out and use a dedicated API account.
- Disable thinking mode for rewrite calls; record the snapshot, prices, and
  terms version in every run manifest.
- Keep the fallback: an open-weight attacker on a rented GPU. The DeepSeek
  V4.1 Flash weights are MIT, but the checkpoint is about 763B parameters
  (fp8/int8), so it cannot run on the 24 GB Mac. A smaller open-weight model
  would replace `deepseek-flash` for the search without changing the design.

**Model and price record (accessed 2026-11-17):**

- API model: `deepseek-flash`, serving DeepSeek-V4.1-Flash-1017 (updated
  2026-10-17). Thinking mode is on by default.
- Prices per million tokens: input $0.30 peak / $0.15 off-peak; output $1.20
  peak / $0.60 off-peak; cache hit $0.006 peak / $0.003 off-peak.
- Peak hours are 01:00–04:00 and 06:00–10:00 UTC on weekdays. The search can be
  scheduled off-peak.

### 4.2 Anthropic — second-attacker ablation

**Documents reviewed (accessed 2026-11-17):**

| Document | Version | URL |
| --- | --- | --- |
| Usage Policy (AUP) | Effective 2026-11-12 | `https://www.anthropic.com/legal/aup` |
| Commercial Terms of Service | Retrieved 2026-11-17 | `https://www.anthropic.com/legal/commercial-terms` |
| Text watermark explainer | Updated 2026-09-01 | `https://www.anthropic.com/news/claude-text-watermark` |

**Clauses that matter:**

| Clause | Text or substance | Reading |
| --- | --- | --- |
| AUP, applicable law | No use to violate law or infringe IP | The study uses public benchmark prompts and self-authored text, and publishes no third-party content |
| AUP, fraudulent or predatory practices | Includes circumventing "the guardrails or terms of other platforms or services" | The clause concerns guardrails and platform terms; a statistical provenance mark is not an access control; the study does not bypass the provider's terms |
| AUP, abuse of the platform | No bypassing Anthropic's own safeguards | Not applicable: the API is used as intended |
| Commercial Terms B | Anthropic may not train on Customer Content; the customer owns outputs | Inputs and outputs remain the author's; no training use |
| Commercial Terms D.1/D.2 | Comply with law, the AUP, and the Supported Regions Policy | France is supported |
| Commercial Terms D.4 | No competing product, reverse engineering, or resale | Not applicable |
| Data retention | Prompts and outputs are not retained by default; Covered Models require 30-day retention; ZDR by agreement | Record the console retention setting in the run manifest |

**Watermark context.** Anthropic applies a text watermark to Claude outputs and
is rolling it out globally, in line with the EU AI Act marking obligations that
applied from 2026-08-02. The method is a version of the SynthID-Text approach.
A detection API is in private preview for regulators, law enforcement, media,
fact-checkers, and independent researchers. Consequence for the study: Claude
rewrites may themselves carry a watermark. The study's detector is keyed to
OPT/Qwen, so this does not affect detection, but attacked documents must not be
released as if they were unmarked.

**Assessment.** Permitted. The AUP contains no watermark-removal prohibition,
and the closest clause is about platform guardrails, which the study does not
circumvent. The courtesy notice in §7 covers Anthropic's interest in the
deployed mark.

**Decision.** Use `claude-sonnet-5-5` for the ablation, at $2/$10 per million
tokens. Claude 4.7 and later tokenizers produce about 30% more tokens for the
same text, so the budget uses a 30% token allowance. Record the snapshot and
the retention setting in every run manifest.

### 4.3 Local models and the scheme

| Component | Terms | Consequence |
| --- | --- | --- |
| `facebook/opt-1.3b` | OPT-175B License Agreement | Non-commercial research only; no weight redistribution; attribution notice on distribution; restrictions on commercial distribution of data produced by the software |
| `Qwen/Qwen2.5-1.5B-Instruct` | Apache-2.0 | Attribution |
| `roberta-large` | MIT | Attribution |
| MarkLLM | Apache-2.0 at the pinned commit `0a4fe8c` | Include the licence and NOTICE; state modifications; the PyPI metadata says MIT, and the repository licence governs |
| `google-deepmind/synthid-text` | Apache-2.0, research-only, explicitly not production | Not used; cite only |

### 4.4 Hosted-provider checklist

Before the first paid call and at each gate:

- [ ] Re-read the terms and privacy policy; update the version and date above.
- [ ] Pin the exact model snapshot in `configs/attackers.yaml` and the run
      manifest.
- [ ] Confirm the training opt-out and the data-retention setting.
- [ ] Disable thinking mode and any feature that changes output length or cost.
- [ ] Confirm that no prompt contains personal, confidential, or third-party
      restricted text.
- [ ] Confirm the per-run spend cap and the stop rule.
- [ ] Record the provider's current price, not the planning estimate.

## 5. Data protection and privacy

| Data | Content | Storage | Release |
| --- | --- | --- | --- |
| Prompts | Self-authored and public benchmark tasks | Local, `data/` | Self-authored only, under CC BY 4.0; benchmark text is loaded, not redistributed |
| Generated documents | Model output from OPT and Qwen | Local, `data/` | Not released |
| Attacked documents | Transformed generated text | Local, `data/` | Not released |
| Metric scores and results | Aggregate and per-document scores | Local, `results/` | Aggregate results released under CC BY 4.0 |
| API metadata | Model ID, timestamps, token counts, cost | Local run manifests | Released with the artifact |
| Account data | Email and billing for the API accounts | Provider-side | Not collected by the study |

No personal data is processed in the prompts or outputs. No special-category
data is processed. If a prompt source is later found to contain personal data
(for example, forum text), that source is excluded rather than redacted.

DeepSeek processes account data in the PRC. No study content beyond prompts and
generated documents is sent. Anthropic does not retain API prompts or outputs by
default; Covered Models require 30-day retention, and a Zero Data Retention
arrangement is available by agreement. The study keeps a local copy of the
results and does not rely on provider-side retention.

## 6. Third-party licences and attribution

| Component | Licence | Obligation or issue |
| --- | --- | --- |
| MarkLLM | Apache-2.0 | Include the licence and NOTICE; state modifications |
| MarkMyWords | Apache-2.0 code | Bundled task text includes third-party Codewars kata; the data is not covered by the repository licence and is not redistributed |
| `watermarks-remover` | MIT | Credited in `NOTICE` |
| `facebook/opt-1.3b` | OPT-175B License Agreement | Non-commercial research only; attribution notice; no weight redistribution; no commercial redistribution of data produced by the software |
| `Qwen/Qwen2.5-1.5B-Instruct` | Apache-2.0 | Attribution |
| `roberta-large` | MIT | Attribution |
| BERTScore | MIT | Attribution |
| COMET | Apache-2.0 | Attribution; model `wmt22-comet-da` is Apache-2.0 |
| BLEURT | Apache-2.0 | Attribution |
| **MAUVE** | **GPLv3** | **Not importable into the MIT core.** Kept as an optional `metrics-gpl` extra and invoked as a separate process |
| sentence-transformers | Apache-2.0 | Attribution |
| PyTorch | BSD-3-Clause | Attribution |
| Paper text and figures | CC BY 4.0 | Already in `LICENSE-paper` |

**MAUVE boundary (E2).** The upstream repository and the PyPI package are
GPLv3. Importing MAUVE into an MIT module would make the combined work GPLv3.
The package therefore keeps `mauve-text` out of the `metrics` extra, puts it in
`metrics-gpl`, and the runner calls a separate script as a subprocess. The core
install, the tests that do not need metrics, and the MIT licence are unaffected.
`NOTICE` records the boundary. The W2.7 implementation must keep the subprocess
boundary; a direct `import mauve` in `efface/` is a licence defect.

**OPT boundary.** `facebook/opt-1.3b` is licensed for non-commercial research.
The artifact does not redistribute the weights, and it does not relicense
OPT-derived text. The released result files contain aggregate metrics, not the
documents. If an example document is ever released, it carries the OPT-175B
notice and the AI-generated label.

**Prompt data.** Self-authored prompts are released under CC BY 4.0. The
MarkMyWords task text is third-party content; the manifest records the upstream
commit, the loader, and checksums. No prompt text from that source is
redistributed.

**Artifact licence split.** Code is MIT. The paper is CC BY 4.0. Aggregate
result JSON is CC BY 4.0. No OPT-derived text, no attacked corpus, and no model
weights are released.

## 7. Responsible disclosure

The study measures a known property of a research implementation. It does not
find a code-execution vulnerability, a key leak, or an unexpected bypass in the
implementation under test. The notice is a courtesy, not a security embargo.

**Recipients and channels:**

| Recipient | Why | Channel |
| --- | --- | --- |
| MarkLLM maintainers | The implementation under test | Lijie Wen `wenlj@tsinghua.edu.cn` (corresponding author); Aiwei Liu `liuaw20@mails.tsinghua.edu.cn`; GitHub `THU-BPM/MarkLLM` issue or private security advisory |
| Google DeepMind SynthID team | The scheme family; production detector not tested | `security@google.com`; Google Bug Hunters AI VRP at `https://bughunters.google.com/` |
| Anthropic | Claude's deployed mark uses the same scheme family | `usersafety@anthropic.com`; watermark detection API interest form |

**Timeline.** Notify at least ten days before posting, matching `PLAN.md` W5.8.
Follow up after five business days if there is no acknowledgement. Grant up to
90 days if a maintainer asks for more time. If a recipient confirms in writing
that it has no objection, the preprint may post earlier. The ten-day floor is a
minimum, not a target.

**Notice content:**

- the study's scope and the detector commit (`0a4fe8c`);
- the tactic classes that remove the mark and the measured preservation cost;
- the affected configurations;
- no exploit code and no attacked corpus;
- an offer to share the draft;
- a request to confirm any factual error or objection.

**Log.** Every contact is recorded in `docs/disclosure-log.md` with date,
recipient, channel, message reference, response, and window end. No contact has
been sent at the time of writing.

## 8. Conflicts of interest and funding

The author maintains `watermarks-remover` (MIT), a separate tool and HTTP
service that removes provenance marks from content its users own. EFFACE reuses
that project's strategy parser, document split, rank-based AUROC, Pareto
frontier, and cost accounting, as recorded in `NOTICE`. The tool is public.

This is a competing interest and is disclosed in the paper and the README.
EFFACE itself ships no service and no hosted endpoint; the study reports
measurement, not a deployed capability.

No funding, sponsorship, or in-kind support was received from a provider,
vendor, or standards body. API spend is self-funded. The author has no
affiliation with MarkLLM, Google DeepMind, or Anthropic.

## 9. Human subjects and research integrity

**Human subjects.** None. The human-rating component was dropped (decision D3),
so no ethics approval is required. The paper and the README state that the
ratings were dropped because a rating study was out of scope. The Appendix A
rating protocol is deleted.

**Preregistration.** `PREREGISTRATION.md` was frozen on 2026-11-17 before any
result existed. Deviations, including any τ revision after the pilot, are dated
in `PREREGISTRATION.md` and `docs/decisions.md`.

**Detector framing.** The detector is MarkLLM's SynthID reimplementation with
its own keying. The paper never claims production SynthID behaviour. The
limitations section states the same-config caveat.

**Traceability.** Every number in the paper is generated from a result file.
The claims audit in Week 4 traces each abstract and introduction sentence to a
table or figure. The artifact records the git SHA, MarkLLM commit, HF revisions,
API model IDs, seeds, timings, and cost.

**Release integrity.** The artifact tag, DOI, and reproduction commands are
checked before posting. `NOTICE` and the licence split are part of the release
checklist.

## 10. Compliance checklist

**Before the first paid API call:**

- [ ] `docs/ethics.md` approved (this file).
- [ ] Provider terms, privacy policy, and prices re-read and recorded.
- [ ] Model snapshots pinned; thinking mode disabled for DeepSeek.
- [ ] Training opt-out and retention setting confirmed.
- [ ] No personal, confidential, or third-party restricted text in prompts.
- [ ] Spend cap and stop rule set.
- [ ] `NOTICE`, `pyproject.toml`, and `configs/metrics.yaml` match the licence
      record.

**Before the pilot:**

- [ ] Prompt manifest with source, licence, loader, checksums, and split hash.
- [ ] MarkMyWords data loaded, not redistributed.
- [ ] MAUVE subprocess boundary documented and enforced.
- [ ] Data-protection review of the prompt set.

**Before the main runs:**

- [ ] Gate G2 passed; τ revision, if any, recorded.
- [ ] Terms re-checked.
- [ ] Attack catalogue matches the code one-to-one.
- [ ] Per-run manifests complete.

**Before the artifact release:**

- [ ] Competing-interest statement in the paper and README.
- [ ] `NOTICE` correct: MAUVE GPLv3, OPT attribution, MarkMyWords caveat.
- [ ] No attacked corpus, weights, or service in the artifact.
- [ ] Responsible-use notice in the README.
- [ ] DOI resolves; reproduction commands run.

**Before the arXiv submission:**

- [ ] Disclosure notice sent at least ten days earlier; log complete.
- [ ] Paper §9 consistent with this file.
- [ ] Metadata, licence, categories, and AI-use statement set.
- [ ] Claims audit closed.

## 11. Decision log

| ID | Date | Decision | Rationale | Review |
| --- | --- | --- | --- | --- |
| E1 | 2026-11-17 | Proceed with the DeepSeek hosted API for the search, with the §4.1 mitigations | Academic research is expressly permitted; the label clause concerns DeepSeek's own labels; no outputs are published; the residual §3.6(2) ambiguity is accepted with a fallback | At G2 and before release |
| E2 | 2026-11-17 | Keep MAUVE as an optional GPLv3 extra invoked as a separate process | Preserves the preregistered Tier A metric without relicensing the MIT core | At W2.7 and before release |
| E3 | 2026-11-17 | Ten-day disclosure floor, with follow-up and extensions | Matches `PLAN.md` W5.8; the finding is a design trade-off, not a vulnerability | Before posting |
| E4 | 2026-11-17 | Disclose the prior removal tool in the paper and README | It is a competing interest and the code is reused | Done in this change |
| E5 | 2026-11-17 | Load MarkMyWords task text; do not redistribute it | The repository licence covers the code, and the bundled text is third-party | At W2.10 |
| E6 | 2026-11-17 | Release code, configs, and aggregate results only | Measurement and reproducibility without releasing an attacked corpus or a service | Before release |

## 12. Sources

All accessed 2026-11-17.

- DeepSeek Terms of Use, last updated 2026-03-27:
  `https://cdn.deepseek.com/policies/en-UK/deepseek-terms-of-use.html`
- DeepSeek Open Platform Terms of Service, effective 2026-04-29:
  `https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html`
- DeepSeek Privacy Policy, last updated 2026-02-10:
  `https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html`
- DeepSeek API pricing and model list:
  `https://api-docs.deepseek.com/quick_start/pricing`
- Anthropic Usage Policy, effective 2026-11-12:
  `https://www.anthropic.com/legal/aup`
- Anthropic Commercial Terms of Service:
  `https://www.anthropic.com/legal/commercial-terms`
- Anthropic text watermark explainer, updated 2026-09-01:
  `https://www.anthropic.com/news/claude-text-watermark`
- Anthropic data retention:
  `https://platform.claude.com/docs/en/manage-claude/api-and-data-retention`
- Anthropic model pricing:
  `https://platform.claude.com/docs/en/about-claude/pricing`
- Anthropic supported countries:
  `https://www.anthropic.com/supported-countries`
- EU AI Act Article 50:
  `https://artificialintelligenceact.eu/article/50/`
- EU Code of Practice on Transparency of AI-generated Content:
  `https://digital-strategy.ec.europa.eu/en/news/strong-backing-code-practice-transparency-ai-generated-content`
- MarkLLM repository and licence:
  `https://github.com/THU-BPM/MarkLLM`
- MarkMyWords repository:
  `https://github.com/wagner-group/MarkMyWords`
- OPT-175B License Agreement:
  `https://huggingface.co/facebook/opt-1.3b/raw/main/LICENSE.md`
- Qwen2.5-1.5B-Instruct model card:
  `https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct`
- MAUVE repository licence:
  `https://github.com/krishnap25/mauve/blob/main/LICENSE`
- SynthID-Text reference implementation:
  `https://github.com/google-deepmind/synthid-text`
- Google security reporting:
  `https://www.google.com/corporate/security.html`
- Google Bug Hunters:
  `https://bughunters.google.com/`
