"""The numerical setting of Section 5.3 beyond the four panels of Figure 1.

Setting of the caption of Figure 1: prices {2, 4}, c_B = 1, beta = 0.1, X ~ U[5, 15]. Swept here:
gamma = 0.1, 0.2, ..., 3.0, c_A in {0.1, 0.3, 0.5, 0.7, 0.95}, theta = 0, 0.05, ..., 1, both scenarios
(3150 parameter points, 6300 price games), with c2c.pricing.pricing_equilibrium.

Reported
  * N1 ("the resulting split ratios remain constant over time"): at how many solved points
    alpha_{A,1} != alpha_{A,2}, the price paths that occur, and how often the solver refuses a
    point (no or several constant continuations) or finds no or several first-period pure
    equilibria.
  * The summary sentences of the Introduction and the Conclusion, and N2 to N4 in context: for
    c_A = 0.1 (retailer A, as in panels a, b) and c_A = 0.95 (retailer B, as in panels c, d), the sign
    of Pi^N - Pi^S at theta = 0 and theta = 1 for each gamma, i.e. whether the crossing pattern of
    Propositions 5(c2) / 6(c2) appears ("cross") or Scenario N dominates ("N>S").
  * Context for the excluded N7: the price paths of Scenarios S and N in the same setting for larger
    gamma (5, 10, 30, 100, 1000), c_A in {0.1, 0.5, 0.95}, theta in {0, 0.5, 1}: whether a path
    with a falling price occurs at the pure-S or pure-N end (N7 concerns the mixed scenarios, which
    the repository cannot solve).
Run from the repository root: python verification/2026-11-22_claude-opus-5-5-b/scripts/N1_gamma_cost_sweep.py
"""
from __future__ import annotations

import sys
import warnings
from collections import Counter

import numpy as np

sys.path.insert(0, "numerics")
from c2c import figures as F  # noqa: E402
from c2c.pricing import PricingError, pricing_equilibrium  # noqa: E402

P = F.FIG1_PARAMS
GAMMAS = np.round(np.arange(1, 31) * 0.1, 10)
COSTS = (0.1, 0.3, 0.5, 0.7, 0.95)
THETA = np.round(np.linspace(0.0, 1.0, 21), 10)


def solve(scenario, theta, ca, gamma):
    """Returns (outcome, result, number of warnings). The outcome is "ok" for exactly one
    first-period pure equilibrium, "k first-period equilibria" otherwise, or "refused"."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            res = pricing_equilibrium(scenario, P["prices"], theta, ca, P["cb"], P["beta"], P["mu"], P["sigma"], gamma)
        except PricingError:
            return "refused", None, len(caught)
    k = res["total_profits"].shape[0]
    return ("ok" if k == 1 else f"{k} first-period equilibria"), res, len(caught)


def main():
    status, paths, unequal, warned, solved, eq_checked = Counter(), Counter(), 0, 0, 0, 0
    multiple = Counter()
    pattern, all_fours = {}, {}
    for ca in COSTS:
        for gamma in GAMMAS:
            gap, fours = {}, True
            for theta in THETA:
                prof = {}
                for s in ("S", "N"):
                    st, res, nw = solve(s, float(theta), ca, float(gamma))
                    status[st] += 1
                    warned += nw > 0
                    if res is None:
                        continue
                    pa2, pb2 = res["period2_prices"]
                    for pa1, pb1 in res["period1_prices"]:            # every first-period pure equilibrium
                        eq_checked += 1
                        unequal += (0.5 + P["beta"] * (pb1 - pa1)) != (0.5 + P["beta"] * (pb2 - pa2))
                    if st != "ok":
                        multiple[(s, tuple(map(tuple, res["period1_prices"])), (pa2, pb2))] += 1
                        continue
                    solved += 1
                    pa1, pb1 = res["period1_prices"][0]
                    paths[(s, (pa1, pb1, pa2, pb2))] += 1
                    fours &= (pa1, pb1, pa2, pb2) == (4.0, 4.0, 4.0, 4.0)
                    prof[s] = res["total_profits"][0]
                if len(prof) == 2:
                    gap[float(theta)] = prof["N"] - prof["S"]
            if ca in (0.1, 0.95) and 0.0 in gap and 1.0 in gap:
                k = 0 if ca == 0.1 else 1
                g0, g1 = gap[0.0][k], gap[1.0][k]
                pattern[(ca, float(gamma))] = "cross" if (g0 < 0 < g1) else ("N>S" if (g0 > 0 and g1 > 0) else f"{g0:+.3g},{g1:+.3g}")
                all_fours[(ca, float(gamma))] = fours
    print(f"price games: {sum(status.values())}; outcome counts: {dict(status)}; games with a warning: {warned}")
    print(f"games with one first-period equilibrium: {solved}; first-period equilibria checked (all games): {eq_checked}; "
          f"with alpha_A1 != alpha_A2: {unequal}")
    print(f"games with several first-period equilibria (scenario, equilibria, continuation): {dict(multiple)}")
    print("price paths (scenario, (pa1, pb1, pa2, pb2)): count")
    for key, n in sorted(paths.items()):
        print(f"  {key}: {n}")
    for ca, who in ((0.1, "A"), (0.95, "B")):
        row = [f"{g:.1f}:{pattern.get((ca, float(g)), 'n/a')}{'*' if all_fours.get((ca, float(g))) else ''}" for g in GAMMAS]
        print(f"retailer {who} (c_A = {ca}): sign of Pi^N - Pi^S at theta = 0 and 1, by gamma")
        for i in range(0, len(row), 10):
            print("   " + "  ".join(row[i:i + 10]))
    print("n/a: several first-period equilibria at theta = 0 or 1. *: every equilibrium at this gamma has prices (4, 4, 4, 4)"
          " in both scenarios, so the comparison is that of the exogenous-price model at those prices.")

    large, falling = Counter(), 0
    for ca in (0.1, 0.5, 0.95):
        for gamma in (5.0, 10.0, 30.0, 100.0, 1000.0):
            for theta in (0.0, 0.5, 1.0):
                for s in ("S", "N"):
                    st, res, nw = solve(s, theta, ca, gamma)
                    if res is None:
                        large[(s, st)] += 1
                        continue
                    pa2, pb2 = res["period2_prices"]
                    for pa1, pb1 in res["period1_prices"]:
                        large[(s, (pa1, pb1, pa2, pb2), st, nw > 0)] += 1
                        falling += pa2 < pa1 or pb2 < pb1
    print("larger gamma (5 to 1000): (scenario, (pa1, pb1, pa2, pb2), outcome, warned): count")
    for key, n in sorted(large.items(), key=str):
        print(f"  {key}: {n}")
    print(f"first-period equilibria followed by a lower price of either retailer: {falling}")


if __name__ == "__main__":
    main()
