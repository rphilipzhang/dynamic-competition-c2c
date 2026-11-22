"""Figure B.1 and statement N5 on a fine grid of theta, and the wider reading of Appendix B.

Parameters of the caption of Figure B.1 (c2c.figures.FIGB1_PARAMS / FIGB1_SCENARIOS / FIGB1_PANELS):
p_{i,t} = 2, c_B = 1, beta = 0.1, X ~ U[5, 15]; GS: gamma = 2, (lambda_S, lambda_N) = (0.8, 0.2);
GN: gamma = 2, (0.2, 0.8); benchmark 0: gamma = 0. Values from c2c.closed_form.find_general_exo
at theta = 0, 0.005, ..., 1 (201 values).

Reported
  * N5, panel (b): steps of y^GN_{B,1} (all negative = strictly decreasing in theta).
  * N5, panels (c) and (d): sign pattern of Pi^GS - Pi^GN of the plotted retailer and where it changes
    (the crossing of Propositions 5(c2) and 6(c2)); also panel (a) (Proposition 1(ii)), which the lead
    sentence of the paragraph ("our main results ... still hold") covers.
  * Analogues of the other parts of Propositions 2, 5 and 6 at the panels' parameters: Pi^GS_A increasing
    (5a), Pi^GN_B increasing and the range of Pi^GS_B (6a), both profits above the benchmark gamma = 0
    (5b, 6b), y^0_B < y^GN_B < y^GS_B (2b).
Run from the repository root: python verification/2026-11-22_claude-opus-5-5-b/scripts/FB1_fine_theta_grid.py
"""
from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, "numerics")
from c2c import closed_form as cf  # noqa: E402
from c2c import figures as F  # noqa: E402

THETA = np.round(np.linspace(0.0, 1.0, 201), 12)
P = F.FIGB1_PARAMS


def value(quantity, ca, scenario, theta):
    gamma, lam_s, lam_n = F.FIGB1_SCENARIOS[scenario]
    out = cf.find_general_exo(P["pa1"], P["pb1"], P["pa2"], P["pb2"], float(theta), ca, P["cb"], P["beta"],
                              P["mu"], P["sigma"], gamma, lam_s, lam_n)
    return out[{"ya1": 0, "yb1": 1, "profit_a": 2, "profit_b": 3}[quantity]]


def curve(quantity, ca, scenario):
    return np.array([value(quantity, ca, scenario, t) for t in THETA])


def sign_report(name, gap):
    s = np.sign(gap)
    changes = np.nonzero(np.diff(s) != 0)[0]
    where = ", ".join(f"({THETA[j]:.3f}, {THETA[j + 1]:.3f})" for j in changes)
    print(f"  {name}: at theta=0 {gap[0]:+.6f}, at theta=1 {gap[-1]:+.6f}, sign changes {len(changes)} {where}")


def main():
    # panel (b), c_A = 0.5
    b = {s: curve("yb1", 0.5, s) for s in ("GS", "GN", "0")}
    d = np.diff(b["GN"])
    print("panel (b), c_A = 0.5: y_B1")
    print(f"  y^GN_B steps: max {d.max():+.3e} (all < 0: {bool(np.all(d < 0))}); y^GN_B from {b['GN'][0]:.6f} to {b['GN'][-1]:.6f}")
    print(f"  y^GS_B range {np.ptp(b['GS']):.4f}, steps max {np.diff(b['GS']).max():+.3e}; y^0_B range {np.ptp(b['0']):.3e}")
    print(f"  y^0_B < y^GN_B < y^GS_B at every theta: {bool(np.all(b['0'] < b['GN']) and np.all(b['GN'] < b['GS']))}")
    # panel (a), c_A = 0.5
    a = {s: curve("ya1", 0.5, s) for s in ("GS", "GN")}
    print("panel (a), c_A = 0.5: y_A1")
    sign_report("y^GS_A - y^GN_A", a["GS"] - a["GN"])
    print(f"  y^GS_A, y^GN_A strictly increasing: {bool(np.all(np.diff(a['GS']) > 0))}, {bool(np.all(np.diff(a['GN']) > 0))}")
    # panel (c), c_A = 0.1: retailer A's profit
    c = {s: curve("profit_a", 0.1, s) for s in ("GS", "GN")}
    c0 = np.array([value("profit_a", 0.1, "0", t) for t in THETA])
    print("panel (c), c_A = 0.1: Pi_A")
    sign_report("Pi^GS_A - Pi^GN_A", c["GS"] - c["GN"])
    print(f"  Pi^GS_A strictly increasing: {bool(np.all(np.diff(c['GS']) > 0))}; Pi^GN_A min step {np.diff(c['GN']).min():+.3e}")
    print(f"  min over theta of Pi^GS_A - Pi^0_A {np.min(c['GS'] - c0):.4f}, of Pi^GN_A - Pi^0_A {np.min(c['GN'] - c0):.4f}")
    # panel (d), c_A = 0.92: retailer B's profit
    dd = {s: curve("profit_b", 0.92, s) for s in ("GS", "GN")}
    d0 = np.array([value("profit_b", 0.92, "0", t) for t in THETA])
    print("panel (d), c_A = 0.92: Pi_B")
    sign_report("Pi^GS_B - Pi^GN_B", dd["GS"] - dd["GN"])
    print(f"  Pi^GN_B strictly increasing: {bool(np.all(np.diff(dd['GN']) > 0))}; Pi^GS_B range {np.ptp(dd['GS']):.4e}, "
          f"min step {np.diff(dd['GS']).min():+.3e}")
    print(f"  min over theta of Pi^GS_B - Pi^0_B {np.min(dd['GS'] - d0):.4f}, of Pi^GN_B - Pi^0_B {np.min(dd['GN'] - d0):.4f}")


if __name__ == "__main__":
    main()
