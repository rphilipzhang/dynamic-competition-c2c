"""F1: the first-period inventory equilibria behind every cell of the Figure 1 payoff matrices,
at all 44 plotted points (the repository check uses 3 values of theta), from the model primitives.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5/scripts/F1_inventory_equilibria_all_points.py

For each panel, theta of Figure 1, scenario S and N, and first-period price pair in {2, 4}^2:
the orders of section4.claimed_first_period at the solver's second-period prices, and
primitives.nash_gap of the two-period payoffs of section4.Game (built from primitives.py).
Also the largest difference between the solver's payoff matrix and the model payoff at those orders.
"""
import sys

import numpy as np

sys.path.insert(0, "numerics")
from c2c import figures as F                                    # noqa: E402
from c2c import primitives as pm                                # noqa: E402
from c2c.pricing import pricing_equilibrium                     # noqa: E402
from c2c.section4 import Game, Params, claimed_first_period    # noqa: E402

p = F.FIG1_PARAMS
dist = pm.Uniform(p["mu"] - p["sigma"], p["mu"] + p["sigma"])
worst_gain = worst_dist = worst_pay = 0.0
games = b_high = 0
for panel, (ret, ca, gamma) in F.FIG1_PANELS.items():
    for th in F.FIG1_THETA:
        th = float(th)
        for s in ("S", "N"):
            res = pricing_equilibrium(s, p["prices"], th, ca, p["cb"], p["beta"], p["mu"], p["sigma"], gamma)
            pa2, pb2 = res["period2_prices"]
            for i, pa1 in enumerate(p["prices"]):
                for j, pb1 in enumerate(p["prices"]):
                    prm = Params(pa1, pb1, pa2, pb2, ca, p["cb"], p["beta"], th, gamma)
                    ya, yb, qa, qb, a_high = claimed_first_period(prm, s, dist.ppf)
                    b_high += (not a_high)
                    pay_a, pay_b = Game(prm, s, dist).period1_payoffs()
                    g = pm.nash_gap(pay_a, pay_b, ya, yb, 1.5 * (p["mu"] + p["sigma"]))
                    worst_gain, worst_dist = max(worst_gain, g["gain"]), max(worst_dist, g["dist"])
                    va = float(np.ravel(pay_a(np.array([ya]), yb))[0])
                    vb = float(np.ravel(pay_b(ya, np.array([yb])))[0])
                    worst_pay = max(worst_pay, abs(va - res["payoff_a"][i, j]), abs(vb - res["payoff_b"][i, j]))
                    games += 1
print(f"inventory games: {games} (cells where retailer B has the higher fractile: {b_high})")
print(f"largest gain from a unilateral order deviation: {worst_gain:.3g}; largest distance of a best response to the claim: {worst_dist:.3g}")
print(f"largest |solver payoff - model payoff|: {worst_pay:.3g}")
