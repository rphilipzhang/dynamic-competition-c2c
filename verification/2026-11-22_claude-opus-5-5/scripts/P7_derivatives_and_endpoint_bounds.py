"""Proposition 7: the derivative formulas of the proof, the shape of each piece, and the
bounds at the upper price bound.

Symbolic (SymPy): y^0_{i,2} on the two branches of Lemma 1 (either retailer with the higher
fractile), uniform seed demand; own- and rival-price derivatives against the printed
formulas; second derivatives (concave own-price pieces, convex first rival-price piece);
the jump of the own-price derivative at the switching price; the N-shift of the derivatives.

Numerical: an adversarial random search over the whole admissible region of Section 5
(A1, A12, A13, I1, theta in [0, 1], rival price in [p_lo, p_hi]) for the endpoint bounds
    d y_{i,2} / d p_{i,2} at p_{i,2} = p_hi  <=  -beta (mu^2 - mu sigma + sigma^2) / (mu + sigma),
    d y_{A,2} / d p_{B,2} at p_{B,2} = p_hi  >=  +beta (mu^2 - mu sigma + sigma^2) / (mu + sigma),
    d y_{B,2} / d p_{A,2} at p_{A,2} = p_hi  >=  +beta (mu^2 - mu sigma + sigma^2) / (mu + sigma),
on whichever branch contains p_hi. Prices and costs scale with 1/beta and orders with mu, so
c_B = 1 and mu = 1 without loss of generality.

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5/scripts/P7_derivatives_and_endpoint_bounds.py
"""
from __future__ import annotations

import numpy as np
import sympy as sp


