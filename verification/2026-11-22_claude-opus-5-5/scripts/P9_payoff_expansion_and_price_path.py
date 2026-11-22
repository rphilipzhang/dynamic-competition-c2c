"""Proposition 9: probes of the steps of its proof along increasing gamma (light).

1. Scenario N, fixed theta < 1: the expansion of the total profit used by the proof,
   Pi_i^N = gamma nu_i mu + K_i(theta) + alpha_{i,1}(mu p_{i,1} - c_i (mu + sigma)) + O_{C^2}(gamma^-1).
   On a 3 x 3 patch of first-period prices the residual
   rho_i = Pi_i^N - gamma nu_i mu - alpha_{i,1}(mu p_{i,1} - c_i(mu+sigma)) must be a constant up to
   O(1/gamma): its spread over the patch and its second differences (in units of the patch
   step squared) must shrink like 1/gamma. Also shown at theta = 1 - 1/gamma, where the
   proof does not claim the expansion.
2. Scenario S: d Pi_i^S / d p_{i,1} against -gamma (p_hi - c_i) beta mu, on the price box.
3. Scenario N, fixed theta < 1: the first-period price equilibrium of the reduced game by
   best-response iteration, against the limit prices of the proof, and the gap
   p_{i,1} - p_{i,2} at the mean seed demand against sigma (2 c_i + c_j) / (3 mu).

Orders: Scenario S uses the closed form of Lemma A.1(a); Scenario N solves the model's
first-order conditions (section5.inventory_equilibrium) from the closed form of Lemma A.2(a).
Continuations: section5.SecondPeriodS and section5.SecondPeriodN, built from the primitives.

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5/scripts/P9_payoff_expansion_and_price_path.py
"""
from __future__ import annotations

import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, "numerics")
from c2c import primitives as pm  # noqa: E402
from c2c import section5 as s5  # noqa: E402


def market(seed=91):
    rng = np.random.default_rng(seed)
    return s5.draw_market(rng)


def reduced_n(mk, cont, gamma, pa1, pb1):
    pa1, pb1 = np.broadcast_arrays(np.asarray(pa1, float), np.asarray(pb1, float))
    start = s5.claimed_orders_n(mk, gamma, pa1, pb1)
    ya, yb = s5.inventory_equilibrium(mk, cont, gamma, pa1, pb1, start)
    fa, fb = s5.marginal_profits(mk, cont, gamma, pa1, pb1, ya, yb)
    assert np.max(np.abs(fa)) < 1e-9 * (10 + gamma) and np.max(np.abs(fb)) < 1e-9 * (10 + gamma)
    return s5.first_period_profits(mk, cont, gamma, pa1, pb1, ya, yb)


def expansion_probe(mk):
    print(f"== 1. Pi^N expansion; market: c_A={mk.ca:.3f}, c_B={mk.cb:.3f}, beta={mk.beta:.3f}, mu={mk.mu:.2f}, "
          f"sigma={mk.sigma:.2f}, p in [{mk.p_lo:.3f}, {mk.p_hi:.3f}]")
    nua, nub = s5.claimed_nu(mk)
    centre = 0.5 * (mk.p_lo + mk.p_hi)
    h = 0.15 * (mk.p_hi - mk.p_lo)
    off = np.array([-h, 0.0, h])
    pa1, pb1 = np.meshgrid(centre + off, centre + off, indexing="ij")
    share = pm.share(pa1, pb1, mk.beta)
    for label, theta_of in (("theta = 0.5 (fixed)", lambda g: 0.5), ("theta = 1 - 1/gamma (not claimed)", lambda g: 1 - 1 / g)):
        print(f"   {label}:")
        for gamma in (1e2, 1e3, 1e4):
            m = replace(mk, theta=theta_of(gamma))
            cont = s5.SecondPeriodN(m, 2.0 / (gamma * m.lo))
            assert not cont.problems, cont.problems
            pia, pib = reduced_n(m, cont, gamma, pa1, pb1)
            rho_a = pia - gamma * nua * m.mu - share * (m.mu * pa1 - m.ca * m.hi)
            rho_b = pib - gamma * nub * m.mu - (1 - share) * (m.mu * pb1 - m.cb * m.hi)
            spread = max(np.ptp(rho_a), np.ptp(rho_b))
            d2 = max(np.max(np.abs(np.diff(r, 2, axis=ax))) for r in (rho_a, rho_b) for ax in (0, 1)) / h ** 2
            print(f"      gamma={gamma:8.0f}: spread of rho over patch = {spread:.3e} (x gamma = {spread * gamma:.3g}); "
                  f"max |second difference|/h^2 = {d2:.3e} (x gamma = {d2 * gamma:.3g}); K_A ~ {rho_a[1, 1]:.5f}, K_B ~ {rho_b[1, 1]:.5f}")


