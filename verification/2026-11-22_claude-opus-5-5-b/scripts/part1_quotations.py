"""Part 1, item 5: the quotations of numerics/numerical_statements.yaml and of the checks, against the paper.

Independent of numerics/c2c/paper.py. For each quotation it reports
  * whether it occurs in the LaTeX source with TeX comments removed (the repository's check also
    accepts commented-out text), after printing every \\ref{...} as the number of
    numerics/paper_labels.json, and how often,
  * the file and line where it occurs and the result (lemma/proposition label, or the nearest
    "Proof of ..." heading, section heading or figure label) that encloses it, so that the name the
    check gives the quotation can be compared with its place in the paper.
Quotations of the checks are collected from the source of numerics/tests/*.py with the ast module:
every call quoted(..., latex) or paper.assert_quoted(latex), the dict QUOTES, and module constants
passed by name.
Finally it lists every sentence of both TeX files that contains a word typical of a numerical claim
and is not part of a quotation of numerical_statements.yaml, for the omission check.
Run from the repository root: python verification/2026-11-22_claude-opus-5-5-b/scripts/part1_quotations.py
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import yaml

FILES = ("paper/Manuscript.tex", "paper/OnlineAppendix.tex")
labels = json.loads(Path("numerics/paper_labels.json").read_text(encoding="utf-8"))
NUMBER = {lab: e["number"] for table in labels.values() for lab, e in table.items()}


def strip_comments(line: str) -> str:
    return re.sub(r"(?<!\\)%.*$", "", line)


def resolve(text: str) -> str:
    return re.sub(r"\\ref\{([^}]*)\}", lambda m: NUMBER.get(m.group(1), "??"), text)


def norm(text: str) -> str:
    return " ".join(text.split())


SRC = {}
for f in FILES:
    raw = Path(f).read_text(encoding="utf-8").split("\n")
    stripped = [strip_comments(l) for l in raw]
    SRC[f] = {"raw": raw, "stripped": stripped}


def locate(quote: str, use_refs: bool):
    """[(file, line, enclosing)] of every occurrence in comment-free text."""
    q = norm(quote)
    hits = []
    for f, s in SRC.items():
        lines = s["stripped"]
        # character offset -> line number map on the normalised, resolved text
        pieces, starts, pos = [], [], 0
        for i, l in enumerate(lines):
            t = norm(resolve(l) if use_refs else l)
            starts.append(pos)
            pieces.append(t)
            pos += len(t) + 1
        joined = " ".join(pieces)
        start = 0
        while True:
            k = joined.find(q, start)
            if k < 0:
                break
            line = max(i for i, st in enumerate(starts) if st <= k)
            hits.append((f, line + 1, enclosing(lines, line)))
            start = k + 1
    return hits


ENV = re.compile(r"\\begin\{(lemma|proposition)\}|\\label\{([^}]*)\}|Proof of ([^:}]*)|\\(sub)*section\*?\{([^}]*)\}")


def enclosing(lines, line):
    for i in range(line, -1, -1):
        found = ENV.findall(lines[i])
        for env, label, proof, _, sec in reversed(found):
            if label and (label.startswith(("lem", "prop", "fig", "sys", "eq")) or ":" in label):
                return f"label {label} (line {i + 1})"
            if proof:
                return f"'Proof of {proof.strip()}' (line {i + 1})"
            if sec:
                return f"section '{sec}' (line {i + 1})"
    return "start of file"


def raw_occurs(quote: str) -> bool:
    text = norm(resolve(" ".join(" ".join(s["raw"]) for s in SRC.values())))
    return norm(quote) in text


def quotes_in_tests():
    out = []
    for path in sorted(Path("numerics/tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        consts = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                try:
                    consts[node.targets[0].id] = ast.literal_eval(node.value)
                except Exception:  # noqa: BLE001
                    pass
        names = {k: v for k, v in consts.items() if isinstance(v, str)}
        if "QUOTES" in consts or any(isinstance(n, ast.Name) and n.id == "QUOTES" for n in ast.walk(tree)):
            src = path.read_text(encoding="utf-8")
            m = re.search(r"^QUOTES = \{.*?^\}", src, re.S | re.M)
            if m:
                keys = {k: v for k, v in consts.items() if isinstance(v, str)}
                d = eval(m.group(0)[len("QUOTES = "):], {}, keys)    # noqa: S307  (repository test source, literals only)
                for result, strings in d.items():
                    for s in strings:
                        out.append((path.name, result, s))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
                if fn in ("quoted", "assert_quoted") and node.args:
                    arg = node.args[-1]
                    result = ast.literal_eval(node.args[0]) if fn == "quoted" and isinstance(node.args[0], ast.Constant) else "?"
                    if isinstance(arg, ast.Name) and arg.id in names:
                        out.append((path.name, result, names[arg.id]))
                    else:
                        try:
                            out.append((path.name, result, ast.literal_eval(arg)))
                        except Exception:  # noqa: BLE001  (a variable, e.g. the loop over QUOTES)
                            pass
    return out


def main():
    entries = yaml.safe_load(Path("numerics/numerical_statements.yaml").read_text(encoding="utf-8"))
    print("== numerical_statements.yaml")
    for e in entries:
        hits = locate(e["quote"], use_refs=True)
        print(f"{e['id']}: in comment-free text {len(hits)}x, in raw text {raw_occurs(e['quote'])}; "
              f"{'; '.join(f'{f}:{l} in {enc}' for f, l, enc in hits)}; excluded: {'excluded' in e}")
    print("\n== quotations in numerics/tests")
    qs = quotes_in_tests()
    bad = 0
    for fn, result, latex in qs:
        hits = locate(latex, use_refs=False)
        bad += len(hits) == 0
        where = "; ".join(f"{f.split('/')[-1]}:{l} in {enc}" for f, l, enc in hits) or "NOT FOUND"
        print(f"[{fn}] {result}: {len(hits)}x  {where}\n      {latex[:110]}")
    print(f"quotations in tests: {len(qs)}, not found in comment-free text: {bad}")

    print("\n== sentences with numerical-claim keywords that no yaml quote covers")
    covered = [norm(e["quote"]) for e in entries]
    kw = re.compile(r"numerical|numerically|experiment|we find|we found|simulat|robust|we test|tested|"
                    r"we observe|observation|illustrat|shows that|show that|graph|Figure", re.I)
    for f, s in SRC.items():
        for i, line in enumerate(s["stripped"], 1):
            if line.lstrip().startswith(("\\includegraphics", "\\begin{", "\\end{", "\\usepackage", "\\numberwithin")):
                continue
            for sent in re.split(r"(?<=[.!?])\s+", resolve(line)):
                ns = norm(sent)
                if kw.search(ns) and len(ns) > 30 and not any(ns in c or c in ns for c in covered):
                    print(f"{f}:{i}: {ns[:300]}")


if __name__ == "__main__":
    main()
