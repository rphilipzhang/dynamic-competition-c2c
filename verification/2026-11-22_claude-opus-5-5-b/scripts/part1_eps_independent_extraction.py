"""Independent, minimal re-extraction of the plotted points of the eight published EPS panels.

Written for this run without using numerics/figures/extract_published_data.py. It reads the
page body of each EPS in paper/ as text (never executes it), and
  * takes every stroked path "<colour> [dash] ... <w> LW N x y M x y L ... S" with line width >= 2
    and at least 5 vertices (a path without a colour operator is black) as a data polyline (legend samples have 2 vertices),
  * takes every tick label "[1 0 0 1 X Y] CT ... (label) t" and calibrates each axis by a
    least-squares line through (label anchor coordinate, label value),
  * labels series by colour: red = Scenario S / GS, blue = Scenario N / GN, black = Scenario 0.
    (The legend text is drawn as glyph outlines; the colour-to-label map was read off the
    rendered panels in verification/<run>/build/*-eps-converted-to.pdf.)
It then compares the result with numerics/figures/published_data.csv and with the values that
c2c.figures recomputes, and prints the largest differences.
Run from the repository root:  python verification/2026-11-22_claude-opus-5-5-b/scripts/part1_eps_independent_extraction.py
"""
from __future__ import annotations

import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "numerics")
from c2c import figures as F  # noqa: E402

PANELS = {("1", "a"): "figure1.eps", ("1", "b"): "figure2.eps", ("1", "c"): "figure3.eps", ("1", "d"): "figure4.eps",
          ("B.1", "a"): "yaG.eps", ("B.1", "b"): "ybG.eps", ("B.1", "c"): "piaG.eps", ("B.1", "d"): "pibG.eps"}
NUM = r"-?[\d.]+"
PATH = re.compile(r"GS\s+(?:(?P<r>" + NUM + r") (?P<g>" + NUM + r") (?P<b>" + NUM + r") RC\s+|(?P<gray>" + NUM + r") GC\s+)?"
                  r"(?P<pre>(?:\[[^\]]*\] " + NUM + r" setdash\s+|\d+ setlinecap\s+|\d+ LJ\s+)*)"
                  r"(?P<lw>" + NUM + r") LW\s+N\s+(?P<pts>(?:" + NUM + r" " + NUM + r" [ML]\s+)+)S\b")
LABEL = re.compile(r"\[1 0 0 1 (" + NUM + r") (" + NUM + r")\] CT\s+" + NUM + r" GC\s+/Helvetica " + NUM + r" F\s+GS\s+"
                   r"\[1 0 0 1 0 0\] CT\s+" + NUM + r" " + NUM + r" moveto\s+1 -1 scale\s+\(([^()]*)\) t")


def body(path: Path) -> str:
    text = path.read_text(encoding="latin-1")
    return "\n".join(l for l in text.split("%%EndPageSetup", 1)[1].splitlines() if not l.startswith("%"))


def extract(path: Path):
    b = body(path)
    series = []
    for m in PATH.finditer(b):
        lw = float(m["lw"])
        pts = np.array([[float(v) for v in t.split()[:2]] for t in re.findall(NUM + r" " + NUM + r" [ML]", m["pts"])])
        if lw < 2 or len(pts) < 5:
            continue
        if m["r"] is not None:
            rgb = (float(m["r"]), float(m["g"]), float(m["b"]))
        elif m["gray"] is not None:
            rgb = (float(m["gray"]),) * 3
        else:
            rgb = (0.0, 0.0, 0.0)                                  # no colour operator: PostScript default black
        name = {(1.0, 0.0, 0.0): "red", (0.0, 0.0, 1.0): "blue", (0.0, 0.0, 0.0): "black"}[rgb]
        series.append((name, pts))
    labels = [(float(x), float(y), s) for x, y, s in LABEL.findall(b)]
    y_bottom = max(y for _, y, _ in labels)                       # x tick labels sit lowest on the page
    xl = [(x, float(s)) for x, y, s in labels if y == y_bottom]
    x_left = min(x for x, _, _ in labels)
    yl = [(y, float(s)) for x, y, s in labels if x == x_left and y != y_bottom]
    fx = np.polyfit([p for p, _ in xl], [v for _, v in xl], 1)
    fy = np.polyfit([p for p, _ in yl], [v for _, v in yl], 1)
    res_x = max(abs(np.polyval(fx, p) - v) for p, v in xl)
    res_y = max(abs(np.polyval(fy, p) - v) for p, v in yl)
    out = {}
    for name, pts in series:
        out[name] = (np.polyval(fx, pts[:, 0]), np.polyval(fy, pts[:, 1]))
    return out, len(xl), len(yl), res_x, res_y


def main():
    pub = pd.read_csv("numerics/figures/published_data.csv", dtype={"figure": str})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f1 = F.figure1_data()
    fb1 = F.figureB1_data()
    label_of = {"1": {"red": "Scenario S", "blue": "Scenario N"},
                "B.1": {"red": "Scenario GS", "blue": "Scenario GN", "black": "Scenario 0"}}
    worst_csv = worst_rec = 0.0
    print("panel     file          series        n  x-ticks y-ticks  max|mine-csv|  max|mine-recomputed|  max tick residual")
    for (fig, panel), fn in PANELS.items():
        ext, nx, ny, rx, ry = extract(Path("paper") / fn)
        for colour, (theta, value) in ext.items():
            lab = label_of[fig][colour]
            sub = pub[(pub.figure == fig) & (pub.panel == panel) & (pub.series == lab)].sort_values("theta")
            d_csv = max(float(np.abs(sub.theta.to_numpy() - theta).max()), float(np.abs(sub.value.to_numpy() - value).max()))
            if fig == "1":
                mine = f1[f1.panel == panel].sort_values("theta")
                rec = mine["profit_" + lab[-1]].to_numpy()
                d_th = float(np.abs(mine.theta.to_numpy() - theta).max())
            else:
                rec = fb1[f"{panel}_{lab.split()[-1]}"].to_numpy()
                d_th = float(np.abs(fb1.theta.to_numpy() - theta).max())
            d_rec = max(d_th, float(np.abs(rec - value).max()))
            worst_csv, worst_rec = max(worst_csv, d_csv), max(worst_rec, d_rec)
            print(f"{fig:>3}({panel})  {fn:<13} {lab:<13} {len(theta):>2}  {nx:>6} {ny:>7}  {d_csv:13.3e}  {d_rec:20.3e}  {max(rx, ry):.2e}")
    print(f"largest |independent extraction - published_data.csv| = {worst_csv:.3e}")
    print(f"largest |independent extraction - recomputed (unrounded)| = {worst_rec:.3e}")


if __name__ == "__main__":
    main()
