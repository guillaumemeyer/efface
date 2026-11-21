"""Ten-pair metric fixture.

The real stack downloads roberta-large and a COMET checkpoint, so this test
runs only when EFFACE_METRICS=1 and the libraries are installed:

    uv pip install -e ".[metrics]"
    EFFACE_METRICS=1 .venv/bin/python -m pytest tests/test_preservation_fixture.py

Values are stored in tests/fixtures/metrics/expected.json, recorded from the
run that produced docs/metric-calibration.md.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "metrics" / "pairs.json"
EXPECTED = Path(__file__).parent / "fixtures" / "metrics" / "expected.json"
TOLERANCE = 0.02

pytestmark = pytest.mark.skipif(
    os.environ.get("EFFACE_METRICS") != "1",
    reason="set EFFACE_METRICS=1 with the metrics extra installed",
)


@pytest.fixture(scope="module")
def reports():
    pytest.importorskip("bert_score")
    pytest.importorskip("comet")
    from efface.evaluate import BertScore, Comet, score_pairs

    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    pairs = [(row["source"], row["candidate"]) for row in rows]
    return score_pairs(pairs, metrics=[BertScore(), Comet()])


def test_ten_pairs(reports):
    assert len(reports) == 10


def test_values_are_in_range(reports):
    for report in reports:
        assert 0.0 <= report.composite <= 1.0
        for value in report.reported.values():
            assert 0.0 <= value <= 2.0


def test_values_reproduce_the_stored_fixture(reports):
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    stored = {row["id"]: row["S"] for row in expected["documents"]}
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert set(stored) == {row["id"] for row in rows}
    for row, report in zip(rows, reports, strict=True):
        assert report.composite == pytest.approx(stored[row["id"]], abs=TOLERANCE)
