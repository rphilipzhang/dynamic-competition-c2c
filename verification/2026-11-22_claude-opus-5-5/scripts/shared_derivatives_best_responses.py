"""First-order derivatives and best responses in the proofs of Lemmas 2, 3 and B.1, against the model.

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5/scripts/shared_derivatives_best_responses.py

The payoffs are those of `section4.Game` (two-period payoffs built from `c2c.primitives`, with the
continuation pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2}; C9 of shared_exact_identities.py proves that
continuation pathwise). Uniform seed demand, exact expectations, rho = 1.

D1  The piecewise derivative of retailer i's payoff in its own order, as the proofs state it
    (proof of Lemma 3, displays before (A.13); the two displayed equations of the proof of Lemma B.1;
    Lemma 2 is the case gamma^C = 0), against a central difference of the model payoff, in both
    regions y_A/a_A >= y_B/a_B and y_A/a_A < y_B/a_B, scenarios S, N and G.
D2  (A.13): retailer A's best response is nonincreasing in y_B, equals the first branch for
    y_B <= a_B zeta_A, and tends to a_A F^{-1}(1 - c_A/(p_A1 + K_A (1 - theta))) as y_B grows.
    (A.15): the same for retailer B with its own limit.
Points: 40 points of `section4.draw_exogenous` (seed 8101), and theta replaced by 0 and 1 at
every fourth point.
"""
import sys
from dataclasses import replace
import numpy as np

sys.path.insert(0, "numerics")
from c2c import primitives as pm                                       # noqa: E402
from c2c.section4 import Game, draw_exogenous, seeded_rng            # noqa: E402

rng = seeded_rng(8101)
worst_d1 = 0.0
d2_monotone_fail = d2_branch_err = d2_limit_err = 0.0
n_d1 = 0
n_region = {True: 0, False: 0}
for k in range(40):
    prm, mu, sigma = draw_exogenous(rng)
    if k % 4 == 1:
        prm = replace(prm, theta=0.0)
    if k % 4 == 3:
        prm = replace(prm, theta=1.0)
    lo, hi = mu - sigma, mu + sigma
    dist = pm.Uniform(lo, hi)
    F = lambda x: float(np.clip((x - lo) / (hi - lo), 0.0, 1.0))
    Finv = dist.ppf
    aA, aB, th = prm.aa1, 1 - prm.aa1, prm.theta
    mA, mB = prm.pa2 - prm.ca, prm.pb2 - prm.cb
    for scen in ("S", "N", "G"):
        gA, gB, gcA, gcB = prm.weights(scen)
        pay_a, pay_b = Game(prm, scen, dist).period1_payoffs()

        def dA(ya, yb):
            a, b = ya / aA, yb / aB
            u, w = (ya + th * yb) / (aA + th * aB), (yb + th * ya) / (aB + th * aA)
            if a >= b:
                return prm.pa1 - prm.ca + mA * gA - (prm.pa1 + mA * gA) * F(u)
            return prm.pa1 - prm.ca + mA * gA - (prm.pa1 + mA * (gA - gcA * th)) * F(a) - mA * gcA * th * F(w)

        def dB(ya, yb):
            a, b = ya / aA, yb / aB
            u, w = (ya + th * yb) / (aA + th * aB), (yb + th * ya) / (aB + th * aA)
            if b >= a:
                return prm.pb1 - prm.cb + mB * gB - (prm.pb1 + mB * gB) * F(w)
            return prm.pb1 - prm.cb + mB * gB - (prm.pb1 + mB * (gB - gcB * th)) * F(b) - mB * gcB * th * F(u)

        h = 1e-5 * mu
        for _ in range(6):
            ya, yb = rng.uniform(0.05, 1.2) * hi * aA, rng.uniform(0.05, 1.2) * hi * aB
            fd_a = (pay_a(np.array([ya + h]), yb)[0] - pay_a(np.array([ya - h]), yb)[0]) / (2 * h)
            fd_b = (pay_b(ya, np.array([yb + h]))[0] - pay_b(ya, np.array([yb - h]))[0]) / (2 * h)
            sc = max(prm.pa1, prm.pb1) * (1 + prm.gamma)
            # a central difference straddling a kink of F is off by O(h); skip those
            a, b = ya / aA, yb / aB
            u, w = (ya + th * yb) / (aA + th * aB), (yb + th * ya) / (aB + th * aA)
            near = min(abs(x - e) for x in (a, b, u, w) for e in (lo, hi)) < 10 * h / min(aA, aB)
            if abs(a - b) < 10 * h / min(aA, aB) or near:
                continue
            worst_d1 = max(worst_d1, abs(fd_a - dA(ya, yb)) / sc, abs(fd_b - dB(ya, yb)) / sc)
            n_d1 += 1
            n_region[a >= b] += 1
        if scen == "N":
            KA, KB = mA * gA, mB * gB
            zA = Finv(1 - prm.ca / (prm.pa1 + KA))
            limA = aA * Finv(1 - prm.ca / (prm.pa1 + KA * (1 - th)))
            zBp = Finv(1 - prm.cb / (prm.pb1 + KB))
            limB = aB * Finv(1 - prm.cb / (prm.pb1 + KB * (1 - th)))
            ybs = np.linspace(0.0, 3 * hi, 25)
            brA = [pm.best_response(lambda y: pay_a(y, yb), 1.5 * hi)[0] for yb in ybs]
            d2_monotone_fail = max(d2_monotone_fail, max(np.diff(brA)) / mu)
            for yb, br in zip(ybs, brA):
                if yb <= aB * zA:
                    d2_branch_err = max(d2_branch_err, abs(br - ((aA + th * aB) * zA - th * yb)) / mu)
            far = 10 * hi * (aB + th * aA)                    # w >= hi for any y_A >= 0, so F(w) = 1
            d2_limit_err = max(d2_limit_err, abs(pm.best_response(lambda y: pay_a(y, far), 1.5 * hi)[0] - limA) / mu)
            farA = 10 * hi * (aA + th * aB)
            d2_limit_err = max(d2_limit_err, abs(pm.best_response(lambda y: pay_b(farA, y), 1.5 * hi)[0] - limB) / mu)
print(f"D1: {n_d1} derivative comparisons (S, N, G; {n_region[True]} with y_A/a_A >= y_B/a_B, {n_region[False]} with <); max |central difference - stated derivative| "
      f"/ (max p_1 (1+gamma)) = {worst_d1:.2e}")
print(f"D2: largest increase of BR_A along y_B (relative to mu) = {d2_monotone_fail:.2e} (the numerical best response is accurate to ~1.5e-8 of its size)")
print(f"D2: max |BR_A - first branch| for y_B <= a_B zeta_A, relative to mu = {d2_branch_err:.2e}")
print(f"D2: max |BR - stated limit| as the rival's order grows (A.13 and A.15), relative to mu = {d2_limit_err:.2e}")
