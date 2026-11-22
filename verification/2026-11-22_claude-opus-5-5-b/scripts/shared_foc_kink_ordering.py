"""Steps of the proofs of L3 and LB1 (and the L2 special case): derivative formulas, the kink,
the inversion of (A.17), and the critical-ratio orderings.

Run from the repository root, no arguments:
    python verification/2026-11-22_claude-opus-5-5-b/scripts/shared_foc_kink_ordering.py

Weights (g_A, g_B, gC_A, gC_B) with Z_{i,2} = g_i R_{i,1} + gC_i R_{j,1} cover Scenario S
(gamma, gamma, 0, 0), Scenario N (a gamma, (1-a) gamma, a gamma, (1-a) gamma) and the mixed
scenario G of Online Appendix B. P_A = p_{A,1} + rho g_A m_A, K_A = rho gC_A m_A theta,
m_i = p_{i,2} - c_i.

(1) Finite differences of the payoff of A ((A.1) for the benchmark, (A.8), (A.12)) and of B, built from the
    demand system, against the first-order derivatives printed in the proofs of L3 and B.1:
      region y_A/a_A >= y_B/a_B :  P_A - c_A - P_A F(w_A)
      region y_A/a_A <  y_B/a_B :  P_A - c_A - (P_A - K_A) F(y_A/a_A) - K_A F(w_B)
    with w_A = (y_A + th y_B)/(a_A + th a_B), w_B = (y_B + th y_A)/(a_B + th a_A), and the mirror
    for B; laws beta(2,5) on [2, 12] and exponential; Richardson-extrapolated one-sided
    differences on both sides of A's kink.
(2) SymPy: solving the first equation of (A.17) for F(w_A) and the second for F(y_B/a_B)
    gives the printed zeta_B (Lemma 3 with rho; Lemma B.1); both derivative branches agree at
    the kink.
(3) Exact rational arithmetic at random and edge points of A1, A11, I1, I2 (theta in {0,1},
    A11 equality in one or both periods, p_A = p_B, gamma down to 1/10^6, lambda_S in {0,1},
    rho in (0,1]): c_A/P_A <= c_B/P'_B with P'_B = p_{B,1} + rho g_B m_B (the ordering used
    to exclude the region y_A/a_A < y_B/a_B), P_A - K_A > 0, 0 < q_B <= q_A < 1 for the
    printed fractiles, strict q^N_A > q^N_B in Scenario N, q^N_A < q^S_A, g_A >= g_B, and the
    chain c_A/c_B (p_{B,1} + rho m_B a_B gamma) <= p_{A,1} + rho m_A a_B gamma
    <= p_{A,1} + rho m_A a_A gamma of the proof of Lemma 3.
(4) The limit of A's best response in L3 as y_B grows (uniform law): BR_A equals
    a_A F^{-1}(1 - c_A/(p_{A,1} + rho m_A a gamma (1 - theta))) once w_B passes the support.
"""
from __future__ import annotations

import random
import sys
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
import sympy as sp
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared_eqlemmas_unbounded_support import Law, NODES, WEIGHTS, best_response, sales, weights  # noqa: E402


class Bounded:
    """Gauss-Legendre between kinks and quantiles for a law with bounded support."""
    def __init__(self, name, dist):
        self.name, self.dist = name, dist
        self.lo, self.hi = (float(v) for v in dist.support())
        self.fixed = np.unique(dist.ppf(np.linspace(0, 1, 21)))
        self.mean = float(dist.mean())

    def ppf(self, q):
        return float(self.dist.ppf(q))

    def cdf(self, x):
        return float(self.dist.cdf(x))

    def expected_sales(self, ya, yb, aa, ab, th, za=0.0, zb=0.0):
        ya, yb = np.broadcast_arrays(np.atleast_1d(np.asarray(ya, float)), np.atleast_1d(np.asarray(yb, float)))
        ks = [(ya - za) / aa, (yb - zb) / ab, (ya - za + th * (yb - zb)) / (aa + th * ab), (yb - zb + th * (ya - za)) / (ab + th * aa)]
        pts = np.concatenate([np.broadcast_to(self.fixed, (ya.size, self.fixed.size)), np.stack(ks, axis=1)], axis=1)
        pts = np.sort(np.clip(pts, self.lo, self.hi), axis=1)
        half, mid = (pts[:, 1:] - pts[:, :-1]) / 2, (pts[:, 1:] + pts[:, :-1]) / 2
        x = mid[:, :, None] + half[:, :, None] * NODES
        w = half[:, :, None] * WEIGHTS * self.dist.pdf(x)
        ra, rb = sales(x, ya[:, None, None], yb[:, None, None], aa, ab, th, za, zb)
        return (ra * w).sum(axis=(1, 2)), (rb * w).sum(axis=(1, 2))


