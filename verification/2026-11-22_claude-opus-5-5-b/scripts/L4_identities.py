"""L4: the identities behind the proof, and the inequalities at equilibria found from the model.

Run from the repository root, no arguments:
    python verification/2026-11-22_claude-opus-5-5-b/scripts/L4_identities.py

(1) SymPy: for y_A = (a_A + th a_B) z_A - th a_B z_B and y_B = a_B z_B,
    y_A/a_A - y_B/a_B = (a_A + th a_B)(z_A - z_B)/a_A  (the display of the proof of L4(a), (b)).
(2) SymPy: with y^k_{i,2} = y^0_{i,2} + Z^k_{i,2} (Lemmas 2 and 3), (y^k_{i,2} - Z^k_{i,2})/a_{i,2}
    = y^0_{i,2}/a_{i,2} for Z^S_{i,2} = gamma R_{i,1} and Z^N_{i,2} = a_{i,2} gamma R_1, which is
    the "analogous argument" for Scenario N in the second period.
(3) From the primitives only (numerics/c2c/primitives.py via section4.Game, uniform law):
    equilibria found by iterating best responses (not from the closed forms), first period
    for S and N, second period at a random sales state for S and N, at points with A11
    (random and with equality), theta in [0, 0.9]; the inequalities of L4 at those equilibria.
"""
from __future__ import annotations

import sys

import numpy as np
import sympy as sp

sys.path.insert(0, "numerics")
from c2c import primitives as pm  # noqa: E402
from c2c.section4 import Game, Params  # noqa: E402


def part1_2():
    aA, aB, th, zA, zB, g, RA, RB, a2, y0A, y0B = sp.symbols("a_A a_B theta z_A z_B gamma R_A R_B a_2 y0_A y0_B", positive=True)
    yA, yB = (aA + th * aB) * zA - th * aB * zB, aB * zB
    ok1 = sp.simplify(yA / aA - yB / aB - (aA + th * aB) * (zA - zB) / aA) == 0
    b2 = 1 - a2
    okS = all(sp.simplify(((y0 + Z) - Z) / a - y0 / a) == 0 for y0, Z, a in ((y0A, g * RA, a2), (y0B, g * RB, b2)))
    okN = all(sp.simplify(((y0 + a * g * (RA + RB)) - a * g * (RA + RB)) / a - y0 / a) == 0 for y0, a in ((y0A, a2), (y0B, b2)))
    print(f"(1) identity of the proof of L4(a)/(b): {ok1}")
    print(f"(2) second period net of Z equals the benchmark per unit of share: S {okS}, N {okN}")
    assert ok1 and okS and okN


def br_equilibrium(pay_a, pay_b, upper, y0=(0.0, 0.0), iters=200):
    ya, yb = y0
    for _ in range(iters):
        na = pm.best_response(lambda y: pay_a(y, yb), upper)[0]
        nb = pm.best_response(lambda y: pay_b(na, y), upper)[0]
        if abs(na - ya) + abs(nb - yb) < 1e-7 * upper:
            return na, nb
        ya, yb = na, nb
    raise RuntimeError("no convergence")


def part3(rng):
    worst = {"S1": np.inf, "N1": np.inf, "S2": np.inf, "N2": np.inf}
    n = 0
    for k in range(10):
        cb = rng.uniform(0.5, 3); ca = cb * rng.uniform(0.05, 0.98)
        pb1, pb2 = cb * rng.uniform(1.05, 4, 2)
        pa1, pa2 = (ca / cb * pb1, ca / cb * pb2) if k % 3 == 0 else (rng.uniform(ca / cb * pb1, pb1), rng.uniform(ca / cb * pb2, pb2))
        beta = min(0.5, rng.uniform(0, 0.45) / max(pb1 - pa1, pb2 - pa2))
        mu = rng.uniform(5, 20); sigma = mu * rng.uniform(0.1, 0.95)
        prm = Params(pa1, pb1, pa2, pb2, ca, cb, beta, theta=rng.uniform(0, 0.9), gamma=rng.uniform(0.05, 20))
        law = pm.Uniform(mu - sigma, mu + sigma)
        for scn in ("S", "N"):
            game = Game(prm, scn, law)
            ya, yb = br_equilibrium(*game.period1_payoffs(), 1.5 * (mu + sigma))
            worst[scn + "1"] = min(worst[scn + "1"], (ya / prm.aa1 - yb / (1 - prm.aa1)) / mu)
            ra1, rb1 = rng.uniform(0, mu + sigma), rng.uniform(0, mu + sigma)
            pay_a, pay_b, za, zb = game.period2_payoffs(ra1, rb1)
            ya2, yb2 = br_equilibrium(pay_a, pay_b, game.upper, (za, zb))
            worst[scn + "2"] = min(worst[scn + "2"], ((ya2 - za) / prm.aa2 - (yb2 - zb) / (1 - prm.aa2)) / mu)
            n += 1
    print(f"(3) {n} (point, scenario) pairs, equilibria by best-response iteration from the primitives: smallest value of"
          f" [y_A/a_A - y_B/a_B]/mu: period 1 S {worst['S1']:.2e}, N {worst['N1']:.2e}; period 2 net of Z: S {worst['S2']:.2e},"
          f" N {worst['N2']:.2e} (negative values above -1e-6 are rounding of the numerical best response)")
    assert min(worst.values()) > -1e-6


if __name__ == "__main__":
    part1_2()
    part3(np.random.default_rng(44))
    print("all checks passed")
