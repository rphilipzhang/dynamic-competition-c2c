"""P3 (Proposition 3): expected first-period sales.  Symbolic identities plus exact probes.

Method: first an identity for expected sales in terms of the critical ratios (q_A, q_B),
proved symbolically for the generic period game; then every theta-statement uses that
compact form with q_A free of theta and 1 - q_B = r(theta) (Lemma 3).

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5-b/scripts/P3_symbolic_steps.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from random import Random

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared_sec4_closed_forms import (J, PN_A, PS_A, PS_B, aA1, aA2, aB1, aB2, ca, cb, first_period, g, mu, pa1, pa2,
                                      pb1, pb2, r_N, random_point, scen_N, scen_S, sg, subs_point, th)

qA, qB, aA = sp.symbols("q_A q_B a_A", positive=True)
gen = first_period(aA, qA, qB, th)
ERA = lambda a, tA, tB, t: a * mu - sg * ((a + t * (1 - a)) * tA**2 - t * (1 - a) * tB**2)   # tails tA = 1 - q_A
ERB = lambda a, tB: (1 - a) * (mu - sg * tB**2)
print("Identity: E[R_A] = a_A mu - sigma[(a_A + th a_B)(1-q_A)^2 - th a_B (1-q_B)^2] (uniform law, z_A >= z_B):",
      sp.expand(gen["RA"] - ERA(aA, 1 - qA, 1 - qB, th)) == 0)
print("Identity: E[R_B] = a_B (mu - sigma (1-q_B)^2) = E[min(a_B X, a_B z_B)]:",
      sp.expand(gen["RB"] - ERB(aA, 1 - qB)) == 0)

uA_S, uB_S, uA_N = ca / PS_A, cb / PS_B, ca / PN_A        # tails 1 - F(zeta)
r = r_N()
RA_S, RA_N = ERA(aA1, uA_S, uB_S, th), ERA(aA1, uA_N, r, th)
RB_S, RB_N = ERB(aA1, uB_S), ERB(aA1, r)
rng = Random(31)
same = 0
for k in range(10):                                         # the compact forms equal the full closed forms
    pt = random_point(rng, equal_shares=(k % 2 == 0), bind=(k % 3 == 0, False))
    rep = {th: sp.Rational(rng.randint(0, 20), 20), g: sp.Rational(rng.randint(1, 9999), 17)}
    S, N = scen_S(), scen_N()
    same += all(subs_point(a_ - b_, pt, rep) == 0 for a_, b_ in ((S["RA"], RA_S), (N["RA"], RA_N), (S["RB"], RB_S), (N["RB"], RB_N)))
print(f"Compact forms equal the closed forms of shared_sec4_closed_forms exactly at {same}/10 points")

print("(a) dE[R^S_A1]/dtheta = a_B1 sigma [(1-F(zS_B))^2 - (1-F(zS_A))^2]:",
      sp.simplify(sp.diff(RA_S, th) - aB1 * sg * (uB_S**2 - uA_S**2)) == 0)
R_ = sp.Function("r")
RA_gen = ERA(aA1, uA_N, R_(th), th)
d1 = sp.diff(RA_gen, th)
print("(a) dE[R^N_A1]/dtheta = a_B1 sigma [r^2 - (c_A/P^N_A)^2] + 2 sigma a_B1 th r r':",
      sp.simplify(d1 - (aB1 * sg * (R_(th)**2 - uA_N**2) + 2 * sg * aB1 * th * R_(th) * sp.diff(R_(th), th))) == 0)
Q1 = cb * pa1 - ca * pb1
Q2 = aA2 * cb * (pa2 - ca) - aB2 * ca * (pb2 - cb)
print("    r(0) - c_A/P^N_A = (Q1 + gamma Q2)/[(p_B1 + J) P^N_A]  (> 0, so the right derivative at 0 is > 0):",
      sp.simplify(r.subs(th, 0) - uA_N - (Q1 + g * Q2) / ((pb1 + J) * PN_A)) == 0)
d2 = sp.diff(RA_gen, th, 2)
rr, rp, rpp = R_(th), sp.diff(R_(th), th), sp.diff(R_(th), th, 2)
print("(a) d^2 E[R^N_A1]/dtheta^2 = sigma a_B1 (4 r r' + 2 th r'^2 + 2 th r r''):",
      sp.simplify(d2 - sg * aB1 * (4 * rr * rp + 2 * th * rp**2 + 2 * th * rr * rpp)) == 0)
den = pb1 + J * (1 - th)
print("    with r > 0, r' = J (Q1 + gamma Q2)/(P^N_A den^2) >= 0, r'' = 2 J r'/den >= 0:",
      sp.simplify(sp.diff(r, th) - J * (Q1 + g * Q2) / (PN_A * den**2)) == 0,
      sp.simplify(sp.diff(r, th, 2) - 2 * J * sp.diff(r, th) / den) == 0)
print("(a) E[R^S_A1] affine in theta:", sp.diff(RA_S, th, 2) == 0)
d = RA_S - RA_N
printed0 = (aA1 * aB2 * g * ca**2 * sg * (pa2 - ca) * ((aA2 + 1) * g * (pa2 - ca) + 2 * pa1)
            / ((g * (pa2 - ca) + pa1)**2 * (aA2 * g * (pa2 - ca) + pa1)**2))
print("(a) theta = 0: E[R^S_A1] - E[R^N_A1] equals the printed expression:", sp.simplify(d.subs(th, 0) - printed0) == 0)

v, w = pa2 - ca, pb2 - cb
r1_num = cb * PN_A - aB2 * g * w * ca
print("    r(1) = (c_B P^N_A - a_B2 gamma w c_A)/(p_B1 P^N_A):", sp.simplify(r.subs(th, 1) - r1_num / (pb1 * PN_A)) == 0)
num = sp.expand(-ca**2 * pb1**2 * PS_B**2 * PN_A**2 + aB1 * cb**2 * pb1**2 * PS_A**2 * PN_A**2
                + ca**2 * pb1**2 * PS_A**2 * PS_B**2 - aB1 * PS_A**2 * PS_B**2 * r1_num**2)
print("    sigma^-1 p_B1^2 (P^S_A P^S_B P^N_A)^2 d(theta=1) equals that numerator:",
      sp.simplify(d.subs(th, 1) * pb1**2 * (PS_A * PS_B * PN_A)**2 / sg - num) == 0)
qt, rem = sp.div(sp.Poly(num, g), sp.Poly(g, g))
print("    numerator divisible by gamma:", rem.is_zero)
gR = qt.as_expr()
printed_den = pb1**2 * (g * ca - pa1 - g * pa2)**2 * (g * cb - pb1 - g * pb2)**2 * (aA2 * g * ca - pa1 - aA2 * g * pa2)**2
print("    printed denominator equals p_B1^2 (P^S_A P^S_B P^N_A)^2:", sp.expand(printed_den - pb1**2 * (PS_A * PS_B * PN_A)**2) == 0)
P = sp.Poly(gR, g)
print("    degree of g_R^SN in gamma:", P.degree(), "; leading coefficient = -a_B1 (p_A2-c_A)^2 (p_B2-c_B)^2 Q2^2:",
      sp.expand(P.LC() + aB1 * v**2 * w**2 * Q2**2) == 0, "; d^5 g/dgamma^5 = 120 LC")

cut, small_nonneg, cross_bad, mono_bad = [], 0, 0, 0
for k in range(150):
    pt = random_point(rng, equal_shares=(k % 3 == 0), bind=(k % 5 == 0, k % 7 == 0), equal_prices=(k % 11 == 0))
    poly = sp.Poly(subs_point(gR, pt), g)
    roots = [float(x) for x in poly.real_roots() if x > 0]
    cut.append(max(roots) if roots else 0.0)
    for gv in (sp.Rational(1, 20), sp.Rational(1), sp.Rational(50), sp.Rational(10**4)):
        vals = [subs_point(d, pt, {g: gv, th: sp.Rational(j, 40)}) for j in range(41)]
        ra = [subs_point(RA_N, pt, {g: gv, th: sp.Rational(j, 40)}) for j in range(41)]
        small_nonneg += int(gv == sp.Rational(1, 20) and bool(vals[-1] >= 0))
        nz = [1 if x > 0 else -1 for x in vals if x != 0]
        changes = sum(1 for a_, b_ in zip(nz, nz[1:]) if a_ != b_)
        cross_bad += int(not (bool(vals[0] > 0) and changes <= 1 and (changes == 0 or nz[-1] == -1)))
        mono_bad += int(any(bool(b_ < a_) for a_, b_ in zip(ra, ra[1:])))
print("    positive root of g_R^SN beyond which E[R^S_A1] < E[R^N_A1] at theta = 1: min %.3g, median %.3g, max %.3g"
      % (min(cut), sorted(cut)[75], max(cut)))
print("    points with E[R^S_A1] >= E[R^N_A1] at theta = 1 when gamma = 1/20 (cutoff theta' = 1):", small_nonneg, "/150")
print("    curves (150 points x 4 gammas, 41 theta nodes) violating 'positive at 0, at most one change, to negative':", cross_bad)
print("    curves on which E[R^N_A1] decreases between nodes (gammas 1/20, 1, 50, 1e4):", mono_bad)

print("(b) dE[R^N_B1]/dtheta = -2 sigma a_B1 r r' (<= 0):",
      sp.simplify(sp.diff(ERB(aA1, R_(th)), th) + 2 * sg * aB1 * rr * rp) == 0)
print("(b) E[R^S_B1] free of theta:", sp.diff(RB_S, th) == 0)
print("(b) E[R^S_B1] - E[R^N_B1] = sigma a_B1 (r^2 - (c_B/P^S_B)^2), > 0 since r > c_B/P^S_B by (A.20):",
      sp.simplify(RB_S - RB_N - sg * aB1 * (r**2 - uB_S**2)) == 0)
