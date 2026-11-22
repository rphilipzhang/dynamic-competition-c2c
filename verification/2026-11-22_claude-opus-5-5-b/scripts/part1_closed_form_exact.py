"""Part 1: numerics/c2c/closed_form.py against the paper and the model, by an independent route.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5-b/scripts/part1_closed_form_exact.py

What it does (nothing here reuses the formulas of the test suite):
 1. Symbolic: pfta_t2_case1 / pftb_t2_case1 equal pi^0 of Lemma 1, with the expected leftovers obtained
    here by integrating the demand system of Section 3 over X ~ U[mu - sigma, mu + sigma].
 2. Symbolic: _leftover_high / _leftover_low equal those integrals in generic symbols.
 3. Symbolic: the branch inequalities of first_period_s / first_period_n are the fractile orderings,
    and in Scenario N the ordering zeta_A >= zeta_B with Lemma 3's zeta_B is equivalent to the code's test.
 4. Exact rational arithmetic at random points (A11 not imposed, both branches): the first-period
    orders of first_period_s, first_period_n and find_general_exo against this script's own derivation
    from the first-order conditions, the FOC residuals of the systems in the proofs of Lemmas 2, 3, B.1,
    and the total profits spfta_t1, spftb_t1, npfta_t1, npftb_t1, find_general_exo against profits
    computed here from the model (expected sales by exact piecewise integration, continuation
    pi^0 + (p2 - c) E[Z]).
 5. Floating point: the share (1 + 2 beta d) / 2 of the port is bit-identical to MATLAB's 1/2 + beta d.
"""
from __future__ import annotations

import random
import sys
from fractions import Fraction as Fr

sys.path.insert(0, "numerics")
import numpy as np
import sympy as sp

from c2c import closed_form as cf

# ------------------------------------------------------------------------------------------ 1-2 symbolic
pa, pb, th, ca, cb, be, mu, sg = sp.symbols("p_A p_B theta c_A c_B beta mu sigma", positive=True)
x = sp.symbols("x", real=True)


def model_leftovers_sym(a_h, a_l, z_h, z_l, theta, mu_, sg_):
    """E[(y - D)^+] of the retailer with the higher fractile (h) and the lower one (l), at
    y_h = (a_h + theta a_l) z_h - theta a_l z_l, y_l = a_l z_l, from D_i = a_i X + theta (a_j X - y_j)^+.
    For X <= z_l nobody is out of stock; for z_l < X <= z_h only l is out; above z_h both are."""
    y_h = (a_h + theta * a_l) * z_h - theta * a_l * z_l
    y_l = a_l * z_l
    lo = mu_ - sg_
    L_h = (sp.integrate(y_h - a_h * x, (x, lo, z_l))
           + sp.integrate(y_h - (a_h * x + theta * (a_l * x - y_l)), (x, z_l, z_h))) / (2 * sg_)
    L_l = sp.integrate(y_l - a_l * x, (x, lo, z_l)) / (2 * sg_)
    # demand of h reaches y_h exactly at X = z_h
    assert sp.simplify(y_h - (a_h * z_h + theta * (a_l * z_h - y_l))) == 0
    return y_h, y_l, L_h, L_l


aA = sp.Rational(1, 2) + be * (pb - pa)
aB = 1 - aA
zA = mu - sg + 2 * sg * (1 - ca / pa)
zB = mu - sg + 2 * sg * (1 - cb / pb)
yA, yB, LA, LB = model_leftovers_sym(aA, aB, zA, zB, th, mu, sg)
piA = (pa - ca) * yA - pa * LA
piB = (pb - cb) * yB - pb * LB
dA = sp.cancel(sp.together(cf.pfta_t2_case1(pa, pb, th, ca, cb, be, mu, sg) - piA))
dB = sp.cancel(sp.together(cf.pftb_t2_case1(pa, pb, cb, be, mu, sg) - piB))
print("1. pfta_t2_case1 - pi^0_A (Lemma 1 + model leftovers), simplified:", dA)
print("1. pftb_t2_case1 - pi^0_B (Lemma 1 + model leftovers), simplified:", dB)

ah, al, zh, zl = sp.symbols("a_h a_l z_h z_l", positive=True)
_, _, Lh, Ll = model_leftovers_sym(ah, al, zh, zl, th, mu, sg)
print("2. _leftover_high - model integral:", sp.expand(cf._leftover_high(ah, al, th, zh, zl, mu, sg) - Lh))
print("2. _leftover_low  - model integral:", sp.expand(cf._leftover_low(al, zl, mu, sg) - Ll))

