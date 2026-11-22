"""F1 and N1 to N4: how the two-price game of Section 5.3 is solved at the points of Figure 1,
how robust the selected equilibria are, and whether the statements survive a finer theta grid.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5/scripts/F1_price_game_details.py

Uses the port (c2c.pricing, c2c.figures) only in memory. Prints
  - per panel, the equilibrium prices (pa1, pb1, pa2, pb2) in S and N, and whether they vary with theta,
  - the smallest strict deviation loss at the selected first-period equilibrium (a margin against ties),
  - the number of pure first-period equilibria of each 2x2 game,
  - a fine theta grid (0..1 step 0.005): solver failures, uniqueness, split ratios, sign changes of the gap,
  - the crossings of the recomputed gap against a linear interpolation of the published points.
"""
import sys
import warnings

import numpy as np
import pandas as pd

sys.path.insert(0, "numerics")
from c2c import figures as F                       # noqa: E402
from c2c.pricing import PricingError, pricing_equilibrium   # noqa: E402

P = F.FIG1_PARAMS
BETA = P["beta"]


def solve(scen, theta, ca, gamma):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        res = pricing_equilibrium(scen, P["prices"], theta, ca, P["cb"], BETA, P["mu"], P["sigma"], gamma)
    return res, len(w)


def margin(res):
    """Smallest loss from a unilateral first-period price deviation at each pure equilibrium."""
    pa, pb = res["payoff_a"], res["payoff_b"]
    out = []
    for (p1a, p1b) in res["period1_prices"]:
        i = list(P["prices"]).index(p1a)
        j = list(P["prices"]).index(p1b)
        la = pa[i, j] - pa[1 - i, j]
        lb = pb[i, j] - pb[i, 1 - j]
        out.append(min(la, lb))
    return out


print("== Figure 1 points: equilibrium prices, number of equilibria, margins, warnings")
for panel, (ret, ca, gamma) in F.FIG1_PANELS.items():
    rows = []
    for th in F.FIG1_THETA:
        for s in ("S", "N"):
            res, nw = solve(s, float(th), ca, gamma)
            rows.append(dict(theta=float(th), s=s, n_eq=res["total_profits"].shape[0], warn=nw,
                             prices=tuple(res["period1_prices"][0]) + tuple(res["period2_prices"]),
                             margin=min(margin(res)) if res["total_profits"].shape[0] else np.nan))
    df = pd.DataFrame(rows)
    for s in ("S", "N"):
        d = df[df.s == s]
        print(f"panel {panel} ({ret}, cA={ca}, gamma={gamma}) {s}: price paths {sorted(set(d.prices))}, "
              f"#eq {sorted(set(d.n_eq))}, warnings {int(d.warn.sum())}, min deviation loss {d.margin.min():.4g}")

print("\n== Fine grid theta = 0, 0.005, ..., 1")
fine = np.round(np.linspace(0, 1, 201), 10)
for panel, (ret, ca, gamma) in F.FIG1_PANELS.items():
    k = "AB".index(ret)
    gaps, fails, multi, warns, unequal_split, changes = [], 0, 0, 0, 0, 0
    paths = {"S": set(), "N": set()}
    for th in fine:
        prof = {}
        ok = True
        for s in ("S", "N"):
            try:
                res, nw = solve(s, float(th), ca, gamma)
            except PricingError:
                fails += 1
                ok = False
                break
            warns += nw
            if res["total_profits"].shape[0] != 1:
                multi += 1
                ok = False
                break
            pa1, pb1 = res["period1_prices"][0]
            pa2, pb2 = res["period2_prices"]
            paths[s].add((pa1, pb1, pa2, pb2))
            if (0.5 + BETA * (pb1 - pa1)) != (0.5 + BETA * (pb2 - pa2)):
                unequal_split += 1
            if (pa1, pb1) != (pa2, pb2):
                changes += 1
            prof[s] = res["total_profits"][0][k]
        gaps.append(prof["N"] - prof["S"] if ok else np.nan)
    g = np.array(gaps)
    sc = np.nonzero(np.diff(np.sign(g)) != 0)[0]
    print(f"panel {panel}: solver errors {fails}, non-unique {multi}, warnings {warns}, unequal splits {unequal_split}, "
          f"price changes across periods {changes}, price paths S {sorted(paths['S'])} N {sorted(paths['N'])}, "
          f"gap at 0 {g[0]:.6g}, at 1 {g[-1]:.6g}, min gap {np.nanmin(g):.6g}, sign changes between "
          f"{[(float(fine[j]), float(fine[j + 1])) for j in sc]}")

print("\n== Crossings: recomputed (Brent, as the MATLAB code) vs linear interpolation of the published points")
pub = pd.read_csv("numerics/figures/published_data.csv", dtype={"figure": str})
cross = F.figure1_crossings()
for panel in "abcd":
    s = pub[(pub.figure == "1") & (pub.panel == panel) & (pub.series == "Scenario S")].sort_values("theta")
    n = pub[(pub.figure == "1") & (pub.panel == panel) & (pub.series == "Scenario N")].sort_values("theta")
    th = s.theta.to_numpy()
    gap = n.value.to_numpy() - s.value.to_numpy()
    roots = []
    for j in np.nonzero(np.diff(np.sign(gap)) != 0)[0]:
        roots.append(th[j] - gap[j] * (th[j + 1] - th[j]) / (gap[j + 1] - gap[j]))
    print(f"panel {panel}: recomputed {cross[panel]}, published (linear interpolation) {[round(r, 4) for r in roots]}, "
          f"published gap at first/last point {gap[0]:.4f} / {gap[-1]:.4f}, min published gap {gap.min():.4f}")

print("\n== Recomputed vs published values, per panel (max abs difference to 4-decimal rounding and to unrounded)")
data = F.figure1_data()
for panel in "abcd":
    mine = data[data.panel == panel].sort_values("theta")
    w4 = wr = 0.0
    for lab, col in (("Scenario S", "profit_S"), ("Scenario N", "profit_N")):
        v = pub[(pub.figure == "1") & (pub.panel == panel) & (pub.series == lab)].sort_values("theta").value.to_numpy()
        w4 = max(w4, float(np.abs(v - mine[col].round(4).to_numpy()).max()))
        wr = max(wr, float(np.abs(v - mine[col].to_numpy()).max()))
    print(f"panel {panel}: {w4:.3g} (4-decimal), {wr:.3g} (unrounded)")

print("\n== Section 5.3 text, Figure 1(b): first-period profit of A in S vs N at the plotted points (c_A=0.1, gamma=2)")
from c2c import closed_form as cf   # noqa: E402
for th in (0.01, 0.5, 0.99):
    out = []
    for s in ("S", "N"):
        res, _ = solve(s, th, 0.10, 2.0)
        pa1, pb1 = res["period1_prices"][0]
        pa2, pb2 = res["period2_prices"]
        a = (pa1, pb1, pa2, pb2, th, 0.10, P["cb"], BETA, P["mu"], P["sigma"], 2.0)
        fp = cf.first_period_s(*a) if s == "S" else cf.first_period_n(*a)
        ya1, yb1, la, lb = fp[:4]
        out.append(f"{s}: prices {pa1, pb1, pa2, pb2}, period-1 profit of A {pa1 * (ya1 - la) - 0.10 * ya1:.4f}, "
                   f"total {res['total_profits'][0][0]:.4f}")
    print(f"theta={th}: " + " | ".join(out))
