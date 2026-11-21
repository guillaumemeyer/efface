"""Prompt templates for the model-backed tactics.

Each template asks for the text only. The intensity clause is a request, not a
guarantee: the achieved edit rate is measured and reported, and the model may
depart from the target.
"""

from __future__ import annotations

PROMPTS: dict[str, str] = {
    "instruction_paraphrase": (
        "Rewrite the passage so that it says the same thing in different words. "
        "Keep every entity, number, and claim. {intensity} "
        "Return only the rewritten passage.\n\nPASSAGE:\n{text}"
    ),
    "discourse_paraphrase": (
        "Rewrite the passage as a careful editor would, changing sentence "
        "boundaries and paragraph order where that keeps the meaning. Keep "
        "every entity, number, and claim. {intensity} "
        "Return only the rewritten passage.\n\nPASSAGE:\n{text}"
    ),
    "document_rewrite": (
        "Rewrite this passage from scratch. Preserve its claims, entities, and "
        "numbers, but choose new structure and wording throughout. {intensity} "
        "Return only the rewritten passage.\n\nPASSAGE:\n{text}"
    ),
    "regeneration": (
        "Read the passage, list its claims to yourself, then write a new "
        "passage from those claims alone. Keep every entity and number. "
        "Return only the new passage.\n\nPASSAGE:\n{text}"
    ),
    "to_pivot": "Translate the passage into {language}. Return only the translation.\n\n{text}",
    "from_pivot": (
        "Translate the passage into {language}. Return only the translation.\n\n{text}"
    ),
    "rewrite_in_pivot": (
        "Rewrite this {language} passage so that it says the same thing in "
        "different words. Keep every entity, number, and claim. {intensity} "
        "Return only the rewritten passage.\n\n{text}"
    ),
    "synonyms": (
        "For each word in the list, give one synonym that fits the passage. "
        "Return a JSON object mapping each word to its synonym, and nothing "
        "else.\n\nPASSAGE:\n{text}\n\nWORDS: {words}"
    ),
}


def intensity_clause(kind: str, level: float) -> str:
    """How hard to push, in the tactic's own unit."""
    if not 0.0 < level <= 1.0:
        raise ValueError("intensity must lie in (0, 1]")
    if kind == "rewrite_ratio":
        return f"Change roughly {round(level * 100)}% of the wording."
    if kind == "rewrite_strength":
        return f"Rewrite at about {round(level * 100)}% of the way to a fresh draft."
    raise ValueError(f"unknown intensity kind {kind!r}")
