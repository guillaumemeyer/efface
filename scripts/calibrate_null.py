#!/usr/bin/env python3
"""Fit the unwatermarked null for one generator row.

Generates unwatermarked documents with the row's model and decoding settings,
scores them under one key array, and fits the normal null used by
`efface.detect.NullModel`. Writes the fit and its diagnostics as JSON.

The preregistration requires at least 200 documents before the detection gate
is read; this script accepts fewer for a pilot and records the count.

Usage:
    python scripts/calibrate_null.py --row g1 --prompts data/prompts.jsonl \
      --seeds 20 --key 3 --output results/null-g1.json
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

from efface.config import load
from efface.detect import MarkLLMDetector, NullModel
from efface.watermark import MarkLLMBackend, read_jsonl
from efface.watermark.base import GenerationRequest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/generators.yaml")
    parser.add_argument("--row", default="g1")
    parser.add_argument("--markllm-dir", default="~/MarkLLM")
    parser.add_argument("--prompts", required=True)
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--key", type=int, default=3)
    parser.add_argument("--max-prompts", type=int, default=None)
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    row = load(args.config)["rows"][args.row]
    prompts = list(read_jsonl(args.prompts))
    if args.max_prompts:
        prompts = prompts[: args.max_prompts]

    backend = MarkLLMBackend(
        markllm_dir=args.markllm_dir,
        model=row["model"],
        revision=row.get("revision"),
        key_seed=int(row.get("key_seed", 20261117)),
    )
    detector = MarkLLMDetector(backend)

    samples: list[tuple[float, int]] = []
    for prompt in prompts:
        for seed in range(args.seeds):
            request = GenerationRequest(
                doc_id=f"null-{prompt['prompt_id']}-{seed}",
                prompt=prompt["prompt"],
                key=args.key,
                model=row["model"],
                scheme=row["scheme"],
                max_new_tokens=int(row.get("max_new_tokens", 400)),
                temperature=float(row.get("temperature", 0.7)),
                top_p=float(row.get("top_p", 0.9)),
                seed=seed,
                domain=str(prompt.get("domain", "")),
            )
            text = backend.generate_unwatermarked(
                request.prompt, key=args.key, seed=seed, request=request
            )
            score = detector.score(text, args.key)
            samples.append((score.score, score.n_eff))

    null = NullModel.fit(samples)
    scores = [score for score, _ in samples]
    analytic = NullModel.analytic()
    analytic_zs = [analytic.pvalue(score, n) for score, n in samples]
    # In-sample z uses the fit, so its sd is close to 1 by construction. The
    # split-half check is the diagnostic that can fail.
    even, odd = samples[::2], samples[1::2]
    held = NullModel.fit(even)
    holdout_zs = [
        (score - held.mean) / math.sqrt(held.variance_scale / n_eff) for score, n_eff in odd
    ]
    diagnostics = {
        "documents": len(samples),
        "key": args.key,
        "model": row["model"],
        "mean_score": statistics.mean(scores),
        "sd_score": statistics.pstdev(scores),
        "n_eff_min": min(n_eff for _, n_eff in samples),
        "n_eff_max": max(n_eff for _, n_eff in samples),
        "analytic_mean_p": statistics.mean(analytic_zs),
        "analytic_fraction_p_below_005": sum(1 for p in analytic_zs if p < 0.05) / len(analytic_zs),
        "holdout_documents": len(odd),
        "holdout_z_mean": statistics.mean(holdout_zs),
        "holdout_z_sd": statistics.pstdev(holdout_zs),
        "holdout_fraction_p_below_005": sum(
            1 for z in holdout_zs if 0.5 * math.erfc(z / math.sqrt(2)) < 0.05
        )
        / len(holdout_zs),
    }
    report = {"null": null.to_dict(), "diagnostics": diagnostics, "samples": samples}
    print(json.dumps(report, indent=2))
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
