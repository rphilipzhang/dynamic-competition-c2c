"""Part 1: compare numerics/paper_labels.json with the labels of a fresh LaTeX build.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5-b/scripts/part1_label_map.py

It reads the .aux files of the build in verification/2026-11-22_claude-opus-5-5-b/build/
(made by copying paper/ there and running `latexmk -pdf Manuscript.tex OnlineAppendix.tex`).
If the build is missing it makes it (about 20 s). It prints:
  * every label whose number or page differs between the build and the JSON map,
  * labels present in one and not the other,
  * labels defined inside unnumbered environments (empty anchor in the .aux) and whether
    the TeX sources reference them with \\ref or \\eqref.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

RUN = Path("verification/2026-11-22_claude-opus-5-5-b")
BUILD = RUN / "build"


def ensure_build() -> None:
    if (BUILD / "Manuscript.aux").exists() and (BUILD / "OnlineAppendix.aux").exists():
        return
    BUILD.mkdir(parents=True, exist_ok=True)
    for p in Path("paper").iterdir():
        shutil.copy2(p, BUILD / p.name)
    env = dict(os.environ, TMPDIR=str((RUN / "tmp").resolve()))
    subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "Manuscript.tex", "OnlineAppendix.tex"],
                   cwd=BUILD, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


def newlabels(aux: Path) -> dict[str, dict]:
    out = {}
    pat = re.compile(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}\{([^}]*)\}\{.*?\}\{([^}]*)\}\{\}\}")
    for line in aux.read_text(encoding="utf-8", errors="replace").splitlines():
        m = pat.match(line)
        if m:
            out[m.group(1)] = {"number": m.group(2), "page": m.group(3), "anchor": m.group(4)}
    return out


def starred_labels(t: str) -> set[str]:
    """Labels whose innermost enclosing environment is unnumbered (name ending in *)."""
    out, stack = set(), []
    for m in re.finditer(r"\\(begin|end)\{([^}]*)\}|\\label\{([^}]*)\}", t):
        if m.group(1) == "begin":
            stack.append(m.group(2))
        elif m.group(1) == "end":
            if stack:
                stack.pop()
        else:
            maths = [e for e in stack if e not in ("document",)]
            if maths and maths[-1].endswith("*"):
                out.add(m.group(3))
    return out


def main() -> None:
    ensure_build()
    stored = json.loads(Path("numerics/paper_labels.json").read_text(encoding="utf-8"))
    tex = {d: Path(f"paper/{d}.tex").read_text(encoding="utf-8") for d in ("Manuscript", "OnlineAppendix")}
    total_diff = 0
    for doc in ("Manuscript", "OnlineAppendix"):
        built = newlabels(BUILD / f"{doc}.aux")
        starred = starred_labels(tex[doc])
        unnumbered = {k: v for k, v in built.items() if k in starred or not v["anchor"]}
        numbered = {k: v for k, v in built.items() if k not in unnumbered}
        mine = stored.get(doc, {})
        print(f"== {doc}: {len(built)} labels in .aux, {len(numbered)} outside unnumbered environments, {len(mine)} in JSON")
        for k in sorted(set(numbered) | set(mine)):
            a, b = numbered.get(k), mine.get(k)
            if a is None:
                print(f"  only in JSON: {k} -> {b}")
                total_diff += 1
            elif b is None:
                print(f"  only in build: {k} -> {a['number']} p.{a['page']}")
                total_diff += 1
            elif (a["number"], a["page"]) != (b.get("number"), b.get("page")):
                print(f"  differs: {k} build {a['number']} p.{a['page']} json {b.get('number')} p.{b.get('page')}")
                total_diff += 1
        for k, v in sorted(unnumbered.items()):
            refs = [d for d, t in tex.items() if re.search(r"\\(?:eq)?ref\{" + re.escape(k) + r"\}", t)]
            print(f"  unnumbered-env label {k} (aux number {v['number']}): referenced in {refs or 'none'}")
    print(f"label differences between build and JSON: {total_diff}")
    # every \ref / \eqref in the sources resolves to a label of the same document
    for doc, t in tex.items():
        built = newlabels(BUILD / f"{doc}.aux")
        missing = sorted({m for m in re.findall(r"\\(?:eq)?ref\{([^}]*)\}", t) if m not in built})
        print(f"{doc}: references to labels not defined in the same document: {missing or 'none'}")


if __name__ == "__main__":
    main()