def printed_derivative(own, P, K, c, F, y_own, y_oth, a_own, a_oth, th):
    """Derivative of the payoff of the retailer `own` as printed in the proofs of L3 and B.1."""
    if y_own / a_own >= y_oth / a_oth:
        return P - c - P * F((y_own + th * y_oth) / (a_own + th * a_oth))
    return P - c - (P - K) * F(y_own / a_own) - K * F((y_oth + th * y_own) / (a_oth + th * a_own))


def part1(rng):
    laws = [Bounded("beta(2,5) on [2,12]", stats.beta(2, 5, loc=2.0, scale=10.0)),
            Law("exponential(scale 10)", stats.expon(scale=10.0))]
    worst, worst_kink, n = 0.0, 0.0, 0
    for law in laws:
        F = (law.cdf if hasattr(law, "cdf") else (lambda x, d=law.dist: float(d.cdf(x))))
        for _ in range(12):
            cb = rng.uniform(0.5, 3); ca = cb * rng.uniform(0.05, 0.98)
            pb1, pb2 = cb * rng.uniform(1.05, 4, 2)
            pa1, pa2 = rng.uniform(ca / cb * pb1, pb1), rng.uniform(ca / cb * pb2, pb2)
            beta = min(0.5, rng.uniform(0, 0.45) / max(pb1 - pa1, pb2 - pa2))
            a1, a2 = 0.5 + beta * (pb1 - pa1), 0.5 + beta * (pb2 - pa2)
            th, g, rho, lam = rng.choice([0.0, 1.0, rng.uniform()]), rng.uniform(0.05, 20), rng.choice([1.0, rng.uniform(0.2, 1)]), rng.uniform()
            for scn in ("0", "S", "N", "G"):
                gA, gB, cA, cB = weights(scn, g, a2, lam)
                mA, mB = pa2 - ca, pb2 - cb
                PA, KA = pa1 + rho * gA * mA, rho * cA * mA * th
                PB, KB = pb1 + rho * gB * mB, rho * cB * mB * th

                def pay_a(ya, yb):
                    ra, rb = law.expected_sales(ya, yb, a1, 1 - a1, th)
                    return pa1 * ra - ca * np.atleast_1d(ya) + rho * mA * (gA * ra + cA * rb)

                def pay_b(ya, yb):
                    ra, rb = law.expected_sales(ya, yb, a1, 1 - a1, th)
                    return pb1 * rb - cb * np.atleast_1d(yb) + rho * mB * (gB * rb + cB * ra)
                x_hi = law.ppf(0.98)
                for _k in range(4):
                    ya, yb = rng.uniform(0.0, x_hi * a1), rng.uniform(0.0, x_hi * (1 - a1))
                    h = 1e-5 * law.mean
                    fd_a = (pay_a(ya + h, yb)[0] - pay_a(ya - h, yb)[0]) / (2 * h)
                    fd_b = (pay_b(ya, yb + h)[0] - pay_b(ya, yb - h)[0]) / (2 * h)
                    da = printed_derivative("A", PA, KA, ca, F, ya, yb, a1, 1 - a1, th)
                    db = printed_derivative("B", PB, KB, cb, F, yb, ya, 1 - a1, a1, th)
                    err = max(abs(fd_a - da) / PA, abs(fd_b - db) / PB)
                    worst = max(worst, err); n += 1
                    assert err < 1e-5, (law.name, scn, ya, yb, fd_a, da, fd_b, db)
                # one-sided differences at A's kink y_A = a_A y_B / a_B
                yb = rng.uniform(0.2, 0.9) * x_hi * (1 - a1)
                yk = a1 * yb / (1 - a1)
                h = 1e-4 * law.mean
                f0 = pay_a(yk, yb)[0]

                def one_sided(s, hh):                           # Richardson-extrapolated one-sided derivative
                    d1 = s * (pay_a(yk + s * hh, yb)[0] - f0) / hh
                    d2 = s * (pay_a(yk + s * hh / 2, yb)[0] - f0) / (hh / 2)
                    return 2 * d2 - d1
                left, right = one_sided(-1, h), one_sided(+1, h)
                worst_kink = max(worst_kink, abs(left - right) / PA)
    print(f"(1) {n} finite-difference derivatives (benchmark 0 as in (A.1)-(A.3), S, N, G; theta in {{0,1,random}}; rho in {{1,random}}):"
          f" max |FD - printed| / P = {worst:.2e}; max |left - right| extrapolated one-sided derivatives at A's kink / P = {worst_kink:.2e}")


