"""Tactics that need no model: style, edits, noise, and the Unicode control.

Each is deterministic given ``seed`` and reports the fraction it changed on the
output, so the achieved edit rate can be checked against the requested
intensity. The style rules follow the deterministic subset of the humanizer
pass in ``watermarks-remover`` (MIT): the edits below are always safe, while
voice and rhythm are left to the model-backed paraphrase.
"""

from __future__ import annotations

import random
import re
import unicodedata

from efface.attacks.base import register

_PHRASE_SWAPS: tuple[tuple[str, str], ...] = (
    (r"\bin order to\b", "to"),
    (r"\bdue to the fact that\b", "because"),
    (r"\bat this point in time\b", "now"),
    (r"\bin the event that\b", "if"),
    (r"\bhas the ability to\b", "can"),
    (r"\bhave the ability to\b", "can"),
    (r"\bit is important to note that\b", "note that"),
    (r"\bit is worth noting that\b", "note that"),
    (r"\bdelve into\b", "explore"),
    (r"\bdelve[sd]? into\b", "explores"),
)

_WORD_SWAPS = {
    "utilize": "use",
    "utilizes": "uses",
    "utilized": "used",
    "utilizing": "using",
}


def _match_case(matched: str, replacement: str) -> str:
    if matched.isupper():
        return replacement.upper()
    return replacement[:1].upper() + replacement[1:] if matched[:1].isupper() else replacement


@register
class StyleNormalisation:
    """Normalise surface style: quotes, dashes, contractions, filler phrases.

    Operational difference from MarkMyWords' style perturbation: the rule set
    is fixed and deterministic, and it targets the register markers that a
    humaniser would remove rather than random character noise.
    """

    name = "style_normalisation"
    default_intensity = 1.0

    def apply(self, text: str, *, intensity: float = 1.0, seed: int = 0) -> str:
        result = text
        result = result.replace("\u2018", "'").replace("\u2019", "'")
        result = result.replace("\u201c", '"').replace("\u201d", '"')
        result = re.sub(
            r"(?<!\d)\s*[\u2014\u2013]\s*(?!\d)",
            ", ",
            result,
        )
        for pattern, replacement in _PHRASE_SWAPS:
            result = re.sub(
                pattern,
                lambda m, r=replacement: _match_case(m.group(0), r),
                result,
                flags=re.IGNORECASE,
            )
        for word, replacement in _WORD_SWAPS.items():
            result = re.sub(
                rf"\b{word}\b",
                lambda m, r=replacement: _match_case(m.group(0), r),
                result,
                flags=re.IGNORECASE,
            )
        result = re.sub(r"[ \t]{2,}", " ", result)
        return result


_FILLER_WORDS = ("the", "a", "of", "and", "to", "in", "that", "it", "is", "was")


@register
class RandomEdits:
    """Swap, insert, or delete a fraction of word positions.

    Operational difference from MarkMyWords' random perturbation: the three
    edit types are chosen with equal probability from a seeded RNG, and the
    fraction is of whitespace-delimited tokens.
    """

    name = "random_edits"
    default_intensity = 0.1

    def apply(self, text: str, *, intensity: float = 0.1, seed: int = 0) -> str:
        tokens = text.split()
        if len(tokens) < 2:
            return text
        rng = random.Random(seed)
        count = max(1, round(len(tokens) * intensity))
        positions = rng.sample(range(len(tokens)), min(count, len(tokens)))
        for position in sorted(positions, reverse=True):
            operation = rng.choice(("swap", "insert", "delete"))
            if operation == "delete" and len(tokens) > 1:
                del tokens[position]
            elif operation == "insert":
                tokens.insert(position, rng.choice(_FILLER_WORDS))
            elif position + 1 < len(tokens):
                tokens[position], tokens[position + 1] = tokens[position + 1], tokens[position]
        return " ".join(tokens)


_NEIGHBOURS = {
    "a": "s",
    "e": "r",
    "i": "o",
    "o": "p",
    "u": "i",
    "s": "a",
    "t": "r",
    "n": "m",
}


@register
class TypoNoise:
    """Character-level noise: transpose, delete, or replace at a fixed rate.

    Operational difference from MarkMyWords: the error rate is applied per
    character over the whole document, so it scales with length in the same way
    as a typing model rather than per word.
    """

    name = "typo_noise"
    default_intensity = 0.05

    def apply(self, text: str, *, intensity: float = 0.05, seed: int = 0) -> str:
        if not text:
            return text
        rng = random.Random(seed)
        characters = list(text)
        count = max(1, round(len(characters) * intensity))
        positions = rng.sample(range(len(characters)), min(count, len(characters)))
        for position in sorted(positions, reverse=True):
            operation = rng.choice(("transpose", "delete", "replace"))
            if operation == "delete" and len(characters) > 1:
                del characters[position]
            elif operation == "transpose" and position + 1 < len(characters):
                characters[position], characters[position + 1] = (
                    characters[position + 1],
                    characters[position],
                )
            else:
                character = characters[position]
                characters[position] = _NEIGHBOURS.get(character.lower(), character)
        return "".join(characters)


@register
class UnicodeScrub:
    """Remove invisible characters and normalise exotic spaces.

    This is the control row. A sampling-time mark lives in token choice, so
    this scrub should leave the detector score unchanged; a change means the
    measurement is picking up an edit-based carrier.
    """

    name = "unicode_scrub"
    default_intensity = 1.0

    def apply(self, text: str, *, intensity: float = 1.0, seed: int = 0) -> str:
        kept = []
        for character in text:
            category = unicodedata.category(character)
            if category == "Cf":
                continue
            if character.isspace():
                kept.append(" ")
                continue
            kept.append(character)
        result = "".join(kept)
        result = re.sub(r" {2,}", " ", result)
        return result
