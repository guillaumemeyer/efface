# Paper source

LaTeX source for **EFFACE: Finding the Most Effective Meaning-Preserving Attack Chain against SynthID-Text-Class Watermarks**. The paper is a draft: every field wrapped in red `[TODO: …]` is a placeholder for a measurement or a fact the experiments must still supply.

## Layout

| Path | Contents |
| --- | --- |
| `main.tex` | Preamble, title block, section includes, bibliography, appendices |
| `sections/` | One file per section, numbered in reading order |
| `appendix/` | Prompts and rating protocol, hyperparameters, extra results, reproducibility checklist |
| `refs.bib` | BibTeX entries for every work cited |
| `figures/` | Generated figure assets; `frontier.pdf` is produced from the results archive |

## Build

```sh
make            # tectonic -X compile main.tex --keep-logs -> main.pdf
make latexmk    # latexmk -pdf main.tex
make fallback   # pdflatex + bibtex + pdflatex + pdflatex
make clean      # remove intermediates
```

`make` uses [Tectonic](https://tectonic-typesetting.github.io/), which downloads packages on first use and runs BibTeX itself (`brew install tectonic`). The `latexmk` target needs a full TeX Live installation, and the `fallback` target needs a plain `pdflatex`/`bibtex` install.

The PDF is a build artifact and is not tracked. Cite the arXiv version once one exists.

## Placeholders

Run `grep -rn '\\ph{' sections appendix` to list every open placeholder. Each marker names the quantity that is missing, so the list doubles as a to-do list for the experimental runs. The results tables in `sections/07-results.tex` and the generator, attacker, and data tables in `sections/06-experimental-setup.tex` are the main consumers.

## Conventions

- Citations use `natbib` numeric style; add new entries to `refs.bib` and cite with `\citep{key}`.
- Tables use `booktabs` rules and no vertical lines.
- New sections go in `sections/` with a two-digit prefix and an `\input` line in `main.tex`.
- Numbers that come from a run are always `\ph{}` until the run is in the results archive.
