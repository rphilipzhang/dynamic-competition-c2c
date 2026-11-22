"""P4 (Proposition 4): total expected first-period sales in Scenario N.

Derivation (mine): with Delta = Q1 + gamma Q2 = c_B P^N_A - c_A (p_B1 + J) and u = J (1 - theta),
  dE[R^N_1]/dtheta = alpha_B1 sigma Delta * g(theta) / [(P^N_A)^2 den^3],
  g(theta) = 2 c_A p_B1 (p_B1 + u) + Delta (p_B1 - u),  linear in theta.

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5-b/scripts/P4_symbolic_steps.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from random import Random

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared_sec4_closed_forms import (J, PN_A, aA1, aA2, aB1, aB2, ca, cb, g, mu, pa1, pa2, pb1, pb2, r_N,
                                      random_point, scen_N, sg, subs_point, th)

Q1 = cb * pa1 - ca * pb1
Q2 = aA2 * cb * (pa2 - ca) - aB2 * ca * (pb2 - cb)
Dl = Q1 + g * Q2
w = pb2 - cb
r = r_N()
den = pb1 + J * (1 - th)
u = J * (1 - th)
ER1 = mu - sg * (aA1 + th * aB1) * (ca / PN_A)**2 - sg * (1 - th) * aB1 * r**2     # from the P3 identity
rng = Random(41)
N = scen_N()
same = sum(subs_point(N["RA"] + N["RB"] - ER1, pt, {th: sp.Rational(rng.randint(0, 9), 9), g: sp.Rational(rng.randint(1, 999), 7)}) == 0
           for pt in (random_point(rng, equal_shares=(k % 2 == 0)) for k in range(8)))
print(f"E[R^N_1] = mu - sigma (a_A1 + th a_B1)(c_A/P^N_A)^2 - sigma (1-th) a_B1 r^2: exact at {same}/8 points")
dER = sp.diff(ER1, th)
gmine = 2 * ca * pb1 * (pb1 + u) + Dl * (pb1 - u)
print("dE[R^N_1]/dtheta = a_B1 sigma Delta g(theta) / [(P^N_A)^2 den^3]:",
      sp.simplify(dER - aB1 * sg * Dl * gmine / (PN_A**2 * den**3)) == 0)
bracket = ca * (pb1 - (aA2 - 1) * g * pb2) - cb * (g * (-2 * aA2 * ca + ca + aA2 * pa2) + pa1)
print("printed prefactor bracket [c_A(p_B1-(a_A2-1) gamma p_B2) - c_B(...)] = -Delta (so -a_B1[..]sigma = a_B1 sigma Delta > 0):",
      sp.expand(bracket + Dl) == 0)
print("printed denominator (a_A2 gamma c_A - p_A1 - a_A2 gamma p_A2)^2 = (P^N_A)^2:",
      sp.expand((aA2 * g * ca - pa1 - aA2 * g * pa2)**2 - PN_A**2) == 0)
print("g(theta) is linear in theta:", sp.Poly(sp.expand(gmine), th).degree() == 1)
g1_printed = pb1 * (ca * pb1 + cb * pa1) + g * pb1 * (cb * (-2 * aA2 * ca + ca + aA2 * pa2) + (aA2 - 1) * ca * pb2)
print("g(1) equals the printed g_R^N(1):", sp.expand(gmine.subs(th, 1) - g1_printed) == 0)
print("g(1) = p_B1 (c_A p_B1 + c_B p_A1 + gamma Q2) > 0:", sp.expand(gmine.subs(th, 1) - pb1 * (ca * pb1 + cb * pa1 + g * Q2)) == 0)
g0 = sp.Poly(sp.expand(gmine.subs(th, 0)), g)
print("g(0) has degree", g0.degree(), "in gamma; d^2 g(0)/d gamma^2 / 2 = -a_B2 (p_B2-c_B) Q2 (< 0):",
      sp.expand(g0.LC() + aB2 * w * Q2) == 0)

bad, n, gR_list, small_monotone = 0, 0, [], 0
for k in range(200):
    pt = random_point(rng, equal_shares=(k % 3 == 0), bind=(k % 5 == 0, k % 7 == 0), equal_prices=(k % 11 == 0))
    roots = [x for x in sp.Poly(subs_point(gmine.subs(th, 0), pt), g).real_roots() if x > 0]
    gR = max(roots) if roots else sp.Integer(0)
    gR_list.append(float(gR))
    gv = sp.Rational(int(float(gR) * 100) + 1, 100) * 2
    nodes = sorted({sp.Rational(j, 100) for j in range(101)} | {1 - sp.Rational(t, 1) / gv for t in (1, 2, 5, 10) if t < gv})
    vals = [subs_point(ER1, pt, {g: gv, th: x}) for x in nodes]
    signs = ["+" if b_ > a_ else "-" for a_, b_ in zip(vals, vals[1:]) if b_ != a_]
    pattern = "".join(s_ for i, s_ in enumerate(signs) if i == 0 or s_ != signs[i - 1])
    n += 1
    bad += pattern != "-+"
    small_monotone += int(bool(subs_point(gmine, pt, {g: sp.Rational(1, 20), th: 0}) > 0))
print(f"At gamma = 2 gamma^R (+0.02) the directions of E[R^N_1] on a theta grid are '-+' at {n - bad}/{n} points")
print("gamma^R (largest positive root of g(0)): min %.3g, median %.3g, max %.3g" % (min(gR_list), sorted(gR_list)[100], max(gR_list)))
print("points where E[R^N_1] is increasing at theta = 0 when gamma = 1/20 (threshold needed):", small_monotone, "/200")
