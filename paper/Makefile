MAIN    = main
LATEXMK ?= latexmk

SOURCES = $(MAIN).tex refs.bib $(wildcard sections/*.tex) $(wildcard appendix/*.tex)

all: $(MAIN).pdf

$(MAIN).pdf: $(SOURCES)
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

# Without latexmk: three passes so that references and citations resolve.
fallback:
	pdflatex -interaction=nonstopmode $(MAIN).tex
	bibtex $(MAIN)
	pdflatex -interaction=nonstopmode $(MAIN).tex
	pdflatex -interaction=nonstopmode $(MAIN).tex

# Self-contained engine: fetches packages on demand and runs bibtex itself.
tectonic:
	tectonic -X compile $(MAIN).tex --keep-logs

clean:
	$(LATEXMK) -C $(MAIN).tex

.PHONY: all fallback tectonic clean
