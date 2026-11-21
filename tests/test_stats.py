import pytest

from efface.evaluate.stats import (
    auroc,
    clustered_rate,
    detection_check_pass,
    holm,
    is_removed,
    normal_quantile,
    paired_bootstrap_diff,
    removal_rate,
    tpr_at_fpr,
    tpr_at_fpr_parametric,
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


def test_removed_uses_the_generating_key():
    assert is_removed(0.31) is True
    assert is_removed(0.049) is False
    assert is_removed(0.05) is False
    with pytest.raises(ValueError):
        is_removed(1.5)
    with pytest.raises(ValueError):
        is_removed(0.2, alpha=0.0)


def test_clustered_rate_resamples_prompts():
    removed = [True, True, False, False, True, True]
    clusters = ["p1", "p1", "p1", "p2", "p2", "p2"]
    rate = clustered_rate(removed, clusters, n_resamples=500, seed=3)
    assert rate.value == pytest.approx(4 / 6)
    assert rate.low <= rate.value <= rate.high
    with pytest.raises(ValueError):
        clustered_rate(removed, clusters[:-1])


def test_clustered_rate_is_wider_than_documents_when_keys_agree():
    # Three keys agree inside every prompt: a document bootstrap would pretend
    # the sample is three times larger than it is.
    removed = [True] * 15 + [False] * 15
    clusters = [f"p{i // 3}" for i in range(30)]
    prompt_rate = clustered_rate(removed, clusters, n_resamples=2_000, seed=1)
    document_rate = removal_rate(removed)
    assert prompt_rate.n == document_rate.n
    assert (prompt_rate.high - prompt_rate.low) > (document_rate.high - document_rate.low)


def test_normal_quantile_known_values():
    assert normal_quantile(0.5) == pytest.approx(0.0, abs=1e-9)
    assert normal_quantile(0.975) == pytest.approx(1.9599639845, abs=1e-6)
    assert normal_quantile(0.025) == pytest.approx(-1.9599639845, abs=1e-6)


def test_tpr_at_fpr_parametric_uses_the_null():
    negatives = [0.5 + 0.05 * ((i % 7) - 3) for i in range(300)]
    positives = [0.9] * 40 + [0.5] * 60
    value = tpr_at_fpr_parametric(positives, negatives, fpr=0.01)
    assert 0.35 < value < 0.45


def test_detection_check_gate():
    assert detection_check_pass([True] * 190 + [False] * 10) is True
    assert detection_check_pass([True] * 150 + [False] * 50) is False
    with pytest.raises(ValueError):
        detection_check_pass([])


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
