"""LB1, listed difference 1: without the price condition A11 the closed form of Lemma B.1 is in
general not an equilibrium.

Run from the repository root, no arguments:
    python verification/2026-11-22_claude-opus-5-5-b/scripts/LB1_without_a11.py

The orders below are transcribed here from the printed statement of Lemma B.1 (and Lemma 1 for
y^0_{i,2}), always in the printed form, in which retailer A has the higher fractile. They are
tested against payoffs built from the model primitives (numerics/c2c/primitives.py through
section4.Game) and, independently, against this run's own demand system and quadrature
(shared_eqlemmas_unbounded_support.py). Uniform seed demand on [2, 18].

  Point 1: A11 fails in period 1 (p_{A,1} < (c_A/c_B) p_{B,1}) and c_A/P_A > c_B/P'_B: the
           printed first-period orders are not an equilibrium; the mirrored form is.
  Point 2: A11 fails in period 2 only (p_{A,2} < (c_A/c_B) p_{B,2}): the printed second-period
           orders y^0_{i,2} + Z_{i,2} (Lemma 1's form of y^0) are not an equilibrium of the
           second-period subgame; the mirrored benchmark plus Z is.
  Point 3: A11 fails (p_{A,t} > p_{B,t}) but c_A/P_A <= c_B/P'_B and zeta^0_{A,2} >= zeta^0_{B,2}
           still hold: the printed form is an equilibrium, so the failure is "in general", not
           everywhere.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, "numerics")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from c2c import primitives as pm  # noqa: E402
from c2c.section4 import Game, Params, claimed_benchmark, claimed_first_period  # noqa: E402
from shared_foc_kink_ordering import Bounded  # noqa: E402
from shared_eqlemmas_unbounded_support import nash_gap as own_nash_gap  # noqa: E402

LO, HI = 2.0, 18.0
UNIF = pm.Uniform(LO, HI)
OWN = Bounded("uniform", stats.uniform(loc=LO, scale=HI - LO))


def printed_first_period(p: Params):
    """Lemma B.1 as printed (rho = 1), A-higher form, whatever the prices."""
    gA, gB, cA, cB = p.weights("G")
    a1 = p.aa1
    mA, mB = p.pa2 - p.ca, p.pb2 - p.cb
    r = p.ca / (p.pa1 + gA * mA)
    qA = 1 - r
    qB = 1 - (p.cb - cB * p.theta * mB * r) / (p.pb1 + (gB - cB * p.theta) * mB)
    zA, zB = UNIF.ppf(qA), UNIF.ppf(qB)
    return (a1 + p.theta * (1 - a1)) * zA - p.theta * (1 - a1) * zB, (1 - a1) * zB, qA, qB, r, p.cb / (p.pb1 + gB * mB)


def printed_benchmark(pa, pb, p: Params):
    """Lemma 1 as printed, A-higher form."""
    a = pm.share(pa, pb, p.beta)
    zA, zB = UNIF.ppf(1 - p.ca / pa), UNIF.ppf(1 - p.cb / pb)
    return (a + p.theta * (1 - a)) * zA - p.theta * (1 - a) * zB, (1 - a) * zB, 1 - p.ca / pa, 1 - p.cb / pb


def own_period1(p: Params):
    gA, gB, cA, cB = p.weights("G")
    mA, mB = p.pa2 - p.ca, p.pb2 - p.cb

    def pay_a(ya, yb):
        ra, rb = OWN.expected_sales(ya, yb, p.aa1, 1 - p.aa1, p.theta)
        return p.pa1 * ra - p.ca * np.atleast_1d(ya) + mA * (gA * ra + cA * rb)

    def pay_b(ya, yb):
        ra, rb = OWN.expected_sales(ya, yb, p.aa1, 1 - p.aa1, p.theta)
        return p.pb1 * rb - p.cb * np.atleast_1d(yb) + mB * (gB * rb + cB * ra)
    return pay_a, pay_b


def a11(p):
    return all(pb >= pa >= p.ca / p.cb * pb for pa, pb in ((p.pa1, p.pb1), (p.pa2, p.pb2)))


def report_first(label, p):
    ya, yb, qA, qB, rA, rB = printed_first_period(p)
    pay_a, pay_b = Game(p, "G", UNIF).period1_payoffs()
    gap = pm.nash_gap(pay_a, pay_b, ya, yb, 1.5 * HI)
    own_gain, own_dist = own_nash_gap(*own_period1(p), ya, yb, 1.5 * HI)
    my, mb, *_ = claimed_first_period(p, "G", UNIF.ppf)          # the code mirrors when B's ratio is higher
    gap_m = pm.nash_gap(pay_a, pay_b, my, mb, 1.5 * HI)
    print(f"{label}: A11 holds: {a11(p)}; alpha_A1 = {p.aa1:.4f}, alpha_A2 = {p.aa2:.4f}; c_A/P_A = {rA:.6f}, c_B/P'_B = {rB:.6f}")
    print(f"    printed form: y_A = {ya:.6f}, y_B = {yb:.6f}, q_A = {qA:.6f}, q_B = {qB:.6f}")
    print(f"    primitives (section4.Game): best responses ({gap['br_a']:.6f}, {gap['br_b']:.6f}), largest gain from deviating {gap['gain']:.6e}")
    print(f"    own quadrature:             largest gain from deviating {own_gain:.6e}, distance of best response {own_dist:.6f}")
    print(f"    mirrored form ({my:.6f}, {mb:.6f}): largest gain {gap_m['gain']:.3e}, distance {gap_m['dist']:.2e}")
    return gap["gain"], own_gain, gap_m["gain"]


def report_second(label, p, ra1=4.0, rb1=3.0):
    y0a, y0b, q0a, q0b = printed_benchmark(p.pa2, p.pb2, p)
    game = Game(p, "G", UNIF)
    pay_a, pay_b, za, zb = game.period2_payoffs(ra1, rb1)
    ya, yb = y0a + za, y0b + zb
    gap = pm.nash_gap(pay_a, pay_b, ya, yb, game.upper)
    m0a, m0b, *_ = claimed_benchmark(p.pa2, p.pb2, p.ca, p.cb, p.beta, p.theta, UNIF.ppf)
    gap_m = pm.nash_gap(pay_a, pay_b, m0a + za, m0b + zb, game.upper)
    print(f"{label}: A11 holds: {a11(p)}; zeta^0 fractiles in period 2: q_A = {q0a:.6f}, q_B = {q0b:.6f}; state R_A1 = {ra1}, R_B1 = {rb1}")
    print(f"    printed y^0_2 + Z_2 = ({ya:.6f}, {yb:.6f}); best responses ({gap['br_a']:.6f}, {gap['br_b']:.6f}); largest gain {gap['gain']:.6e}")
    print(f"    mirrored benchmark + Z = ({m0a + za:.6f}, {m0b + zb:.6f}); largest gain {gap_m['gain']:.3e}")
    return gap["gain"], gap_m["gain"]


if __name__ == "__main__":
    p1 = Params(pa1=1.3, pb1=4.4, pa2=4.2, pb2=4.6, ca=1.0, cb=1.5, beta=0.1, theta=0.6, gamma=0.5, lam_s=0.5, lam_n=0.5)
    g1, g1own, g1m = report_first("Point 1", p1)
    assert g1 > 1e-3 and g1own > 1e-3 and g1m < 1e-9

    p2 = Params(pa1=4.0, pb1=4.4, pa2=1.4, pb2=4.6, ca=1.0, cb=1.5, beta=0.1, theta=0.6, gamma=0.5, lam_s=0.5, lam_n=0.5)
    g2, g2m = report_second("Point 2", p2)
    assert g2 > 1e-3 and g2m < 1e-9

    p3 = Params(pa1=4.6, pb1=4.4, pa2=4.8, pb2=4.6, ca=1.0, cb=1.5, beta=0.1, theta=0.6, gamma=0.5, lam_s=0.5, lam_n=0.5)
    g3, g3own, _ = report_first("Point 3", p3)
    g3b, _ = report_second("Point 3, period 2", p3)
    assert g3 < 1e-9 and g3own < 1e-9 and g3b < 1e-9
    print("all assertions hold")
