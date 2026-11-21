import pytest

from efface.evaluate import (
    REPORTED_ONLY,
    SELECTING,
    PreservationReport,
    aggregate,
    below_floor_fraction,
    composite,
    length_ratio,
    score_pairs,
)


class FixedMetric:
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def score(self, pairs):
        return list(self.values)


def test_selecting_pair_is_exactly_bertscore_and_comet():
    assert SELECTING == ("bertscore", "comet")
    assert "mauve" in REPORTED_ONLY
    assert "mauve" not in SELECTING


def test_composite_is_the_unweighted_mean():
    assert composite({"bertscore": 0.8, "comet": 0.6}) == pytest.approx(0.7)


def test_composite_rejects_mauve():
    with pytest.raises(ValueError, match="extra=\\['mauve'\\]"):
        composite({"bertscore": 0.8, "comet": 0.6, "mauve": 0.9})


def test_composite_rejects_a_missing_selecting_metric():
    with pytest.raises(ValueError, match="missing"):
        composite({"bertscore": 0.8})


def test_composite_rejects_out_of_range():
    with pytest.raises(ValueError):
        composite({"bertscore": 1.2, "comet": 0.6})


def test_length_ratio():
    assert length_ratio("one two three", "one two") == pytest.approx(2 / 3)
    with pytest.raises(ValueError):
        length_ratio("", "x")


def test_score_pairs_keeps_bleurt_out_of_the_floor():
    pairs = [("a b c", "a b c"), ("d e f", "d e")]
    metrics = [
        FixedMetric("bertscore", [0.9, 0.7]),
        FixedMetric("comet", [0.8, 0.5]),
        FixedMetric("bleurt", [0.95, 0.4]),
    ]
    reports = score_pairs(pairs, metrics=metrics)
    assert [report.composite for report in reports] == pytest.approx([0.85, 0.6])
    assert reports[0].reported["bleurt"] == 0.95
    assert reports[0].reported["length_ratio"] == pytest.approx(1.0)
    assert "bleurt" not in {"bertscore", "comet"}


def test_score_pairs_needs_both_selecting_metrics():
    with pytest.raises(ValueError, match="floor needs"):
        score_pairs([("a", "b")], metrics=[FixedMetric("bertscore", [0.9])])


def test_score_pairs_rejects_unknown_metric_names():
    with pytest.raises(ValueError, match="unknown metric"):
        score_pairs([("a", "b")], metrics=[FixedMetric("vibes", [0.9])])


def test_aggregate_and_floor_fraction():
    reports = [
        PreservationReport(source_id="0", composite=0.9, reported={"length_ratio": 1.0}),
        PreservationReport(source_id="1", composite=0.7, reported={"length_ratio": 0.8}),
    ]
    summary = aggregate(reports)
    assert summary["S"] == pytest.approx(0.8)
    assert summary["length_ratio"] == pytest.approx(0.9)
    assert below_floor_fraction(reports, tau=0.8) == pytest.approx(0.5)


def test_below_floor_uses_the_composite():
    assert PreservationReport("0", 0.79).below_floor(0.8) is True
    assert PreservationReport("0", 0.80).below_floor(0.8) is False
