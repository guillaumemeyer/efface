import json

import pytest

from efface.attacks import LOCAL, MODEL_BACKED, available, build, get
from efface.attacks.local import RandomEdits, StyleNormalisation, TypoNoise, UnicodeScrub
from efface.attacks.mlm import MaskedLMInfill
from efface.attacks.model import (
    BacktranslateMulti,
    BacktranslateSingle,
    CrosslingualGeneration,
    SynonymSubstitution,
)
from efface.search.strategy import REMOVAL_TACTICS

SAMPLE = (
    "In order to reduce costs, the city will utilize a new transit plan. "
    "It is important to note that the vote passed 7 to 4."
)


class FakeChat:
    """Records prompts and returns a deterministic transformation."""

    def __init__(self, reply=None):
        self.prompts = []
        self.seeds = []
        self.reply = reply

    def complete(self, prompt: str, *, seed: int = 0) -> str:
        self.prompts.append(prompt)
        self.seeds.append(seed)
        if self.reply is not None:
            return self.reply(prompt) if callable(self.reply) else self.reply
        return prompt.split("PASSAGE:\n", 1)[-1].split("\n\n", 1)[0]


class FakeFiller:
    def __init__(self):
        self.calls = []

    def fill(self, texts):
        self.calls.append(list(texts))
        return [text.replace("<mask>", "FILL") for text in texts]


def test_registry_covers_the_catalogue():
    assert len(available()) == 13
    assert set(REMOVAL_TACTICS) | {"unicode_scrub"} == set(available())
    assert get("typo_noise") is TypoNoise


def test_every_tactic_has_a_default_intensity():
    for name in available():
        tactic = build(
            name,
            chat=FakeChat(),
            filler=FakeFiller(),
        )
        assert 0.0 < tactic.default_intensity <= 1.0


def test_style_normalisation_rewrites_filler_and_dashes():
    tactic = StyleNormalisation()
    out = tactic.apply(SAMPLE + " The plan — approved today — starts in May.")
    assert "In order to" not in out
    assert "utilize" not in out
    assert "It is important to note that" not in out
    assert "\u2014" not in out
    assert "7 to 4" in out


def test_style_normalisation_keeps_numeric_ranges():
    out = StyleNormalisation().apply("The years 2019–2020 were busy.")
    assert "2019–2020" in out


def test_unicode_scrub_removes_invisible_characters():
    text = "Hello\u200b world\u200f with\ufeff marks\u00a0here."
    out = UnicodeScrub().apply(text)
    assert out == "Hello world with marks here."


def test_random_edits_is_deterministic_and_seeded():
    first = RandomEdits().apply(SAMPLE, intensity=0.3, seed=7)
    second = RandomEdits().apply(SAMPLE, intensity=0.3, seed=7)
    other = RandomEdits().apply(SAMPLE, intensity=0.3, seed=8)
    assert first == second
    assert first != other
    assert first.split() != SAMPLE.split()


def test_typo_noise_is_deterministic_and_changes_text():
    first = TypoNoise().apply(SAMPLE, intensity=0.05, seed=1)
    assert first == TypoNoise().apply(SAMPLE, intensity=0.05, seed=1)
    assert first != SAMPLE
    assert len(first) > 0


def test_mask_fills_one_span_per_call():
    filler = FakeFiller()
    out = MaskedLMInfill(filler).apply("one two three four five", intensity=0.4, seed=0)
    assert len(filler.calls) == 2
    assert all(call[0].count("<mask>") == 1 for call in filler.calls)
    assert "FILL" in out


def test_model_paraphrase_uses_the_passage_and_intensity():
    chat = FakeChat()
    tactic = build("instruction_paraphrase", chat=chat)
    out = tactic.apply(SAMPLE, intensity=0.6, seed=3)
    assert chat.prompts and SAMPLE in chat.prompts[0]
    assert "60%" in chat.prompts[0]
    assert out == SAMPLE.strip()
    assert chat.seeds == [3]


def test_backtranslate_single_goes_pivot_then_english():
    chat = FakeChat()
    BacktranslateSingle(chat).apply("Hello there.", seed=0)
    assert "into French" in chat.prompts[0]
    assert "into English" in chat.prompts[1]


def test_backtranslate_multi_visits_each_pivot():
    chat = FakeChat(reply="TGT")
    BacktranslateMulti(chat).apply("Hello there.", seed=0)
    assert [("into French" in p) for p in chat.prompts] == [True, False, False]
    assert [("into German" in p) for p in chat.prompts] == [False, True, False]
    assert [("into English" in p) for p in chat.prompts] == [False, False, True]


def test_crosslingual_generation_translates_rewrites_translates():
    chat = FakeChat(lambda prompt: "REWRITTEN" if "Rewrite this French" in prompt else "X")
    out = CrosslingualGeneration(chat).apply("Hello.", seed=0)
    assert len(chat.prompts) == 3
    assert "Rewrite this French" in chat.prompts[1]
    assert out == "X"


def test_synonym_substitution_applies_the_model_mapping():
    def reply(prompt):
        words = prompt.split("WORDS: ", 1)[1]
        return json.dumps({word.strip(): word.strip() + "_SYN" for word in words.split(",")})

    chat = FakeChat(reply)
    out = SynonymSubstitution(chat).apply(
        "The council approved a transit plan.", intensity=0.5, seed=0
    )
    assert "_SYN" in out
    assert "The council" in out


@pytest.mark.parametrize("name", sorted(LOCAL))
def test_local_tactics_need_no_model(name):
    assert build(name).name == name


@pytest.mark.parametrize("name", sorted(MODEL_BACKED))
def test_model_tactics_need_a_model(name):
    with pytest.raises(ValueError):
        build(name)


def test_unknown_tactic_fails_loudly():
    with pytest.raises(KeyError):
        build("teleport")


def test_cli_attack_applies_a_chain(tmp_path):
    from efface.cli import main
    from efface.watermark import read_jsonl, write_jsonl

    source = tmp_path / "docs.jsonl"
    write_jsonl([{"doc_id": "d-k3", "key": 3, "text": SAMPLE}], source)
    output = tmp_path / "attacked.jsonl"
    code = main(
        [
            "attack",
            "--tactic",
            "style_normalisation",
            "--input",
            str(source),
            "--output",
            str(output),
        ]
    )
    assert code == 0
    record = list(read_jsonl(output))[0]
    assert record["chain"] == [
        {"tactic": "style_normalisation", "intensity": 1.0, "seed": 0}
    ]
    assert "utilize" not in record["text"]
    assert record["key"] == 3


def test_cli_attack_rejects_unknown_tactic(tmp_path, capsys):
    from efface.cli import main

    source = tmp_path / "docs.jsonl"
    source.write_text('{"doc_id": "d", "key": 3, "text": "x"}\n', encoding="utf-8")
    code = main(["attack", "--tactic", "teleport", "--input", str(source)])
    assert code == 2
    assert "unknown tactic" in capsys.readouterr().err
