"""Proposition 1: symbolic re-derivation of every displayed formula and sign claim of the
proof, from the closed forms of Lemmas 1 to 3 under A10 (shared_sec4_closed_forms.py), and a
probe of the crossing in theta for large gamma, including boundary points.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5/scripts/P1_symbolic_checks.py
"""
from __future__ import annotations

import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
from shared_sec4_closed_forms import (pa1, pb1, pa2, pb2, cA, cB, aA1, aA2, aB1, aB2, th, g, mu, sg,
                                 quantities, tails, P_S, Q_S, P_N, D_N)

mA, mB = pa2 - cA, pb2 - cB
X1 = cB * pa1 - cA * pb1            # A11 slack, period 1 (>= 0)
X2 = cB * pa2 - cA * pb2            # A11 slack, period 2 (>= 0)
W = aA2 * cB * mA - aB2 * cA * mB   # = aA2 X2 + (aA2 - aB2) cA mB > 0 under A1, A11, I1, I2, beta > 0

Q0, QS, QN = quantities("0"), quantities("S"), quantities("N")
zero = lambda e: sp.simplify(sp.together(e)) == 0

print("W - [aA2 X2 + (aA2 - aB2) cA mB] == 0:", zero(W - (aA2 * X2 + (aA2 - aB2) * cA * mB)))

# k = 0, S: y_A = alpha_A zeta_A + theta alpha_B (zeta_A - zeta_B), slope 2 sigma alpha_B (r_B - r_A)
for name, Q in (("0", Q0), ("S", QS)):
    ok = zero(Q["yA"] - (aA1 * Q["zA"] + th * aB1 * (Q["zA"] - Q["zB"])))
    slope = sp.diff(Q["yA"], th)
    print(f"[{name}] y_A = a_A zeta_A + theta a_B (zeta_A - zeta_B): {ok}; d2y/dtheta2 == 0: {zero(sp.diff(slope, th))}")
# interpretation: sign of the slope
print("[0] (r_B - r_A) pA1 pB1 == X1:", zero((Q0["rB"] - Q0["rA"]) * pa1 * pb1 - X1))
print("[S] (r_B - r_A) P_S Q_S == X1 + gamma X2:", zero((QS["rB"] - QS["rA"]) * P_S * Q_S - (X1 + g * X2)))

# Scenario N
yN = QN["yA"]
rB = QN["rB"]
zB = QN["zB"]
dzB = sp.diff(zB, th)
print("[N] y_A = a_A zeta_A + theta a_B (zeta_A - zeta_B):", zero(yN - (aA1 * QN["zA"] + th * aB1 * (QN["zA"] - zB))))
print("[N] dy_A/dtheta == a_B (zA - zB) - theta a_B dzB/dtheta:",
      zero(sp.diff(yN, th) - (aB1 * (QN["zA"] - zB) - th * aB1 * dzB)))
print("(A.18) dzeta_B/dtheta == -(1/f) d r_B/dtheta with f = 1/(2 sigma):", zero(dzB + 2 * sg * sp.diff(rB, th)))
Nnum = aB2 * g * mB * (X1 + g * W) / P_N
print("(A.19) d r_B/dtheta == aB2 gamma mB (X1 + gamma W) / (P_N D_N^2):", zero(sp.diff(rB, th) - Nnum / D_N**2))
print("      d r_B/dtheta does not depend on theta except through D_N^2: numerator independent of theta:",
      sp.diff(sp.simplify(sp.diff(rB, th) * D_N**2), th).equals(0))
d2y = sp.diff(yN, th, 2)
print("[N] d2y_A/dtheta2 == 4 sigma aB1 N / D_N^2 + 4 sigma theta aB1 aB2 gamma mB N / D_N^3:",
      zero(d2y - (4 * sg * aB1 * Nnum / D_N**2 + 4 * sg * th * aB1 * aB2 * g * mB * Nnum / D_N**3)))

# theta = 0
d0 = (yN - QS["yA"]).subs(th, 0)
printed0 = -2 * aA1 * aB2 * g * cA * sg * mA / ((g * mA + pa1) * (aA2 * g * mA + pa1))
print("theta = 0: y^N_A - y^S_A equals the printed expression:", zero(d0 - printed0))