def part2():
    PA, PB, KB, cAs, cBs, u, v = sp.symbols("P_A P_B K_B c_A c_B u v", positive=True)
    # first equation of (A.17): P_A - c_A = P_A u  ->  u = 1 - c_A/P_A
    u_sol = sp.solve(sp.Eq(PA - cAs, PA * u), u)[0]
    # second equation: P_B - c_B = (P_B - K_B) v + K_B u
    v_sol = sp.solve(sp.Eq(PB - cBs, (PB - KB) * v + KB * u_sol), v)[0]
    printed = 1 - (cBs - KB * cAs / PA) / (PB - KB)
    ok = sp.simplify(v_sol - printed) == 0
    # with Lemma 3's symbols (rho kept): K_B = rho a_B gamma theta m_B, P_B = p_B1 + rho a_B gamma m_B
    pb1, rho, aB, g, th, mB = sp.symbols("p_B1 rho alpha_B2 gamma theta m_B", positive=True)
    lem3 = 1 - (cBs - rho * aB * g * th * mB * cAs / PA) / (pb1 + rho * aB * g * (1 - th) * mB)
    ok3 = sp.simplify(printed.subs({KB: rho * aB * g * th * mB, PB: pb1 + rho * aB * g * mB}) - lem3) == 0
    gBs, gCs = sp.symbols("gamma_B2 gammaC_B2", positive=True)
    lemb1 = 1 - (cBs - gCs * th * mB * cAs / PA) / (pb1 + (gBs - gCs * th) * mB)
    okb = sp.simplify(printed.subs({KB: gCs * th * mB, PB: pb1 + gBs * mB}) - lemb1) == 0
    # kink: both branches at y_A/a_A = y_B/a_B = k agree
    K, Fk = sp.symbols("K F_k")
    kink = sp.simplify((PA - cAs - PA * Fk) - (PA - cAs - (PA - K) * Fk - K * Fk)) == 0
    print(f"(2) SymPy: inversion of (A.17) gives the printed fractile: {ok}; equals Lemma 3's zeta_B with rho: {ok3};"
          f" equals Lemma B.1's zeta_B: {okb}; derivative branches agree at the kink: {kink}")
    assert ok and ok3 and okb and kink


def lattice(r, lo, hi, den=1000):
    return Fr(r.randint(round(lo * den), round(hi * den)), den)


