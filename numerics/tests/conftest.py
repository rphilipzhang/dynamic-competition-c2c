"""Shared pytest configuration for the numerical checks.

Every check names the results of the paper it bears on:

    @pytest.mark.claims("L2.first", "P5.c1")     # the check tests these parts of results directly
    @pytest.mark.supports("P1", "P2")            # the check confirms a tool that checks of these results rely on
    def test_...():

IDs are those of `theory.md` (L1 to L4, P1 to P9, LA1, LA2, LB1) and of
`numerics/numerical_statements.yaml` (F1, FB1, N1 to N8, N7 excluded). A part is written after a
dot, as in `P5.c1`. Each ID, without its part, is added to the keywords of the check,
so that

    pytest numerics -k P5

runs every check that names Proposition 5, directly or as support.

With `--results FILE` the run writes one JSON record per check: its IDs, its
docstring, its outcome, and the measurements it recorded through the `record`
fixture. `numerics/run.py` uses that file to write a report.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "numerics"))

_results: dict[str, dict] = {}


def pytest_addoption(parser):
    parser.addoption("--results", default=None, help="write one JSON record per check to this file")


def pytest_configure(config):
    config.addinivalue_line("markers", "claims(*ids): results or parts of results that this check tests directly")
    config.addinivalue_line("markers", "supports(*ids): results whose checks rely on what this check confirms")


def _marked(item, name: str) -> list[str]:
    """The IDs of every marker of that name on the check, in order, without repeats."""
    ids: list[str] = []
    for marker in item.iter_markers(name=name):
        ids += [a for a in marker.args if a not in ids]
    return ids


def pytest_collection_modifyitems(config, items):
    for item in items:
        claims, supports = _marked(item, "claims"), _marked(item, "supports")
        item.extra_keyword_matches.update(i.split(".")[0] for i in claims + supports)
        _results[item.nodeid] = {
            "test": item.nodeid.split("numerics/")[-1],
            "claims": claims,
            "supports": supports,
            "doc": (item.function.__doc__ or "").strip(),
            "outcome": "not_run",
            "measurements": {},
            "rounding": {},
        }


def _plain(value):
    """Convert a measurement to a JSON type. Floats keep six significant digits."""
    if isinstance(value, (list, tuple, set)):
        return [_plain(v) for v in (sorted(value) if isinstance(value, set) else value)]
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    if isinstance(value, float):
        return float(f"{value:.6g}")
    return str(value)


@pytest.fixture
def record(request):
    """Record a named measurement (a number or a short string) for the report.

    `stable=False` marks a value at the level of rounding error, which differs from
    one machine to the next. The report lists such values separately.
    """
    def _record(name, value, stable=True):
        _results[request.node.nodeid]["measurements" if stable else "rounding"][name] = _plain(value)
    return _record


def pytest_runtest_logreport(report):
    entry = _results.get(report.nodeid)
    if entry is None:
        return
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        entry["outcome"] = report.outcome
        if report.outcome == "failed":
            entry["message"] = str(report.longrepr)[-1500:]
        entry["seconds"] = round(getattr(report, "duration", 0.0), 2)


def pytest_sessionfinish(session, exitstatus):
    path = session.config.getoption("--results")
    if path:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        tests = sorted(_results.values(), key=lambda e: e["test"])
        out.write_text(json.dumps({"exit_status": int(exitstatus), "tests": tests}, indent=2) + "\n", encoding="utf-8")


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT
