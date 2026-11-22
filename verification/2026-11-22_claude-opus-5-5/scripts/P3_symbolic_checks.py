"""Proposition 3: symbolic re-derivation of the theta-derivatives of expected first-period
sales, the values of E[R^S_A] - E[R^N_A] at theta = 0 and theta = 1, the degree and fifth
derivative of g_R^SN, the convexity of E[R^N_A] in theta, and part (b), from the closed
forms of Lemmas 1 to 3 under A10. Followed by a probe of the cutoff theta'.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5/scripts/P3_symbolic_checks.py
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
zero = lambda e: sp.cancel(sp.together(e)) == 0
QS, QN = quantities("S"), quantities("N")
rB = QN["rB"]
drB = sp.diff(rB, th)
NN = aB2 * g * mB * (X1 + g * W) / P_N          # d r_B/dtheta = NN / D_N^2 (P1 script)

# (a) Scenario S
print("dE[R^S_A]/dtheta == aB1 sigma [(1-F(zeta_B))^2 - (1-F(zeta_A))^2]:",
      zero(sp.diff(QS["RA"], th) - aB1 * sg * (QS["rB"]**2 - QS["rA"]**2)))
print("E[R^S_A] affine in theta:", zero(sp.diff(QS["RA"], th, 2)))
# (a) Scenario N, right derivative at theta = 0
dRN = sp.diff(QN["RA"], th)
print("dE[R^N_A]/dtheta at theta = 0 == aB1 sigma [r_B(0)^2 - r_A^2]:",
      zero(dRN.subs(th, 0) - aB1 * sg * (rB.subs(th, 0)**2 - QN["rA"]**2)))
print("   r_B(0) - r_A == (X1 + gamma W) / ((p_B1 + aB2 gamma mB) P_N) > 0:",
      zero(rB.subs(th, 0) - QN["rA"] - (X1 + g * W) / ((pb1 + aB2 * g * mB) * P_N)))
d2RN = sp.diff(QN["RA"], th, 2)
claimed = 2 * aB1 * sg * (2 * rB * drB + th * (drB**2 + rB * sp.diff(drB, th)))
import random
random.seed(3)
_syms = (pa1, pb1, pa2, pb2, cA, cB, aA1, aA2, th, g, mu, sg)
_fd = sp.lambdify(_syms, d2RN - claimed, "sympy")
_ok = all(sp.nsimplify(_fd(*[sp.Rational(random.randint(1, 997), random.randint(1, 97)) for _ in _syms])) == 0 for _ in range(200))
print("d2E[R^N_A]/dtheta2 == 2 aB1 sigma [2 r_B r_B' + theta (r_B'^2 + r_B r_B'')], exact at 200 random rational points:", _ok)
print("   r_B'' == 2 aB2 gamma mB NN / D_N^3 >= 0:", zero(sp.diff(drB, th) - 2 * aB2 * g * mB * NN / D_N**3))
print("   r_B >= 0: numerator c_B P_N - aB2 gamma theta mB c_A >= c_B p_A1 + gamma theta W > 0:",
      zero((cB * P_N - aB2 * g * th * mB * cA) - (cB * pa1 + g * aA2 * cB * mA * (1 - th) + g * th * W)))

# theta = 0
d0 = (QS["RA"] - QN["RA"]).subs(th, 0)
printed0 = (aA1 * aB2 * g * cA**2 * sg * mA * ((aA2 + 1) * g * mA + 2 * pa1)) / ((g * mA + pa1)**2 * (aA2 * g * mA + pa1)**2)
print("theta = 0: E[R^S_A] - E[R^N_A] equals the printed expression:", zero(d0 - printed0))

# theta = 1
d1x = aB1 * sg * ((cB / Q_S)**2 - ((cB * P_N - aB2 * g * mB * cA) / (P_N * pb1))**2) - sg * ((cA / P_S)**2 - (cA / P_N)**2)
print("theta = 1: E[R^S_A] - E[R^N_A] == aB1 sigma (r^S_B^2 - r^N_B(1)^2) - sigma (r^S_A^2 - r^N_A^2):",
      zero((QS["RA"] - QN["RA"]).subs(th, 1) - d1x))
d1 = d1x
printed_den = pb1**2 * (g * cA - pa1 - g * pa2)**2 * (g * cB - pb1 - g * pb2)**2 * (aA2 * g * cA - pa1 - aA2 * g * pa2)**2
gR = sp.cancel(sp.together(d1 * printed_den / (g * sg)))
P = sp.Poly(sp.expand(gR), g)
print("theta = 1: g_R^SN is a polynomial in gamma:", sp.denom(sp.together(gR)) == 1, "; degree:", P.degree())
lead = P.all_coeffs()[0]
print("   leading coefficient == -aB1 mA^2 mB^2 W^2:", zero(lead + aB1 * mA**2 * mB**2 * W**2),
      "; so d5 g_R^SN/dgamma5 = 120 x that < 0")
print("   g_R^SN at gamma = 0 (constant term):", sp.factor(P.all_coeffs()[-1]))

# (b): R_B = min(aB1 X, y_B), E[R_B] = aB1 (mu - sigma r_B^2), strictly decreasing in r_B on [0, 1]
print("(b) E[R^N_B] == aB1 (mu - sigma r_B^2):", zero(QN["RB"] - aB1 * (mu - sg * rB**2)),
      "; dE[R^N_B]/dtheta == -2 aB1 sigma r_B r_B':", zero(sp.diff(QN["RB"], th) + 2 * aB1 * sg * rB * drB))
print("    E[R^S_B] independent of theta:", zero(sp.diff(QS["RB"], th)))


# ----------------------------------------------------------------------------- probe
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
    num, den = sp.fraction(sp.cancel(sp.together((QS["RA"] - QN["RA"]).subs(sub))))
    pn, pd = sp.Poly(num, th, g), sp.Poly(den, th, g)
    roots = [float(sp.re(r)) for r in sp.Poly(P.as_expr().subs(sub), g).nroots() if abs(sp.im(r)) < 1e-9 and sp.re(r) > 0]
    out = []
    for gam in (Fr(1, 10), Fr(1), Fr(10), Fr(10**4)):
        G = sp.Rational(gam.numerator, gam.denominator)
        vals = [pn.eval({th: sp.Rational(k, 200), g: G}) / pd.eval({th: sp.Rational(k, 200), g: G}) for k in range(201)]
        signs = "".join("+" if v > 0 else "-" if v < 0 else "0" for v in vals)
        runs = "".join(ch for i, ch in enumerate(signs) if i == 0 or ch != signs[i - 1])
        out.append(f"gamma={float(gam):g}: signs {runs}")
    print(f"probe [{name}] positive roots of g_R^SN: {roots}; " + "; ".join(out))
