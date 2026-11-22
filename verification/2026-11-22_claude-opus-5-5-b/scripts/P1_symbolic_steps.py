"""P1 (Proposition 1): symbolic re-derivation of every step of the proof, plus probes.

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5-b/scripts/P1_symbolic_steps.py
Closed forms: shared_sec4_closed_forms.py (independent transcription of Lemmas 1-3 under A10).
"""
from __future__ import annotations

import sys
from fractions import Fraction as Fr
from pathlib import Path
from random import Random

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared_sec4_closed_forms import (J, PN_A, PS_A, PS_B, aA1, aA2, aB1, aB2, benchmark, ca, cb, g, mu, pa1, pa2,
                                      pb1, pb2, r_N, random_point, scen_N, scen_S, sg, subs_point, th)

z = sp.simplify
Q1 = cb * pa1 - ca * pb1                                   # >= 0 by A11 in period 1
Q2 = aA2 * cb * (pa2 - ca) - aB2 * ca * (pb2 - cb)         # > 0 under A1, A11, I1, I2 (see note)
den = pb1 + J * (1 - th)
S, N, B = scen_S(), scen_N(), benchmark(1)

print("Step 1: y^k_A1 = a_A1 z_A + theta a_B1 (z_A - z_B) for k = 0, S, N:",
      all(z(e["yA"] - (aA1 * e["zA"] + th * aB1 * (e["zA"] - e["zB"]))) == 0 for e in (B, S, N)))
print("Step 1: slope of y^0_A1 equals a_B1 * 2 sigma (c_B p_A1 - c_A p_B1)/(p_A1 p_B1):",
      z(sp.diff(B["yA"], th) - aB1 * 2 * sg * Q1 / (pa1 * pb1)) == 0)
s_slope = sp.diff(S["yA"], th) - aB1 * 2 * sg * (Q1 + g * (cb * pa2 - ca * pb2)) / (PS_A * PS_B)
print("Interpretation: slope of y^S_A1 equals a_B1 * 2 sigma [Q1 + gamma (c_B p_A2 - c_A p_B2)]/(P^S_A P^S_B):",
      z(s_slope) == 0)

# (A.19): derivative of the ratio r_N in theta
dr = sp.diff(r_N(), th)
print("(A.19): d r_N/d theta = J (Q1 + gamma Q2) / (P^N_A den^2):", z(dr - J * (Q1 + g * Q2) / (PN_A * den**2)) == 0)
print("        Q2 = a_A2 (c_B p_A2 - c_A p_B2) + (a_A2 - a_B2) c_A (p_B2 - c_B):",
      sp.expand(Q2 - (aA2 * (cb * pa2 - ca * pb2) + (aA2 - aB2) * ca * (pb2 - cb))) == 0)
print("        c_B P^N_A - c_A (p_B1 + J) = Q1 + gamma Q2:", sp.expand(cb * PN_A - ca * (pb1 + J) - Q1 - g * Q2) == 0)
print("(A.18): d zeta^N_B/d theta = -2 sigma d r_N/d theta:", z(sp.diff(N["zB"], th) + 2 * sg * dr) == 0)
dyN = sp.diff(N["yA"], th)
print("Step 2: d y^N_A1/d theta = a_B1 (zN_A - zN_B) - theta a_B1 d zN_B/d theta:",
      z(dyN - (aB1 * (N["zA"] - N["zB"]) - th * aB1 * sp.diff(N["zB"], th))) == 0)

# theta = 0
d0 = (N["yA"] - S["yA"]).subs(th, 0)
printed0 = -2 * aA1 * aB2 * g * ca * sg * (pa2 - ca) / ((g * (pa2 - ca) + pa1) * (aA2 * g * (pa2 - ca) + pa1))
print("theta = 0: y^N_A1 - y^S_A1 equals the printed expression:", z(d0 - printed0) == 0)

# theta = 1
d1 = sp.together((N["yA"] - S["yA"]).subs(th, 1))
pref = 2 * g * sg / (pb1 * (-g * ca + pa1 + g * pa2) * (-g * cb + pb1 + g * pb2) * (-aA2 * g * ca + pa1 + aA2 * g * pa2))
gA = sp.cancel(d1 / pref)
gA_poly = sp.Poly(sp.expand(gA), g)
print("theta = 1: (y^N - y^S)/prefactor is a polynomial in gamma:", sp.denom(sp.together(gA)) == 1 or
      sp.simplify(sp.denom(sp.together(gA))).is_number, " degree:", gA_poly.degree())
