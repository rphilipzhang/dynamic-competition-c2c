"""Proposition 6: symbolic re-derivation of the proof from the closed forms of Lemmas 1 to 3
under A10 (shared_sec4_closed_forms.py):
  (a)  Pi^S_B independent of theta, E[L^k_B1] = aB1 E(zeta - X)^+, and
       dPi^N_B/dtheta = sigma aB1 aB2 gamma mB h^N_B / (P_N^2 D_N^2) with
       h^N_B = (X1 + gamma W)(c_B P_N + c_A (p_B1 + aB2 gamma mB)) > 0, independent of theta;
  (b)  Pi^k_B - Pi^0_B = [first-period terms] + gamma x (margin) x (sales);
  (c1) h_B(theta, gamma) := (Pi^S_B - Pi^N_B) Q_S P_N^2 D_N / (mB gamma): closed form, linear in theta, the
       printed fourth derivative (theta < 1) and third derivative (theta = 1);
  (c2) equal shares: h_B(0, .) and h_B(1, .) quadratics with the printed second derivatives; the bracket is
       decreasing in alpha_A2; alpha_A2 <= 1/2 + beta (1 - c_A/c_B) p_B2 under A11; a lower bound of the bracket
       that depends on (c_A, c_B, p_B2, beta) only and is positive as c_A -> c_B.
Run from the repository root:  python verification/2026-11-22_claude-opus-5-5/scripts/P6_symbolic_checks.py
"""
from __future__ import annotations

import os
import random
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp
from shared_sec4_closed_forms import (pa1, pb1, pa2, pb2, cA, cB, aA1, aA2, aB1, aB2, th, g, mu, sg,
                                 quantities, P_S, Q_S, P_N, D_N)

mA, mB = pa2 - cA, pb2 - cB
X1, X2 = cB * pa1 - cA * pb1, cB * pa2 - cA * pb2
W = aA2 * cB * mA - aB2 * cA * mB
JB = aB2 * g * mB
zero = lambda e: sp.cancel(sp.together(e)) == 0
SYMS = (pa1, pb1, pa2, pb2, cA, cB, aA1, aA2, th, g, mu, sg)
random.seed(9)
Q0, QS, QN = quantities("0"), quantities("S"), quantities("N")

# (a)
print("(a) dPi^S_B/dtheta == 0:", zero(sp.diff(QS["PiB"], th)))
for name, Q in (("0", Q0), ("S", QS)):
    print(f"(a) [{name}] E[L_B1] = y_B - E[R_B] == aB1 sigma (1 - r_B)^2 = aB1 E(zeta_B - X)^+:",
          zero(Q["yB"] - Q["RB"] - aB1 * sg * (1 - Q["rB"])**2))
hNB = (X1 + g * W) * (cB * P_N + cA * (pb1 + aB2 * g * mB))
print("(a) dPi^N_B/dtheta == sigma aB1 aB2 gamma mB h^N_B / (P_N^2 D_N^2):",
      zero(sp.diff(QN["PiB"], th) - sg * aB1 * aB2 * g * mB * hNB / (P_N**2 * D_N**2)))
print("    h^N_B quadratic in gamma:", sp.Poly(sp.expand(hNB), g).degree(), "; free of theta:", not hNB.has(th))

# (b)
f0 = pb1 * Q0["RB"] - cB * Q0["yB"]
print("(b) Pi^S_B - Pi^0_B == (p_B1 E[R^S_B] - c_B y^S_B - pi^0_B1) + gamma mB E[R^S_B]:",
      zero(QS["PiB"] - Q0["PiB"] - (pb1 * QS["RB"] - cB * QS["yB"] - f0 + g * mB * QS["RB"])))
print("(b) Pi^N_B - Pi^0_B == (p_B1 E[R^N_B] - c_B y^N_B - pi^0_B1) + gamma aB2 mB E[R^N_1]:",
      zero(QN["PiB"] - Q0["PiB"] - (pb1 * QN["RB"] - cB * QN["yB"] - f0 + g * aB2 * mB * (QN["RA"] + QN["RB"]))))

# (c1-c2): h_B
hB = (mu * (aB1 - aB2) * Q_S * P_N**2 * D_N - aB1 * sg * cB**2 * P_N**2 * (1 - aB2 * (1 - th))
      + aB2 * sg * cA**2 * Q_S * ((aA1 + th * aB1) * (pb1 + JB) - aA1 * JB * th))
