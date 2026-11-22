"""Proposition 2: symbolic re-derivation of (a), (A.20) and the bounds of (b), and of the
derivative in gamma of (c) with the signs of the coefficients of g_B^SN, from the closed forms
of Lemmas 1 to 3 under A10. A probe of the single peak in gamma follows.

Sign identities used (all quantities positive under A1, A11, I1, I2, beta > 0):
  mA = p_A2 - c_A, mB = p_B2 - c_B, X1 = c_B p_A1 - c_A p_B1 >= 0,
  W  = aA2 c_B mA - aB2 c_A mB > 0 (see P1 script),
  E1 = aA2^2 c_B mA (1 - theta) + theta W,  E0 = aA2 c_B p_A1 + theta aB2 X1 > 0.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5/scripts/P2_symbolic_checks.py
"""
from __future__ import annotations

import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
from shared_sec4_closed_forms import (pa1, pb1, pa2, pb2, cA, cB, aA1, aA2, aB1, aB2, th, g, mu, sg,
                                 quantities, P_S, Q_S, P_N, D_N)

mA, mB = pa2 - cA, pb2 - cB
X1 = cB * pa1 - cA * pb1
W = aA2 * cB * mA - aB2 * cA * mB
E1 = aA2**2 * cB * mA * (1 - th) + th * W
E0 = aA2 * cB * pa1 + th * aB2 * X1
zero = lambda e: sp.cancel(sp.together(e)) == 0

Q0, QS, QN = quantities("0"), quantities("S"), quantities("N")

# (a)
print("(a) d y^0_B/dtheta == 0:", zero(sp.diff(Q0["yB"], th)), "; d y^S_B/dtheta == 0:", zero(sp.diff(QS["yB"], th)))
print("(a) d y^N_B/dtheta == -2 sigma aB1 aB2 gamma mB (X1 + gamma W)/(P_N D_N^2):",
      zero(sp.diff(QN["yB"], th) + 2 * sg * aB1 * aB2 * g * mB * (X1 + g * W) / (P_N * D_N**2)))

# (b): y_B = aB1 (mu + sigma - 2 sigma r_B), so the ordering of y_B is the reverse ordering of r_B: (A.20)
print("(b) y_B is aB1 (mu + sigma - 2 sigma r_B) in all scenarios:",
      all(zero(Q["yB"] - aB1 * (mu + sg - 2 * sg * Q["rB"])) for Q in (Q0, QS, QN)))
rN = QN["rB"]
print("(b) r^N_B(theta=1) == (c_B - aB2 gamma mB c_A/P_N)/p_B1:", zero(rN.subs(th, 1) - (cB - aB2 * g * mB * cA / P_N) / pb1))
print("(b) r^N_B(theta=0) == c_B/(p_B1 + aB2 gamma mB):", zero(rN.subs(th, 0) - cB / (pb1 + aB2 * g * mB)))
print("(b) c_B/p_B1 - r^N_B(1) == aB2 gamma mB c_A/(P_N p_B1) > 0:",
      zero(cB / pb1 - rN.subs(th, 1) - aB2 * g * mB * cA / (P_N * pb1)))
print("(b) r^N_B(0) - c_B/Q_S == c_B aA2 gamma mB / ((p_B1 + aB2 gamma mB) Q_S) > 0:",
      zero(rN.subs(th, 0) - cB / Q_S - cB * aA2 * g * mB / ((pb1 + aB2 * g * mB) * Q_S)))

# (c)
gap = QS["yB"] - QN["yB"]
dgap = sp.diff(gap, g)
printed_den = (g * cB - pb1 - g * pb2)**2 * (aA2 * g * cA - pa1 - aA2 * g * pa2)**2 * \
    (aA2 * g * cB * th - aA2 * g * cB - g * cB * th + g * cB - pb1 - aA2 * g * th * pb2 + aA2 * g * pb2 + g * th * pb2 - g * pb2)**2
