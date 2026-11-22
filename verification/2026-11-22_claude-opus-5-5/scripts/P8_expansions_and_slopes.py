"""Proposition 8: symbolic checks of the derivative formulas and light probes of the model.

Symbolic (SymPy), from the closed forms of Lemmas A.1(a) and A.2(a) (uniform seed demand):
  (a)   y^S_{i,1} - alpha_{i,1}(mu+sigma) and its price derivatives are O(1/gamma) (exact forms);
  (b1)  d y^N_{B,1}/d p_{A,1} - beta zeta^N_B and d y^N_{A,1}/d p_{A,1} + beta[(1-theta) zeta^N_A + theta zeta^N_B]
        are O(1/gamma) uniformly in theta (the bounds are printed as gamma times the remainder at large gamma);
  (A.25) the replacement error of theta gamma nu_B c_A/(p_A + gamma nu_A) by c_A nu_B/nu_A and its p_A-derivative
        when gamma (1 - theta) = l is held fixed;
  (A.26) the p_B-derivative of the leading term of (A.25).
Numerical:
  (A.22) <=> existence of an interior pair satisfying (A.23), on random markets (grid search);
  the model's slope d y^N_{B,1}/d p_{B,1} at theta = 1 - l/gamma against the leading term of (A.26),
  along gamma, at one market satisfying (A.22), and the sign of the slope as l grows.

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5/scripts/P8_expansions_and_slopes.py
"""
from __future__ import annotations

import sys
from dataclasses import replace

import numpy as np
import sympy as sp

sys.path.insert(0, "numerics")
from c2c import section5 as s5  # noqa: E402


def symbolic():
    print("== symbolic")
    pA, pB, cA, cB, b, mu, sg, th, g, ph, nA, nB, ell = sp.symbols(
        "p_A p_B c_A c_B beta mu sigma theta gamma pbar nu_A nu_B ell", positive=True)
    aA = sp.Rational(1, 2) + b * (pB - pA)
    aB = 1 - aA
    Finv1m = lambda x: mu + sg - 2 * sg * x  # noqa: E731   F^{-1}(1 - x)
    # (a) Scenario S exact closed form
    zA, zB = Finv1m(cA / (pA + g * (ph - cA))), Finv1m(cB / (pB + g * (ph - cB)))
    yA, yB = (aA + th * aB) * zA - th * aB * zB, aB * zB
    for name, expr, lead in (("y^S_A", yA, aA * (mu + sg)), ("y^S_B", yB, aB * (mu + sg))):
        rem = sp.simplify(expr - lead)
        lim = [sp.limit(sp.simplify(g * sp.diff(rem, v)), g, sp.oo) if v is not None else sp.limit(g * rem, g, sp.oo)
               for v in (None, pA, pB)]
        print(f"(a) gamma * (remainder, d/dp_A, d/dp_B) of {name} - alpha (mu+sigma) as gamma -> oo:", [sp.simplify(x) for x in lim])
    # (b1) Scenario N closed form without the O(gamma^-2) term
    q0 = cA / (pA + g * nA)
    t0 = (cB - th * g * nB * q0) / (pB + (1 - th) * g * nB)
    zA, zB = Finv1m(q0), Finv1m(t0)
    yA, yB = (aA + th * aB) * zA - th * aB * zB, aB * zB
    rB = sp.diff(yB, pA) - b * zB
    rA = sp.diff(yA, pA) + b * ((1 - th) * zA + th * zB)
    print("(b1) d yB/d pA - beta zeta_B =", sp.factor(sp.simplify(rB)))
    print("(b1) d yA/d pA + beta[(1-theta) zeta_A + theta zeta_B] =", sp.factor(sp.simplify(rA)))
    # bound of |gamma rB| uniformly in theta in [0, 1]: rB = -alpha_B * 2 sigma * d t0/d p_A
    dt0 = sp.simplify(sp.diff(t0, pA))
    print("     d t0/d p_A =", sp.factor(dt0), " (<= theta gamma nu_B c_A / ((gamma nu_A)^2 p_B) since the denominator factor >= p_B)")
    # (A.25) replacement error with gamma (1 - theta) = l fixed
    thl = 1 - ell / g
    err = sp.simplify((thl * g * nB * cA / (pA + g * nA) - cA * nB / nA))
    print("(A.25) replacement error =", sp.factor(err), "; gamma * error -> ", sp.limit(g * err, g, sp.oo),
          "; gamma * d/dp_A error ->", sp.limit(g * sp.diff(err, pA), g, sp.oo))
    # (A.26)
    K = sp.symbols("K", positive=True)        # K = c_B - c_A nu_B / nu_A
    lead = aB * (mu + sg - 2 * sg * K / (pB + ell * nB))
    printed = -b * (mu + sg) + sg * K * (1 + 2 * b * pA + 2 * b * ell * nB) / (pB + ell * nB) ** 2
    print("(A.26) d/dp_B of leading term of (A.25) - printed (A.26) =", sp.simplify(sp.diff(lead, pB) - printed))
    lead_sum = (aA + th * aB) * Finv1m(q0) + (1 - th) * aB * Finv1m(t0)
    print("(A.25) second line: gamma * [y_A + y_B - (mu+sigma)] and gamma * d/dp_B at gamma(1-theta)=l, gamma -> oo:",
          sp.simplify(sp.limit(g * (lead_sum.subs(th, thl) - (mu + sg)), g, sp.oo)), ",",
          sp.simplify(sp.limit(g * sp.diff(lead_sum.subs(th, thl), pB), g, sp.oo)))


def a22_equivalence(n=3000, seed=8):
    print("== (A.22) <=> interior pair with (A.23)")
    rng = np.random.default_rng(seed)
    agree = total = holds = 0
    for _ in range(n):
        mk = s5.draw_market(rng)
        ratio = s5.claimed_condition_a22(mk)
        if abs(ratio - 1) < 1e-3:
            continue                              # the grid cannot resolve the boundary case
        pa = np.linspace(mk.p_lo, mk.p_hi, 4002)[1:-1]
        bound = np.minimum(mk.p_hi, s5.claimed_bound_a23(mk, pa))
        exists = bool(np.any(bound > mk.p_lo))
        agree += exists == (ratio > 1)
        holds += ratio > 1
        total += 1
    print(f"   {total} markets, (A.22) holds at {holds}; agreement with the grid search: {agree}/{total}")


def model_slopes(seed=5302):
    print("== model slope d y_B/d p_B (Scenario N) against the leading term of (A.26)")
    rng = np.random.default_rng(seed)
    while True:
        mk = s5.draw_market(rng)
        if s5.claimed_condition_a22(mk) > 1.05:
            break
    nua, nub = s5.claimed_nu(mk)
    K = mk.cb - mk.ca * nub / nua
    pa0 = mk.p_hi - 0.05 * (mk.p_hi - mk.p_lo)
    pb0 = mk.p_lo + 0.3 * (min(mk.p_hi, float(s5.claimed_bound_a23(mk, pa0))) - mk.p_lo)
    print(f"   market: (A.22) ratio {s5.claimed_condition_a22(mk):.3f}, price pair ({pa0:.4f}, {pb0:.4f}), bound of (A.23) "
          f"{float(s5.claimed_bound_a23(mk, pa0)):.4f}")
    h = 1e-4 * (mk.p_hi - mk.p_lo)

    def slope(m, gamma):
        cont = s5.SecondPeriodN(m, max(2.0 / (gamma * m.lo), 1.001 / (gamma * m.smallest_share * m.lo)))
        assert not cont.problems
        out = []
        for d in (h, -h):
            pa, pb = np.array(pa0), np.array(pb0 + d)
            ya, yb = s5.inventory_equilibrium(m, cont, gamma, pa, pb, s5.claimed_orders_n(m, gamma, pa, pb))
            out.append((float(ya), float(yb)))
        return (out[0][0] - out[1][0]) / (2 * h), (out[0][1] - out[1][1]) / (2 * h)

    for ell in (0.0, 0.5):
        print(f"   gamma (1 - theta) = {ell}:")
        lead = -mk.beta * mk.hi + mk.sigma * K * (1 + 2 * mk.beta * pa0 + 2 * mk.beta * ell * nub) / (pb0 + ell * nub) ** 2
        for gamma in (1e2, 1e3, 1e4):
            m = replace(mk, theta=1 - ell / gamma)
            sa, sb = slope(m, gamma)
            print(f"      gamma={gamma:6.0f}: dyB/dpB = {sb:.5f} (leading term {lead:.5f}, gamma x gap = {gamma * (sb - lead):.3g}); "
                  f"dyA/dpB = {sa:.5f}")
    print("   sign of the leading term of (A.26) as gamma(1 - theta) = l grows:")
    for ell in (0.0, 1.0, 5.0, 20.0, 100.0):
        lead = -mk.beta * mk.hi + mk.sigma * K * (1 + 2 * mk.beta * pa0 + 2 * mk.beta * ell * nub) / (pb0 + ell * nub) ** 2
        print(f"      l = {ell:6.1f}: {lead:+.5f}")


if __name__ == "__main__":
    symbolic()
    a22_equivalence()
    model_slopes()
