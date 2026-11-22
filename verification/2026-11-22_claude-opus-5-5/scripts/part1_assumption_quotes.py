"""Check that every quoted sentence of the Assumptions list of theory.md occurs in the paper.

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5/scripts/part1_assumption_quotes.py

Each quotation in "..." of the lines starting with "- **A<n>." is reduced to alphanumeric
tokens and searched for as a contiguous token sequence in the tokenised LaTeX of
paper/Manuscript.tex and paper/OnlineAppendix.tex (same normalisation as
part1_text_compare.py). Prints one line per quotation with its location or MISSING.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from part1_text_compare import norm_md, norm_tex  # noqa: E402

docs = {name: norm_tex(Path(f"paper/{name}").read_text(encoding="utf-8"), {})
        for name in ("Manuscript.tex", "OnlineAppendix.tex")}
lines = Path("theory.md").read_text(encoding="utf-8").splitlines()
missing = 0
for ln in lines:
    m = re.match(r"- \*\*(A\d+)\.", ln)
    if not m:
        continue
    for q in re.findall(r"“(.*?)”|\"(.*?)\"", ln):
        q = q[0] or q[1]
        q = q.replace("[Footnote:", " ").replace("]", " ")
        tok = norm_md(q)
        where = None
        for name, t in docs.items():
            s = " ".join(t)
            if " ".join(tok) in s:
                where = name
                break
        if where is None:
            missing += 1
        print(f"{m.group(1)}: {'MISSING' if where is None else 'found in ' + where} ({len(tok)} tokens): {q[:70]}")
print("missing quotations:", missing)
