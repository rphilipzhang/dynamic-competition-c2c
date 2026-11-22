"""Part 1: compare theory.md with the LaTeX sources, token by token.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5-b/scripts/part1_theory_vs_tex.py

For each part of theory.md that must be the paper's text (the model, the setup paragraphs,
and the Statement and Proof of each of the 16 results) the script extracts the matching
LaTeX, resolves \\ref and \\eqref with numerics/paper_labels.json (checked against a fresh
build by part1_label_map.py), normalises markup on both sides, tokenises (TeX commands,
words, numbers, single characters; whitespace dropped) and prints every span where the
token sequences differ. It also checks that every quoted sentence of the section
*Assumptions* occurs in the normalised LaTeX.

Normalisation removes only markup: $, environments, \\label, \\tag, alignment & and \\\\,
spacing commands, bold/italic markup, list markers, end-of-proof marks, Markdown
headings, the header line "**Lemma 1** (`lem:model0`)**.**" of each statement, and
citation syntax (\\citep[pre][]{a,b} is written [pre @a; @b] as in theory.md).
"""
from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

LABELS = json.loads(Path("numerics/paper_labels.json").read_text(encoding="utf-8"))
MS = Path("paper/Manuscript.tex").read_text(encoding="utf-8")
OA = Path("paper/OnlineAppendix.tex").read_text(encoding="utf-8")
TH = Path("theory.md").read_text(encoding="utf-8")


