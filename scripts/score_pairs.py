#!/usr/bin/env python3
"""Score a pair fixture with the preservation metrics.

Reads a JSON list of ``{id, source, candidate}`` and writes per-pair values,
``S``, and the aggregate. Used to record the fixture values the test checks and
to smoke-test the metric stack before a sweep.

Usage:
    python scripts/score_pairs.py --pairs tests/fixtures/metrics/pairs.json \
      --output results/metrics-fixture.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from efface.evaluate import BertScore, Comet, aggregate, below_floor_fraction, score_pairs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", required=True)
    parser.add_argument("--output", default=None)
    parser.add_argument("--tau", type=float, default=0.80)
    parser.add_argument("--bleurt", action="store_true", help="also run BLEURT if installed")
    parser.add_argument("--device", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = json.loads(Path(args.pairs).read_text(encoding="utf-8"))
    pairs = [(row["source"], row["candidate"]) for row in rows]
    metrics = [BertScore(device=args.device), Comet(device=args.device)]
    if args.bleurt:
        from efface.evaluate import Bleurt

        metrics.append(Bleurt(device=args.device))

    reports = score_pairs(pairs, metrics=metrics)
    summary = {
        "pairs": len(pairs),
        "tau": args.tau,
        "aggregate": aggregate(reports),
        "below_floor_fraction": below_floor_fraction(reports, args.tau),
        "documents": [
            {
                "id": row["id"],
                "S": report.composite,
                **report.reported,
            }
            for row, report in zip(rows, reports, strict=True)
        ],
    }
    print(json.dumps(summary, indent=2))
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
