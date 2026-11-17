#!/usr/bin/env python3
"""Measure MarkLLM SynthID generation and detection on this machine.

This is the Week 1 throughput spike. It loads one open-weight model, generates
one watermarked document under one key, and times the detector on the result.
The numbers set the scope for the main sweep.

Usage:
    python scripts/spike_mps.py --markllm-dir ~/MarkLLM --model facebook/opt-1.3b
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

PROMPT = (
    "Write a 300-word news report about a city council approving a new "
    "public transit plan. Include the vote, the cost, and two quotes."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--markllm-dir", default="~/MarkLLM")
    parser.add_argument("--model", default="facebook/opt-1.3b")
    parser.add_argument("--device", default=None, choices=["mps", "cpu", "cuda"])
    parser.add_argument("--max-new-tokens", type=int, default=300)
    parser.add_argument("--prompt", default=PROMPT)
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    markllm = Path(args.markllm_dir).expanduser().resolve()
    if not (markllm / "watermark" / "synthid" / "synthid.py").exists():
        raise SystemExit(f"MarkLLM checkout not found at {markllm}")

    sys.path.insert(0, str(markllm))

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from utils.transformers_config import TransformersConfig
    from watermark.synthid.synthid import SynthID

    device = args.device or ("mps" if torch.backends.mps.is_available() else "cpu")

    start = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model)
    model.to(device)
    model.eval()
    load_seconds = time.perf_counter() - start

    config = TransformersConfig(
        model=model,
        tokenizer=tokenizer,
        device=device,
        max_new_tokens=args.max_new_tokens,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )
    # MarkLLM's SynthID logits processor mishandles top_k > 0: it returns a
    # (batch, top_k) tensor where the caller expects (batch, vocab_size). Keep
    # top_k at its default of -1 so the full distribution is reweighted.
    config.temperature = 0.7
    watermark = SynthID(str(markllm / "config" / "SynthID.json"), config)

    start = time.perf_counter()
    text = watermark.generate_watermarked_text(args.prompt)
    generate_seconds = time.perf_counter() - start

    start = time.perf_counter()
    detection = watermark.detect_watermark(text, return_dict=True)
    detect_seconds = time.perf_counter() - start

    tokens = len(tokenizer(text)["input_ids"])
    peak_gb = None
    if device == "mps":
        peak_gb = torch.mps.driver_allocated_memory() / 1e9

    result = {
        "model": args.model,
        "device": device,
        "torch": torch.__version__,
        "load_seconds": round(load_seconds, 3),
        "generate_seconds": round(generate_seconds, 3),
        "detect_seconds": round(detect_seconds, 3),
        "tokens": tokens,
        "tokens_per_second": round(tokens / generate_seconds, 2),
        "peak_mps_gb": round(peak_gb, 2) if peak_gb is not None else None,
        "detection": detection,
        "prompt": args.prompt,
        "text_chars": len(text),
    }
    print(json.dumps(result, indent=2))
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
