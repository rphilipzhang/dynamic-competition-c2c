# make checks                      run every numerical check (about three minutes)
# make checks ID=P5                only the checks that name P5
# make report RUN=<run-id>         run every check and write verification/<run-id>/numerical_checks.md
# make figures                     recompute and redraw Figure 1 and Figure B.1
#
# Every target accepts PYTHON=/path/to/python (default: python3).

PYTHON ?= python3

.PHONY: checks report figures help

checks:
	$(PYTHON) numerics/run.py $(if $(ID),-k $(ID))

report:
	@test -n "$(RUN)" || { echo "usage: make report RUN=<date>_<model>, for example RUN=2026-11-21_claude-opus-5-5"; exit 2; }
	$(PYTHON) numerics/run.py --report verification/$(RUN)/numerical_checks.md

figures:
	$(PYTHON) numerics/figures/make_figures.py

help:
	@sed -n '1,7p' Makefile
