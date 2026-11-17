import pytest

from efface.evaluate.stats import (
    auroc,
    holm,
    paired_bootstrap_diff,
    removal_rate,
    removed_from_pvalues,
    tpr_at_fpr,
    wilson_interval,
)


def test_wilson_interval_known_value():
    low, high = wilson_interval(50, 100)
    assert low == pytest.approx(0.4038, abs=1e-4)
    assert high == pytest.approx(0.5962, abs=1e-4)


def test_wilson_interval_boundaries():
    assert wilson_interval(0, 10) == (0.0, pytest.approx(0.2775, abs=1e-4))
    low, high = wilson_interval(10, 10)
    assert low == pytest.approx(0.7225, abs=1e-4)
    assert high == 1.0


def test_wilson_rejects_bad_counts():
    with pytest.raises(ValueError):
        wilson_interval(1, 0)
    with pytest.raises(ValueError):
        wilson_interval(4, 3)


def test_removal_rate():
    rate = removal_rate([True] * 8 + [False] * 2)
    assert rate.value == 0.8
    assert rate.n == 10
    assert rate.low < rate.value < rate.high


def test_removed_requires_every_key_to_fail():
    assert removed_from_pvalues([0.31, 0.42, 0.07]) is True
    assert removed_from_pvalues([0.31, 0.01, 0.07]) is False
    with pytest.raises(ValueError):
        removed_from_pvalues([])


def test_auroc_perfect_and_tied():
    assert auroc([2.0, 3.0], [1.0]) == 1.0
    assert auroc([1.0], [2.0, 3.0]) == 0.0
    assert auroc([1.0, 2.0], [2.0]) == pytest.approx(0.25)


def test_tpr_at_fpr_respects_threshold():
    negatives = [float(i) for i in range(100)]
    assert tpr_at_fpr([99.0, 100.0, 50.0], negatives, 0.01) == pytest.approx(2 / 3)
    assert tpr_at_fpr([100.0], negatives, 0.01) == 1.0
    assert tpr_at_fpr([0.5], negatives, 0.01) == 0.0


def test_tpr_at_fpr_without_enough_negatives():
    # No negative threshold reaches 1%, so the threshold sits above the highest
    # negative. A positive above it is still detected at an empirical FPR of 0.
    assert tpr_at_fpr([1.0], [0.0, 0.5], 0.01) == 1.0
    assert tpr_at_fpr([0.4], [0.0, 0.5], 0.01) == 0.0


def test_paired_bootstrap_identical():
    observed, low, high, pvalue = paired_bootstrap_diff([1.0, 2.0], [1.0, 2.0], n_resamples=200)
    assert observed == 0.0
    assert low == 0.0
    assert high == 0.0
    assert pvalue == 1.0


def test_paired_bootstrap_detects_shift():
    a = [1.0] * 20
    b = [0.0] * 20
    observed, low, high, pvalue = paired_bootstrap_diff(a, b, n_resamples=500, seed=1)
    assert observed == 1.0
    assert low == high == 1.0
    assert pvalue < 0.01


def test_paired_bootstrap_length_mismatch():
    with pytest.raises(ValueError):
        paired_bootstrap_diff([1.0], [1.0, 2.0])


def test_holm_is_monotone_and_preserves_order():
    adjusted = holm([0.01, 0.04, 0.03])
    assert adjusted[0] == pytest.approx(0.03)
    assert adjusted[1] == pytest.approx(0.06)
    assert adjusted[2] == pytest.approx(0.06)
