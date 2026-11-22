#!/usr/bin/env python3
"""Run the numerical checks and summarise them by result.

    python numerics/run.py                          # all checks, summary on the terminal
    python numerics/run.py -k P5                    # only the checks that name P5
    python numerics/run.py --report FILE            # also write a Markdown report to FILE

The report lists, for every result of theory.md and every entry of
numerics/numerical_statements.yaml, the checks that test it directly and the checks
that support those, with their outcome. With -k, the tables count only the IDs that the
expression selects. The report then describes each check once: its points, what it
computes, its pass criterion, and the numbers it recorded, with values at the level of
rounding error listed separately. The exit status is that of pytest.

The IDs are read from the headings `### <ID>` of theory.md and from the entries of
numerics/numerical_statements.yaml that have no field `excluded`.
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
import tempfile
from datetime import date
from importlib import metadata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LIBRARIES = ["numpy", "scipy", "sympy", "mpmath", "pandas", "matplotlib", "PyYAML", "pytest"]


def result_ids() -> list[str]:
    text = (ROOT / "theory.md").read_text(encoding="utf-8")
    return re.findall(r"^### ([A-Z]+[0-9]+)\s*$", text, flags=re.M)


def statement_ids() -> list[str]:
    entries = yaml.safe_load((ROOT / "numerics" / "numerical_statements.yaml").read_text(encoding="utf-8")) or []
    return [e["id"] for e in entries if not e.get("excluded")]


def run_pytest(keyword: str | None, out: Path) -> int:
    cmd = [sys.executable, "-m", "pytest", "numerics", "-q", "-p", "no:cacheprovider", "--results", str(out)]
    if keyword:
        cmd += ["-k", keyword]
    return subprocess.run(cmd, cwd=ROOT).returncode


def ids_of(entries: list[str]) -> list[str]:
    return list(dict.fromkeys(e.split(".")[0] for e in entries))


def selected(keyword: str | None, ids: list[str]) -> set[str] | None:
    """The IDs that a -k expression selects, for example P8 and P9 in 'P8 or P9'.

    None when there is no expression or it names no ID. An ID after `not` is not selected.
    """
    words = re.findall(r"[\w.]+", keyword or "")
    named = {w for i, w in enumerate(words) if w in ids and (i == 0 or words[i - 1].lower() != "not")}
    return named or None


def shown(ids: list[str], focus: set[str] | None) -> list[str]:
    return [i for i in ids if focus is None or i in focus]


def parts(doc: str) -> dict[str, str]:
    """Split a docstring into its opening text and its Points, Computed and Criterion parts."""
    text = " ".join(doc.split())
    out, pieces = {}, re.split(r"\b(Points|Computed|Criterion):", text)
    out["summary"] = pieces[0].strip()
    for label, body in zip(pieces[1::2], pieces[2::2]):
        out[label] = body.strip()
    return out


def tally(tests: list[dict], key: str, rid: str) -> tuple[int, int]:
    mine = [t for t in tests if rid in ids_of(t[key])]
    return sum(t["outcome"] == "passed" for t in mine), len(mine)


def fmt(passed: int, total: int) -> str:
    return "–" if total == 0 else f"{passed}/{total}"


def summary_rows(tests: list[dict], ids: list[str]) -> list[str]:
    rows = ["| ID | Direct checks passed | Supporting checks passed |", "|---|---|---|"]
    for rid in ids:
        rows.append(f"| [{rid}](#{rid.lower()}) | {fmt(*tally(tests, 'claims', rid))} | {fmt(*tally(tests, 'supports', rid))} |")
    return rows


def report(tests: list[dict], status: int, keyword: str | None, results: list[str], statements: list[str]) -> str:
    anchor = {t["test"]: f"check-{i}" for i, t in enumerate(tests, 1)}
    passed = sum(t["outcome"] == "passed" for t in tests)
    focus = selected(keyword, results + statements)
    results, statements = shown(results, focus), shown(statements, focus)
    scope = []
    if focus:
        scope = [f"The selection counts only {', '.join(results + statements)}. Other IDs that the selected checks "
                 "name appear only in the description of each check below.", ""]
    versions = ", ".join(f"{lib} {metadata.version(lib)}" for lib in LIBRARIES if _installed(lib))
    lines = [
        "# Numerical checks",
        "",
        f"Written by `numerics/run.py` on {date.today().isoformat()}. "
        f"Command: `python numerics/run.py{' -k ' + keyword if keyword else ''} --report ...`. "
        f"Python {platform.python_version()} on {platform.system()}, with {versions}.",
        "",
        f"**{passed} of {len(tests)} checks passed.** pytest exit status: {status}.",
        "",
        "A *direct* check tests a part of the result itself. A *supporting* check confirms a tool that direct checks rely on, "
        "for example that a closed form equals the model at random points. Every check computes at finitely many points. "
        "For a result that holds for all parameters it is a search for counterexamples. For a result that holds for "
        "a parameter large enough it probes large values of that parameter.",
        "",
        *scope,
    ]
    for title, ids in (("Results of theory.md", results), ("Numerical statements of the paper", statements)):
        if ids:
            lines += [f"## {title}", "", *summary_rows(tests, ids), ""]
    lines += ["## Checks by ID", ""]
    for rid in results + statements:
        direct = [t for t in tests if rid in ids_of(t["claims"])]
        support = [t for t in tests if rid in ids_of(t["supports"]) and t not in direct]
        if not direct and not support:
            continue
        lines += [f"### {rid}", ""]
        for kind, group in (("direct", direct), ("supporting", support)):
            for t in group:
                named = [c for c in t["claims"] if c.split(".")[0] == rid] if kind == "direct" else []
                tag = f" ({', '.join(named)})" if named and named != [rid] else ""
                lines.append(f"- {kind}{tag}: [{t['test'].split('::')[-1]}](#{anchor[t['test']]}): {t['outcome']}")
        lines.append("")
    lines += ["## Checks", ""]
    for t in tests:
        p = parts(t["doc"])
        lines += [f"<a id=\"{anchor[t['test']]}\"></a>", f"### `{t['test']}`", ""]
        lines.append(f"- **Outcome:** {t['outcome']} ({t.get('seconds', 0):.1f} s)")
        if t["claims"]:
            lines.append(f"- **Tests directly:** {', '.join(t['claims'])}")
        if t["supports"]:
            lines.append(f"- **Supports:** {', '.join(t['supports'])}")
        if p.get("summary"):
            lines.append(f"- **What:** {p['summary']}")
        for label in ("Points", "Computed", "Criterion"):
            if label in p:
                lines.append(f"- **{label}:** {p[label]}")
        if t["measurements"]:
            recorded = "; ".join(f"{k.replace('_', ' ')} = {v}" for k, v in t["measurements"].items())
            lines.append(f"- **Recorded:** {recorded}")
        if t.get("rounding"):
            rounding = "; ".join(f"{k.replace('_', ' ')} = {v}" for k, v in t["rounding"].items())
            lines.append(f"- **At the level of rounding error (differs between machines):** {rounding}")
        if t["outcome"] == "failed":
            lines += ["- **Failure:**", "", "```", t.get("message", "").strip()[-1200:], "```"]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _installed(lib: str) -> bool:
    try:
        metadata.version(lib)
        return True
    except metadata.PackageNotFoundError:
        return False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-k", dest="keyword", help="pytest keyword expression, for example P5 or 'P5 or P6'")
    parser.add_argument("--report", type=Path, help="write a Markdown report to this file")
    args = parser.parse_args(argv)
    results, statements = result_ids(), statement_ids()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "results.json"
        status = run_pytest(args.keyword, out)
        if not out.exists():
            print("pytest wrote no results")
            return status or 1
        tests = [t for t in json.loads(out.read_text())["tests"] if t["outcome"] != "not_run" or not args.keyword]
    print()
    width = max([len(i) for i in results + statements] + [2])
    focus = selected(args.keyword, results + statements)
    for title, ids in (("Results of theory.md", results), ("Numerical statements", statements)):
        named = [rid for rid in shown(ids, focus) if any(rid in ids_of(t["claims"] + t["supports"]) for t in tests)]
        if named:
            print(title)
            for rid in named:
                print(f"  {rid:<{width}} direct {fmt(*tally(tests, 'claims', rid)):>6}   supporting {fmt(*tally(tests, 'supports', rid)):>6}")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report(tests, status, args.keyword, results, statements), encoding="utf-8")
        print(f"wrote {args.report}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
