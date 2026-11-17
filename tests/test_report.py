import pytest

from efface.report import escape_latex, latex_table, markdown_table


def test_markdown_table():
    table = markdown_table(["Tactic", "Removal"], [["typo_noise", 0.42]])
    assert table.splitlines() == [
        "| Tactic | Removal |",
        "| --- | --- |",
        "| typo_noise | 0.420 |",
    ]


def test_markdown_rejects_ragged_rows():
    with pytest.raises(ValueError):
        markdown_table(["a", "b"], [["only one"]])


def test_latex_escape():
    assert escape_latex("50% & more_than_3") == r"50\% \& more\_than\_3"


def test_latex_table_contains_label_and_rows():
    fragment = latex_table(
        ["Chain", "Removal"],
        [["paraphrase", 0.5]],
        caption="Best pair",
        label="tab:pair",
    )
    assert r"\label{tab:pair}" in fragment
    assert "paraphrase & 0.500" in fragment
    assert fragment.startswith(r"\begin{table}")