printed_den = (-g * cB + pb1 + g * pb2) * (-aA2 * g * cA + pa1 + aA2 * g * pa2)**2 * ((1 - aA2) * g * (1 - th) * (pb2 - cB) + pb1)
print("(c) printed denominator == Q_S P_N^2 D_N:", zero(printed_den - Q_S * P_N**2 * D_N))
print("(c) Pi^S_B - Pi^N_B == mB gamma h_B / (Q_S P_N^2 D_N) with the closed form h_B above:",
      zero(QS["PiB"] - QN["PiB"] - mB * g * hB / printed_den))
HB = sp.Poly(sp.expand(hB), th)
print("(c) h_B degree in theta:", HB.degree())
d4 = sp.diff(hB, g, 4)
print("(c1) theta < 1: d4 h_B/dgamma4 == 24 aB2 aA2^2 (1-theta) mu (aB1 - aB2) mA^2 mB^2:",
      zero(d4 - 24 * aB2 * aA2**2 * (1 - th) * mu * (aB1 - aB2) * mA**2 * mB**2),
      "; degree in gamma:", sp.Poly(sp.expand(hB), g).degree())
h1 = hB.subs(th, 1)
print("(c1) theta = 1: degree in gamma", sp.Poly(sp.expand(h1), g).degree(),
      "; d3 h_B(1,.)/dgamma3 == 6 aA2^2 mu p_B1 (aB1 - aB2) mA^2 mB:",
      zero(sp.diff(h1, g, 3) - 6 * aA2**2 * mu * pb1 * (aB1 - aB2) * mA**2 * mB))
print("(c1) linearity: h_B(theta) == (1-theta) h_B(0) + theta h_B(1):",
      zero(hB - ((1 - th) * hB.subs(th, 0) + th * hB.subs(th, 1))),
      "=> endpoint signs for gamma >= max of the two endpoint thresholds give the sign on all of [0, 1]")

# (c2) equal shares
eq = {aA2: aA1}
h0E = sp.Poly(sp.expand(hB.subs(th, 0).subs(eq)), g)
h1E = sp.Poly(sp.expand(hB.subs(th, 1).subs(eq)), g)
print("(c2) equal shares: h_B(0,.) degree", h0E.degree(), "; h_B(1,.) degree", h1E.degree())
bracket = -2 * cB**2 * mA**2 * aA2**2 - 2 * cA**2 * mB**2 * aA2 + 2 * cA**2 * mB**2
print("(c2) d2 h_B(0,.)/dgamma2 == (1 - aA1) aA1 sigma [printed bracket] at aA2 = aA1:",
      zero(sp.diff(h0E.as_expr(), g, 2) - ((1 - aA1) * aA1 * sg * bracket).subs(eq)))
print("     printed bracket == 2 [aB2 c_A^2 mB^2 - aA2^2 c_B^2 mA^2]:", zero(bracket - 2 * (aB2 * cA**2 * mB**2 - aA2**2 * cB**2 * mA**2)))
print("     d bracket / d aA2 (mA, mB held fixed) == -4 aA2 c_B^2 mA^2 - 2 c_A^2 mB^2 < 0:",
      zero(sp.diff(bracket, aA2) - (-4 * aA2 * cB**2 * mA**2 - 2 * cA**2 * mB**2)))
beta = sp.symbols("beta", positive=True)
abar = sp.Rational(1, 2) + beta * (1 - cA / cB) * pb2
print("     abar - aA2 == beta X2 / c_B >= 0 with aA2 = 1/2 + beta (p_B2 - p_A2):",
      zero(abar - (sp.Rational(1, 2) + beta * (pb2 - pa2)) - beta * X2 / cB))
Lb = 2 * ((1 - abar) * cA**2 * (pb2 - cB)**2 - abar**2 * cB**2 * (pb2 - cA)**2)
print("     lower bound L(c_A; c_B, p_B2, beta) = bracket at (abar, mA = p_B2 - c_A); L at c_A = c_B:",
      sp.factor(Lb.subs(cA, cB)), "> 0")