printed_d2 = -2 * aB1 * (pa2 - ca) * (pb2 - cb) * (ca * ((aA2 - aB2) * cb - aA2 * pb2 + pb2) - aA2 * cb * pa2)
print("theta = 1: d^2 g_A^SN / d gamma^2 equals the printed expression:", z(sp.diff(gA, g, 2) - printed_d2) == 0)
print("           printed expression = 2 a_B1 (p_A2-c_A)(p_B2-c_B) Q2:", z(printed_d2 - 2 * aB1 * (pa2 - ca) * (pb2 - cb) * Q2) == 0)
coeffs = [sp.factor(c) for c in gA_poly.all_coeffs()]
print("           coefficients of g_A^SN (gamma^2, gamma^1, gamma^0):")
for c in coeffs:
    print("             ", c)

# convexity in theta
r = r_N()
rp = sp.diff(r, th)
rpp = sp.diff(r, th, 2)
d2 = sp.diff(N["yA"], th, 2)
print("Convexity: d^2 y^N_A1/d theta^2 = 2 sigma a_B1 (2 r' + theta r''):", z(d2 - 2 * sg * aB1 * (2 * rp + th * rpp)) == 0)
print("           r'' = 2 J r' / den:", z(rpp - 2 * J * rp / den) == 0)
print("y^S_A1 is affine in theta:", sp.diff(S["yA"], th, 2) == 0)

# exact probes over admissible points: sign facts and the gamma threshold
rng = Random(11)
ok = {"Q2>0": True, "A19>=0": True, "printed_d2>0": True, "theta0<0": True}
thresholds = []
fails_small_gamma = 0
for k in range(400):
    pt = random_point(rng, equal_shares=(k % 3 == 0), bind=(k % 5 == 0, k % 7 == 0), equal_prices=(k % 11 == 0))
    ok["Q2>0"] &= bool(subs_point(Q2, pt) > 0)
    ok["printed_d2>0"] &= bool(subs_point(printed_d2, pt) > 0)
    gv = sp.Rational(rng.randint(1, 10**4), 100)
    for tv in (0, sp.Rational(1, 3), 1):
        ok["A19>=0"] &= bool(subs_point(dr, pt, {g: gv, th: tv}) >= 0)
    ok["theta0<0"] &= bool(subs_point(d0, pt, {g: gv}) < 0)
    gpoly = sp.Poly(subs_point(gA, pt), g)
    roots = [float(x) for x in sp.Poly(gpoly).real_roots() if x > 0]
    thresholds.append(max(roots) if roots else 0.0)
    if subs_point(gA, pt, {g: sp.Rational(1, 100)}) < 0:
        fails_small_gamma += 1
print("Exact probes at 400 admissible points (incl. A11 binding, equal shares, equal prices):", ok)
print("  largest positive root of g_A^SN (threshold for y^N > y^S at theta=1): min %.3g, median %.3g, max %.3g"
      % (min(thresholds), sorted(thresholds)[200], max(thresholds)))
print("  points where g_A^SN(1/100) < 0, i.e. y^N_A1 < y^S_A1 at theta = 1 for small gamma:", fails_small_gamma)

# convexity and single crossing at the cutoff gamma: check on a theta grid at points just above the root
crossing_ok = True
for k in range(60):
    pt = random_point(rng, equal_shares=(k % 2 == 0), bind=(k % 4 == 0, k % 6 == 0))
    gpoly = sp.Poly(subs_point(gA, pt), g)
    roots = [x for x in gpoly.real_roots() if x > 0]
    gv = (sp.Rational(int(float(max(roots)) * 1000) + 1, 1000) if roots else sp.Rational(1, 100)) * 2
    diff = [subs_point(S["yA"] - N["yA"], pt, {g: gv, th: sp.Rational(j, 200)}) for j in range(201)]
    signs = [1 if v > 0 else (-1 if v < 0 else 0) for v in diff]
    nz = [s for s in signs if s != 0]
    crossing_ok &= nz[0] == 1 and nz[-1] == -1 and sum(1 for a, b in zip(nz, nz[1:]) if a != b) == 1
print("At 60 points with gamma = twice the root: y^S - y^N > 0 at 0, < 0 at 1, one sign change on 201 nodes:", crossing_ok)
