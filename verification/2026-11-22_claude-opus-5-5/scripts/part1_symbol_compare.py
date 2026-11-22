"""Symbol-level comparison of the statements and proofs of L1, L2, L3, L4 and LB1.

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5/scripts/part1_symbol_compare.py

part1_text_compare.py compares alphanumeric tokens only, so a changed sign, inequality or
operator (+, -, <, >, =, /, ^, _, parentheses) would not show. This script tokenises both
passages into alphanumeric runs AND single operator characters, after dropping LaTeX and
Markdown layout (eqnarray alignment '&', line breaks '\\\\', \\left, \\right, size
modifiers, \\nonumber, \\label, \\tag, $ and braces). \\ref/\\eqref are resolved with the
printed numbers in numerics/paper_labels.json (cross-checked by hand against the order of
the numbered displays in paper/OnlineAppendix.tex: (A.1) to (A.17)).
Prints each differing block; a passage with no block is identical up to layout.
"""
import json
import re
import difflib
from pathlib import Path

LAB = json.loads(Path("numerics/paper_labels.json").read_text())
LABELS = {}
for doc in ("OnlineAppendix", "Manuscript"):
    for k, v in LAB[doc].items():
        LABELS.setdefault(doc + ":" + k, v["number"])

DROP = (r"label|emph|textit|textbf|mbox|text|left|right|big|Big|bigg|Bigg|bigl|bigr|Bigl|Bigr|"
        r"displaystyle|quad|qquad|hspace|vspace|nonumber|notag|mathrm|noindent|bf|qed|item|tag")
OPS = "+-<>=/^_()[]|"


def passage(spec):
    path, a, b = spec.rsplit(":", 2)
    return "\n".join(Path(path).read_text(encoding="utf-8").splitlines()[int(a) - 1:int(b)])


def toks(s, doc=None):
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\label\{[^}]*\}", " ", s)
    s = re.sub(r"\\tag\{[^}]*\}", " ", s)
    if doc:
        s = re.sub(r"\\eqref\{([^}]*)\}", lambda m: " (" + LABELS.get(doc + ":" + m.group(1), "REF") + ") ", s)
        s = re.sub(r"\\ref\{([^}]*)\}", lambda m: " " + LABELS.get(doc + ":" + m.group(1), "REF") + " ", s)
    s = re.sub(r"\\(begin|end)\{[^}]*\}(\{[^}]*\})?", " ", s)
    s = re.sub(r"\\(" + DROP + r")\b", " ", s)
    s = s.replace("\\\\", " ").replace("\\[", " ").replace("\\]", " ").replace("\\{", " ").replace("\\}", " ")
    s = re.sub(r"\[\d+pt\]", " ", s)
    s = re.sub(r"\\,|\\;|\\!|\\ ", " ", s)
    s = re.sub(r"^#+.*$", " ", s, flags=re.M) if not doc else s
    s = s.replace("**", " ")
    out = re.findall(r"[A-Za-z0-9]+|[" + re.escape(OPS) + "]", s)
    return out


PAIRS = [
    ("L1 statement", "paper/Manuscript.tex:183:183", "Manuscript", "theory.md:324:324"),
    ("L1 proof", "paper/OnlineAppendix.tex:40:72", "OnlineAppendix", "theory.md:328:369"),
    ("L2 statement", "paper/Manuscript.tex:192:192", "Manuscript", "theory.md:387:387"),
    ("L2 proof", "paper/OnlineAppendix.tex:74:132", "OnlineAppendix", "theory.md:391:471"),
    ("L3 statement", "paper/Manuscript.tex:201:206", "Manuscript", "theory.md:489:496"),
    ("L3 proof", "paper/OnlineAppendix.tex:134:204", "OnlineAppendix", "theory.md:500:583"),
    ("L4 statement", "paper/Manuscript.tex:225:228", "Manuscript", "theory.md:600:601"),
    ("L4 proof", "paper/OnlineAppendix.tex:206:210", "OnlineAppendix", "theory.md:605:609"),
    ("App. B opening (mixed scenario)", "paper/OnlineAppendix.tex:480:480", "OnlineAppendix", "theory.md:1163:1163"),
    ("LB1 statement", "paper/OnlineAppendix.tex:484:489", "OnlineAppendix", "theory.md:1181:1188"),
    ("LB1 proof", "paper/OnlineAppendix.tex:492:513", "OnlineAppendix", "theory.md:1192:1218"),
]

for name, tex, doc, md in PAIRS:
    t = toks(passage(tex), doc)
    m = toks(passage(md))
    # drop the Markdown heading words "Proof of Lemma X" are in both; drop leading md "Lemma n (`lab`)"
    sm = difflib.SequenceMatcher(a=t, b=m, autojunk=False)
    blocks = [op for op in sm.get_opcodes() if op[0] != "equal"]
    print(f"== {name}: paper {len(t)} tokens, theory.md {len(m)} tokens, differing blocks {len(blocks)}")
    for op, i1, i2, j1, j2 in blocks:
        print(f"   {op}: paper '{' '.join(t[max(0,i1-5):i1])} [[{' '.join(t[i1:i2])}]]' vs theory.md [[{' '.join(m[j1:j2])}]]")
