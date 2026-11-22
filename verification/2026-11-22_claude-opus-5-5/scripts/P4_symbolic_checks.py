"""Proposition 4: symbolic re-derivation of dE[R^N_1]/dtheta, its printed prefactor, the
linearity of g_R^N in theta, g_R^N(0) as a quadratic in gamma with negative leading
coefficient, and the printed g_R^N(1) > 0, from the closed forms of Lemma 3 under A10.
Followed by the threshold gamma^R and the location of the minimum at sample points.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5/scripts/P4_symbolic_checks.py
"""
from __future__ import annotations

import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
from shared_sec4_closed_forms import (pa1, pb1, pa2, pb2, cA, cB, aA1, aA2, aB1, aB2, th, g, mu, sg,
                                 quantities, P_N, D_N)

mA, mB = pa2 - cA, pb2 - cB
X1 = cB * pa1 - cA * pb1
W = aA2 * cB * mA - aB2 * cA * mB
zero = lambda e: sp.cancel(sp.together(e)) == 0
QN = quantities("N")
ER1 = QN["RA"] + QN["RB"]
print("mu - E[R^N_1] == sigma (aA1 + theta aB1) r_A^2 + sigma (1 - theta) aB1 r_B^2:",
      zero(mu - ER1 - (sg * (aA1 + th * aB1) * QN["rA"]**2 + sg * (1 - th) * aB1 * QN["rB"]**2)))
dER = sp.diff(ER1, th)
bracket = cA * (pb1 - (aA2 - 1) * g * pb2) - cB * (g * (-2 * aA2 * cA + cA + aA2 * pa2) + pa1)
print("printed bracket == -(X1 + gamma W) < 0:", zero(bracket + X1 + g * W))
pref = -aB1 * bracket * sg / ((aA2 * g * cA - pa1 - aA2 * g * pa2)**2 * D_N**3)
gN = sp.cancel(sp.together(dER / pref))
print("g_R^N = dE/dtheta / prefactor is a polynomial:", sp.denom(gN) == 1,
      "; degree in theta:", sp.Poly(sp.expand(gN), th).degree(), "; degree in gamma:", sp.Poly(sp.expand(gN), g).degree())
g0 = sp.Poly(sp.expand(gN.subs(th, 0)), g)
print("g_R^N(0) degree in gamma:", g0.degree())
c2, c1, c0 = g0.all_coeffs()
print("  gamma^2 coefficient == -aB2 mB W  (so d2/dgamma2 = -2 aB2 mB W < 0):", zero(c2 + aB2 * mB * W))
print("  gamma^1 coefficient:", sp.factor(c1))
print("  gamma^0 coefficient == c_A p_B1^2 + c_B p_A1 p_B1 > 0:", zero(c0 - (cA * pb1**2 + cB * pa1 * pb1)))
printed_g1 = pb1 * (cA * pb1 + cB * pa1) + g * pb1 * (cB * (-2 * aA2 * cA + cA + aA2 * pa2) + (aA2 - 1) * cA * pb2)
print("g_R^N(1) equals the printed expression:", zero(gN.subs(th, 1) - printed_g1))
print("  printed g_R^N(1) == p_B1 (c_A p_B1 + c_B p_A1) + gamma p_B1 W > 0:",
      zero(printed_g1 - (pb1 * (cA * pb1 + cB * pa1) + g * pb1 * W)))
# gamma^R: the largest root of g_R^N(0); it depends on prices and costs only
print("free symbols of g_R^N(0):", sorted(str(s) for s in g0.as_expr().free_symbols))


def point(ca, cb, pb, lam, beta):
    PA = [p * (ca + (cb - ca) * l) / cb for p, l in zip(pb, lam)]
    return {pa1: PA[0], pb1: pb[0], pa2: PA[1], pb2: pb[1], cA: ca, cB: cb,
            aA1: Fr(1, 2) + beta * (pb[0] - PA[0]), aA2: Fr(1, 2) + beta * (pb[1] - PA[1]), mu: Fr(10), sg: Fr(4)}


cases = {
    "regular": point(Fr(1), Fr(3, 2), (Fr(4), Fr(5)), (Fr(1, 2), Fr(1, 3)), Fr(1, 10)),
    "A11 binds both periods": point(Fr(1), Fr(3, 2), (Fr(4), Fr(5)), (Fr(0), Fr(0)), Fr(1, 10)),
    "equal prices": point(Fr(1), Fr(3, 2), (Fr(4), Fr(5)), (Fr(1), Fr(1)), Fr(1, 10)),
    "c_A/c_B near 1": point(Fr(999, 1000), Fr(1), (Fr(3, 2), Fr(2)), (Fr(1, 2), Fr(1, 2)), Fr(1, 10)),
}
for name, sub in cases.items():
    p0 = sp.Poly(g0.as_expr().subs(sub), g)
    roots = sorted(float(sp.re(r)) for r in p0.nroots() if abs(sp.im(r)) < 1e-9 and sp.re(r) > 0)
    lin = sp.Poly(sp.expand(gN.subs(sub)), th)
    out = []
    for gam in (Fr(1, 2), Fr(10), Fr(10**4)):
        a1, a0 = [sp.Poly(c, g).eval(sp.Rational(gam.numerator, gam.denominator)) for c in lin.all_coeffs()]
        root = -a0 / a1
        out.append(f"gamma={float(gam):g}: g(0)={'+' if a0 > 0 else '-'}, root theta={float(root):.6f}")
    print(f"probe [{name}] gamma^R = {roots[-1] if roots else None}; " + "; ".join(out))