print("(c) printed denominator == Q_S^2 P_N^2 D_N^2:", zero(printed_den - Q_S**2 * P_N**2 * D_N**2))
# gap = 2 sigma aB1 (r^N_B - r^S_B); write r^N_B = nN / (P_N D_N) and r^S_B = c_B / Q_S explicitly
nN = cB * P_N - aB2 * g * th * mB * cA
print("(c) gap == 2 sigma aB1 (nN/(P_N D_N) - c_B/Q_S):", zero(gap - 2 * sg * aB1 * (nN / (P_N * D_N) - cB / Q_S)))
dN = sp.diff(nN, g) * P_N * D_N - nN * sp.diff(P_N * D_N, g)        # numerator of d r^N_B / d gamma over (P_N D_N)^2
dS = -cB * sp.diff(Q_S, g)                                            # numerator of d r^S_B / d gamma over Q_S^2
gB_num = sp.expand(dN * Q_S**2 - dS * P_N**2 * D_N**2)
q, rem = sp.div(sp.Poly(gB_num, g), sp.Poly(mB, g))
gB = q.as_expr() if rem.is_zero else gB_num / mB
P = sp.Poly(sp.expand(gB), g)
import random
random.seed(5)
syms = (pa1, pb1, pa2, pb2, cA, cB, aA1, aA2, th, g, mu, sg)
fd = sp.lambdify(syms, dgap - 2 * mB * aB1 * sg * gB / printed_den, "sympy")
vals = [fd(*[sp.Rational(random.randint(1, 997), random.randint(1, 97)) for _ in syms]) for _ in range(200)]
print("(c) d gap / d gamma == 2 mB aB1 sigma g_B^SN / printed denominator, exact at 200 random rational points:",
      all(sp.nsimplify(v) == 0 for v in vals))
print("(c) g_B^SN = (dN Q_S^2 - dS P_N^2 D_N^2)/mB is a polynomial in gamma:", rem.is_zero, "; degree:", P.degree())
a = dict(zip(range(P.degree(), -1, -1), P.all_coeffs()))
claimed = {4: -aA2 * aB2 * mA * mB**2 * (1 - th) * E1, 3: -2 * aA2 * aB2 * mA * mB**2 * (1 - th) * E0,
           1: 2 * pa1 * pb1**2 * E1, 0: pa1 * pb1**2 * E0}
for k, expr in claimed.items():
    print(f"(c) a_{k} == {expr}:", zero(a[k] - expr))
print("(c) E1 bracket identity (aA2^2 c_B mA (1-theta) + theta W) and E0 identity verified above through a_1 and a_0.")
print("    => for theta < 1: a4 < 0, a3 < 0, a1 > 0, a0 > 0, so exactly one sign change whatever the sign of a2.")
eps = sp.symbols("epsilon", positive=True)
at_inf = sp.cancel(sp.together(gap.subs(g, 1 / eps)))       # gamma = 1/eps, rational in eps
print("(c) limits: gap at gamma = 0:", sp.cancel(sp.together(gap.subs(g, 0))),
      "; gap as gamma -> oo (eps = 1/gamma -> 0), general theta:", sp.factor(at_inf.subs(eps, 0)))
print("    i.e. zero for theta < 1; at theta = 1 the limit is",
      sp.factor(sp.cancel(sp.together(gap.subs(th, 1).subs(g, 1 / eps))).subs(eps, 0)))


# ----------------------------------------------------------------------------- probe of the peak
def point(ca, cb, pb, lam, beta):
    PA = [p * (ca + (cb - ca) * l) / cb for p, l in zip(pb, lam)]
    return {pa1: PA[0], pb1: pb[0], pa2: PA[1], pb2: pb[1], cA: ca, cB: cb,
            aA1: Fr(1, 2) + beta * (pb[0] - PA[0]), aA2: Fr(1, 2) + beta * (pb[1] - PA[1]), mu: Fr(10), sg: Fr(4)}


cases = {
    "regular": point(Fr(1), Fr(3, 2), (Fr(4), Fr(5)), (Fr(1, 2), Fr(1, 3)), Fr(1, 10)),
    "A11 binds both periods": point(Fr(1), Fr(3, 2), (Fr(4), Fr(5)), (Fr(0), Fr(0)), Fr(1, 10)),
    "equal prices": point(Fr(1), Fr(3, 2), (Fr(4), Fr(5)), (Fr(1), Fr(1)), Fr(1, 10)),
}
for name, sub in cases.items():
    for t in (Fr(0), Fr(1, 2), Fr(999, 1000)):
        poly = sp.Poly(P.as_expr().subs(sub).subs(th, t), g)
        pos = sorted(float(sp.re(r)) for r in poly.nroots() if abs(sp.im(r)) < 1e-9 and sp.re(r) > 0)
        print(f"probe [{name}] theta = {t}: positive roots of g_B^SN: {pos}")
