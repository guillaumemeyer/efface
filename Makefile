PY ?= .venv/bin/python
UV ?= uv

.PHONY: install test lint smoke pdf check-placeholders

install:
	$(UV) venv --python 3.11 .venv
	$(UV) pip install -e ".[dev]"

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check .

smoke:
	$(PY) -m efface.cli smoke

pdf:
	$(MAKE) -C paper tectonic

check-placeholders:
	@if grep -rn '\\ph{' paper/sections paper/appendix paper/main.tex; then \
		echo "placeholders remain"; exit 1; \
	else \
		echo "no placeholders"; \
	fi
