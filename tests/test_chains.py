import pytest

from efface.attacks import build
from efface.chains import ChainExecutor, DiskCache, MemoryCache, cache_key, edit_rate
from efface.chains.cache import text_digest
from efface.search.strategy import parse_strategy


class CountingAttack:
    """Wraps a tactic and counts applications."""

    def __init__(self, inner, counter, name):
        self.inner = inner
        self.counter = counter
        self.name = name

    def apply(self, text, *, intensity=1.0, seed=0):
        self.counter[self.name] = self.counter.get(self.name, 0) + 1
        return self.inner.apply(text, intensity=intensity, seed=seed)


def factory(counter):
    def make(name):
        return CountingAttack(build(name), counter, name)

    return make


def test_depth_three_reuses_the_depth_two_prefix():
    counter = {}
    executor = ChainExecutor(factory(counter), cache=MemoryCache())
    pair = parse_strategy("typo_noise@0.02,random_edits@0.1")
    triple = parse_strategy("typo_noise@0.02,random_edits@0.1,style_normalisation@1.0")

    executor.run("The council approved the plan.", pair, doc_id="d")
    assert counter == {"typo_noise": 1, "random_edits": 1}

    result = executor.run("The council approved the plan.", triple, doc_id="d")
    assert result.resumed_at == 2
    assert result.evaluated == 1
    assert counter == {"typo_noise": 1, "random_edits": 1, "style_normalisation": 1}


def test_cached_and_fresh_runs_agree():
    text = "The council approved the transit plan on Tuesday."
    steps = parse_strategy("typo_noise@0.03,random_edits@0.15")
    cold = ChainExecutor(factory({}), cache=MemoryCache()).run(text, steps, doc_id="d")
    warm = ChainExecutor(factory({}), cache=MemoryCache())
    warm.run(text, steps, doc_id="d")
    again = warm.run(text, steps, doc_id="d")
    assert again.text == cold.text
    assert again.resumed_at == 2
    assert again.evaluated == 0


def test_seed_change_does_not_reuse():
    counter = {}
    steps = parse_strategy("typo_noise@0.03")
    text = "The council approved the transit plan."
    cache = MemoryCache()
    ChainExecutor(factory(counter), cache=cache, seed=0).run(text, steps, doc_id="d")
    second = ChainExecutor(factory(counter), cache=cache, seed=1).run(text, steps, doc_id="d")
    assert second.resumed_at == 0
    assert counter["typo_noise"] == 2


def test_different_source_does_not_reuse():
    counter = {}
    steps = parse_strategy("typo_noise@0.03")
    cache = MemoryCache()
    ChainExecutor(factory(counter), cache=cache).run("First document.", steps, doc_id="d")
    second = ChainExecutor(factory(counter), cache=cache).run("Second document.", steps, doc_id="d")
    assert second.resumed_at == 0
    assert counter["typo_noise"] == 2


def test_disk_cache_persists_across_executors(tmp_path):
    steps = parse_strategy("typo_noise@0.03,random_edits@0.1")
    text = "The council approved the transit plan."
    first = ChainExecutor(factory({}), cache=DiskCache(tmp_path)).run(text, steps, doc_id="d")
    counter = {}
    second = ChainExecutor(factory(counter), cache=DiskCache(tmp_path)).run(
        text, steps, doc_id="d"
    )
    assert second.resumed_at == 2
    assert second.text == first.text
    assert counter == {}


def test_depth_limit():
    steps = parse_strategy("typo_noise@0.01,random_edits@0.05,style_normalisation@1.0")
    executor = ChainExecutor(factory({}), max_depth=2)
    with pytest.raises(ValueError):
        executor.run("Some text here.", steps)


def test_edit_rate_bounds():
    assert edit_rate("same", "same") == 0.0
    assert edit_rate("abc", "xyz") > 0.9
    assert 0.0 < edit_rate("abc", "abd") < 1.0


def test_cache_key_depends_on_every_component():
    base = dict(doc_id="d", seed=0, source_digest=text_digest("t"), prefix="a")
    assert cache_key(**base) == cache_key(**base)
    for field, value in [
        ("doc_id", "e"),
        ("seed", 1),
        ("source_digest", text_digest("u")),
        ("prefix", "b"),
    ]:
        assert cache_key(**{**base, field: value}) != cache_key(**base)