# ------------------------------------------------------------------------------------------ 3 branch algebra
pa1, pb1, pa2, pb2, g, a2 = sp.symbols("p_A1 p_B1 p_A2 p_B2 gamma alpha_A2", positive=True)
code_s = pa1 - (ca / cb * pb1 + g / cb * (ca * (pb2 - cb) - cb * (pa2 - ca)))
code_n = pa1 - (ca / cb * pb1 + g / cb * ((1 - a2) * ca * (pb2 - cb) - a2 * cb * (pa2 - ca)))
cross_s = cb * (pa1 + g * (pa2 - ca)) - ca * (pb1 + g * (pb2 - cb))
cross_n = cb * (pa1 + a2 * g * (pa2 - ca)) - ca * (pb1 + (1 - a2) * g * (pb2 - cb))
print("3. cb*(code S test) - [cb(pA1+g mA) - cA(pB1+g mB)]:", sp.expand(cb * code_s - cross_s))
print("3. cb*(code N test) - [cb(pA1+aA2 g mA) - cA(pB1+aB2 g mB)]:", sp.expand(cb * code_n - cross_n))
kA = ca / (pa1 + a2 * g * (pa2 - ca))
one_minus_FzB = (cb - (1 - a2) * g * th * (pb2 - cb) * kA) / (pb1 + (1 - a2) * g * (1 - th) * (pb2 - cb))
ident = sp.simplify((one_minus_FzB - kA) - (cb - kA * (pb1 + (1 - a2) * g * (pb2 - cb)))
                    / (pb1 + (1 - a2) * g * (1 - th) * (pb2 - cb)))
print("3. [1-F(zeta^N_B) - kappa_A] - [cB - kappa_A (pB1 + aB2 g mB)]/(pB1 + aB2 g (1-th) mB):", ident)
print("   so zeta^N_A >= zeta^N_B  <=>  kappa_A (pB1 + aB2 g mB) <= cB  <=>  code N test >= 0")

# ------------------------------------------------------------------------------------------ 4 exact points
def integ(c0, c1, u, v):
    """Integral of c0 - c1 x over [u, v]."""
    return c0 * (v - u) - c1 * (v * v - u * u) / 2


def leftovers_exact(a_h, a_l, z_h, z_l, theta, mu_, sg_):
    lo = mu_ - sg_
    y_h = (a_h + theta * a_l) * z_h - theta * a_l * z_l
    y_l = a_l * z_l
    L_l = integ(y_l, a_l, lo, z_l) / (2 * sg_)
    L_h = (integ(y_h, a_h, lo, z_l) + integ(y_h + theta * y_l, a_h + theta * a_l, z_l, z_h)) / (2 * sg_)
    return y_h, y_l, L_h, L_l


def equilibrium(p1, p2, c, a1, theta, w, mu_, sg_):
    """First-period equilibrium derived here from the FOCs, for continuation weights
    w = (g_A, g_B, gc_A, gc_B): Z_{i,2} = g_i R_i + gc_i R_j. Returns orders, leftovers, fractiles, A_high."""
    (pA1, pB1), (pA2, pB2), (cA, cB), (gA, gB, gcA, gcB) = p1, p2, c, w
    mA, mB = pA2 - cA, pB2 - cB
    kA, kB = cA / (pA1 + gA * mA), cB / (pB1 + gB * mB)
    if kA <= kB:
        qA, qB = 1 - kA, 1 - (cB - gcB * theta * mB * kA) / (pB1 + (gB - gcB * theta) * mB)
    else:
        qB, qA = 1 - kB, 1 - (cA - gcA * theta * mA * kB) / (pA1 + (gA - gcA * theta) * mA)
    zA_, zB_ = mu_ - sg_ + 2 * sg_ * qA, mu_ - sg_ + 2 * sg_ * qB
    if kA <= kB:
        yA_, yB_, LA_, LB_ = leftovers_exact(a1, 1 - a1, zA_, zB_, theta, mu_, sg_)
    else:
        yB_, yA_, LB_, LA_ = leftovers_exact(1 - a1, a1, zB_, zA_, theta, mu_, sg_)
    return yA_, yB_, LA_, LB_, zA_, zB_, qA, qB, kA <= kB