# theta = 1
d1 = sp.together((yN - QS["yA"]).subs(th, 1))
gA = sp.factor(sp.together(d1 * pb1 * P_S * Q_S * P_N / (2 * g * sg)))
polyg = sp.Poly(sp.expand(sp.numer(sp.together(gA))), g)
print("theta = 1: g_A^SN is a polynomial in gamma (denominator after cancel):", sp.denom(sp.together(gA)))
print("           degree in gamma:", polyg.degree())
printed_d2 = -2 * aB1 * mA * mB * (cA * ((aA2 - aB2) * cB - aA2 * pb2 + pb2) - aA2 * cB * pa2)
print("           d2 g_A^SN / dgamma2 equals printed:", zero(sp.diff(gA, g, 2) - printed_d2))
print("           printed inner bracket == -W:", zero((cA * ((aA2 - aB2) * cB - aA2 * pb2 + pb2) - aA2 * cB * pa2) + W))
coeffs = [sp.factor(c) for c in polyg.all_coeffs()]
print("           coefficients of g_A^SN (gamma^2, gamma^1, gamma^0):")
for c in coeffs:
    print("             ", c)
# constant coefficient: sign
print("           g_A^SN(0) == -cB sigma? check symbolic:", sp.factor(gA.subs(g, 0)))


# ----------------------------------------------------------------------------- numerical probe (exact)
def point(ca, cb, pb, lam, beta):
    PA = [p * (ca + (cb - ca) * l) / cb for p, l in zip(pb, lam)]
    return {pa1: PA[0], pb1: pb[0], pa2: PA[1], pb2: pb[1], cA: ca, cB: cb,
            aA1: Fr(1, 2) + beta * (pb[0] - PA[0]), aA2: Fr(1, 2) + beta * (pb[1] - PA[1]), mu: Fr(10), sg: Fr(4)}


def crossing_report(sub, gamma, n=400):
    f = sp.lambdify(th, (QS["yA"] - yN).subs(sub).subs(g, gamma), "sympy")
    vals = [sp.Rational(f(sp.Rational(k, n))) for k in range(n + 1)]
    signs = "".join("+" if v > 0 else "-" if v < 0 else "0" for v in vals)
    runs = "".join(ch for i, ch in enumerate(signs) if ch != "0" and (i == 0 or ch != signs[i - 1]))
    return vals[0] > 0, vals[-1] < 0, runs


cases = {
    "regular": point(Fr(1), Fr(3, 2), (Fr(4), Fr(5)), (Fr(1, 2), Fr(1, 3)), Fr(1, 10)),
    "A11 binds both periods": point(Fr(1), Fr(3, 2), (Fr(4), Fr(5)), (Fr(0), Fr(0)), Fr(1, 10)),
    "equal prices both periods": point(Fr(1), Fr(3, 2), (Fr(4), Fr(5)), (Fr(1), Fr(1)), Fr(1, 10)),
    "c_A/c_B near 1": point(Fr(999, 1000), Fr(1), (Fr(3, 2), Fr(2)), (Fr(1, 2), Fr(1, 2)), Fr(1, 10)),
    "tiny alpha_B": point(Fr(1), Fr(3, 2), (Fr(4), Fr(4)), (Fr(0), Fr(0)), Fr(499, 1000) / (Fr(4) - Fr(8, 3))),
}
for name, sub in cases.items():
    gpoly = sp.Poly(sp.expand(sp.numer(sp.together(gA.subs(sub)))), g)
    roots = [r for r in sp.Poly(gpoly).nroots() if abs(sp.im(r)) < 1e-12 and sp.re(r) > 0]
    line = []
    for gam in (Fr(1, 10), Fr(1), Fr(10), Fr(10**3), Fr(10**6)):
        pos0, neg1, runs = crossing_report(sub, gam)
        line.append(f"g={float(gam):g}: d(0)>0 {pos0}, d(1)<0 {neg1}, signs {runs}")
    print(f"probe [{name}] positive roots of g_A^SN: {[float(sp.re(r)) for r in roots]}")
    for l in line:
        print("     ", l)