def strip_comments(t: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", t)


def braced(t: str, i: int) -> int:
    """Index just after the brace group that starts at t[i] == '{'."""
    depth = 0
    for j in range(i, len(t)):
        if t[j] == "{":
            depth += 1
        elif t[j] == "}":
            depth -= 1
            if depth == 0:
                return j + 1
    raise ValueError("unbalanced")


def replace_command(t: str, cmd: str, fn) -> str:
    out, i = [], 0
    pat = re.compile(r"\\" + cmd + r"(?![A-Za-z])\s*")
    while True:
        m = pat.search(t, i)
        if not m:
            out.append(t[i:])
            return "".join(out)
        out.append(t[i:m.start()])
        j = m.end()
        if j < len(t) and t[j] == "{":
            k = braced(t, j)
            out.append(fn(t[j + 1:k - 1]))
            i = k
        else:
            out.append(fn(""))
            i = j


def resolve_refs(t: str, doc: str) -> str:
    def num(lbl):
        for d in (doc, "Manuscript", "OnlineAppendix"):
            if lbl in LABELS.get(d, {}):
                return LABELS[d][lbl]["number"]
        return "??" + lbl
    t = re.sub(r"\\eqref\{([^}]*)\}", lambda m: "(" + num(m.group(1)) + ")", t)
    t = re.sub(r"\\ref\{([^}]*)\}", lambda m: num(m.group(1)), t)
    return t


def cites(t: str) -> str:
    def keys(s):
        return "; ".join("@" + k.strip() for k in s.split(","))
    t = re.sub(r"\\citep\[([^\]]*)\]\[\]\{([^}]*)\}", lambda m: "[" + m.group(1) + " " + keys(m.group(2)) + "]", t)
    t = re.sub(r"\\citep\{([^}]*)\}", lambda m: "[" + keys(m.group(1)) + "]", t)
    t = re.sub(r"\\cite\{([^}]*)\}", lambda m: keys(m.group(1)), t)
    return t


def common(t: str) -> str:
    t = t.replace("``", '"').replace("''", '"').replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = t.replace("---", "—").replace("--", "–")
    t = re.sub(r"\\(label|tag)\{[^}]*\}", " ", t)
    t = re.sub(r"\\(begin|end)\{[^}]*\}(\[[^\]]*\])?", " ", t)
    t = re.sub(r"\\(hspace|vspace)\*?\{[^}]*\}", " ", t)
    t = re.sub(r"\\\\(\[[^\]]*\])?", " ", t)
    t = t.replace("\\noindent", " ")
    t = re.sub(r"\\(nonumber|notag|qquad|quad|displaystyle|qed|Halmos|medskip|smallskip|bigskip|par)(?![A-Za-z])", " ", t)
    t = re.sub(r"\\[,;:! ]", " ", t)
    t = t.replace("\\[", " ").replace("\\]", " ").replace("\\(", " ").replace("\\)", " ").replace("\\&", " ").replace("&", " ")
    t = t.replace("$", " ").replace("*", " ").replace("~", " ").replace("∎", " ")
    t = t.replace("\\{", " LBRACE ").replace("\\}", " RBRACE ")
    return t


def norm_tex(t: str, doc: str) -> str:
    t = strip_comments(t)
    t = resolve_refs(t, doc)
    t = cites(t)
    t = replace_command(t, "footnote", lambda s: "[Footnote: " + s + "]")
    for c in ("textbf", "emph", "textit", "paragraph"):
        t = replace_command(t, c, lambda s: s)
    t = re.sub(r"\\(bf|it|em)(?![A-Za-z])", " ", t)
    t = re.sub(r"\\item\s*(\[[^\]]*\])?", lambda m: " " + (m.group(1) or "")[1:-1] + " ", t)
    t = t.replace("\\S", "§")
    t = re.sub(r"\\(sub)*section\*?\{[^}]*\}", " ", t)
    return common(t)


def norm_md(t: str) -> str:
    t = re.sub(r"^#+ .*$", " ", t, flags=re.M)
    t = re.sub(r"^\*\*(Lemma|Proposition) [A-Z0-9.]+\*\* \(`[^`]*`\)\*\*\.\*\*", " ", t, flags=re.M)
    t = re.sub(r"^\s*- ", " ", t, flags=re.M)
    t = t.replace("\\{", " LBRACE ").replace("\\}", " RBRACE ")
    return common(t)


TOKEN = re.compile(r"\\[A-Za-z]+|[A-Za-z]+|\d+|\S")


KEEP_BRACES = False


def tokens(t: str) -> list[str]:
    toks = TOKEN.findall(t)
    if KEEP_BRACES:
        return toks
    # braces are grouping only; dropping them avoids noise such as {\bf X} vs X
    return [x for x in toks if x not in ("{", "}")]


def compare(name: str, md: str, tex: str, doc: str) -> int:
    a, b = tokens(norm_md(md)), tokens(norm_tex(tex, doc))
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    diffs = [op for op in sm.get_opcodes() if op[0] != "equal"]
    print(f"\n=== {name}: {len(a)} tokens in theory.md, {len(b)} in TeX, {len(diffs)} differing spans")
    for tag, i1, i2, j1, j2 in diffs:
        ctx = " ".join(a[max(0, i1 - 6):i1])
        print(f"  [{tag}] after '...{ctx}'")
        print(f"      theory.md: {' '.join(a[i1:i2])[:600]}")
        print(f"      TeX      : {' '.join(b[j1:j2])[:600]}")
    return len(diffs)


def md_section(start: str, end: str | None) -> str:
    i = TH.index(start)
    j = TH.index(end, i + len(start)) if end else len(TH)
    return TH[i + len(start):j]


def md_block(rid: str, part: str) -> str:
    sec = md_section(f"\n### {rid}\n", None)
    nxt = re.search(r"\n## |\n### ", sec)
    sec = sec[:nxt.start()] if nxt else sec
    i = sec.index(f"#### {part}\n")
    rest = sec[i + len(part) + 6:]
    k = rest.find("\n#### ")
    return rest if k < 0 else rest[:k]


def env_with_label(t: str, env: str, label: str) -> str:
    for m in re.finditer(r"\\begin\{" + env + r"\}(.*?)\\end\{" + env + r"\}", t, flags=re.S):
        if "\\label{" + label + "}" in m.group(1):
            return m.group(1)
    raise KeyError(label)


PROOF_STARTS = {
    "L1": "{\\bf Proof of Lemma 1}", "L2": "{\\bf Proof of Lemma 2}", "L3": "{\\bf Proof of Lemma 3}",
    "L4": "{\\bf Proof of Lemma 4: (a).}", "P1": "{\\bf Proof of Proposition 1: }",
    "P2": "{\\noindent\\bf Proof of Proposition 2: (a).}", "P3": "{\\bf Proof of Proposition 3: (a).}",
    "P4": "{\\bf Proof of Proposition 4:}", "P5": "{\\bf Proof of Proposition 5: (a).}",
    "P6": "{\\bf Proof of Proposition 6: (a).}",
    "LA1": "\\noindent\\textbf{Proof of Lemmas \\ref{lem:modelS-g}--\\ref{lem:modelN-g}.}",
    "P7": "{\\bf Proof of Proposition 7: }", "P8": "{\\bf Proof of Proposition 8: }",
    "P9": "{\\bf Proof of Proposition 9: }", "LB1": "{\\bf Proof of Lemma \\ref{lem:modelg}: }",
}


def proof_segment(rid: str) -> str:
    """The Online Appendix text from the proof heading of rid to the next proof heading or sectioning command."""
    start = OA.index(PROOF_STARTS[rid])
    ends = [OA.find(v, start + 5) for v in PROOF_STARTS.values()]
    ends += [OA.find(s, start + 5) for s in ("\\subsection{", "\\section{", "\\begin{lemma}", "Next, we test the robustness")]
    end = min([e for e in ends if e > start] + [len(OA)])
    return OA[start:end]


RESULTS = [
    ("L1", "lemma", "lem:model0", MS, "Lemma 1"), ("L2", "lemma", "lem:models", MS, "Lemma 2"),
    ("L3", "lemma", "lem:modeln", MS, "Lemma 3"), ("L4", "lemma", "lem:oneside", MS, "Lemma 4"),
    ("P1", "proposition", "prop:yacompare", MS, "Proposition 1"), ("P2", "proposition", "prop:ybcompare", MS, "Proposition 2"),
    ("P3", "proposition", "prop:indsales", MS, "Proposition 3"), ("P4", "proposition", "prop:tsales", MS, "Proposition 4"),
    ("P5", "proposition", "prop:pfta", MS, "Proposition 5"), ("P6", "proposition", "prop:pftb", MS, "Proposition 6"),
    ("LA1", "lemma", "lem:modelS-g", OA, "Lemmas \\ref{lem:modelS-g}–\\ref{lem:modelN-g}"),
    ("LA2", "lemma", "lem:modelN-g", OA, None),
    ("P7", "proposition", "prop:orderprice2", MS, "Proposition 7"), ("P8", "proposition", "prop:orderprice1", MS, "Proposition 8"),
    ("P9", "proposition", "prop:price", MS, "Proposition 9"), ("LB1", "lemma", "lem:modelg", OA, "Lemma \\ref{lem:modelg}"),
]


def main() -> None:
    total = 0
    # Model: Section 3 of the manuscript
    ms3 = MS[MS.index("\\section{General Model Framework}"):MS.index("\\section{Exogenous Price Model}")]
    total += compare("Model (Section 3)", md_section("## Model (Section 3 of the paper)\n", "## Notation and assumptions"), ms3, "Manuscript")
    # Setup paragraphs
    s4 = MS[MS.index("\\section{Exogenous Price Model}"):MS.index("\\subsection{Equilibrium Analysis}")]
    total += compare("Setup of Section 4", md_section("### Setup of the Exogenous Price Model (Section 4, opening paragraph)\n", "### L1"), s4, "Manuscript")
    s5 = MS[MS.index("\\section{Endogenous Price Model}"):MS.index("\\subsection{The Impact of Pricing on Order Quantities}")]
    total += compare("Setup of Section 5", md_section("### Setup of the Endogenous Price Model (Section 5, opening paragraphs)\n", "### Notation used in the proofs"), s5, "Manuscript")
    a2 = OA[OA.index("\\subsection{Proof of Statements in Section 5}"):OA.index("\\begin{lemma} \\label{lem:modelS-g}")]
    total += compare("Notation of Online Appendix A.2", md_section("### Notation used in the proofs for Section 5 (Online Appendix A.2, opening paragraph)\n", "### LA1"), a2, "OnlineAppendix")
    b0 = OA[OA.index("\\section{Scenario with a Mix"):OA.index("\\begin{lemma}\n\\label{lem:modelg}")]
    total += compare("Definition of the mixed scenario (Online Appendix B)", md_section("### Definition of the mixed scenario (Online Appendix B, opening paragraph)\n", "### LB1"), b0, "OnlineAppendix")
    for rid, env, label, src, proofkey in RESULTS:
        doc = "Manuscript" if src is MS else "OnlineAppendix"
        total += compare(f"{rid} Statement", md_block(rid, "Statement"), env_with_label(src, env, label), doc)
        if proofkey is None:
            continue
        total += compare(f"{rid} Proof", md_block(rid, "Proof"), proof_segment(rid), "OnlineAppendix")
    # Assumptions: every quoted sentence occurs in the paper
    print("\n=== Assumptions: quoted sentences")
    paper = " ".join(tokens(norm_tex(MS, "Manuscript")) + tokens(norm_tex(OA, "OnlineAppendix")))
    block = md_section("### Assumptions\n", "### Implicit conditions")
    for line in block.splitlines():
        m = re.match(r"- \*\*(A\d+)\.", line)
        if not m:
            continue
        quotes = re.findall(r'"([^"]+)"', line)
        for q in quotes:
            parts = [p for p in re.split(r"\[Footnote: |\]$", q) if p.strip()]
            for p in parts:
                found = " ".join(tokens(norm_md(p.rstrip("]")))) in paper
                print(f"  {m.group(1)}: {'found' if found else 'NOT FOUND'}: {p[:90]}")
    print(f"\ntotal differing spans: {total}")


if __name__ == "__main__":
    main()
    # Second pass with braces kept as tokens, so that a regrouping such as \frac{a}{b}c vs
    # \frac{a}{bc} would show. Differences that are only markup braces are expected here.
    print("\n\n######## second pass: braces kept ########")
    KEEP_BRACES = True
    main()
