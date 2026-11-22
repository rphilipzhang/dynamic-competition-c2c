"""Word-level comparison of a passage of theory.md with a passage of the LaTeX source.

Usage (from the repository root):
    python verification/2026-11-22_claude-opus-5-5/scripts/part1_text_compare.py \
        --tex paper/Manuscript.tex:83:172 --md theory.md:119:218

Both passages are reduced to sequences of alphanumeric tokens. LaTeX structural and
formatting commands (sectioning, \\label, \\emph, equation environments, \\left/\\right
and size modifiers) and Markdown markup are dropped; citation keys are kept as tokens.
Each block of differing tokens is printed with a few tokens of context, so that every
departure of theory.md from the paper can be inspected by hand. \\ref and \\eqref are
replaced by the printed numbers read from the .aux files of a local build when
--aux is given (comma-separated list of .aux files), otherwise by the token REF.
"""
from __future__ import annotations

import argparse
import difflib
import re
from pathlib import Path

DROP_CMDS = r"label|emph|textit|textbf|mbox|text|paragraph|subsubsection|subsection|section|left|right|big|Big|bigg|Bigg|bigl|bigr|Bigl|Bigr|biggl|biggr|displaystyle|quad|qquad|hspace|vspace|nonumber|notag|mathrm|operatorname|footnote|noindent|smallskip|medskip|bigskip|tfrac|dfrac"


def load_labels(aux_files):
    labels = {}
    for f in aux_files:
        for m in re.finditer(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", Path(f).read_text(errors="ignore")):
            labels.setdefault(m.group(1), m.group(2))
    return labels


def norm_tex(s: str, labels) -> list[str]:
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\label\{[^}]*\}", " ", s)
    def ref(m):
        key = m.group(2)
        val = labels.get(key, "REF")
        return f" ({val}) " if m.group(1) == "eqref" else f" {val} "
    s = re.sub(r"\\(ref|eqref)\{([^}]*)\}", ref, s)
    s = re.sub(r"\\cite[pt]?\*?(\[[^\]]*\])?(\[[^\]]*\])?\{([^}]*)\}",
               lambda m: " " + (m.group(1) or "") + " " + (m.group(2) or "") + " " + m.group(3).replace(",", " ") + " ", s)
    s = re.sub(r"\\(begin|end)\{[^}]*\}", " ", s)
    s = re.sub(r"\\(" + DROP_CMDS + r")\b", " ", s)
    s = s.replace("\\[", " ").replace("\\]", " ")
    return tokens(s)


def norm_md(s: str) -> list[str]:
    s = re.sub(r"\\tag\{[^}]*\}", " ", s)
    s = re.sub(r"\\(begin|end)\{[^}]*\}", " ", s)
    s = re.sub(r"\\(" + DROP_CMDS + r")\b", " ", s)
    s = re.sub(r"^#+\s*", " ", s, flags=re.M)
    return tokens(s)


def tokens(s: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", s)


def passage(spec: str) -> str:
    path, a, b = spec.rsplit(":", 2)
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[int(a) - 1:int(b)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tex", required=True, action="append")
    ap.add_argument("--md", required=True, action="append")
    ap.add_argument("--aux", default="")
    ap.add_argument("--context", type=int, default=6)
    args = ap.parse_args()
    labels = load_labels([f for f in args.aux.split(",") if f])
    t = sum((norm_tex(passage(x), labels) for x in args.tex), [])
    m = sum((norm_md(passage(x)) for x in args.md), [])
    sm = difflib.SequenceMatcher(a=t, b=m, autojunk=False)
    n = 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        n += 1
        c = args.context
        print(f"--- {op}: paper[{i1}:{i2}] vs theory.md[{j1}:{j2}]")
        print("  context:", " ".join(t[max(0, i1 - c):i1]))
        print("  paper   :", " ".join(t[i1:i2]))
        print("  theory  :", " ".join(m[j1:j2]))
        print("  after   :", " ".join(t[i2:i2 + c]))
    print(f"tokens: paper {len(t)}, theory.md {len(m)}, similarity {sm.ratio():.4f}, blocks differing {n}")


if __name__ == "__main__":
    main()
