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
        if name == "score":
            command.add_argument("--alpha", type=float, default=0.05)
            command.add_argument("--row", default="g1", help="generator row key")
            command.add_argument("--markllm-dir", default="~/MarkLLM")
            command.add_argument("--null", default=None, help="calibrated null JSON")
        if name == "generate":
            command.add_argument("--row", default="g1", help="generator row key")
            command.add_argument("--prompts", default=None, help="prompt JSONL")
            command.add_argument("--markllm-dir", default="~/MarkLLM")
            command.add_argument("--seed", type=int, default=0)
            command.add_argument("--limit", type=int, default=None)
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

    from efface.detect import NullModel, pvalue_from_score

    assert pvalue_from_score(0.55, 1000) < 0.05
    assert NullModel.fit([(0.49, 1000), (0.51, 1000)]).mean == 0.5
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


def _build_generator(row: dict, args: argparse.Namespace):
    """Factory kept separate so tests can substitute a fake backend."""
    from efface.watermark import MarkLLMBackend, WatermarkGenerator

    backend = MarkLLMBackend(
        markllm_dir=args.markllm_dir,
        model=row["model"],
        revision=row.get("revision"),
        key_seed=int(row.get("key_seed", 20261117)),
    )
    return WatermarkGenerator(backend)


def _generate(args: argparse.Namespace) -> int:
    from efface.config import load
    from efface.watermark import generate_corpus, read_jsonl, write_jsonl

    if not args.config or not args.prompts:
        print("generate needs --config and --prompts", file=sys.stderr)
        return 2
    config = load(args.config)
    try:
        row = config["rows"][args.row]
    except KeyError:
        print(f"unknown generator row {args.row!r}", file=sys.stderr)
        return 2

    prompts = list(read_jsonl(args.prompts))
    if args.limit is not None:
        prompts = prompts[: args.limit]
    if not prompts:
        print(f"no prompts in {args.prompts}", file=sys.stderr)
        return 2

    output = args.output or f"results/corpus-{args.row}.jsonl"
    count = write_jsonl(
        generate_corpus(
            prompts=prompts,
            row=row,
            generator=_build_generator(row, args),
            config_path=args.config,
            markllm_dir=args.markllm_dir,
            model_revision=row.get("revision"),
            seed=args.seed,
        ),
        output,
    )
    print(f"generate: wrote {count} records to {output}")
    return 0


def _build_detector(args: argparse.Namespace):
    """Factory kept separate so tests can substitute a fake detector."""
    from efface.config import load
    from efface.watermark import MarkLLMBackend

    config = load(args.config or "configs/generators.yaml")
    row = config["rows"][args.row]
    backend = MarkLLMBackend(
        markllm_dir=args.markllm_dir,
        model=row["model"],
        revision=row.get("revision"),
        key_seed=int(row.get("key_seed", 20261117)),
    )
    from efface.detect import MarkLLMDetector, NullModel

    null = None
    if getattr(args, "null", None):
        import json
        from pathlib import Path

        data = json.loads(Path(args.null).read_text(encoding="utf-8"))
        # Accept either the bare null or the calibration report that wraps it.
        null = NullModel.from_dict(data.get("null", data))
    return MarkLLMDetector(backend, null=null)


def _score(args: argparse.Namespace) -> int:
    from efface.evaluate import is_removed
    from efface.watermark import read_jsonl, write_jsonl

    if not args.input:
        print("score needs --input", file=sys.stderr)
        return 2
    detector = _build_detector(args)

    def results():
        for record in read_jsonl(args.input):
            score = detector.score(record["text"], int(record["key"]))
            yield {
                "doc_id": record["doc_id"],
                "prompt_id": record.get("prompt_id"),
                "domain": record.get("domain"),
                "key": score.key,
                "detector": score.detector,
                "score": score.score,
                "pvalue": score.pvalue,
                "n_eff": score.n_eff,
                "alpha": args.alpha,
                "removed": is_removed(score.pvalue, alpha=args.alpha),
                "manifest": record.get("manifest"),
            }

    output = args.output or "results/scores.jsonl"
    count = write_jsonl(results(), output)
    print(f"score: wrote {count} records to {output}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "smoke":
        return _smoke()
    if args.command == "generate":
        return _generate(args)
    if args.command == "score":
        return _score(args)
    print(f"{args.command}: not implemented yet (planned in PLAN.md)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
