MAIN    = main
TECTONIC ?= tectonic
LATEXMK ?= latexmk

SOURCES = $(MAIN).tex refs.bib $(wildcard sections/*.tex) $(wildcard appendix/*.tex)

# Tectonic is the default because it needs no separate BibTeX pass and is the
# only engine installed on the development machine.
all: pdf

pdf: $(MAIN).pdf

$(MAIN).pdf: $(SOURCES)
	$(TECTONIC) -X compile $(MAIN).tex --keep-logs

tectonic: pdf

# Kept for machines with a full TeX Live installation.
latexmk:
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

# Without latexmk: three passes so that references and citations resolve.
fallback:
	pdflatex -interaction=nonstopmode $(MAIN).tex
	bibtex $(MAIN)
	pdflatex -interaction=nonstopmode $(MAIN).tex
	pdflatex -interaction=nonstopmode $(MAIN).tex

clean:
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).fdb_latexmk \
		$(MAIN).fls $(MAIN).log $(MAIN).out $(MAIN).toc $(MAIN).synctex.gz
	rm -rf $(MAIN).tectonic

.PHONY: all pdf tectonic latexmk fallback clean
