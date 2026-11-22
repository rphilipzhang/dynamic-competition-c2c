"""P2 (Proposition 2): re-derivation of (a), (b) via (A.20), and (c) via g_B^SN.

g_B^SN is built as an explicit polynomial (quotient rule, no rational cancellation) and
the printed identity  d/dgamma (y^S_B1 - y^N_B1) = 2 (p_B2-c_B) a_B1 sigma g_B^SN / [..]^2
is checked in exact rational arithmetic at random admissible points (Schwartz-Zippel style),
because full symbolic cancellation takes too long.

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5-b/scripts/P2_symbolic_steps.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from random import Random

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared_sec4_closed_forms import (J, K, PN_A, PS_B, aA1, aA2, aB1, aB2, benchmark, ca, cb, g, pa1, pa2, pb1, pb2,
                                      r_N, random_point, scen_N, scen_S, sg, subs_point, th)

z = sp.simplify
Q1 = cb * pa1 - ca * pb1
Q2 = aA2 * cb * (pa2 - ca) - aB2 * ca * (pb2 - cb)
v, w = pa2 - ca, pb2 - cb
S, N, B = scen_S(), scen_N(), benchmark(1)
r = r_N()

print("(a) y^0_B1, y^S_B1 free of theta:", sp.diff(B["yB"], th) == 0 and sp.diff(S["yB"], th) == 0)
print("(a) d y^N_B1/d theta = -2 sigma a_B1 d r/d theta  (and d r/d theta >= 0 by (A.19), see P1 script):",
      z(sp.diff(N["yB"], th) + 2 * sg * aB1 * sp.diff(r, th)) == 0)

r0, r1 = r.subs(th, 0), r.subs(th, 1)
print("(b) r(0) = c_B/(p_B1 + a_B2 gamma (p_B2-c_B)):", z(r0 - cb / (pb1 + aB2 * g * w)) == 0)
print("(b) r(1) = (c_B - a_B2 gamma (p_B2-c_B) c_A/P^N_A)/p_B1:", z(r1 - (cb - aB2 * g * w * ca / PN_A) / pb1) == 0)
print("(b) c_B/p_B1 - r(1) = K/p_B1 with K = a_B2 gamma (p_B2-c_B) c_A / P^N_A > 0:", z(cb / pb1 - r1 - K / pb1) == 0)
print("(b) r(0) - c_B/P^S_B = c_B a_A2 gamma (p_B2-c_B)/[(p_B1 + a_B2 gamma (p_B2-c_B)) P^S_B] > 0:",
      z(r0 - cb / PS_B - cb * aA2 * g * w / ((pb1 + aB2 * g * w) * PS_B)) == 0)

# (c) explicit polynomial: r = Nr / (P^N_A den)
den = pb1 + aB2 * g * w * (1 - th)
Nr = cb * PN_A - th * aB2 * g * w * ca
print("(c) r = Nr/(P^N_A den):", z(r - Nr / (PN_A * den)) == 0)
M = PN_A * den
num_dr = sp.diff(Nr, g) * M - Nr * sp.diff(M, g)                 # d r/d gamma = num_dr / M^2
gB_w = sp.expand(cb * w * M**2 + num_dr * PS_B**2)               # = w * g_B^SN
q, rem = sp.div(sp.Poly(gB_w, g, th, pa1, pb1, pa2, pb2, ca, cb, aA2), sp.Poly(w, g, th, pa1, pb1, pa2, pb2, ca, cb, aA2))
print("(c) w * g_B^SN is divisible by (p_B2 - c_B):", rem.is_zero)
gB = q.as_expr()
den_c = ((g * cb - pb1 - g * pb2)**2 * (aA2 * g * ca - pa1 - aA2 * g * pa2)**2 *
         (aA2 * g * cb * th - aA2 * g * cb - g * cb * th + g * cb - pb1 - aA2 * g * th * pb2 + aA2 * g * pb2
          + g * th * pb2 - g * pb2)**2)
print("(c) third printed factor = -(p_B1 + a_B2 gamma (1-theta)(p_B2-c_B)):",
      sp.expand((aA2 * g * cb * th - aA2 * g * cb - g * cb * th + g * cb - pb1 - aA2 * g * th * pb2 + aA2 * g * pb2
                 + g * th * pb2 - g * pb2) + den) == 0)
D = sp.diff(S["yB"] - N["yB"], g)
rng = Random(21)
agree = 0
for k in range(40):
    pt = random_point(rng, equal_shares=(k % 2 == 0), bind=(k % 3 == 0, k % 5 == 0))
    rep = {th: sp.Rational(rng.randint(0, 50), 50), g: sp.Rational(rng.randint(1, 10**4), 37)}
    lhs = subs_point(D, pt, rep)
    rhs = subs_point(2 * w * aB1 * sg * gB / den_c, pt, rep)
    agree += (lhs - rhs) == 0
print(f"(c) printed factorization of d(y^S_B1 - y^N_B1)/d gamma holds exactly at {agree}/40 random points")

P = sp.Poly(sp.expand(gB), g)
print("(c) degree of g_B^SN in gamma:", P.degree())
cf = {k: sp.expand(P.coeff_monomial(g**k)) for k in range(5)}
B0 = aA2 * cb * pa1 + th * aB2 * Q1                              # > 0
B1 = aA2**2 * cb * v + th * aB2 * (aA2 * cb * v - ca * w)        # linear in theta, = a_A2^2 c_B v > 0 at 0 and Q2 > 0 at 1
forms = {0: pa1 * pb1**2 * B0, 1: 2 * pa1 * pb1**2 * B1, 3: -2 * aA2 * aB2 * v * w**2 * (1 - th) * B0,
         4: -aA2 * aB2 * v * w**2 * (1 - th) * B1}
for k_, f in forms.items():
    print(f"(c) a_{k_} equals the sign-revealing form {f}:", sp.expand(cf[k_] - f) == 0)
print("(c) B1 at theta = 1 equals Q2:", sp.expand(B1.subs(th, 1) - Q2) == 0)

# root count: one sign change in (a4, a3, a2, a1, a0) for theta < 1 -> exactly one positive root (Descartes)
cnt_bad, n = 0, 0
for k in range(300):
    pt = random_point(rng, equal_shares=(k % 3 == 0), bind=(k % 5 == 0, k % 7 == 0), equal_prices=(k % 11 == 0))
    for tv in (0, sp.Rational(1, 2), sp.Rational(99, 100)):
        poly = sp.Poly(subs_point(gB, pt, {th: tv}), g)
        pos = {x for x in poly.real_roots() if x > 0}
        cnt_bad += len(pos) != 1
        n += 1
print(f"(c) curves with theta < 1 on which g_B^SN has not exactly one positive root: {cnt_bad}/{n}")

gap = S["yB"] - N["yB"]
print("(c) gap at gamma = 0:", z(gap.subs(g, 0)))
pt5 = random_point(Random(5))
lim_half = sp.limit(subs_point(gap, pt5, {th: sp.Rational(1, 2)}), g, sp.oo)
lim_one = sp.limit(subs_point(gap, pt5, {th: 1}), g, sp.oo)
print("(c) one point: gap as gamma -> oo at theta = 1/2:", lim_half, "; at theta = 1:", float(lim_one))
