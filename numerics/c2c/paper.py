"""The LaTeX source of the paper, for checks that quote it.

A check that transcribes a formula of the paper into code quotes the LaTeX it was
written from and asserts that the quotation occurs in `paper/Manuscript.tex` or
`paper/OnlineAppendix.tex`. Whitespace is normalised before the comparison.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ("paper/Manuscript.tex", "paper/OnlineAppendix.tex")


def _normalise(text: str) -> str:
    return " ".join(text.split())


@lru_cache(maxsize=None)
def text() -> str:
    """Both LaTeX files of the paper, concatenated, with whitespace normalised."""
    return _normalise(" ".join((ROOT / name).read_text(encoding="utf-8") for name in SOURCES))


def assert_quoted(latex: str) -> None:
    """Fail unless `latex` occurs verbatim in the LaTeX source of the paper."""
    assert _normalise(latex) in text(), f"not found in {' or '.join(SOURCES)}: {latex}"