def scenario_s_slope(mk):
    print("== 2. Scenario S: d Pi_i^S / d p_{i,1} over -gamma (p_hi - c_i) beta mu, 5 x 5 grid of the box")
    cont = s5.SecondPeriodS(mk)
    grid = np.linspace(mk.p_lo, mk.p_hi, 5)
    pa1, pb1 = np.meshgrid(grid, grid, indexing="ij")
    for gamma in (1e2, 1e3, 1e4, 1e5):
        d = 1e-6 * (mk.p_hi - mk.p_lo)
        def pi(pa, pb):
            ya, yb = s5.claimed_orders_s(mk, gamma, pa, pb)
            return s5.first_period_profits(mk, cont, gamma, pa, pb, ya, yb)
        da = (pi(pa1 + d, pb1)[0] - pi(pa1 - d, pb1)[0]) / (2 * d)
        db = (pi(pa1, pb1 + d)[1] - pi(pa1, pb1 - d)[1]) / (2 * d)
        ra = da / (-gamma * (mk.p_hi - mk.ca) * mk.beta * mk.mu)
        rb = db / (-gamma * (mk.p_hi - mk.cb) * mk.beta * mk.mu)
        dom_ok = gamma * min(mk.smallest_share * mk.lo / 2, 1e9) > max(cont.dominance)
        print(f"   gamma={gamma:8.0f}: ratio range A [{ra.min():.4f}, {ra.max():.4f}], B [{rb.min():.4f}, {rb.max():.4f}]; "
              f"max d Pi_i/d p_i = {max(da.max(), db.max()):.3g}; gamma delta above dominance numbers: {dom_ok}")


def price_path_n(mk, theta=0.5):
    print(f"== 3. Scenario N price path at theta = {theta}")
    m = replace(mk, theta=theta)
    lim1 = s5.proof_first_period_limit_prices(m)
    lim2 = s5.claimed_limit_prices(m)
    print(f"   limit prices: period 1 ({lim1[0]:.5f}, {lim1[1]:.5f}), period 2 ({lim2[0]:.5f}, {lim2[1]:.5f}); "
          f"limit gaps sigma(2c_i+c_j)/(3mu) = ({m.sigma * (2 * m.ca + m.cb) / (3 * m.mu):.5f}, {m.sigma * (2 * m.cb + m.ca) / (3 * m.mu):.5f})")
    for gamma in (1e2, 1e3):
        cont = s5.SecondPeriodN(m, 2.0 / (gamma * m.lo))
        assert not cont.problems, cont.problems
        reduced = lambda pa, pb: reduced_n(m, cont, gamma, pa, pb)  # noqa: E731
        replies = s5.price_replies(reduced, m, first=41, points=17, levels=5)
        pa1, pb1, sweeps = s5.iterate_best_responses(*replies, (m.p_lo, m.p_hi), sweeps=12, tol=2e-6 * m.p_hi)
        ya, yb = (float(v) for v in s5.inventory_equilibrium(m, cont, gamma, np.array(pa1), np.array(pb1),
                                                              s5.claimed_orders_n(m, gamma, pa1, pb1)))
        share = pm.share(pa1, pb1, m.beta)
        ra, rb = pm.sales(m.mu, ya, yb, share, 1 - share, m.theta)
        pa2, pb2 = (float(v) for v in cont.prices(gamma, np.array(ra + rb)))
        print(f"   gamma={gamma:6.0f}: p_1 = ({pa1:.5f}, {pb1:.5f}) [{sweeps} sweeps], gamma |p_1 - phat_1| = "
              f"{gamma * max(abs(pa1 - lim1[0]), abs(pb1 - lim1[1])):.4g}; p_2 at mean demand = ({pa2:.5f}, {pb2:.5f}); "
              f"gaps p_1 - p_2 = ({pa1 - pa2:.5f}, {pb1 - pb2:.5f}); interior and ordered: "
              f"{m.p_lo < min(pa2, pb2) and pa2 < pa1 < m.p_hi and pb2 < pb1 < m.p_hi}")


if __name__ == "__main__":
    mk = market()
    expansion_probe(mk)
    scenario_s_slope(mk)
    price_path_n(mk)