def foc_residuals(p1, p2, c, a1, theta, w, yA_, yB_, mu_, sg_, a_high):
    """Residuals of the FOC systems (modeln:eq1, modelg:eq1 and their mirror) at the given orders."""
    (pA1, pB1), (pA2, pB2), (cA, cB), (gA, gB, gcA, gcB) = p1, p2, c, w
    mA, mB = pA2 - cA, pB2 - cB
    F = lambda u: (u - mu_ + sg_) / (2 * sg_)
    aA1, aB1 = a1, 1 - a1
    if a_high:
        xs = (yA_ + theta * yB_) / (aA1 + theta * aB1)
        r1 = pA1 - cA + gA * mA - (pA1 + gA * mA) * F(xs)
        r2 = pB1 - cB + gB * mB - (pB1 + (gB - gcB * theta) * mB) * F(yB_ / aB1) - gcB * theta * mB * F(xs)
    else:
        xs = (yB_ + theta * yA_) / (aB1 + theta * aA1)
        r1 = pB1 - cB + gB * mB - (pB1 + gB * mB) * F(xs)
        r2 = pA1 - cA + gA * mA - (pA1 + (gA - gcA * theta) * mA) * F(yA_ / aA1) - gcA * theta * mA * F(xs)
    return r1, r2


def pi0_exact(pA2, pB2, cA, cB, beta, theta, mu_, sg_):
    a2_ = Fr(1, 2) + beta * (pB2 - pA2)
    yA_, yB_, LA_, LB_, *_ = equilibrium((pA2, pB2), (pA2, pB2), (cA, cB), a2_, theta, (0, 0, 0, 0), mu_, sg_)
    return pA2 * (yA_ - LA_) - cA * yA_, pB2 * (yB_ - LB_) - cB * yB_


def model_profits(pt, w, a_high_out=None):
    pA1, pB1, pA2, pB2, theta, cA, cB, beta, mu_, sg_, gam = pt
    a1 = Fr(1, 2) + beta * (pB1 - pA1)
    yA_, yB_, LA_, LB_, zA_, zB_, qA, qB, a_high = equilibrium((pA1, pB1), (pA2, pB2), (cA, cB), a1, theta, w, mu_, sg_)
    gA, gB, gcA, gcB = w
    RA, RB = yA_ - LA_, yB_ - LB_
    p0A, p0B = pi0_exact(pA2, pB2, cA, cB, beta, theta, mu_, sg_)
    PiA = pA1 * RA - cA * yA_ + (pA2 - cA) * (gA * RA + gcA * RB) + p0A
    PiB = pB1 * RB - cB * yB_ + (pB2 - cB) * (gB * RB + gcB * RA) + p0B
    res = foc_residuals((pA1, pB1), (pA2, pB2), (cA, cB), a1, theta, w, yA_, yB_, mu_, sg_, a_high)
    return dict(y=(yA_, yB_), L=(LA_, LB_), z=(zA_, zB_), q=(qA, qB), a_high=a_high, Pi=(PiA, PiB), foc=res)


def lat(rng, lo, hi, den=1000):
    return Fr(rng.randint(int(lo * den), int(hi * den)), den)


def draw(rng, a11):
    cB = lat(rng, 0.5, 3)
    cA = cB * lat(rng, 0.05, 0.98)
    mu_ = lat(rng, 5, 20)
    sg_ = mu_ * lat(rng, 0.1, 0.95)
    if a11:
        pB1, pB2 = cB * lat(rng, 1.05, 4), cB * lat(rng, 1.05, 4)
        pA1 = cA / cB * pB1 + (pB1 - cA / cB * pB1) * lat(rng, 0, 1)
        pA2 = cA / cB * pB2 + (pB2 - cA / cB * pB2) * lat(rng, 0, 1)
    else:
        pA1, pB1, pA2, pB2 = (cB * lat(rng, 1.05, 4) for _ in range(4))
    gap = max(abs(pB1 - pA1), abs(pB2 - pA2), Fr(1, 10**6))
    beta = min(Fr(1, 2), Fr(45, 100) / gap * lat(rng, 0, 1))
    theta = rng.choice([Fr(0), Fr(1), lat(rng, 0, 1)])
    gam = rng.choice([Fr(1, 20), Fr(50), lat(rng, 0.05, 10)])
    return (pA1, pB1, pA2, pB2, theta, cA, cB, beta, mu_, sg_, gam)


