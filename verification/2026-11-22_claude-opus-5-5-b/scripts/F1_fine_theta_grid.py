"""Figure 1 and statements N1 to N4 between and beyond the 11 plotted values of theta.

The checks of the repository evaluate Figure 1 at theta = 0.01, 0.1, ..., 0.9, 0.99. This script
evaluates the same two-price game (c2c.figures.figure1_point, which runs c2c.pricing) at the 201
values theta = 0, 0.005, ..., 1 for each panel, and reports
  * whether the solver certifies a unique constant continuation and a unique first-period pure
    equilibrium at every theta (it raises otherwise), and whether it warns,
  * the equilibrium price paths that occur and whether alpha_{A,1} = alpha_{A,2} (N1),
  * the sign pattern of Pi^N - Pi^S of the plotted retailer and its crossings (N2, N3, N4),
  * the monotonicity of the plotted curves, for the reading of N2 that panels (a) and (c)
    "replicate" parts (a) of Propositions 5 and 6 (Pi^S_A increasing; Pi^S_B constant and
    Pi^N_B increasing),
  * for information only, retailer A's first-period profit in panel (b), which Section 5.3 uses
    to explain N3 ("suppresses retailer A's first-period profit").
Run from the repository root: python verification/2026-11-22_claude-opus-5-5-b/scripts/F1_fine_theta_grid.py
"""
from __future__ import annotations

import sys
import warnings
from collections import Counter

import numpy as np

sys.path.insert(0, "numerics")
from c2c import closed_form as cf  # noqa: E402
from c2c import figures as F  # noqa: E402

THETA = np.round(np.linspace(0.0, 1.0, 201), 12)
P = F.FIG1_PARAMS


def first_period_profit_a(scenario, prices, theta, ca, gamma):
    pa1, pb1, pa2, pb2 = prices
    fp = cf.first_period_s if scenario == "S" else cf.first_period_n
    ya, yb, left_a, left_b, *_ = fp(pa1, pb1, pa2, pb2, theta, ca, P["cb"], P["beta"], P["mu"], P["sigma"], gamma)
    return pa1 * (ya - left_a) - ca * ya


def main():
    beta = P["beta"]
    for panel, (retailer, ca, gamma) in F.FIG1_PANELS.items():
        k = "AB".index(retailer)
        gaps, s_curve, n_curve, paths, n_warn, n_err, unequal = [], [], [], Counter(), 0, 0, 0
        for th in THETA:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                try:
                    pt = F.figure1_point(float(th), ca, gamma)
                except Exception:                      # noqa: BLE001  (solver refuses the point)
                    n_err += 1
                    continue
            n_warn += len(caught)
            for s in ("S", "N"):
                pa1, pb1, pa2, pb2 = pt[s]["prices"]
                paths[(s, pt[s]["prices"])] += 1
                unequal += (0.5 + beta * (pb1 - pa1)) != (0.5 + beta * (pb2 - pa2))
            s_curve.append(pt["S"]["profits"][k])
            n_curve.append(pt["N"]["profits"][k])
            gaps.append(pt["N"]["profits"][k] - pt["S"]["profits"][k])
        gaps, s_curve, n_curve = map(np.array, (gaps, s_curve, n_curve))
        signs = np.sign(gaps)
        changes = int(np.sum(np.diff(signs) != 0))
        print(f"panel ({panel}): retailer {retailer}, c_A = {ca}, gamma = {gamma}, {len(THETA)} values of theta in [0, 1]")
        print(f"  solver refused {n_err} points, warnings {n_warn}")
        print(f"  price paths (scenario, (pa1, pb1, pa2, pb2)): {dict(paths)}")
        print(f"  pairs (theta, scenario) with alpha_A1 != alpha_A2: {unequal}")
        print(f"  Pi^N - Pi^S: at theta=0 {gaps[0]:+.6f}, at theta=1 {gaps[-1]:+.6f}, min {gaps.min():+.6f}, max {gaps.max():+.6f}, "
              f"sign changes on the grid {changes}")
        if changes:
            j = int(np.nonzero(np.diff(signs) != 0)[0][0])
            print(f"  sign change between theta = {THETA[j]:.3f} and {THETA[j + 1]:.3f}")
        ds, dn = np.diff(s_curve), np.diff(n_curve)
        print(f"  Pi^S steps: min {ds.min():+.3e}, max {ds.max():+.3e}; Pi^N steps: min {dn.min():+.3e}, max {dn.max():+.3e}; "
              f"range of Pi^S {np.ptp(s_curve):.3e}")
        if panel == "b":
            th = 0.01
            pt = F.figure1_point(th, ca, gamma)
            fa = {s: first_period_profit_a(s, pt[s]["prices"], th, ca, gamma) for s in ("S", "N")}
            print(f"  [info] theta = 0.01: retailer A's first-period profit S {fa['S']:.4f}, N {fa['N']:.4f}; "
                  f"total S {pt['S']['profits'][0]:.4f}, N {pt['N']['profits'][0]:.4f}")


if __name__ == "__main__":
    main()
