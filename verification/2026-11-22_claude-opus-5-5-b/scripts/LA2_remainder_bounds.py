"""Lemma A.2(a): the inventory remainders and their first two price derivatives are O(gamma^-2),
uniformly in theta (the claim of the joint proof that Proposition 8 differentiates).

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5-b/scripts/LA2_remainder_bounds.py

For four markets of section5.draw_market and one interior first-period price pair each, the
first-period inventory equilibrium of Scenario N is solved from the model's first-order conditions
(section5.inventory_equilibrium, continuation section5.SecondPeriodN, which uses no result of the paper).
Its distance r to the closed form of Lemma A.2(a) and central first differences of r in p_{B,1} and
p_{A,1} (step 0.02 (p_hi - p_lo)) are scaled by gamma^2 for gamma = 1e2, 1e3, 1e4; the central second
difference in p_{B,1} (step 0.15 (p_hi - p_lo)) is scaled by gamma^2 for gamma = 1e2, 3e2, 1e3, 3e3,
next to its rounding floor; theta = 0, 0.5, 1 - 10/gamma, 1 - 1/gamma, 1.
Bounded scaled values along gamma, uniformly over the theta column, are what O_{C^2}(gamma^-2)
uniformly in theta predicts. A remainder of order 1/gamma would grow tenfold per row.
"""
import sys
from dataclasses import replace

sys.path.insert(0, "numerics")

import numpy as np

from c2c import section5 as s5

GAMMAS = (1e2, 1e3, 1e4)


def remainder(mk, gamma, pa1, pb1):
    cont = s5.SecondPeriodN(mk, 2.0 / (gamma * mk.lo))
    assert not cont.problems, cont.problems
    claim = np.array([float(v) for v in s5.claimed_orders_n(mk, gamma, pa1, pb1)])
    ya, yb = (float(v) for v in s5.inventory_equilibrium(mk, cont, gamma, pa1, pb1, tuple(claim)))
    fa, fb = s5.marginal_profits(mk, cont, gamma, pa1, pb1, ya, yb)
    assert max(abs(float(fa)) / mk.ca, abs(float(fb)) / mk.cb) <= 1e-12 * (10 + gamma)
    return np.array([ya, yb]) - claim


rng = np.random.default_rng(7)
THETAS = (("0", lambda g: 0.0), ("0.5", lambda g: 0.5), ("1-10/g", lambda g: 1 - 10 / g),
          ("1-1/g", lambda g: 1 - 1 / g), ("1", lambda g: 1.0))
GAMMAS2 = (1e2, 3e2, 1e3, 3e3)
summary = []
for m in range(4):
    base = s5.draw_market(rng)
    pa1 = base.p_lo + rng.uniform(0.3, 0.7) * (base.p_hi - base.p_lo)
    pb1 = base.p_lo + rng.uniform(0.3, 0.7) * (base.p_hi - base.p_lo)
    h1, h2 = 0.02 * (base.p_hi - base.p_lo), 0.15 * (base.p_hi - base.p_lo)
    print(f"market {m}: c_A={base.ca:.3f} c_B={base.cb:.3f} beta={base.beta:.3f} mu={base.mu:.2f} sigma={base.sigma:.2f} "
          f"p in [{base.p_lo:.3f}, {base.p_hi:.3f}], p_1=({pa1:.3f}, {pb1:.3f})")
    print("   value and first differences (step 0.02 of the price range); max over y_A, y_B of gamma^2 |.|")
    print("    gamma    theta     r          dr/dpB      dr/dpA")
    first = {}
    for gamma in GAMMAS:
        for label, th in THETAS:
            mk = replace(base, theta=th(gamma))
            r0 = remainder(mk, gamma, pa1, pb1)
            d1 = (remainder(mk, gamma, pa1, pb1 + h1) - remainder(mk, gamma, pa1, pb1 - h1)) / (2 * h1)
            da = (remainder(mk, gamma, pa1 + h1, pb1) - remainder(mk, gamma, pa1 - h1, pb1)) / (2 * h1)
            row = [gamma ** 2 * np.abs(v).max() for v in (r0, d1, da)]
            first[(gamma, label)] = row
            print(f"   {gamma:7.0f}  {label:>7}  " + "  ".join(f"{v:10.4g}" for v in row))
    print("   second difference in p_B (step 0.15 of the price range) and its rounding floor, both times gamma^2")
    print("    gamma    theta     d2r/dpB2    floor")
    second = {}
    for gamma in GAMMAS2:
        for label, th in THETAS:
            mk = replace(base, theta=th(gamma))
            r0 = remainder(mk, gamma, pa1, pb1)
            jitter = np.abs(remainder(mk, gamma, pa1, pb1 + 1e-9 * base.p_hi) - r0).max()
            d2 = (remainder(mk, gamma, pa1, pb1 + h2) - 2 * r0 + remainder(mk, gamma, pa1, pb1 - h2)) / h2 ** 2
            second[(gamma, label)] = gamma ** 2 * np.abs(d2).max()
            floor = 4 * max(jitter, 1e-15 * base.hi) / h2 ** 2 * gamma ** 2
            print(f"   {gamma:7.0f}  {label:>7}  {second[(gamma, label)]:10.4g}  {floor:9.2g}")
    g1 = [max(first[(GAMMAS[-1], l)][k] for l, _ in THETAS) / max(first[(GAMMAS[-2], l)][k] for l, _ in THETAS) for k in range(3)]
    g2 = max(second[(GAMMAS2[-1], l)] for l, _ in THETAS) / max(second[(GAMMAS2[-2], l)] for l, _ in THETAS)
    summary.append((m, g1, g2, max(max(v) for v in first.values()), max(second.values())))
print()
for m, g1, g2, big1, big2 in summary:
    print(f"market {m}: growth of the max over theta of gamma^2 |r|, |dr/dpB|, |dr/dpA| from 1e3 to 1e4: "
          + " ".join(f"{v:.3f}" for v in g1) + f"; of gamma^2 |d2r/dpB2| from 1e3 to 3e3: {g2:.3f}; "
          f"largest scaled values {big1:.3g} (first), {big2:.3g} (second)")
