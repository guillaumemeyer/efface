import pytest

from efface.search.strategy import (
    CONTROL_TACTIC,
    REMOVAL_TACTICS,
    normalize_strategy,
    parse_strategy,
    strategy_key,
    strategy_slug,
)


def test_parse_single_step():
    assert parse_strategy("typo_noise@0.05") == (("typo_noise", 0.05),)


def test_parse_ordered_chain():
    chain = parse_strategy("instruction_paraphrase@0.7,typo_noise@0.05")
    assert chain == (("instruction_paraphrase", 0.7), ("typo_noise", 0.05))
    assert strategy_slug(chain) == "instruction_paraphrase@0.7+typo_noise@0.05"


def test_parse_rejects_unknown_tactic():
    with pytest.raises(ValueError, match="unknown tactic"):
        parse_strategy("teleport@1.0")


def test_parse_rejects_four_steps():
    with pytest.raises(ValueError, match="maximum"):
        parse_strategy("typo_noise@0.1,typo_noise@0.1,typo_noise@0.1,typo_noise@0.1")


def test_parse_rejects_bad_intensity():
    with pytest.raises(ValueError, match="intensity"):
        parse_strategy("typo_noise@0")
    with pytest.raises(ValueError, match="intensity"):
        parse_strategy("typo_noise@1.5")


def test_control_is_not_chainable_by_default():
    with pytest.raises(ValueError, match="control"):
        parse_strategy(f"{CONTROL_TACTIC}@1.0")
    assert parse_strategy(f"{CONTROL_TACTIC}@1.0", allow_control=True)


def test_catalogue_has_twelve_removal_tactics():
    assert len(REMOVAL_TACTICS) == 12
    assert len(set(REMOVAL_TACTICS)) == 12


def test_key_is_normalised():
    a = strategy_key((("typo_noise", 0.05000001),))
    b = strategy_key((("typo_noise", 0.05),))
    assert a == b == normalize_strategy((("typo_noise", 0.05),))
