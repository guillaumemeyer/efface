"""Command-line entry points.

Weeks 2 and 3 fill the run commands. ``smoke`` is live from Week 1 and is the
check used by CI.
"""

from __future__ import annotations

import argparse
import sys

from efface import __version__
from efface.evaluate import (
    auroc,
    clustered_rate,
    detection_check_pass,
    is_removed,
    paired_bootstrap_diff,
    removal_rate,
    tpr_at_fpr,
    wilson_interval,
)
from efface.evaluate.pareto import pareto_frontier
from efface.evaluate.splits import split_documents
from efface.search.strategy import parse_strategy, strategy_slug

COMMANDS = ("generate", "attack", "score", "run", "search", "report", "smoke")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="efface",
        description="Constrained search over meaning-preserving watermark removal chains.",
    )
    parser.add_argument("--version", action="version", version=f"efface {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in COMMANDS:
        command = sub.add_parser(name, help=f"{name} (see PLAN.md)")
        command.add_argument("--config", default=None)
        command.add_argument("--input", default=None)
        command.add_argument("--output", default=None)
        if name == "search":
            command.add_argument("--depth", type=int, default=3)
            command.add_argument("--beam", type=int, default=8)
        if name == "attack":
            command.add_argument("--tactic", default=None)
            command.add_argument("--intensity", type=float, default=1.0)
    return parser


def _smoke() -> int:
    checks = 0

    low, high = wilson_interval(50, 100)
    assert 0.40 < low < 0.41 and 0.59 < high < 0.60, (low, high)
    checks += 1

    rate = removal_rate([True] * 8 + [False] * 2)
    assert rate.n == 10 and rate.value == 0.8
    checks += 1

    assert is_removed(0.31) is True
    assert is_removed(0.01) is False
    assert clustered_rate([True, True, False], ["p1", "p2", "p3"], n_resamples=200).n == 3
    assert detection_check_pass([True] * 19 + [False]) is True
    checks += 1

    assert auroc([2.0, 3.0], [1.0]) == 1.0
    assert abs(auroc([1.0, 2.0], [2.0]) - 0.25) < 1e-12
    checks += 1

    assert tpr_at_fpr([99.0, 100.0, 50.0], list(map(float, range(100))), 0.01) == 2 / 3
    checks += 1

    observed, low, high, pvalue = paired_bootstrap_diff([1.0, 1.0], [1.0, 1.0], n_resamples=200)
    assert observed == 0.0 and low == high == 0.0 and pvalue == 1.0
    checks += 1

    assert pareto_frontier([(1.0, 1.0), (0.5, 0.5), (1.0, 0.9)]) == [0]
    checks += 1

    search, holdout = split_documents([f"doc-{i}" for i in range(10)], fraction=0.6, seed=7)
    assert (len(search), len(holdout)) == (6, 4)
    assert split_documents([f"doc-{i}" for i in range(10)], fraction=0.6, seed=7)[0] == search
    checks += 1

    chain = parse_strategy("instruction_paraphrase@0.7,typo_noise@0.05")
    assert strategy_slug(chain) == "instruction_paraphrase@0.7+typo_noise@0.05"
    checks += 1

    print(f"smoke: ok ({checks} checks)")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "smoke":
        return _smoke()
    print(f"{args.command}: not implemented yet (planned in PLAN.md)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
