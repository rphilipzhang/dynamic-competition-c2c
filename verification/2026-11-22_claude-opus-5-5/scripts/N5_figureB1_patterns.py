"""N5 and FB1: the patterns of Figure B.1 that Online Appendix B describes, beyond the crossing
pattern that the repository check tests, and Figure 1 shape facts used by N2.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5/scripts/N5_figureB1_patterns.py

Prints, from the port (c2c.figures, in memory):
  - step signs of every Figure B.1 series (monotonicity in theta),
  - the crossing intervals of panels (a), (c), (d) and a fine-grid location of each crossing,
  - the analogues of Proposition 5(a) and 6(a): Pi_A in GS increasing, Pi_B in GN increasing, Pi_B in GS nearly flat,
  - the A11 / fractile conditions at the Figure B.1 parameters (Lemma B.1 branch),
  - Figure 1(a),(c): the S series of the plotted retailer (P5(a): increasing; P6(a): constant).
"""
import sys

import numpy as np
from scipy import optimize

sys.path.insert(0, "numerics")
from c2c import closed_form as cf   # noqa: E402
from c2c import figures as F        # noqa: E402

b1 = F.figureB1_data()
print("== Figure B.1 series: step signs over theta = 0, 0.1, ..., 1 (+ rising, - falling, 0 flat)")
for col in b1.columns[1:]:
    d = np.diff(b1[col].to_numpy())
    print(f"{col:5s}: {''.join('+' if v > 0 else '-' if v < 0 else '0' for v in d)}  range {np.ptp(b1[col]):.6g}")

p = F.FIGB1_PARAMS


def series(quantity, ca, scen, theta):
    g, ls, ln = F.FIGB1_SCENARIOS[scen]
    k = {"ya1": 0, "yb1": 1, "profit_a": 2, "profit_b": 3}[quantity]
    return cf.find_general_exo(p["pa1"], p["pb1"], p["pa2"], p["pb2"], theta, ca, p["cb"], p["beta"], p["mu"], p["sigma"], g, ls, ln)[k]


print("\n== Crossings GS - GN (fine root by Brent between the bracketing grid nodes)")
for panel in ("a", "c", "d"):
    q, ca, _ = F.FIGB1_PANELS[panel]
    gap = (b1[f"{panel}_GS"] - b1[f"{panel}_GN"]).to_numpy()
    j = int(np.nonzero(np.diff(np.sign(gap)) != 0)[0][0])
    root = optimize.brentq(lambda t: series(q, ca, "GS", t) - series(q, ca, "GN", t), b1.theta[j], b1.theta[j + 1], xtol=1e-12)
    print(f"panel {panel} ({q}, cA={ca}): gap at 0 {gap[0]:.6g}, at 1 {gap[-1]:.6g}, sign change in "
          f"[{b1.theta[j]:.1f}, {b1.theta[j + 1]:.1f}], root {root:.6f}")

print("\n== Lemma B.1 branch and fractiles at the Figure B.1 parameters")
for ca in (0.5, 0.1, 0.92):
    for scen in ("GS", "GN", "0"):
        g, ls, ln = F.FIGB1_SCENARIOS[scen]
        for th in (0.0, 1.0):
            aa2 = 0.5 + p["beta"] * (p["pb2"] - p["pa2"])
            ga, gb = g * (ls + ln * aa2), g * (ls + ln * (1 - aa2))
            gcb = g * ln * (1 - aa2)
            qa = 1 - ca / (p["pa1"] + ga * (p["pa2"] - ca))
            qb = 1 - (p["cb"] - gcb * th * (p["pb2"] - p["cb"]) * ca / (p["pa1"] + ga * (p["pa2"] - ca))) / (
                p["pb1"] + (gb - gcb * th) * (p["pb2"] - p["cb"]))
            unconstrained_b = 1 - p["cb"] / (p["pb1"] + gb * (p["pb2"] - p["cb"]))
            print(f"cA={ca} {scen:2s} theta={th}: q_A={qa:.4f} q_B={qb:.4f} (both in [0,1]: {0 <= qb <= qa <= 1}), "
                  f"A's ratio >= B's unconstrained ratio: {qa >= unconstrained_b}")

print("\n== Figure B.1(c),(d): GS and GN profits against the benchmark (gamma = 0), the analogue of Propositions 5(b), 6(b)")
for panel, q in (("c", "profit_a"), ("d", "profit_b")):
    ca = F.FIGB1_PANELS[panel][1]
    bench = np.array([series(q, ca, "0", float(t)) for t in b1.theta])
    print(f"panel {panel}: min(GS - 0) {np.min(b1[f'{panel}_GS'] - bench):.4f}, min(GN - 0) {np.min(b1[f'{panel}_GN'] - bench):.4f}")

print("\n== Figure 1(a),(c): the plotted retailer's Scenario S and N profits over theta")
d1 = F.figure1_data()
for panel in ("a", "c"):
    for col in ("profit_S", "profit_N"):
        s = d1[d1.panel == panel].sort_values("theta")[col].to_numpy()
        print(f"panel {panel} {col}: steps {''.join('+' if v > 0 else '-' if v < 0 else '0' for v in np.diff(s))}, range {np.ptp(s):.3g}")
