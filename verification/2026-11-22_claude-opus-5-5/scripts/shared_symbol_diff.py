"""Symbol-level comparison of theory.md passages with the TeX source (Part 1, Section 5 results).

part1_text_compare.py compares alphanumeric tokens only, so it cannot see a changed
relation or sign (<, >, +, -, =, ^, /). This script keeps those symbols as tokens,
drops markup that differs between LaTeX and Markdown, and prints every differing block.

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5/scripts/shared_symbol_diff.py
"""
from __future__ import annotations

import difflib
import re
from pathlib import Path

PAIRS = {
    "LA1 statement": ("paper/OnlineAppendix.tex", 335, 341, "theory.md", 913, 917),
    "LA2 statement": ("paper/OnlineAppendix.tex", 343, 349, "theory.md", 999, 1003),
    "LA1-LA2 joint proof": ("paper/OnlineAppendix.tex", 351, 401, "theory.md", 921, 983),
    "A.2 notation": ("paper/OnlineAppendix.tex", 327, 333, "theory.md", 890, 898),
    "P7 statement": ("paper/Manuscript.tex", 363, 369, "theory.md", 1022, 1026),
    "P7 proof": ("paper/OnlineAppendix.tex", 403, 412, "theory.md", 1030, 1039),
    "P8 statement": ("paper/Manuscript.tex", 376, 384, "theory.md", 1055, 1060),
    "P8 proof": ("paper/OnlineAppendix.tex", 414, 458, "theory.md", 1064, 1115),
    "P9 statement": ("paper/Manuscript.tex", 396, 403, "theory.md", 1130, 1134),
    "P9 proof": ("paper/OnlineAppendix.tex", 460, 477, "theory.md", 1138, 1157),
}

# printed numbers of the labels used in these passages (numerics/paper_labels.json,
# cross-checked against the printed paper/OnlineAppendix.pdf)
LABELS = {"lem:modelS-g": "A.1", "lem:modelN-g": "A.2", "sys-lem6": "A.21",
          "eq:prop8b2": "A.22", "eq:p8region": "A.23", "eq:p8rectangle": "A.24",
          "eq:p8expansion": "A.25", "eq:p8derivative": "A.26"}

KEEP = set("<>=+-^_/|()!,.;:")


def common(s: str) -> list[str]:
    s = re.sub(r"\\(begin|end)\{[^}]*\}", " ", s)
    s = re.sub(r"\\(label|tag)\{[^}]*\}", " ", s)
    s = re.sub(r"\\(bf|it|item|textbf|textit|noindent|qed|hspace\{[^}]*\}|bigl|bigr|big|Big|left|right|displaystyle|,|;|!|quad|qquad|dfrac|tfrac|frac|mathrm|text)\b", " ", s)
    s = s.replace("\\leq", " <= ").replace("\\geq", " >= ").replace("\\le ", " <= ").replace("\\ge ", " >= ")
    s = s.replace("\\le", " <= ").replace("\\ge", " >= ")
    s = s.replace("\\[", " ").replace("\\]", " ").replace("&", " ").replace("\\\\", " ")
    s = s.replace("’", "'")
    toks = re.findall(r"[A-Za-z0-9]+|\S", s)
    return [t for t in toks if re.match(r"[A-Za-z0-9]", t) or t in KEEP]


def tex(path, a, b):
    s = "\n".join(Path(path).read_text(encoding="utf-8").splitlines()[a - 1:b])
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\eqref\{([^}]*)\}", lambda m: f"({LABELS.get(m.group(1), 'REF')})", s)
    s = re.sub(r"\\ref\{([^}]*)\}", lambda m: LABELS.get(m.group(1), "REF"), s)
    s = s.replace("\\footnote{", " Footnote: ")
    return common(s)


def md(path, a, b):
    s = "\n".join(Path(path).read_text(encoding="utf-8").splitlines()[a - 1:b])
    s = re.sub(r"\*\*Lemma A\.[12]\*\* \(`[^`]*`\)\*\*\.\*\*", " ", s)
    s = re.sub(r"\*\*Proposition [0-9]\*\* \(`[^`]*`\)\*\*\.\*\*", " ", s)
    s = s.replace("**", " ").replace("`", " ").replace("∎", " ")
    s = re.sub(r"^\s*- ", " ", s, flags=re.M)
    s = re.sub(r"\(\[LA1\]\(#la1\)\)", "", s)
    return common(s)


def main():
    for name, (tp, ta, tb, mp, ma, mb) in PAIRS.items():
        t, m = tex(tp, ta, tb), md(mp, ma, mb)
        sm = difflib.SequenceMatcher(a=t, b=m, autojunk=False)
        blocks = [op for op in sm.get_opcodes() if op[0] != "equal"]
        print(f"== {name}: tokens paper {len(t)}, theory.md {len(m)}, differing blocks {len(blocks)}")
        for op, i1, i2, j1, j2 in blocks:
            print(f"   {op}: paper '{' '.join(t[i1:i2])}' | theory.md '{' '.join(m[j1:j2])}' | context '{' '.join(t[max(0, i1 - 6):i1])}'")


if __name__ == "__main__":
    main()
