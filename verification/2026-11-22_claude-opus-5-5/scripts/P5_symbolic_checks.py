"""Proposition 5: symbolic re-derivation of the proof from the closed forms of Lemmas 1 to 3
under A10 (shared_sec4_closed_forms.py):
  (a)  dPi^S_A/dtheta as a sum of two squares;
  (b), (c1)  the decomposition Pi^S_A - Pi^N_A = [first-period terms] + gamma mA (E[R^S_A] - aA2 E[R^N_1]),
       the O(gamma^-2) and O(gamma^-1) sales bounds, uniform in theta;
  (c2) h_A(theta, gamma) := (Pi^S_A - Pi^N_A) P_S Q_S^2 P_N^2 D_N^2 / gamma: polynomial, degree 3 in theta,
       the third theta-derivative (general shares and equal shares), h_A(0, gamma) with equal shares
       (positive factor times a quadratic with positive leading coefficient), h_A(1, gamma) quartic with
       leading coefficient sigma aB1 mA mB^2 W E, where E is the printed expression, and c_B-bar.
Identities of large rational functions are checked in exact rational arithmetic at random points
(stated in each line); polynomial identities are checked symbolically.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5/scripts/P5_symbolic_checks.py
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
JA = aA2 * g * mA
zero = lambda e: sp.cancel(sp.together(e)) == 0
SYMS = (pa1, pb1, pa2, pb2, cA, cB, aA1, aA2, th, g, mu, sg)
random.seed(7)


def zero_at_random_points(expr, n=60):
    """Exact evaluation at n random rational points (substitution of Rationals, no floating point)."""
    for _ in range(n):
        pt = {s: sp.Rational(random.randint(1, 997), random.randint(1, 97)) for s in SYMS}
        if expr.xreplace(pt) != 0:
            return False
    return True


Q0, QS, QN = quantities("0"), quantities("S"), quantities("N")

# (a)
z0A2, z0B2 = mu + sg - 2 * sg * cA / pa2, mu + sg - 2 * sg * cB / pb2
claimed_a = aB1 * P_S / (4 * sg) * (QS["zA"] - QS["zB"])**2 + aB2 * pa2 / (4 * sg) * (z0A2 - z0B2)**2
print("(a) dPi^S_A/dtheta == aB1 [p_A1 + gamma mA](zA-zB)^2/(4 sigma) + aB2 p_A2 (z0A2-z0B2)^2/(4 sigma):",
      zero(sp.diff(QS["PiA"], th) - claimed_a))

# (b) and (c1)
first_S = pa1 * QS["RA"] - cA * QS["yA"]
first_N = pa1 * QN["RA"] - cA * QN["yA"]
first_0 = pa1 * Q0["RA"] - cA * Q0["yA"]
print("(b) Pi^S_A - Pi^0_A == (p_A1 E[R^S_A] - c_A y^S_A - pi^0_A1) + gamma mA E[R^S_A]:",
      zero(QS["PiA"] - Q0["PiA"] - (first_S - first_0 + g * mA * QS["RA"])))
print("(b) Pi^N_A - Pi^0_A == (p_A1 E[R^N_A] - c_A y^N_A - pi^0_A1) + gamma aA2 mA E[R^N_1]:",
      zero(QN["PiA"] - Q0["PiA"] - (first_N - first_0 + g * aA2 * mA * (QN["RA"] + QN["RB"]))))
print("    first-period terms are bounded: y_A in [0, mu + sigma], E[R_A] in [0, mu + sigma] (zeta in the support)")
print("(c1) E[R^S_A] - aA1 mu == sigma [theta aB1 r_B^2 - (aA1 + theta aB1) r_A^2], with r^S_i <= c_i/(gamma m_i): O(gamma^-2):",
      zero(QS["RA"] - aA1 * mu - sg * (th * aB1 * QS["rB"]**2 - (aA1 + th * aB1) * QS["rA"]**2)))
bound = cB / (g * aB2 * mB) - (1 - th) * QN["rB"]
print("(c1) c_B/(gamma aB2 mB) - (1-theta) r^N_B == [c_B p_B1 + theta (1-theta) J_B^2 r^N_A] / (J_B D_N) >= 0:",
      zero(bound - (cB * pb1 + th * (1 - th) * (aB2 * g * mB)**2 * QN["rA"]) / (aB2 * g * mB * D_N)))
print("(c1) (Pi^S_A - Pi^N_A) == (first_S - first_N) + gamma mA (E[R^S_A] - aA2 E[R^N_1]):",
      zero(QS["PiA"] - QN["PiA"] - (first_S - first_N + g * mA * (QS["RA"] - aA2 * (QN["RA"] + QN["RB"])))))

# (c2): h_A. Rearranged numerator (Pi^S_A - Pi^N_A) * den, den = P_S Q_S^2 P_N^2 D_N^2.
nBN = cB * P_N - aB2 * g * th * mB * cA                  # r^N_B = nBN / (P_N D_N)
den = P_S * Q_S**2 * P_N**2 * D_N**2
printed_den = (-g * cA + pa1 + g * pa2) * (g * cB - pb1 - g * pb2)**2 * (-aA2 * g * cA + pa1 + aA2 * g * pa2)**2 * \
    (aA2 * g * cB * th - aA2 * g * cB - g * cB * th + g * cB - pb1 - aA2 * g * th * pb2 + aA2 * g * pb2 + g * th * pb2 - g * pb2)**2
print("(c2) printed denominator == P_S Q_S^2 P_N^2 D_N^2:", zero(printed_den - den))
terms = [((P_S - P_N) * aA1 * mu - JA * aB1 * mu) * den,
         (aA1 + th * aB1) * sg * cA**2 * (P_N - P_S) * Q_S**2 * P_N * D_N**2,
         th * aB1 * sg * (P_S * cB**2 - 2 * cA * cB * Q_S) * P_S * P_N**2 * D_N**2,
         -aB1 * sg * ((th * P_N - JA) * nBN**2 * P_S * Q_S**2 - 2 * th * cA * nBN * P_N * D_N * P_S * Q_S**2)]
def _pieces_agree(n=40):
    for _ in range(n):
        pt = {s: sp.Rational(random.randint(1, 997), random.randint(1, 97)) for s in SYMS}
        lhs = (QS["PiA"].xreplace(pt) - QN["PiA"].xreplace(pt)) * den.xreplace(pt)
        if lhs != sum(t.xreplace(pt) for t in terms):
            return False
    return True


print("(c2) (Pi^S_A - Pi^N_A) * den == sum of the four rearranged terms, exact at 40 random rational points:", _pieces_agree())
# theta^3 coefficient, general shares, term by term
def theta_degree(t):
    """Degree in theta of a product, as the sum of the degrees of its factors (each factor is small)."""
    total = 0
    for fac in sp.Mul.make_args(t):
        base, e = fac.as_base_exp()
        total += int(e) * sp.Poly(base, th).degree() if base.has(th) else 0
    return total


print("(c2) degree in theta of every term <= 3 (sum of factor degrees):", [theta_degree(t) for t in terms])
c3 = sp.factor(sp.expand(sum(sp.diff(t, th, 3).subs(th, 0) for t in terms) / 6))
claimed_c3 = g * sg * aB1 * aB2**2 * mB**2 * P_N**2 * (X1 + g * X2)**2 * g      # coefficient of theta^3 in gamma h_A
print("(c2) theta^3 coefficient of gamma h_A == gamma^2 sigma aB1 aB2^2 mB^2 P_N^2 (X1 + gamma X2)^2 (general shares):",
      zero(c3 - claimed_c3))
printed_d3 = 6 * aB1**3 * g * sg * mB**2 * (aA1 * g * mA + pa1)**2 * (cB * (pa1 + g * pa2) - cA * (pb1 + g * pb2))**2
print("(c2) printed d3 h_A/dtheta3 == 6 x (theta^3 coefficient of h_A) when aA2 = aA1:",
      zero((6 * c3 / g - printed_d3).subs(aA2, aA1)),
      "; and differs for unequal shares:", not zero(6 * c3 / g - printed_d3))

# equal shares: build h_A as a polynomial
eq = {aA2: aA1}
tot = sp.expand(sum(sp.expand(t.subs(eq)) for t in terms))
print("(c2) equal shares: numerator vanishes at gamma = 0 (divisible by gamma):", sp.expand(tot.subs(g, 0)) == 0)
hE = sp.expand(sp.cancel(tot / g))
print("     h_A polynomial; degree in theta:", sp.Poly(hE, th).degree(), "; degree in gamma:", sp.Poly(hE, g).degree())
WE = W.subs(eq)
h0 = sp.expand(hE.subs(th, 0))
K = sp.cancel(h0 / (-aA1 * aB1 * sg * mA * Q_S**2 * P_N.subs(eq)))
KP = sp.Poly(sp.expand(K), g)
print("(c2) h_A(0, gamma) == -aA1 aB1 sigma mA Q_S^2 P_N K(gamma), K polynomial of degree", KP.degree(),
      "; exact division:", sp.denom(sp.together(K)) == 1)
K2 = KP.all_coeffs()[0]
print("     gamma^2 coefficient of K == aB1^2 c_A^2 mB^2 - aA1 c_B^2 mA^2:", zero(K2 - (aB1**2 * cA**2 * mB**2 - aA1 * cB**2 * mA**2)))
print("     => positive factor aA1 aB1 sigma mA Q_S^2 P_N times -K, whose leading coefficient aA1 c_B^2 mA^2 - aB1^2 c_A^2 mB^2")
print("        >= (1/2 - 1/4) c_A^2 mB^2 > 0 since c_B mA >= c_A mB (A11) and aA1 >= 1/2 >= aB1")
h1 = sp.Poly(sp.expand(hE.subs(th, 1)), g)
E = -2 * aA1 * cA**2 * pb1 + aB1 * cA * pa1 * pb2 + 2 * aA1 * cA * pa2 * pb1 - cB * pa1 * (aA1 * pa2 - (2 * aA1 - 1) * cA)
print("(c2) h_A(1, gamma) degree in gamma:", h1.degree())
print("     leading coefficient == sigma aB1 mA mB^2 W E  (so d4/dgamma4 = 24 x that, sign of E):",
      zero(h1.all_coeffs()[0] - sg * aB1 * mA * mB**2 * WE * E))
print("     aA1 p_A2 - (2 aA1 - 1) c_A == aA1 mA + aB1 c_A > 0:", zero(aA1 * pa2 - (2 * aA1 - 1) * cA - (aA1 * mA + aB1 * cA)))
cbar = (-2 * aA1 * cA**2 * pb1 + aB1 * cA * pa1 * pb2 + 2 * aA1 * cA * pa2 * pb1) / (pa1 * (aA1 * pa2 - (2 * aA1 - 1) * cA))
print("     E == p_A1 (aA1 p_A2 - (2 aA1 - 1) c_A) (c_B-bar - c_B):", zero(E - pa1 * (aA1 * pa2 - (2 * aA1 - 1) * cA) * (cbar - cB)))
bind = {pa1: cA * pb1 / cB, pa2: cA * pb1 / cB, pb2: pb1}
print("     A11 binding in both periods with equal shares (p_B1 = p_B2): E == c_A^2 p_B1 (p_B1/c_B - 1) > 0, so (c2) is silent there:",
      zero(E.subs(bind) - cA**2 * pb1 * (pb1 / cB - 1)))
print("     E does not contain c_B except in the last term: dE/dc_B == -p_A1 (aA1 p_A2 - (2 aA1 - 1) c_A):",
      zero(sp.diff(E, cB) + pa1 * (aA1 * pa2 - (2 * aA1 - 1) * cA)))


# ----------------------------------------------------------------------------- probes (fixed markets)
def market(ca, cb, pb1v, pb2v, gap, beta):
    """Equal shares: the same price gap in both periods."""
    return {pa1: pb1v - gap, pb1: pb1v, pa2: pb2v - gap, pb2: pb2v, cA: ca, cB: cb,
            aA1: Fr(1, 2) + beta * gap, mu: Fr(10), sg: Fr(4)}


def admissible(m):
    ok = all(m[cB] * m[pa] >= m[cA] * m[pb] and m[pb] >= m[pa] > m[cA] and m[pb] > m[cB] for pa, pb in ((pa1, pb1), (pa2, pb2)))
    return ok and 0 < m[cA] < m[cB] and Fr(1, 2) <= m[aA1] < 1


hEnum = sp.Poly(hE, th, g)
for name, m in {
    "symmetric prices, c_B well above c_B-bar": market(Fr(1), Fr(3), Fr(8), Fr(8), Fr(0), Fr(1, 10)),
    "price gap, c_B above c_B-bar": market(Fr(1), Fr(29, 10), Fr(7), Fr(6), Fr(1, 2), Fr(1, 10)),
    "price gap, c_B below c_B-bar (statement silent)": market(Fr(1), Fr(5, 2), Fr(7), Fr(6), Fr(1, 2), Fr(1, 10)),
    "A11 binds in both periods (p_B1 = p_B2), c_B below c_B-bar (statement silent)": market(Fr(1), Fr(5, 2), Fr(6), Fr(6), Fr(6) - Fr(12, 5), Fr(1, 10)),
    "A11 binds in both periods (p_B1 = p_B2), larger c_B, still below c_B-bar (statement silent)": market(Fr(1), Fr(5), Fr(8), Fr(8), Fr(8) - Fr(8, 5), Fr(1, 20)),
    "c_B just above c_B-bar": None,
}.items():
    if m is None:
        base = market(Fr(1), Fr(2), Fr(8), Fr(8), Fr(0), Fr(1, 10))
        cb_bar = sp.Rational(cbar.subs(base))
        m = dict(base)
        m[cB] = Fr(int(cb_bar.p), int(cb_bar.q)) + Fr(1, 100)
    Ev = E.subs(m)
    assert admissible(m), name
    hx = sp.Poly(hEnum.as_expr().subs(m), th, g)
    out = []
    for G in (10, 10**3, 10**6, 10**9):
        ht = sp.Poly(hx.as_expr().subs(g, G), th)
        vals = [ht.eval(sp.Rational(k, 400)) for k in range(401)]
        s = "".join("+" if v > 0 else "-" if v < 0 else "0" for v in vals)
        runs = "".join(ch for i, ch in enumerate(s) if i == 0 or ch != s[i - 1])
        roots = [float(r) for r in ht.real_roots() if 0 <= r <= 1]
        out.append(f"g={G:g}: {runs}, roots in [0,1] {['%.6f' % r for r in roots]}")
    print(f"probe [{name}] c_B = {float(m[cB]):.4f}, c_B-bar = {float(cbar.subs(m)):.4f}, E = {float(Ev):.4f}")
    for o in out:
        print("     ", o)