def symbolic():
    print("== symbolic")
    pA, pB, cA, cB, b, mu, sg, th, gR = sp.symbols("p_A p_B c_A c_B beta mu sigma theta gammaR1", positive=True)
    aA = sp.Rational(1, 2) + b * (pB - pA)
    aB = 1 - aA
    zA = mu + sg - 2 * sg * cA / pA        # F^{-1}(1 - c_A/p_A) for U[mu - sigma, mu + sigma]
    zB = mu + sg - 2 * sg * cB / pB
    # branch "A high" (zeta_A >= zeta_B, i.e. p_A >= (c_A/c_B) p_B) and branch "B high"
    yA_Ahigh, yB_Ahigh = (aA + th * aB) * zA - th * aB * zB, aB * zB
    yA_Bhigh, yB_Bhigh = aA * zA, (aB + th * aA) * zB - th * aA * zA
    printed = {
        "dyA/dpA, p_A <= (c_A/c_B)p_B": (sp.diff(yA_Bhigh, pA), cA * sg * (2 * b * pB + 1) / pA ** 2 - b * (mu + sg)),
        "dyA/dpA, p_A > (c_A/c_B)p_B": (sp.diff(yA_Ahigh, pA),
                                         -b * (mu + sg) + cA * sg * (1 + th + 2 * b * (1 - th) * pB) / pA ** 2 + 2 * b * cB * th * sg / pB),
        "dyA/dpB, p_B < (c_B/c_A)p_A": (sp.diff(yA_Ahigh, pB),
                                         b * (-2 * cA * (1 - th) * sg / pA + mu + sg) - 2 * cB * b * th * pA * sg / pB ** 2 - cB * th * sg / pB ** 2),
        "dyA/dpB, p_B >= (c_B/c_A)p_A": (sp.diff(yA_Bhigh, pB), b * (-2 * cA * sg / pA + mu + sg)),
        "printed piece yA, p_A <= (c_A/c_B)p_B": (yA_Bhigh, (sp.Rational(1, 2) + b * pB - b * pA) * (-2 * cA * sg / pA + mu + sg)),
    }
    for name, (derived, paper) in printed.items():
        print(f"{name}: derived - printed = {sp.simplify(derived - paper)}")
    # mirror formulas for retailer B
    mirror = {
        "dyB/dpB, p_B < (c_B/c_A)p_A": sp.diff(yB_Ahigh, pB),
        "dyB/dpB, p_B >= (c_B/c_A)p_A": sp.diff(yB_Bhigh, pB),
        "dyB/dpA, p_A > (c_A/c_B)p_B": sp.diff(yB_Ahigh, pA),
        "dyB/dpA, p_A <= (c_A/c_B)p_B": sp.diff(yB_Bhigh, pA),
    }
    for name, expr in mirror.items():
        print(f"{name} = {sp.simplify(expr)}")
    # curvature of each piece
    print("d2 yA/dpA2 (B high) =", sp.factor(sp.diff(yA_Bhigh, pA, 2)), " (A high) =", sp.factor(sp.diff(yA_Ahigh, pA, 2)))
    print("d2 yB/dpB2 (A high) =", sp.factor(sp.diff(yB_Ahigh, pB, 2)), " (B high) =", sp.factor(sp.diff(yB_Bhigh, pB, 2)))
    print("d2 yA/dpB2 (A high) =", sp.factor(sp.diff(yA_Ahigh, pB, 2)), " (B high) =", sp.factor(sp.diff(yA_Bhigh, pB, 2)))
    print("d2 yB/dpA2 (B high) =", sp.factor(sp.diff(yB_Bhigh, pA, 2)), " (A high) =", sp.factor(sp.diff(yB_Ahigh, pA, 2)))
    # continuity and derivative jump at the switching price p_A = (c_A/c_B) p_B
    pstar = cA * pB / cB
    print("y^0_A continuous at switch:", sp.simplify((yA_Ahigh - yA_Bhigh).subs(pA, pstar)) == 0)
    jump = sp.factor(sp.simplify((sp.diff(yA_Ahigh, pA) - sp.diff(yA_Bhigh, pA)).subs(pA, pstar)))
    print("jump of dyA/dpA at switch (A-high minus B-high) =", jump)
    pstar_b = cB * pA / cA
    jump_b = sp.factor(sp.simplify((sp.diff(yB_Bhigh, pB) - sp.diff(yB_Ahigh, pB)).subs(pB, pstar_b)))
    print("jump of dyB/dpB at switch p_B = (c_B/c_A) p_A (B-high minus A-high) =", jump_b, "(> 0: B's kink is always upward)")
    # Scenario N shift: y^N_i = y^0_i + alpha_i gamma R_1
    print("d(alpha_A gamma R_1)/dp_A =", sp.diff(aA * gR, pA), "; d(alpha_A gamma R_1)/dp_B =", sp.diff(aA * gR, pB))


