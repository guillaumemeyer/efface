import pytest

from efface.evaluate.cost import Price, estimate_tokens, summarize


def test_estimate_tokens():
    assert estimate_tokens("abcdefgh") == 2
    assert estimate_tokens("") == 1
    with pytest.raises(ValueError):
        estimate_tokens("x", chars_per_token=0)


def test_price():
    price = Price(input_per_mtok=0.15, output_per_mtok=0.60)
    assert price.cost(1_000_000, 0) == pytest.approx(0.15)
    assert price.cost(0, 1_000_000) == pytest.approx(0.60)
    assert price.cost(1_000, 1_000) == pytest.approx(0.00075)


def test_price_rejects_negative_tokens():
    with pytest.raises(ValueError):
        Price(1.0, 1.0).cost(-1, 0)


def test_summarize():
    usage = summarize(
        [
            {"calls": 2, "input_tokens": 100, "output_tokens": 50, "usd": 0.01},
            {"calls": 1, "input_tokens": 20, "output_tokens": 10, "usd": 0.002},
        ]
    )
    assert usage.calls == 3
    assert usage.input_tokens == 120
    assert usage.output_tokens == 60
    assert usage.usd == pytest.approx(0.012)