print("     second derivative at theta = 1 == 2 aB1 sigma [(aB1 c_A mB)^2 - (aA1 c_B mA)^2]:",
      zero(sp.diff(h1E.as_expr(), g, 2) - 2 * aB1 * sg * ((aB1 * cA * mB)**2 - (aA1 * cB * mA)**2)))
print("     aA1 c_B mA - aB1 c_A mB == aA1 X2 + (aA1 - aB1) c_A mB  (> 0 under A1, A11, I1):",
      zero(aA1 * cB * mA - aB1 * cA * mB - (aA1 * X2 + (aA1 - aB1) * cA * mB)))
print("     h_B(0,gamma) at gamma = 0 == aA1 aB1 sigma (c_A p_B1 - c_B p_A1)(c_A p_B1 + c_B p_A1) <= 0:",
      zero(h0E.as_expr().subs(g, 0) - aA1 * aB1 * sg * (cA * pb1 - cB * pa1) * (cA * pb1 + cB * pa1)))


# ----------------------------------------------------------------------------- probes (fixed markets)
def market(ca, cb, pb1v, pb2v, gap, beta_v):
    return {pa1: pb1v - gap, pb1: pb1v, pa2: pb2v - gap, pb2: pb2v, cA: ca, cB: cb,
            aA1: Fr(1, 2) + beta_v * gap, aA2: Fr(1, 2) + beta_v * gap, mu: Fr(10), sg: Fr(4)}


def admissible(m):
    ok = all(m[cB] * m[pa] >= m[cA] * m[pb] and m[pb] >= m[pa] > m[cA] and m[pb] > m[cB] for pa, pb in ((pa1, pb1), (pa2, pb2)))
    return ok and 0 < m[cA] < m[cB] and Fr(1, 2) <= m[aA1] < 1


hBP = sp.Poly(sp.expand(hB), th, g)
for name, m in {
    "symmetric prices, small cost gap": market(Fr(1), Fr(11, 10), Fr(4), Fr(5), Fr(0), Fr(1, 10)),
    "equal gaps, A11 binds in period 1": market(Fr(1), Fr(11, 10), Fr(11, 2), Fr(6), Fr(1, 2), Fr(1, 10)),
    "large cost gap (bracket negative, statement silent)": market(Fr(1), Fr(3), Fr(8), Fr(8), Fr(0), Fr(1, 10)),
}.items():
    assert admissible(m), name
    br = sp.Rational(bracket.subs(m))
    hx = sp.Poly(hBP.as_expr().subs(m), th, g)
    out = []
    for G in (1, 10, 10**3, 10**6):
        ht = sp.Poly(hx.as_expr().subs(g, G), th)
        h0v, h1v = ht.eval(0), ht.eval(1)
        root = h0v / (h0v - h1v) if h0v != h1v else None
        out.append(f"g={G:g}: h_B(0)={'+' if h0v > 0 else '-'}, h_B(1)={'+' if h1v > 0 else '-'}, "
                   f"theta^B={float(root):.6f}" if root is not None else f"g={G:g}: flat")
    print(f"probe [{name}] bracket at theta=0: {float(br):.4f}")
    for o in out:
        print("     ", o)

# Delta^B cannot be chosen independently of beta: a tiny cost gap with A11 binding in both periods
# (p_B1 = p_B2, equal shares) and beta close to its I2 bound gives alpha_A close to 1 and a negative bracket.
ca_, cb_, pb_ = Fr(1), Fr(1001, 1000), Fr(4)
gap_ = pb_ - pb_ * ca_ / cb_
m = market(ca_, cb_, pb_, pb_, gap_, Fr(49, 100) / gap_)
assert admissible(m)
hx = sp.Poly(hBP.as_expr().subs(m), th, g)
signs = []
for G in (10**3, 10**6, 10**9):
    signs.append(f"g={G:g}: h_B(0)={'+' if sp.Poly(hx.as_expr().subs(g, G), th).eval(0) > 0 else '-'}")
print(f"probe [Delta c = 1/1000, alpha_A = {float(m[aA1]):.3f}] bracket at theta=0: {float(sp.Rational(bracket.subs(m))):.4f}; "
      + "; ".join(signs) + "  (Pi^S_B < Pi^N_B at theta = 0: Delta^B must depend on beta, as the proof's abar does)")
