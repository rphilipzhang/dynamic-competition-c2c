"""P5 (Proposition 5): profit of retailer A.  Symbolic identities for (a)-(c2) and exact probes.

h_A is the polynomial (Pi^S_A - Pi^N_A) P^S_A (P^S_B)^2 (P^N_A)^2 den^2 / gamma built in
shared_profit_polys.py; the printed denominator factors are checked to be these.

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5-b/scripts/P5_symbolic_steps.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from random import Random

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared_sec4_closed_forms import (PN_A, PS_A, PS_B, aA1, aA2, aB1, aB2, ca, cb, g, mu, pa1, pa2, pb1, pb2, profits,
                                      r_N, random_point, scen_N, scen_S, benchmark, sg, subs_point, th)
from shared_profit_polys import DEN4, GENS, h_A

v, w = pa2 - ca, pb2 - cb
Q1 = cb * pa1 - ca * pb1
Q2 = aA2 * cb * v - aB2 * ca * w

# ---------------------------------------------------------------- (a)
a, P, c, tA, tB, mu_, s_ = sp.symbols("a P c t_A t_B mu_ s_", positive=True)
ERA = a * mu_ - s_ * ((a + th * (1 - a)) * tA**2 - th * (1 - a) * tB**2)
yA = (a + th * (1 - a)) * (mu_ + s_ - 2 * s_ * tA) - th * (1 - a) * (mu_ + s_ - 2 * s_ * tB)
FP = P * ERA - c * yA                                     # period profit P E[R] - c y, with P tA = c
dFP = sp.diff(FP, th).subs(c, P * tA)
print("(a) generic: d/dtheta [P E R_A - c y_A] = a_B sigma P (t_B - t_A)^2 = a_B P (zeta_A - zeta_B)^2/(4 sigma):",
      sp.expand(dFP - (1 - a) * s_ * P * (tB - tA)**2) == 0)
full = profits(th)
S, B2 = scen_S(), benchmark(2)
printed_a = (aB1 * PS_A / (4 * sg) * (S["zA"] - S["zB"])**2 + aB2 * pa2 / (4 * sg) * (B2["zA"] - B2["zB"])**2)
dPiS = sp.diff(full["PiS_A"], th)
rng0 = Random(50)
ok_a = sum(subs_point(dPiS - printed_a, pt, {th: sp.Rational(rng0.randint(0, 10), 10), g: sp.Rational(rng0.randint(1, 9999), 13)}) == 0
           for pt in (random_point(rng0, bind=(k % 3 == 0, k % 2 == 0)) for k in range(10)))
print(f"(a) dPi^S_A/dtheta equals the printed expression: exact at {ok_a}/10 points (the generic identity above is the proof)")

# ---------------------------------------------------------------- (b)
N = scen_N()
FP_S = pa1 * S["RA"] - ca * S["yA"]
FP_N = pa1 * N["RA"] - ca * N["yA"]
B1 = benchmark(1)
FP_0 = pa1 * B1["RA"] - ca * B1["yA"]
rng = Random(51)
ok_b = 0
for k in range(12):
    pt = random_point(rng, equal_shares=(k % 2 == 0), bind=(k % 3 == 0, k % 4 == 0))
    rep = {th: sp.Rational(rng.randint(0, 10), 10), g: sp.Rational(rng.randint(1, 9999), 11)}
    e1 = full["PiS_A"] - full["Pi0_A"] - (FP_S - FP_0 + g * v * S["RA"])
    e2 = full["PiN_A"] - full["Pi0_A"] - (FP_N - FP_0 + g * aA2 * v * (N["RA"] + N["RB"]))
    e3 = full["PiS_A"] - full["PiN_A"] - (FP_S - FP_N + g * v * (S["RA"] - aA2 * (N["RA"] + N["RB"])))
    ok_b += all(subs_point(e, pt, rep) == 0 for e in (e1, e2, e3))
print(f"(b),(c1) decompositions Pi^S_A-Pi^0_A = dFP + gamma v E[R^S_A1], Pi^N_A-Pi^0_A = dFP + gamma a_A2 v E[R^N_1],"
      f" Pi^S_A-Pi^N_A = dFP + gamma v (E[R^S_A1] - a_A2 E[R^N_1]): exact at {ok_b}/12 points")
print("(b) generic lower bound: E R_A - a_A(mu - sigma) = sigma[a_A (1 - t_A^2) + th a_B (t_B^2 - t_A^2)] (>= 0 as t_A <= t_B <= 1):",
      sp.expand(ERA - a * (mu_ - s_) - s_ * (a * (1 - tA**2) + th * (1 - a) * (tB**2 - tA**2))) == 0)
r = r_N()
print("(c1) (1-theta) r(theta) <= c_B/J (my bound: (1-th)(c_B - K th)/(p_B1 + J(1-th)) <= c_B/J); exact check at 2000 samples,",
      end=" ")
J_ = aB2 * g * w
bad = 0
for k in range(100):
    pt = random_point(rng, bind=(k % 3 == 0, False))
    for j in range(20):
        val = subs_point(cb / J_ - (1 - th) * r, pt, {th: sp.Rational(j, 19), g: sp.Rational(rng.randint(1, 10**5), 97)})
        bad += int(bool(val < 0))
print("violations", bad)

# uniformity probe for (c1): gamma * |(Pi^S-Pi^N)/gamma - mu v (a_A1 - a_A2)| over a theta grid stays bounded
from shared_profit_polys import compact_profits
_cp = compact_profits()
diffA = _cp["PiS_A"] - _cp["PiN_A"]
print("(c1) sup over 21 theta nodes of gamma*|(Pi^S_A-Pi^N_A)/gamma - mu (p_A2-c_A)(a_A1-a_A2)| at gamma = 1e1..1e5, 3 points:")
for k in range(3):
    pt = random_point(rng)
    row = []
    for e in range(1, 6):
        gv = sp.Integer(10)**e
        lead = subs_point(mu * v * (aA1 - aA2), pt)
        row.append(max(abs(subs_point(diffA - gv * lead, pt, {g: gv, th: sp.Rational(j, 20)})) for j in range(21)))
    print("     ", ["%.4g" % float(x) for x in row])

# ---------------------------------------------------------------- (c1-c2): h_A
hA = h_A()
printed_D = ((-g * ca + pa1 + g * pa2) * (g * cb - pb1 - g * pb2)**2 * (-aA2 * g * ca + pa1 + aA2 * g * pa2)**2 *
             (aA2 * g * cb * th - aA2 * g * cb - g * cb * th + g * cb - pb1 - aA2 * g * th * pb2 + aA2 * g * pb2
              + g * th * pb2 - g * pb2)**2)
print("(c) printed denominator = P^S_A (P^S_B)^2 (P^N_A)^2 den^2:",
      sp.expand(printed_D - PS_A * PS_B**2 * PN_A**2 * DEN4**2) == 0)
ok_h = 0
hA_e = hA.as_expr()
for k in range(8):
    pt = random_point(rng, equal_shares=(k % 2 == 0))
    rep = {th: sp.Rational(rng.randint(0, 10), 10), g: sp.Rational(rng.randint(1, 9999), 7)}
    ok_h += subs_point(full["PiS_A"] - full["PiN_A"] - g * hA_e / printed_D, pt, rep) == 0
print(f"(c) Pi^S_A - Pi^N_A = gamma h_A / printed denominator, exact at {ok_h}/8 points;"
      f" h_A degree in theta = {hA.degree(th)}, in gamma = {hA.degree(g)}")

# equal shares
hE = sp.Poly(hA_e.xreplace({aA2: aA1}), *GENS)
h0 = sp.Poly(hE.as_expr().xreplace({th: 0}), *GENS)
f0 = sp.factor_list(h0.as_expr())
print("(c2) factorization of h_A(0, gamma) with a_A1 = a_A2:")
quad = None
for fac, mult in f0[1]:
    d_ = sp.Poly(fac, g).degree()
    print(f"      factor (multiplicity {mult}, degree {d_} in gamma): {sp.factor(fac) if d_ < 2 else '[quadratic, below]'}")
    if d_ == 2:
        quad = sp.Poly(fac, g)
print("      constant:", f0[0])
print("      quadratic leading coefficient:", sp.factor(quad.LC()))
h1 = sp.Poly(hE.as_expr().xreplace({th: 1}), g)
print("(c2) h_A(1, gamma) degree in gamma:", h1.degree())
E_pr = (-2 * aA1 * ca**2 * pb1 + aB1 * ca * pa1 * pb2 + 2 * aA1 * ca * pa2 * pb1 - cb * pa1 * (aA1 * pa2 - (2 * aA1 - 1) * ca))
ratio = sp.factor(sp.cancel(h1.LC() / E_pr))
print("(c2) leading coefficient of h_A(1, gamma) / printed expression E =", ratio)
print("     this ratio = sigma a_B1 (p_A2-c_A) (p_B2-c_B)^2 Q2 (> 0) with equal shares:",
      sp.expand(ratio - (sg * aB1 * v * w**2 * Q2).xreplace({aA2: aA1})) == 0)
print("     quadratic factor of h_A(0, .) has leading coefficient (a_B1 c_A w)^2 - a_A1 (c_B v)^2 (< 0), and"
      " h_A(0, gamma) = [v a_B1 a_A1 sigma P^N_A (P^S_B)^2] * (-quadratic):",
      sp.expand(quad.LC() - ((1 - aA1) * ca * w)**2 + aA1 * (cb * v)**2) == 0,
      sp.expand(h0.as_expr() + (v * aB1 * aA1 * sg * PN_A * PS_B**2).xreplace({aA2: aA1}) * quad.as_expr()) == 0)
cbar = (-2 * aA1 * ca**2 * pb1 + aB1 * ca * pa1 * pb2 + 2 * aA1 * ca * pa2 * pb1) / (pa1 * (aA1 * pa2 - (2 * aA1 - 1) * ca))
cbar_num = -2 * aA1 * ca**2 * pb1 + aB1 * ca * pa1 * pb2 + 2 * aA1 * ca * pa2 * pb1
print("(c2) E = p_A1 (a_A1 p_A2 - (2 a_A1 - 1) c_A) (c-bar_B - c_B):",
      sp.expand(E_pr - cbar_num + pa1 * (aA1 * pa2 - (2 * aA1 - 1) * ca) * cb) == 0,
      "; a_A1 p_A2 - (2a_A1-1) c_A = a_A1 (p_A2-c_A) + (1-a_A1) c_A:",
      sp.expand(aA1 * pa2 - (2 * aA1 - 1) * ca - (aA1 * v + (1 - aA1) * ca)) == 0)
c3_expr = sum(cf * sp.Mul(*[s_**e for s_, e in zip(GENS, mo)]) / th**3 for mo, cf in hE.terms() if mo[1] == 3)
printed_d3 = 6 * aB1**3 * g * sg * w**2 * (aA1 * g * v + pa1)**2 * (cb * (pa1 + g * pa2) - ca * (pb1 + g * pb2))**2
print("(c2) d^3 h_A/dtheta^3 (equal shares) equals the printed expression:", sp.expand(6 * c3_expr - printed_d3) == 0)
cub_gen = sum(cf * sp.Mul(*[s_**e for s_, e in zip(GENS, mo)]) / th**3 for mo, cf in hA.terms() if mo[1] == 3)
print("     general shares: theta^3 coefficient of h_A =", sp.factor(cub_gen))

# probes for (c2) at fixed markets with c_B > c-bar_B; root count of h_A(., gamma) in (0, 1) is exact
count_adm, crossing_ok, n_tested, g4s = 0, 0, 0, []
k = 0
while n_tested < 25 and k < 4000:
    k += 1
    pt = random_point(rng, equal_shares=True, bind=(k % 4 == 0, False), equal_prices=(k % 5 == 0))
    if subs_point(E_pr, pt) >= 0:
        continue
    count_adm += 1
    qd = sp.Poly(subs_point(quad.as_expr(), pt), g)
    q1 = sp.Poly(subs_point(h1.as_expr(), pt), g)
    roots = [x for x in qd.real_roots() + q1.real_roots() if x > 0]
    g4 = max(roots) if roots else sp.Integer(0)
    g4s.append(float(g4))
    for gv in (sp.Rational(int(float(g4) * 1000) + 1, 1000), sp.Rational(int(float(g4) * 1000) + 1, 1000) * 10):
        hpt = sp.Poly(subs_point(hE.as_expr(), pt, {g: gv}), th)
        inside = [x for x in hpt.real_roots() if 0 < x < 1]
        ends = (hpt.eval(0) > 0) and (hpt.eval(1) < 0)
        crossing_ok += int(bool(ends) and len(inside) == 1)
    n_tested += 1
print(f"(c2) {n_tested} equal-share markets with c_B > c-bar_B: at gamma just above gamma_4 and at 10 gamma_4,"
      f" h_A(0)>0>h_A(1) with exactly one root in (0,1): {crossing_ok}/{2 * n_tested}")
print("     gamma_4 over these markets: min %.3g, max %.3g" % (min(g4s), max(g4s)))
ex = {pa1: 10, pb1: 10, pa2: 10, pb2: 10, ca: 2, cb: 6, aA1: sp.Rational(1, 2), aA2: sp.Rational(1, 2), mu: 10, sg: 4}
print("     example market p = 10 (all), c_A = 2, c_B = 6, shares 1/2, mu = 10, sigma = 4: c-bar_B =",
      cbar.xreplace(ex), "< c_B < p_B; E =", E_pr.xreplace(ex))
