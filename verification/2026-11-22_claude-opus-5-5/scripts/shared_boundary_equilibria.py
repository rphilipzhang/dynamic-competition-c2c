"""Boundary probe of Lemmas 1, 2, 3 and B.1: the stated orders against the model at hand-built edge points.

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5/scripts/shared_boundary_equilibria.py

Hand-built points (not from the samplers of numerics/), each with theta in {0, 1/2, 1}:
  E1 equality in A11 in both periods      p_A,t = (c_A/c_B) p_B,t
  E2 equal prices in both periods         p_A,t = p_B,t (shares 1/2)
  E3 critical fractiles near the ends     c_A/c_B = 0.01 (q_A near 1), p_B/c_B = 1.001 (q_B near 0)
  E4 huge gamma (fractiles near 1)        gamma = 1e4, A11 binding in period 1 only
  E5 tiny gamma and a large share gap    gamma = 1e-3, A11 binding, beta x largest gap = 0.49
Scenarios 0 (Lemma 1), S (Lemma 2), N (Lemma 3), G with lambda_S in {0, 0.3, 1} (Lemma B.1).
Distributions on [mu - sigma, mu + sigma]: uniform at every point, beta(2,5) and truncated
normal (density positive on the interior, beta(2,5) vanishing at both ends) at E1 and E3,
theta in {0, 1}, scenarios S, N and G with lambda_S = 0.3.
For each game: `claimed_first_period` (retailer A's fractile must be the higher one, both in [0,1]),
`primitives.nash_gap` on the two-period payoffs of `section4.Game`, relative gain = gain / (mu (1+gamma)),
and the second-period game at one sales state with the orders y^0_{i,2} + Z_{i,2}.
"""
import sys
import numpy as np

sys.path.insert(0, "numerics")
from c2c import primitives as pm                                                  # noqa: E402
from c2c.section4 import Game, Params, claimed_first_period, distributions        # noqa: E402

mu, sigma = 10.0, 6.0
base = dict(cb=1.5, ca=1.0, pb1=4.4, pb2=4.6, beta=0.2)


def point(kind, theta, lam_s):
    ca, cb, pb1, pb2, beta, gamma = base["ca"], base["cb"], base["pb1"], base["pb2"], base["beta"], 2.0
    if kind == "E1":
        pa1, pa2 = ca / cb * pb1, ca / cb * pb2
    elif kind == "E2":
        pa1, pa2 = pb1, pb2
    elif kind == "E3":
        ca = 0.01 * cb
        pb1, pb2 = 1.001 * cb, 1.001 * cb
        pa1, pa2 = 0.5 * (ca / cb * pb1 + pb1), pb2
        beta = 0.45 / (pb1 - pa1)
    elif kind == "E4":
        gamma = 1e4
        pa1, pa2 = ca / cb * pb1, 0.5 * (ca / cb * pb2 + pb2)
    else:
        gamma = 1e-3
        pa1, pa2 = ca / cb * pb1, ca / cb * pb2
        beta = 0.49 / max(pb1 - pa1, pb2 - pa2)
    return Params(pa1, pb1, pa2, pb2, ca, cb, beta, theta, gamma, lam_s, 1 - lam_s)


cases = [("0", 1.0), ("S", 1.0), ("N", 0.0), ("G", 0.0), ("G", 0.3), ("G", 1.0)]
worst1 = worst2 = 0.0
games = 0
order_fail = 0
q_extremes = [1.0, 0.0]
rng = np.random.default_rng(9101)
for kind in ("E1", "E2", "E3", "E4", "E5"):
    for theta in (0.0, 0.5, 1.0):
        for scen, lam in cases:
            prm = point(kind, theta, lam)
            dists = ["uniform"] + (["beta(2,5)", "truncated normal"] if theta in (0.0, 1.0) and kind in ("E1", "E3") and (scen, lam) in (("S", 1.0), ("N", 0.0), ("G", 0.3)) else [])
            for name in dists:
                dist = distributions(mu, sigma)[name]
                ya, yb, qa, qb, a_high = claimed_first_period(prm, scen, dist.ppf)
                order_fail += not (a_high and 0 <= qb <= qa <= 1)
                q_extremes = [min(q_extremes[0], qb), max(q_extremes[1], qa)]
                game = Game(prm, scen, dist)
                pa, pb = game.period1_payoffs()
                scale = mu * (1 + prm.gamma)
                worst1 = max(worst1, pm.nash_gap(pa, pb, ya, yb, 1.5 * (mu + sigma))["gain"] / scale)
                ra1 = float(rng.uniform(0, mu + sigma))
                rb1 = float(rng.uniform(0, mu + sigma - ra1))
                p2a, p2b, *_ = game.period2_payoffs(ra1, rb1)
                _, _, y2a, y2b = game.period2_value(ra1, rb1)
                worst2 = max(worst2, pm.nash_gap(p2a, p2b, y2a, y2b, game.upper)["gain"] / scale)
                games += 1
print(f"games: {games}; claimed ordering or range violated at {order_fail}; "
      f"smallest q_B {q_extremes[0]:.4g}, largest q_A {q_extremes[1]:.6g}")
print(f"first period: max relative gain from a unilateral deviation {worst1:.2e}")
print(f"second period (one sales state per game): max relative gain {worst2:.2e}")
