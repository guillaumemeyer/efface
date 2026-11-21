"""Build a tactic from its name and the dependencies it needs."""

from __future__ import annotations

from typing import Any

from efface.attacks import (
    local,  # noqa: F401  (registers local tactics)
    mlm,
    model,
)
from efface.attacks.base import Attack

MODEL_BACKED = frozenset(
    {
        "instruction_paraphrase",
        "discourse_paraphrase",
        "document_rewrite",
        "regeneration",
        "backtranslate_single",
        "backtranslate_multi",
        "crosslingual_generation",
        "synonym_substitution",
    }
)
LOCAL = frozenset(
    {"style_normalisation", "random_edits", "typo_noise", "unicode_scrub"}
)


def needs_model(name: str) -> bool:
    return name in MODEL_BACKED


def build(
    name: str,
    *,
    chat: model.ChatModel | None = None,
    filler: mlm.Filler | None = None,
    settings: dict[str, Any] | None = None,
) -> Attack:
    """Return a tactic instance, or raise with what is missing.

    ``settings`` carries per-tactic extras such as ``pivot`` or ``pivots``.
    """
    settings = settings or {}
    if name in LOCAL:
        if name == "style_normalisation":
            return local.StyleNormalisation()
        if name == "random_edits":
            return local.RandomEdits()
        if name == "typo_noise":
            return local.TypoNoise()
        return local.UnicodeScrub()

    if name == "mlm_infill":
        if filler is None:
            raise ValueError("mlm_infill needs a filler")
        return mlm.MaskedLMInfill(filler)

    if name not in MODEL_BACKED:
        raise KeyError(f"unknown tactic {name!r}")
    if chat is None:
        raise ValueError(f"{name} needs a chat model")

    mapping = {
        "instruction_paraphrase": model.InstructionParaphrase,
        "discourse_paraphrase": model.DiscourseParaphrase,
        "document_rewrite": model.DocumentRewrite,
        "regeneration": model.Regeneration,
        "synonym_substitution": model.SynonymSubstitution,
    }
    if name in mapping:
        return mapping[name](chat)
    if name == "backtranslate_single":
        return model.BacktranslateSingle(chat, pivot=settings.get("pivot", "French"))
    if name == "backtranslate_multi":
        pivots = tuple(settings.get("pivots", ("French", "German")))
        return model.BacktranslateMulti(chat, pivots=pivots)
    return model.CrosslingualGeneration(chat, pivot=settings.get("pivot", "French"))
