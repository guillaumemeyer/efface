"""Model-backed tactics.

Every tactic takes a ``ChatModel`` and asks for the transformed text. The
provider is responsible for retries; the tactic is responsible for a prompt
that carries the intensity and for returning the model's text unchanged apart
from whitespace trimming.

Attribution: prompt structure follows the rewrite passes in
``watermarks-remover`` (MIT) and the tactics surveyed in MarkMyWords and the
cross-lingual watermark study; the operational differences are listed in
``docs/attack-catalogue.md``.
"""

from __future__ import annotations

import json
import re
from typing import Protocol, runtime_checkable

from efface.attacks.base import register
from efface.attacks.prompts import PROMPTS, intensity_clause


@runtime_checkable
class ChatModel(Protocol):
    """A text completion provider."""

    def complete(self, prompt: str, *, seed: int = 0) -> str: ...


def _text_only(reply: str) -> str:
    return reply.strip()


class _ModelAttack:
    kind = "rewrite_ratio"
    prompt_name = ""

    def __init__(self, model: ChatModel) -> None:
        self.model = model

    def _render(self, text: str, intensity: float) -> str:
        return PROMPTS[self.prompt_name].format(
            text=text, intensity=intensity_clause(self.kind, intensity)
        )

    def apply(self, text: str, *, intensity: float = 1.0, seed: int = 0) -> str:
        if not text.strip():
            return text
        return _text_only(self.model.complete(self._render(text, intensity), seed=seed))


@register
class InstructionParaphrase(_ModelAttack):
    name = "instruction_paraphrase"
    default_intensity = 0.7
    prompt_name = "instruction_paraphrase"


@register
class DiscourseParaphrase(_ModelAttack):
    name = "discourse_paraphrase"
    default_intensity = 0.7
    prompt_name = "discourse_paraphrase"


@register
class DocumentRewrite(_ModelAttack):
    name = "document_rewrite"
    default_intensity = 0.8
    kind = "rewrite_strength"
    prompt_name = "document_rewrite"


@register
class Regeneration(_ModelAttack):
    name = "regeneration"
    default_intensity = 1.0
    kind = "rewrite_strength"
    prompt_name = "regeneration"


class _Translation:
    """Shared translation plumbing for the pivot tactics."""

    def __init__(self, model: ChatModel) -> None:
        self.model = model

    def _translate(self, text: str, language: str, seed: int) -> str:
        prompt = PROMPTS["to_pivot"].format(language=language, text=text)
        return _text_only(self.model.complete(prompt, seed=seed))


@register
class BacktranslateSingle(_Translation):
    name = "backtranslate_single"
    default_intensity = 1.0

    def __init__(self, model: ChatModel, pivot: str = "French") -> None:
        super().__init__(model)
        self.pivot = pivot

    def apply(self, text: str, *, intensity: float = 1.0, seed: int = 0) -> str:
        if not text.strip():
            return text
        middle = self._translate(text, self.pivot, seed)
        return self._translate(middle, "English", seed)


@register
class BacktranslateMulti(_Translation):
    name = "backtranslate_multi"
    default_intensity = 1.0

    def __init__(self, model: ChatModel, pivots: tuple[str, ...] = ("French", "German")) -> None:
        super().__init__(model)
        self.pivots = pivots

    def apply(self, text: str, *, intensity: float = 1.0, seed: int = 0) -> str:
        if not text.strip():
            return text
        current = text
        for language in self.pivots:
            current = self._translate(current, language, seed)
        return self._translate(current, "English", seed)


@register
class CrosslingualGeneration(_Translation):
    name = "crosslingual_generation"
    default_intensity = 1.0

    def __init__(self, model: ChatModel, pivot: str = "French") -> None:
        super().__init__(model)
        self.pivot = pivot

    def apply(self, text: str, *, intensity: float = 1.0, seed: int = 0) -> str:
        if not text.strip():
            return text
        translated = self._translate(text, self.pivot, seed)
        prompt = PROMPTS["rewrite_in_pivot"].format(
            text=translated,
            language=self.pivot,
            intensity=intensity_clause("rewrite_ratio", intensity),
        )
        rewritten = _text_only(self.model.complete(prompt, seed=seed))
        return self._translate(rewritten, "English", seed)


_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]+")


@register
class SynonymSubstitution:
    """Replace a fraction of content words with synonyms from the model.

    Operational difference from Three Bricks: the substitution candidates come
    from a prompted model rather than a masked-language-model distribution, and
    the fraction is applied to distinct word types drawn with a seeded RNG.
    """

    name = "synonym_substitution"
    default_intensity = 0.2

    def __init__(self, model: ChatModel, stopwords: frozenset[str] | None = None) -> None:
        self.model = model
        self.stopwords = stopwords or _STOPWORDS

    def apply(self, text: str, *, intensity: float = 0.2, seed: int = 0) -> str:
        if not text.strip():
            return text
        import random

        words = [
            word
            for word in dict.fromkeys(_WORD_RE.findall(text))
            if word.lower() not in self.stopwords
        ]
        if not words:
            return text
        count = max(1, round(len(words) * intensity))
        chosen = sorted(random.Random(seed).sample(words, min(count, len(words))), key=text.find)
        prompt = PROMPTS["synonyms"].format(text=text, words=", ".join(chosen))
        reply = _text_only(self.model.complete(prompt, seed=seed))
        substitutions = _parse_synonyms(reply)
        result = text
        for word in chosen:
            replacement = substitutions.get(word)
            if replacement and replacement.lower() != word.lower():
                result = re.sub(rf"\b{re.escape(word)}\b", replacement, result)
        return result


def _parse_synonyms(reply: str) -> dict[str, str]:
    try:
        data = json.loads(reply)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(key): str(value) for key, value in data.items()}


_STOPWORDS = frozenset(
    """
    a an the and or but if while of to in on at by for with from as is are was
    were be been being it its this that these those he she they we you i his
    her their our your my not no do does did have has had will would can could
    may might must shall should than then so such into over under about after
    before between during through there here which who whom whose what when
    where why how all any both each few more most other some only own same too
    very just also
    """.split()
)