def endpoint_search(n=2_000_000, seed=7):
    print("== adversarial search of the endpoint bounds (c_B = 1, mu = 1)")
    rng = np.random.default_rng(seed)
    cb, mu = 1.0, 1.0
    ca = cb * rng.uniform(1e-4, 1 - 1e-4, n) ** rng.choice([0.25, 1.0, 4.0], n)
    r = rng.uniform(1e-4, 1 - 1e-4, n) ** rng.choice([0.25, 1.0, 4.0], n)
    sg = r * mu
    beta = 10 ** rng.uniform(-3, 1.5, n)
    half = 1 / (2 * beta)
    w = (mu + sg) * (ca + 2 * cb) / (3 * mu)
    # p_hi just above the A13 bound (geometric emphasis on the boundary)
    p_hi = half + w * (1 + 10 ** rng.uniform(-8, 0.5, n))
    lo_min = np.maximum(cb, p_hi - half)
    lo_max = np.minimum(half + (2 * ca + cb) / 3, p_hi)
    ok = lo_min < lo_max
    u = rng.uniform(0, 1, n) ** rng.choice([0.1, 1.0, 10.0], n)
    p_lo = lo_min + (lo_max - lo_min) * np.where(rng.uniform(0, 1, n) < 0.5, u, 1 - u)
    th = np.where(rng.uniform(0, 1, n) < 0.25, 0.0, np.where(rng.uniform(0, 1, n) < 0.33, 1.0, rng.uniform(0, 1, n)))
    v = rng.uniform(0, 1, n) ** rng.choice([0.1, 1.0, 10.0], n)
    pj = p_lo + (p_hi - p_lo) * np.where(rng.uniform(0, 1, n) < 0.5, v, 1 - v)
    ok &= (p_lo > cb) & (p_lo < half + (2 * ca + cb) / 3) & (p_hi > half + w) & (p_hi - p_lo < half)
    bound = beta * (mu ** 2 - mu * sg + sg ** 2) / (mu + sg)
    P = p_hi
    # own price of A at p_A = p_hi: always the A-high branch since p_hi > (c_A/c_B) p_B
    dA_own = -beta * (mu + sg) + ca * sg * (1 + th + 2 * beta * (1 - th) * pj) / P ** 2 + 2 * beta * cb * th * sg / pj
    # own price of B at p_B = p_hi: A-high branch iff p_hi < (c_B/c_A) p_A
    Ahigh_B = P < cb / ca * pj
    dB_own = np.where(Ahigh_B, -beta * (mu + sg) + sg * cb * (1 + 2 * beta * pj) / P ** 2,
                      -beta * (mu + sg) + cb * sg * (1 + th + 2 * beta * (1 - th) * pj) / P ** 2 + 2 * beta * ca * th * sg / pj)
    # rival price: y_A in p_B at p_B = p_hi (A-high iff p_hi < (c_B/c_A) p_A), y_B in p_A at p_A = p_hi (always A-high)
    dA_riv = np.where(Ahigh_B, beta * (-2 * ca * (1 - th) * sg / pj + mu + sg) - 2 * cb * beta * th * pj * sg / P ** 2 - cb * th * sg / P ** 2,
                      beta * (-2 * ca * sg / pj + mu + sg))
    dB_riv = beta * (mu + sg - 2 * sg * cb / pj)
    m = ok
    print(f"admissible sampled points: {int(m.sum())} of {n}; with theta = 0: {int((m & (th == 0)).sum())}, theta = 1: {int((m & (th == 1)).sum())}; "
          f"B-high branch at p_B = p_hi: {int((m & ~Ahigh_B).sum())}")
    for name, val, sign in (("own A", dA_own, -1), ("own B", dB_own, -1), ("rival A (in p_B)", dA_riv, +1), ("rival B (in p_A)", dB_riv, +1)):
        ratio = sign * val[m] / bound[m]          # must be >= 1
        k = int(np.argmin(ratio))
        idx = np.flatnonzero(m)[k]
        # slack in units of the total sigma-term 3 beta mu sigma / (mu + sigma), which vanishes as sigma -> 0
        scale = 3 * beta[m] * mu * sg[m] / (mu + sg[m])
        slack = np.where(sg[m] > 1e-6, (sign * val[m] - bound[m]) / scale, np.inf)     # must be >= 0; sigma <= 1e-6 is rounding-dominated
        j = int(np.argmin(slack))
        jdx = np.flatnonzero(m)[j]
        print(f"   {name}: min ratio derivative/bound = 1 + {ratio[k] - 1:.3e}; min slack / (3 beta mu sigma/(mu+sigma)) = {slack[j]:.4g} "
              f"at c_A={ca[jdx]:.4g}, sigma={sg[jdx]:.4g}, beta={beta[jdx]:.4g}, p_lo={p_lo[jdx]:.5g}, p_hi={p_hi[jdx]:.5g}, "
              f"theta={th[jdx]:.3g}, p_j={pj[jdx]:.5g}")
    # the derived constraint used in the record: p_lo > (mu + sigma)(c_A + 2 c_B)/(3 mu)
    print(f"   min of p_lo - (mu+sigma)(c_A+2c_B)/(3mu) over admissible points = {np.min(p_lo[m] - w[m]):.3g} (must be > 0)")


if __name__ == "__main__":
    symbolic()
    endpoint_search()
