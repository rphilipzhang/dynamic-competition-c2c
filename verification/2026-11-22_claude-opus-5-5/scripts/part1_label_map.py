"""Compare numerics/paper_labels.json with the label numbers of a fresh LaTeX build.

Build first (from the repository root):
    cp -R paper/. verification/2026-11-22_claude-opus-5-5/build/
    (cd verification/2026-11-22_claude-opus-5-5/build && latexmk -pdf Manuscript.tex OnlineAppendix.tex)
Then run:
    python verification/2026-11-22_claude-opus-5-5/scripts/part1_label_map.py

Reads the first two fields (number, page) of every \\newlabel in the two .aux files,
keeping each document's labels together, and compares them with the map. Also checks
that every \\ref/\\eqref in the two TeX files has a label in its own document, and prints
the hand-typed cross-references (Lemma/Proposition/Section/(A.k) numbers written
without \\ref) of the Online Appendix next to the numbers the build assigns.
"""
import json
import re
from pathlib import Path

BUILD = Path("verification/2026-11-22_claude-opus-5-5/build")
labels_json = json.loads(Path("numerics/paper_labels.json").read_text())


def aux_labels(path):
    out = {}
    for m in re.finditer(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}\{([^}]*)\}", path.read_text(errors="ignore")):
        out[m.group(1)] = {"number": m.group(2), "page": m.group(3)}
    return out


total_diff = 0
for doc in ("Manuscript", "OnlineAppendix"):
    built = aux_labels(BUILD / f"{doc}.aux")
    built = {k: v for k, v in built.items() if not k.endswith("@cref")}
    stored = labels_json.get(doc, {})
    only_b = sorted(set(built) - set(stored))
    only_s = sorted(set(stored) - set(built))
    diff = [(k, built[k], stored[k]) for k in sorted(set(built) & set(stored)) if built[k] != stored[k]]
    total_diff += len(only_b) + len(only_s) + len(diff)
    print(f"{doc}: built {len(built)} labels, map {len(stored)}; only in build {only_b}; only in map {only_s}; differing {diff}")
    tex = Path(f"paper/{doc}.tex").read_text()
    refs = set(re.findall(r"\\(?:eq)?ref\{([^}]*)\}", tex))
    missing = sorted(r for r in refs if r not in built)
    print(f"  refs used {len(refs)}, refs without a label in this document: {missing}")
print("keys of the map:", list(labels_json))
print("total discrepancies:", total_diff)

# printed numbers of the results, for the In-the-paper lines of theory.md
ms, oa = aux_labels(BUILD / "Manuscript.aux"), aux_labels(BUILD / "OnlineAppendix.aux")
for key in ["lem:model0", "lem:models", "lem:modeln", "lem:oneside", "prop:yacompare", "prop:ybcompare",
            "prop:indsales", "prop:tsales", "prop:pfta", "prop:pftb", "prop:orderprice2", "prop:orderprice1",
            "prop:price", "fig:compare"]:
    print(f"Manuscript {key}: {ms[key]['number']}")
for key in ["lem:modelS-g", "lem:modelN-g", "lem:modelg", "fig:general"]:
    print(f"OnlineAppendix {key}: {oa[key]['number']}")
# equation numbers displayed in the Online Appendix, in order of number
eqs = sorted(((v["number"], k) for k, v in oa.items() if re.fullmatch(r"A\.\d+", v["number"])),
             key=lambda t: int(t[0].split(".")[1]))
print("Online Appendix equation labels:", eqs)
# theory.md tags
tags = re.findall(r"\\tag\{(A\.\d+)\}", Path("theory.md").read_text())
print("theory.md tags (A.k):", tags)
