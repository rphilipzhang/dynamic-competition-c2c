"""P6 (Proposition 6): profit of retailer B.  Symbolic identities for (a)-(c2) and exact probes.

My closed form for (a): the theta-dependent part of Pi^N_B is
  sigma a_B1 [c_B^2 (P^N_A)^2 - theta J c_A^2 (p_B1 + J)] / ((P^N_A)^2 den),   J = a_B2 gamma (p_B2 - c_B),
so dPi^N_B/dtheta = sigma a_B1 a_B2 gamma w h^N_B / ((P^N_A)^2 den^2) with
  h^N_B = (Q1 + gamma Q2) (c_B P^N_A + c_A (p_B1 + J))   (quadratic in gamma, free of theta, > 0 for gamma > 0).

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5-b/scripts/P6_symbolic_steps.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from random import Random

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared_sec4_closed_forms import (J, PN_A, PS_B, aA1, aA2, aB1, aB2, ca, cb, g, mu, pa1, pa2, pb1, pb2, profits,
                                      random_point, sg, subs_point, th)
from shared_profit_polys import DEN4, GENS, compact_profits, h_B

v, w = pa2 - ca, pb2 - cb
Q1 = cb * pa1 - ca * pb1
Q2 = aA2 * cb * v - aB2 * ca * w
cp = compact_profits()
full = profits(th)
rng = Random(61)

# ---------------------------------------------------------------- (a)
print("(a) Pi^S_B free of theta (full closed form):", sp.diff(full["PiS_B"], th) == 0)
part = sg * aB1 * (cb**2 * PN_A**2 - th * J * ca**2 * (pb1 + J)) / (PN_A**2 * DEN4)
ok = 0
for k in range(8):
    pt = random_point(rng, equal_shares=(k % 2 == 0), bind=(k % 3 == 0, False))
    gv = sp.Rational(rng.randint(1, 9999), 17)
    t1, t2 = sp.Rational(rng.randint(0, 10), 10), sp.Rational(rng.randint(0, 10), 10)
    lhs = subs_point(full["PiN_B"], pt, {g: gv, th: t1}) - subs_point(full["PiN_B"], pt, {g: gv, th: t2})
    rhs = subs_point(part, pt, {g: gv, th: t1}) - subs_point(part, pt, {g: gv, th: t2})
    ok += lhs == rhs
print(f"(a) Pi^N_B(theta1) - Pi^N_B(theta2) equals the same difference of my theta-part: exact at {ok}/8 point pairs")
hNB = (Q1 + g * Q2) * (cb * PN_A + ca * (pb1 + J))
print("(a) d(theta-part)/dtheta = sigma a_B1 a_B2 gamma w h^N_B / ((P^N_A)^2 den^2):",
      sp.simplify(sp.diff(part, th) - sg * aB1 * aB2 * g * w * hNB / (PN_A**2 * DEN4**2)) == 0)
print("    printed denominator [p_B1 + a_B2 gamma (1-theta)(p_B2-c_B)]^2 (-a_A2 gamma c_A + p_A1 + a_A2 gamma p_A2)^2 matches:",
      sp.expand((-aA2 * g * ca + pa1 + aA2 * g * pa2)**2 * (pb1 + aB2 * g * (1 - th) * w)**2 - PN_A**2 * DEN4**2) == 0)
print("    h^N_B degree in gamma:", sp.Poly(sp.expand(hNB), g).degree(), "; contains theta:", th in hNB.free_symbols,
      "; c_B P^N_A - c_A(p_B1 + J) = Q1 + gamma Q2:", sp.expand(cb * PN_A - ca * (pb1 + J) - Q1 - g * Q2) == 0)

# ---------------------------------------------------------------- (b)
from shared_sec4_closed_forms import scen_N, scen_S, benchmark
S, N, B1 = scen_S(), scen_N(), benchmark(1)
FP = lambda e: pb1 * e["RB"] - cb * e["yB"]
okb = 0
for k in range(8):
    pt = random_point(rng, equal_shares=(k % 2 == 0), bind=(False, k % 3 == 0))
    rep = {th: sp.Rational(rng.randint(0, 10), 10), g: sp.Rational(rng.randint(1, 9999), 11)}
    e1 = full["PiS_B"] - full["Pi0_B"] - (FP(S) - FP(B1) + g * w * S["RB"])
    e2 = full["PiN_B"] - full["Pi0_B"] - (FP(N) - FP(B1) + g * aB2 * w * (N["RA"] + N["RB"]))
    okb += subs_point(e1, pt, rep) == 0 and subs_point(e2, pt, rep) == 0
print(f"(b) Pi^S_B - Pi^0_B = dFP + gamma w E[R^S_B1] and Pi^N_B - Pi^0_B = dFP + gamma a_B2 w E[R^N_1]: exact at {okb}/8")

# ---------------------------------------------------------------- (c1)-(c2)
hB = h_B()
printed_D = ((-g * cb + pb1 + g * pb2) * (-aA2 * g * ca + pa1 + aA2 * g * pa2)**2 * ((1 - aA2) * g * (1 - th) * w + pb1))
okh = 0
hB_e = hB.as_expr()
for k in range(8):
    pt = random_point(rng, equal_shares=(k % 2 == 0))
    rep = {th: sp.Rational(rng.randint(0, 10), 10), g: sp.Rational(rng.randint(1, 9999), 7)}
    okh += subs_point(cp["PiS_B"] - cp["PiN_B"] - w * g * hB_e / printed_D, pt, rep) == 0
print(f"(c) Pi^S_B - Pi^N_B = (p_B2-c_B) gamma h_B / printed denominator: exact at {okh}/8 points;"
      f" h_B degree in theta = {hB.degree(th)}, in gamma = {hB.degree(g)}")


def coeff(poly, **deg):
    """Coefficient of gamma^k theta^j (as an expression) of a Poly over GENS."""
    kg, kt = deg.get("g", 0), deg.get("t", 0)
    return sp.Add(*[cf * sp.Mul(*[s_**e for s_, e in zip(GENS[2:], mo[2:])]) for mo, cf in poly.terms()
                    if mo[0] == kg and mo[1] == kt])


c40, c41 = coeff(hB, g=4, t=0), coeff(hB, g=4, t=1)
print("(c1) d^4 h_B/dgamma^4 = 24 a_B2 a_A2^2 (1-theta) mu (a_B1-a_B2) v^2 w^2:",
      sp.expand(24 * (c40 + th * c41) - 24 * aB2 * aA2**2 * (1 - th) * mu * (aB1 - aB2) * v**2 * w**2) == 0)
c30, c31 = coeff(hB, g=3, t=0), coeff(hB, g=3, t=1)
print("(c1) at theta = 1: gamma^4 coefficient vanishes and d^3 h_B(1,.)/dgamma^3 = 6 a_A2^2 mu p_B1 (a_B1-a_B2) v^2 w:",
      sp.expand(c40 + c41) == 0, sp.expand(6 * (c30 + c31) - 6 * aA2**2 * mu * pb1 * (aB1 - aB2) * v**2 * w) == 0)
print("(c1) uniformity in theta: h_B(theta) = (1-theta) h_B(0) + theta h_B(1) (linear), so the common threshold is the larger"
      " of the two endpoint thresholds")

# equal shares
eq = {aA2: aA1}
h0 = sp.Poly(hB_e.xreplace(eq).xreplace({th: 0}), g)
h1 = sp.Poly(hB_e.xreplace(eq).xreplace({th: 1}), g)
print("(c2) equal shares: degree of h_B(0, .) =", h0.degree(), ", of h_B(1, .) =", h1.degree())
pr0 = (1 - aA1) * aA1 * sg * (-2 * cb**2 * v**2 * aA2**2 - 2 * ca**2 * w**2 * aA2 + 2 * ca**2 * w**2)
print("(c2) d^2 h_B(0,.)/dgamma^2 equals the printed expression:", sp.expand(2 * h0.LC() - pr0.xreplace(eq)) == 0)
pr1 = 2 * aB1 * sg * ((aB1 * ca * w)**2 - (aA1 * cb * v)**2)
print("(c2) d^2 h_B(1,.)/dgamma^2 equals the printed expression:", sp.expand(2 * h1.LC() - pr1) == 0,
      "; and a_A1 c_B v - a_B1 c_A w = Q2 > 0 with equal shares:", sp.expand((aA1 * cb * v - aB1 * ca * w) - Q2.xreplace(eq)) == 0)
al, beta_, abar = sp.symbols("alpha beta abar", positive=True)
brk = -2 * cb**2 * v**2 * al**2 - 2 * ca**2 * w**2 * al + 2 * ca**2 * w**2
print("(c2) d bracket/d alpha_A2 = -4 c_B^2 v^2 alpha - 2 c_A^2 w^2 (< 0):",
      sp.expand(sp.diff(brk, al) + 4 * cb**2 * v**2 * al + 2 * ca**2 * w**2) == 0)
abar_e = sp.Rational(1, 2) + beta_ * (1 - ca / cb) * pb2
phi = brk.xreplace({al: abar_e})
dphi = sp.diff(phi, ca)
expect = 2 * (2 * ca * w**2 * (1 - abar) + ca**2 * w**2 * beta_ * pb2 / cb + 2 * cb**2 * v * abar**2
              + cb**2 * v**2 * 2 * abar * beta_ * pb2 / cb)
print("(c2) at alpha = abar(c_A) = 1/2 + beta (1 - c_A/c_B) p_B2, d phi/d c_A (c_B, prices, beta fixed) ="
      " 2[2 c_A w^2 (1-abar) + c_A^2 w^2 beta p_B2/c_B + 2 c_B^2 v abar^2 + 2 c_B v^2 abar beta p_B2]:",
      sp.simplify(dphi - expect.xreplace({abar: abar_e})) == 0, "(> 0 wherever abar <= 1; phi < 0 where abar > 1)")
print("(c2) at the A11 boundary p_A2 = c_A p_B2/c_B the bracket equals 2 c_A^2 w^2 (1 - alpha - alpha^2):",
      sp.simplify(brk.xreplace({pa2: ca * pb2 / cb}) - 2 * ca**2 * w**2 * (1 - al - al**2)) == 0,
      "; root (sqrt5-1)/2 =", float((sp.sqrt(5) - 1) / 2))

# probes at fixed equal-share markets with a positive bracket (actual shares): gamma_2, gamma_3 and the crossing
n, okc, g23 = 0, 0, []
proof_cond, k = 0, 0
while n < 40 and k < 5000:
    k += 1
    pt = random_point(rng, equal_shares=True, bind=(k % 4 == 0, False), equal_prices=(k % 5 == 0))
    if subs_point(pr0, pt) <= 0:                      # pt has equal shares, so alpha_A2 = alpha_A1 here
        continue
    abar_v = sp.Rational(1, 2) + pt["beta"] * (1 - pt[ca] / pt[cb]) * pt[pb2]
    proof_cond += int(bool(subs_point(brk, pt, {al: abar_v}) > 0))
    q0 = sp.Poly(subs_point(h0.as_expr(), pt), g)
    q1 = sp.Poly(subs_point(h1.as_expr(), pt), g)
    roots = [x for x in q0.real_roots() + q1.real_roots() if x > 0]
    gb = max(roots) if roots else sp.Integer(0)
    g23.append(float(gb))
    for gv in (sp.Rational(int(float(gb) * 1000) + 1, 1000), sp.Rational(int(float(gb) * 1000) + 1, 1000) * 10):
        a0 = subs_point(hB_e, pt, {g: gv, th: 0})
        a1 = subs_point(hB_e, pt, {g: gv, th: 1})
        okc += int(bool(a0 > 0) and bool(a1 < 0))
    n += 1
print(f"(c2) {n} equal-share markets with a positive bracket at the actual shares: h_B(0) > 0 > h_B(1) just above"
      f" max(gamma_2, gamma_3) and at 10 times it: {okc}/{2 * n}; of these markets, {proof_cond} also satisfy the proof's"
      f" sufficient condition (bracket > 0 at abar)")
print("     max(gamma_2, gamma_3): min %.3g, max %.3g" % (min(g23), max(g23)))

# A11-binding market with alpha = 0.7 and a small cost gap: the theta = 0 comparison reverses for large gamma
ex = {pb1: sp.Integer(4), pb2: sp.Integer(4), cb: sp.Integer(2), ca: sp.Rational(199, 100)}
ex[pa1] = ex[pa2] = ex[ca] * ex[pb1] / ex[cb]
beta_v = sp.Rational(2, 10) / (ex[pb1] - ex[pa1])
ex[aA1] = ex[aA2] = sp.Rational(1, 2) + beta_v * (ex[pb1] - ex[pa1])
ex[mu], ex[sg] = sp.Integer(10), sp.Integer(4)
vals = [hB_e.xreplace(ex).xreplace({th: 0, g: sp.Integer(10)**e}) for e in (1, 3, 6)]
print(f"(c2) market Delta c = 0.01, p_B = 4, c_B = 2, A11 binding, beta = {beta_v}, shares {ex[aA1]}: bracket ="
      f" {brk.xreplace(ex).xreplace({al: ex[aA1]})}; sign of h_B(0, gamma) at gamma = 1e1, 1e3, 1e6:",
      [int(sp.sign(x)) for x in vals])
