import json
import math

import pytest

from efface.cli import main
from efface.detect import MarkLLMDetector, mean_score, pvalue_from_score
from efface.watermark import read_jsonl, write_jsonl

# Stored from a real detection run on 2026-11-21: facebook/opt-1.3b, key 3,
# the transit-report prompt, 120 new tokens, under the fitted G1 null.
STORED_SCORE = 0.5388888888888889
STORED_N_EFF = 4860
STORED_PVALUE = 1.5665794297482514e-22
STORED_NULL = {"mean": 0.4978378883018637, "variance_scale": 0.0871147500592364}


def test_mean_score_matches_markllm_definition():
    g_values = [[[1, 0, 1], [0, 0, 1]]]
    mask = [[1, 1]]
    score, n_eff = mean_score(g_values, mask)
    assert score == pytest.approx(3 / 6)
    assert n_eff == 6


def test_mean_score_skips_masked_positions():
    g_values = [[[1, 1], [1, 1]]]
    mask = [[1, 0]]
    score, n_eff = mean_score(g_values, mask)
    assert score == pytest.approx(1.0)
    assert n_eff == 2


def test_mean_score_rejects_empty_text():
    with pytest.raises(ValueError):
        mean_score([[[1.0]]], [[0.0]])


def test_stored_p_value_reproduces():
    from efface.detect import NullModel

    null = NullModel(mean=STORED_NULL["mean"], variance_scale=STORED_NULL["variance_scale"])
    pvalue = pvalue_from_score(STORED_SCORE, STORED_N_EFF, null)
    z = (STORED_SCORE - null.mean) / math.sqrt(null.variance_scale / STORED_N_EFF)
    assert z == pytest.approx(9.70, abs=0.05)
    assert pvalue == pytest.approx(STORED_PVALUE, rel=1e-9)
    assert pvalue < 1e-15


def test_pvalue_is_monotone_and_centred():
    assert pvalue_from_score(0.5, 300) == pytest.approx(0.5)
    assert pvalue_from_score(0.6, 300) < pvalue_from_score(0.55, 300)
    assert pvalue_from_score(0.4, 300) > 0.5


def test_pvalue_rejects_bad_input():
    with pytest.raises(ValueError):
        pvalue_from_score(0.5, 0)
    with pytest.raises(ValueError):
        pvalue_from_score(1.5, 10)


def test_null_fit_recovers_mean_and_scale():
    from efface.detect import NullModel

    samples = [(0.49 + 0.002 * (i % 5), 1000) for i in range(20)]
    null = NullModel.fit(samples)
    assert null.mean == pytest.approx(0.494, abs=1e-3)
    assert null.variance_scale == pytest.approx(1000 * 0.002**2 * 2, rel=0.05)
    assert null.n_documents == 20
    assert null.source == "empirical"


def test_null_round_trip():
    from efface.detect import NullModel

    null = NullModel(mean=0.49, variance_scale=0.2, n_documents=60, source="empirical")
    assert NullModel.from_dict(null.to_dict()) == null


def test_detector_uses_the_supplied_null(monkeypatch):
    from efface.detect import NullModel

    null = NullModel(mean=0.49, variance_scale=0.2, n_documents=60, source="empirical")
    detector = MarkLLMDetector(FakeBackend(), null=null)
    monkeypatch.setattr(
        detector, "_g_values_and_mask", lambda text, key: ([[[1, 0]]], [[1]])
    )
    score = detector.score("text", 3)
    assert score.metadata["null"]["source"] == "empirical"


class FakeScheme:
    class Config:
        threshold = 0.52
        watermark_mode = "non-distortionary"
        device = "cpu"

    config = Config()

    class Processor:
        ngram_len = 5

    logits_processor = Processor()


class FakeBackend:
    def scheme_for(self, key):
        return FakeScheme()


def test_detector_scores_through_the_backend(monkeypatch):
    detector = MarkLLMDetector(FakeBackend())

    def fake_g(text, key):
        return [[[1, 1, 1], [0, 1, 1]]], [[1, 1]]

    monkeypatch.setattr(detector, "_g_values_and_mask", fake_g)
    score = detector.score("text", 3)
    assert score.score == pytest.approx(5 / 6)
    assert score.n_eff == 6
    assert score.key == 3
    assert score.detector == "markllm-synthid-mean"
    assert 0.0 < score.pvalue < 0.5


def test_detector_batch_mode_keeps_order(monkeypatch):
    detector = MarkLLMDetector(FakeBackend())
    monkeypatch.setattr(
        detector, "_g_values_and_mask", lambda text, key: ([[[1, 0]]], [[1]])
    )
    scores = list(detector.score_many([("a", 3), ("b", 42)]))
    assert [score.key for score in scores] == [3, 42]


def test_cli_score_writes_removal_flags(tmp_path, monkeypatch):
    records = [
        {"doc_id": "d-k3", "prompt_id": "d", "key": 3, "text": "x", "manifest": {}},
        {"doc_id": "d-k42", "prompt_id": "d", "key": 42, "text": "y", "manifest": {}},
    ]
    source = tmp_path / "docs.jsonl"
    write_jsonl(records, source)
    output = tmp_path / "scores.jsonl"

    class StubDetector:
        def score(self, text, key):
            from efface.detect.base import DetectorScore

            return DetectorScore(
                pvalue=0.4 if key == 3 else 0.01, score=0.5, key=key, detector="stub"
            )

    monkeypatch.setattr("efface.cli._build_detector", lambda args: StubDetector())
    code = main(["score", "--input", str(source), "--output", str(output)])
    assert code == 0
    scored = list(read_jsonl(output))
    assert [row["removed"] for row in scored] == [True, False]
    assert scored[0]["doc_id"] == "d-k3"
    assert json.loads(json.dumps(scored[0]))["key"] == 3


def test_build_detector_reads_a_calibration_report(tmp_path):
    from efface.cli import _build_detector, build_parser

    path = tmp_path / "null.json"
    path.write_text(
        json.dumps(
            {
                "null": {
                    "mean": 0.4978,
                    "variance_scale": 0.0871,
                    "n_documents": 60,
                    "source": "empirical",
                },
                "diagnostics": {},
            }
        ),
        encoding="utf-8",
    )
    args = build_parser().parse_args(["score", "--input", "x", "--null", str(path)])
    detector = _build_detector(args)
    assert detector.null.source == "empirical"
    assert detector.null.mean == pytest.approx(0.4978)


def test_cli_score_needs_input(capsys):
    assert main(["score"]) == 2
    assert "--input" in capsys.readouterr().err
