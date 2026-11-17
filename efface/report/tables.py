"""Table rendering for generated reports.

The markdown renderer is used by the pilot reports; the LaTeX renderer will
write the paper's table fragments in Week 4. Both take plain values so that a
result file, not a hand-edited table, is the source of truth.
"""

from __future__ import annotations

from collections.abc import Sequence

_LATEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def _format(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def markdown_table(
    headers: Sequence[str], rows: Sequence[Sequence[object]], *, align: str | None = None
) -> str:
    """Render a GitHub-flavoured markdown table."""
    if not headers:
        raise ValueError("headers must not be empty")
    lines = ["| " + " | ".join(headers) + " |"]
    if align is None:
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
    else:
        lines.append("| " + " | ".join(f":{align}:" for _ in headers) + " |")
    for row in rows:
        if len(row) != len(headers):
            raise ValueError("every row must have the same width as headers")
        lines.append("| " + " | ".join(_format(cell) for cell in row) + " |")
    return "\n".join(lines)


def escape_latex(value: object) -> str:
    text = _format(value)
    return "".join(_LATEX_ESCAPES.get(char, char) for char in text)


def latex_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[object]],
    *,
    caption: str,
    label: str,
    column_spec: str | None = None,
) -> str:
    """Render a booktabs table fragment for the paper."""
    if not headers:
        raise ValueError("headers must not be empty")
    spec = column_spec or ("l" * len(headers))
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        rf"\caption{{{escape_latex(caption)}}}",
        rf"\label{{{label}}}",
        rf"\begin{{tabular}}{{{spec}}}",
        r"\toprule",
        " & ".join(escape_latex(header) for header in headers) + r" \\",
        r"\midrule",
    ]
    for row in rows:
        if len(row) != len(headers):
            raise ValueError("every row must have the same width as headers")
        lines.append(" & ".join(escape_latex(cell) for cell in row) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)