rng = random.Random(20261122)
stats = {k: dict(points=0, skipped=0, b_high=0, mismatch=0, foc_nonzero=0) for k in ("S", "N", "G")}
g_detail = dict(p2_b_high=0, mismatch_p2_b_high=0, mismatch_p2_a_high=0, a11_points=0, mismatch_a11=0)
for n in range(240):
    a11 = n % 3 == 0
    pt = draw(rng, a11)
    pA1, pB1, pA2, pB2, theta, cA, cB, beta, mu_, sg_, gam = pt
    a2_ = Fr(1, 2) + beta * (pB2 - pA2)
    lam_s = lat(rng, 0, 1)
    weights = {"S": (gam, gam, 0, 0),
               "N": (a2_ * gam, (1 - a2_) * gam, a2_ * gam, (1 - a2_) * gam),
               "G": ((lam_s + (1 - lam_s) * a2_) * gam, (lam_s + (1 - lam_s) * (1 - a2_)) * gam,
                     (1 - lam_s) * gam * a2_, (1 - lam_s) * gam * (1 - a2_))}
    for sc, w in weights.items():
        m = model_profits(pt, w)
        st = stats[sc]
        if not all(0 <= q <= 1 for q in m["q"]) or (sc == "G" and not m["a_high"]):
            st["skipped"] += 1          # fractile outside [0, 1], or G outside the case the code implements
            continue
        st["points"] += 1
        st["b_high"] += not m["a_high"]
        st["foc_nonzero"] += any(r != 0 for r in m["foc"])
        if sc == "S":
            code_q = cf.first_period_s(*pt)
            code_pi = (cf.spfta_t1(*pt), cf.spftb_t1(*pt))
        elif sc == "N":
            code_q = cf.first_period_n(*pt)
            code_pi = (cf.npfta_t1(*pt), cf.npftb_t1(*pt))
        else:
            ya_g, yb_g, pia_g, pib_g = cf.find_general_exo(*pt, lam_s, 1 - lam_s)
            code_q = (ya_g, yb_g, None, None, None, None, True)
            code_pi = (pia_g, pib_g)
        same = (code_q[0], code_q[1]) == m["y"] and code_pi == m["Pi"] and code_q[6] == m["a_high"]
        if sc != "G":
            same = same and (code_q[2], code_q[3]) == m["L"] and (code_q[4], code_q[5]) == m["z"]
        st["mismatch"] += not same
        if sc == "G":
            p2_b = cA / pA2 > cB / pB2
            g_detail["p2_b_high"] += p2_b
            g_detail["mismatch_p2_b_high" if p2_b else "mismatch_p2_a_high"] += not same
            g_detail["a11_points"] += a11
            g_detail["mismatch_a11"] += a11 and not same
            if not same and not p2_b:
                print("   G mismatch with A-high second period:", [float(v) for v in pt])
for sc, st in stats.items():
    print(f"4. scenario {sc}: exact points {st['points']} (skipped {st['skipped']}), B higher fractile at "
          f"{st['b_high']}, points where code != model (orders, leftovers, fractiles, branch, profits): "
          f"{st['mismatch']}, nonzero FOC residuals: {st['foc_nonzero']}")
print("4. scenario G detail (find_general_exo implements only the A11 ordering in both periods):", g_detail)

# second-period profit with the mirrored branch, exact
mism2 = 0
for _ in range(100):
    pt = draw(rng, False)
    pA1, pB1, pA2, pB2, theta, cA, cB, beta, mu_, sg_, gam = pt
    p0A, p0B = pi0_exact(pA2, pB2, cA, cB, beta, theta, mu_, sg_)
    RA = lat(rng, 0, 1) * (mu_ + sg_)
    RB = lat(rng, 0, 1) * (mu_ + sg_ - RA)
    a2_ = Fr(1, 2) + beta * (pB2 - pA2)
    for sc, (ZA, ZB) in {"S": (gam * RA, gam * RB), "N": (a2_ * gam * (RA + RB), (1 - a2_) * gam * (RA + RB))}.items():
        code = cf.period2_profit(pA2, pB2, theta, cA, cB, beta, mu_, sg_, sc, gam, RA, RB)
        mism2 += code != (p0A + (pA2 - cA) * ZA, p0B + (pB2 - cB) * ZB)
print(f"4. period2_profit vs pi^0 + (p2 - c) Z at 100 exact points without A11, both scenarios: mismatches {mism2}")

# ------------------------------------------------------------------------------------------ 5 share bits
r = np.random.default_rng(5)
b = r.uniform(0, 0.5, 200000)
p = r.uniform(1, 10, 200000)
q = r.uniform(1, 10, 200000)
port = (1 + 2 * b * (q - p)) / 2
matlab = 0.5 + b * (q - p)
print("5. share: bitwise mismatches between (1 + 2 b d)/2 and 1/2 + b d over 200000 random doubles:",
      int(np.count_nonzero(port != matlab)))