def part3():
    r = random.Random(7)
    n, n_strict_eq = 0, 0
    tags = {"theta=0": 0, "theta=1": 0, "A11 eq both": 0, "A11 eq one": 0, "pA=pB": 0, "lam_S=0": 0, "lam_S=1": 0, "small gamma": 0}
    for k in range(4000):
        cb = lattice(r, 0.5, 3); ratio = lattice(r, 0.001, 0.999); ca = cb * ratio
        pb1, pb2 = cb * lattice(r, 1.001, 50), cb * lattice(r, 1.001, 50)
        mode = r.choice(["regular", "eq both", "eq one", "pA=pB", "regular"])
        if mode == "eq both":
            pa1, pa2 = ratio * pb1, ratio * pb2; tags["A11 eq both"] += 1
        elif mode == "eq one":
            pa1, pa2 = ratio * pb1, pb2 * (ratio + lattice(r, 0.001, 1) * (1 - ratio)); tags["A11 eq one"] += 1
        elif mode == "pA=pB":
            pa1, pa2 = pb1, pb2; tags["pA=pB"] += 1
        else:
            pa1, pa2 = (pb * (ratio + lattice(r, 0, 1) * (1 - ratio)) for pb in (pb1, pb2))
        gap = max(pb1 - pa1, pb2 - pa2)
        beta = lattice(r, 0.000001, 0.499, 10**6) / gap if gap > 0 else lattice(r, 0.001, 5)
        a1, a2 = Fr(1, 2) + beta * (pb1 - pa1), Fr(1, 2) + beta * (pb2 - pa2)
        assert Fr(1, 2) <= a1 < 1 and Fr(1, 2) <= a2 < 1
        th = r.choice([Fr(0), Fr(1), lattice(r, 0, 1)]); tags["theta=0"] += th == 0; tags["theta=1"] += th == 1
        g = r.choice([Fr(1, 10**6), lattice(r, 0.01, 1000)]); tags["small gamma"] += g == Fr(1, 10**6)
        rho = r.choice([Fr(1), lattice(r, 0.001, 1)])
        lam = r.choice([Fr(0), Fr(1), lattice(r, 0, 1)]); tags["lam_S=0"] += lam == 0; tags["lam_S=1"] += lam == 1
        mA, mB = pa2 - ca, pb2 - cb
        q = {}
        for scn in ("S", "N", "G"):
            gA, gB, cA, cB = weights(scn, g, a2, lam)
            PA, PBp = pa1 + rho * gA * mA, pb1 + rho * gB * mB
            KA, KB = rho * cA * mA * th, rho * cB * mB * th
            rA = ca / PA
            assert gA >= gB and gA >= cA and gB >= cB                         # weights of Appendix B
            assert rA <= cb / PBp                                            # ordering that excludes region 2
            assert PA - KA > 0 and PBp - KB > 0                               # coefficients of the concave pieces
            qA = 1 - rA
            qB = 1 - (cb - KB * rA) / (pb1 + rho * (gB - cB * th) * mB)
            assert 0 < qB <= qA < 1, (scn, qA, qB)
            q[scn] = (qA, qB)
        assert q["N"][0] > q["N"][1]                                         # strict in Scenario N
        n_strict_eq += q["S"][0] == q["S"][1]
        aB = 1 - a2
        assert ca / cb * (pb1 + rho * mB * aB * g) <= pa1 + rho * mA * aB * g <= pa1 + rho * mA * a2 * g
        assert q["N"][0] < q["S"][0]                                         # zeta^N_A < zeta^S_A
        n += 1
    print(f"(3) exact rational points: {n}; edge counts {tags}; points with q^S_A = q^S_B (A11 equality in both"
          f" periods): {n_strict_eq}; all orderings hold, q^N_A > q^N_B strictly at every point")


def part4():
    lo, hi = 2.0, 12.0
    law = Bounded("uniform on [2,12]", stats.uniform(loc=lo, scale=hi - lo))
    pa1, pb1, pa2, pb2, ca, cb, beta, th, g, rho = 4.0, 4.4, 4.2, 4.6, 1.0, 1.5, 0.2, 0.6, 2.0, 1.0
    a1, a2 = 0.5 + beta * (pb1 - pa1), 0.5 + beta * (pb2 - pa2)
    mA = pa2 - ca
    w = weights("N", g, a2)
    limit = a1 * law.ppf(1 - ca / (pa1 + rho * mA * a2 * g * (1 - th)))
    out = []
    for yb in (3.0, 5.0, 8.0, 20.0, 40.0):
        def pay_a(ya, yb=yb):
            ra, rb = law.expected_sales(ya, yb, a1, 1 - a1, th)
            return pa1 * ra - ca * np.atleast_1d(ya) + rho * mA * (w[0] * ra + w[2] * rb)
        out.append((yb, best_response(lambda y: pay_a(y), 1.5 * hi)[0]))
    print(f"(4) L3, A's best response as y_B grows: {[(b, round(y, 6)) for b, y in out]}; printed limit {limit:.6f}")
    assert all(out[k][1] >= out[k + 1][1] - 1e-7 for k in range(len(out) - 1)) and abs(out[-1][1] - limit) < 1e-6


if __name__ == "__main__":
    part1(np.random.default_rng(11))
    part2()
    part3()
    part4()
    print("all checks passed")
