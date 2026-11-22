"""Section 5, second period: Lemmas A.1(b) and A.2(b) against the model.

Section 5 lets the retailers choose prices in [p_lo, p_hi] before they order, and it drops
the price condition A11 of Section 4. The second period is therefore solved in two steps.

1. The inventory subgame at given second-period prices and first-period sales. The lemmas
   say that its equilibrium is y^0_{i,2} + Z_{i,2}. The tests of Section 4 check this under
   A11 only, where retailer A has the higher critical fractile, and at the parameter values
   of Figure 1. Here it is checked at random price pairs of the box, where either retailer
   can have the higher fractile.
2. The price game whose payoffs are the equilibrium profits of that inventory subgame.
   Lemma A.1(b) says that for gamma large its unique equilibrium in Scenario S is the upper
   price bound for both retailers. Lemma A.2(b) says that in Scenario N it is unique and
   lies within O(1 / gamma) of the limit prices 1 / (2 beta) + (2 c_i + c_j) / 3.

Every payoff is an expectation of `c2c.primitives.sales`. Nothing here uses `c2c.closed_form`.

Both lemmas hold "for sufficiently large gamma", so a test at finite gamma probes them and
does not prove them. Each test runs a ladder of gamma, requires the claim at the two largest
values, and records the smallest value from which it holds at every sampled point.
"""
from __future__ import annotations

import numpy as np
import pytest

from c2c import primitives as pm

from c2c.section4 import claimed_benchmark
from c2c.section5 import (benchmark_orders, benchmark_profits, claimed_limit_prices, claimed_nu,
                    claimed_second_period_prices_s, draw_market, expected_sales, iterate_best_responses,
                    price_equilibrium_n, price_gap, price_replies, pure_equilibria_on_grid, second_period_orders,
                    second_period_profits, threshold_on_ladder)

# GAIN_TOL is the largest admissible payoff gain from a unilateral deviation, relative to the payoff scale.
# DIST_TOL is the largest admissible distance between a best response and the claimed value, relative to its scale.
GAIN_TOL = 1e-8
DIST_TOL = 2e-5

GAMMAS_S = (1.0, 10.0, 100.0, 1e3, 1e4, 1e5, 1e6)
GAMMAS_N = (10.0, 100.0, 1e3, 1e4, 1e5, 1e6)


def _corners(mk):
    """The four corners of the price box."""
    return [(a, b) for a in (mk.p_lo, mk.p_hi) for b in (mk.p_lo, mk.p_hi)]


# ----------------------------------------------------------------------------- the helpers and the inventory subgame
@pytest.mark.supports("LA1", "LA2", "P8", "P9")
def test_helpers_agree_with_the_primitives(record):
    """`section5.expected_sales` and `section5.benchmark_orders` against the primitives.
    Points: 2,000 markets of `draw_market` (seed 5100), each with C2C demands that are zero or
    uniform on [0, 3 (mu + sigma)], orders uniform on [0, 2 (mu + sigma)] above them, a share
    uniform on [0.02, 0.98] and a price pair uniform on the price box.
    Computed: expected sales from `section5.expected_sales` and from `primitives.Uniform`, and
    order quantities from `benchmark_orders` and from `section4.claimed_benchmark`.
    Criterion: every difference is at most 1e-13 (mu + sigma), and retailer B has the higher
    critical fractile at one price pair or more."""
    rng = np.random.default_rng(5100)
    worst_sales = worst_orders = 0.0
    mirrored, n = 0, 2000
    for _ in range(n):
        mk = draw_market(rng)
        za, zb = rng.uniform(0.0, 3.0 * mk.hi, size=2) * rng.integers(0, 2, size=2)
        ya, yb = za + rng.uniform(0.0, 2.0 * mk.hi), zb + rng.uniform(0.0, 2.0 * mk.hi)
        share = rng.uniform(0.02, 0.98)
        mine = expected_sales(mk, ya, yb, share, za, zb)
        theirs = mk.dist.expected_sales(ya, yb, share, 1.0 - share, mk.theta, za, zb)
        worst_sales = max(worst_sales, abs(mine[0] - theirs[0][0]) / mk.hi, abs(mine[1] - theirs[1][0]) / mk.hi)
        pa, pb = rng.uniform(mk.p_lo, mk.p_hi, size=2)
        y0a, y0b, q_a, q_b = claimed_benchmark(pa, pb, mk.ca, mk.cb, mk.beta, mk.theta, mk.dist.ppf)
        mirrored += q_a < q_b
        orders = benchmark_orders(mk, pa, pb)
        worst_orders = max(worst_orders, abs(orders[0] - y0a) / mk.hi, abs(orders[1] - y0b) / mk.hi)
    record("points", n)
    record("price_pairs_where_retailer_B_has_the_higher_fractile", int(mirrored))
    record("max_relative_error_expected_sales", worst_sales, stable=False)
    record("max_relative_error_benchmark_orders", worst_orders, stable=False)
    assert worst_sales <= 1e-13 and worst_orders <= 1e-13 and mirrored > 0


@pytest.mark.parametrize("scenario", [pytest.param("S", marks=pytest.mark.claims("LA1.b")),
                                      pytest.param("N", marks=pytest.mark.claims("LA2.b"))])
def test_second_period_inventory_equilibrium_at_any_price_pair(scenario, record):
    """Lemmas A.1(b) and A.2(b), last sentence of each: at given second-period prices and
    first-period sales the orders y^0_{i,2} + Z_{i,2} are the equilibrium of the inventory
    subgame, and each profit is pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2}.
    Points: 100 markets of `draw_market` (seed 5101), gamma log-uniform on [0.1, 1000], one
    sales state each, uniform on the triangle R_A, R_B >= 0, R_A + R_B <= mu + sigma. At every
    second point the prices are uniform on the price box. At the others they are drawn, where
    the box allows, from the pairs with c_A / p_A > c_B / p_B.
    Computed: from the primitives, `primitives.nash_gap` on [0, U] with
    U = max(Z_A, Z_B) + 1.5 (mu + sigma), the profits at the claimed orders, and at the first
    20 points best-response iteration (801-point grid, at most 60 sweeps) from two random
    starting pairs.
    Criterion: no deviation gains more than 1e-8 p_hi U, each best response lies within
    2e-5 U of the claim, the profit identity holds within 1e-11 p_hi U, every iteration ends
    within 1e-4 U of the claim, and retailer B has the higher fractile at 10 points or more."""
    rng = np.random.default_rng(5101)
    worst_gain = worst_dist = worst_value = worst_return = 0.0
    mirrored, n = 0, 100
    for k in range(n):
        mk = draw_market(rng)
        gamma = float(10.0 ** rng.uniform(-1.0, 3.0))
        pa2, pb2 = rng.uniform(mk.p_lo, mk.p_hi, size=2)
        if k % 2 and mk.ca / mk.cb * mk.p_hi > mk.p_lo:        # Draw a pair at which retailer B has the higher fractile.
            pb2 = rng.uniform(mk.p_lo * mk.cb / mk.ca, mk.p_hi)
            pa2 = rng.uniform(mk.p_lo, mk.ca / mk.cb * pb2)
        ra1 = rng.uniform(0.0, mk.hi)
        rb1 = rng.uniform(0.0, mk.hi - ra1)
        share = pm.share(pa2, pb2, mk.beta)
        ya, yb, za, zb = (float(v) for v in second_period_orders(mk, scenario, gamma, pa2, pb2, ra1, rb1))
        mirrored += mk.ca / pa2 > mk.cb / pb2
        point = (mk, gamma, pa2, pb2, ra1, rb1)

        def sales(y_a, y_b):
            return mk.dist.expected_sales(y_a, y_b, share, 1.0 - share, mk.theta, za, zb)

        def payoff_a(y, other):
            return pa2 * sales(y, other)[0] - mk.ca * np.atleast_1d(y)

        def payoff_b(other, y):
            return pb2 * sales(other, y)[1] - mk.cb * np.atleast_1d(y)

        upper = max(za, zb) + 1.5 * mk.hi                      # An order above the largest possible demand never pays.
        gap = pm.nash_gap(payoff_a, payoff_b, ya, yb, upper)
        worst_gain = max(worst_gain, gap["gain"] / (mk.p_hi * upper))
        worst_dist = max(worst_dist, gap["dist"] / upper)
        assert gap["gain"] <= GAIN_TOL * mk.p_hi * upper, (point, gap)
        assert gap["dist"] <= DIST_TOL * upper, (point, gap)

        base = benchmark_profits(mk, pa2, pb2)
        value = second_period_profits(mk, scenario, gamma, pa2, pb2, ra1, rb1)
        err = max(abs(value[0] - base[0] - (pa2 - mk.ca) * za), abs(value[1] - base[1] - (pb2 - mk.cb) * zb))
        worst_value = max(worst_value, err / (mk.p_hi * upper))
        assert err <= 1e-11 * mk.p_hi * upper, point

        if k < 20:                                             # This is the uniqueness probe.
            for _ in range(2):
                start = (za + rng.uniform(0.0, 1.5 * mk.hi), zb + rng.uniform(0.0, 1.5 * mk.hi))
                a, b, _ = iterate_best_responses(
                    lambda other: pm.best_response(lambda y: payoff_a(y, other), upper, grid=801)[0],
                    lambda other: pm.best_response(lambda y: payoff_b(other, y), upper, grid=801)[0],
                    start, sweeps=60, tol=1e-9 * upper)
                away = (abs(a - ya) + abs(b - yb)) / upper
                worst_return = max(worst_return, away)
                assert away <= 5.0 * DIST_TOL, (point, start, (a, b), (ya, yb))
    record("points", n)
    record("points_where_retailer_B_has_the_higher_fractile", int(mirrored))
    record("tolerance_on_relative_gain_from_deviation", GAIN_TOL)
    record("max_relative_gain_from_deviation", worst_gain, stable=False)
    record("max_relative_distance_best_response_to_claim", worst_dist, stable=False)
    record("max_relative_error_of_profit_identity", worst_value, stable=False)
    record("max_relative_distance_after_best_response_iteration", worst_return, stable=False)
    assert mirrored >= n // 10


# ----------------------------------------------------------------------------- Lemma A.1(b)
def _check_claimed_price_pair_of_scenario_s(mk, gamma, ra1, rb1, claim, grid, extra_start):
    """All checks of Lemma A.1(b) at one market, one gamma and one sales state. Returns
    whether the claimed pair passed them, and for each retailer the smallest advantage of its
    claimed price over another price, per unit of price difference and against every rival
    price of the grid. `extra_start` is a fifth starting pair for the best-response iteration."""
    def payoffs(pa, pb):
        return second_period_profits(mk, "S", gamma, pa, pb, ra1, rb1)

    # In the game restricted to a price grid the claim must be the only pure equilibrium.
    table_a, table_b = payoffs(grid[:, None], grid[None, :])
    cells = pure_equilibria_on_grid(table_a, table_b)
    only_on_grid = len(cells) == 1 and (grid[cells[0][0]], grid[cells[0][1]]) == claim

    ia, ib = int(np.argmin(np.abs(grid - claim[0]))), int(np.argmin(np.abs(grid - claim[1])))
    other_a, other_b = np.arange(grid.size) != ia, np.arange(grid.size) != ib
    edge_a = ((table_a[ia][None, :] - table_a[other_a]) / np.abs(claim[0] - grid[other_a])[:, None]).min()
    edge_b = ((table_b[:, ib][:, None] - table_b[:, other_b]) / np.abs(claim[1] - grid[other_b])[None, :]).min()

    # Each retailer's whole price interval is searched for a deviation from the claim.
    gap = price_gap(payoffs, mk, *claim)
    no_deviation = gap["gain"] <= GAIN_TOL * abs(float(payoffs(*claim)[0])) and gap["dist"] <= 1e-12 * mk.p_hi

    # Best-response iteration starts from the four corners of the box and from one more pair.
    returns = True
    if only_on_grid and no_deviation:
        for start in _corners(mk) + [extra_start]:
            a, b, _ = iterate_best_responses(*price_replies(payoffs, mk), start, sweeps=20, tol=1e-12)
            returns &= abs(a - claim[0]) + abs(b - claim[1]) <= 1e-12 * mk.p_hi
    return bool(only_on_grid and no_deviation and returns), (float(edge_a), float(edge_b))


@pytest.mark.claims("LA1.b")
def test_lemma_a1b_upper_bound_is_the_unique_second_period_price_equilibrium(record):
    """Lemma A.1(b): in Scenario S, given positive first-period sales of both retailers and
    gamma large, the second-period price game has the unique pure equilibrium (p_hi, p_hi).
    Points: 30 markets of `draw_market` (seed 5102), one sales state each with R_{A,1} and
    R_{B,1} uniform on [0.02, 1] (mu + sigma) / 2, gamma = 1, 10, 100, 1e3, 1e4, 1e5 and 1e6.
    Computed: second-period profits from the primitives at the inventory equilibrium, on a
    61 by 61 price grid and on each whole price interval, best-response iteration from the
    four corners of the box and from one random pair (at most 20 sweeps), and the advantage
    of p_hi: the smallest payoff loss from another grid price per unit of price difference.
    Criterion: the claim holds at a market and gamma if (p_hi, p_hi) is the only pure
    equilibrium of the grid game, the search finds no relative gain above 1e-8 and no best
    response farther than 1e-12 p_hi, and every iteration ends within 1e-12 p_hi. Once it
    holds it must keep holding, it must hold at all markets from 1e5 on and fail at gamma = 1
    at one market or more, and the advantage must be positive at 1e5 and grow from 1e5 to
    1e6 by R_{i,1} per unit of gamma within a relative error of 1e-6."""
    rng = np.random.default_rng(5102)
    n = 30
    holds = np.zeros((n, len(GAMMAS_S)), bool)
    worst_rate, smallest_edge = 0.0, np.inf
    for k in range(n):
        mk = draw_market(rng)
        sales = rng.uniform(0.02, 1.0, size=2) * mk.hi / 2.0
        extra_start = tuple(rng.uniform(mk.p_lo, mk.p_hi, size=2))
        claim = claimed_second_period_prices_s(mk)
        grid = np.linspace(mk.p_lo, mk.p_hi, 61)
        edges = []
        for j, gamma in enumerate(GAMMAS_S):
            holds[k, j], edge = _check_claimed_price_pair_of_scenario_s(mk, gamma, *sales, claim, grid, extra_start)
            edges.append(edge)
        assert np.all(np.diff(holds[k].astype(int)) >= 0), (mk, sales, holds[k])    # Once the claim holds, it keeps holding.
        for who in (0, 1):
            rate = (edges[-1][who] - edges[-2][who]) / ((GAMMAS_S[-1] - GAMMAS_S[-2]) * sales[who])
            worst_rate = max(worst_rate, abs(rate - 1.0))
            smallest_edge = min(smallest_edge, edges[-2][who] / (GAMMAS_S[-2] * sales[who]))
            assert edges[-2][who] > 0.0 and abs(rate - 1.0) <= 1e-6, (mk, sales, edges)
    first = threshold_on_ladder(GAMMAS_S, list(holds.all(axis=0)))
    record("markets", n)
    record("gamma_ladder", list(GAMMAS_S))
    record("points_where_the_claim_holds_by_gamma", [int(v) for v in holds.sum(axis=0)])
    record("holds_at_all_points_from_gamma", first)
    record("smallest_advantage_of_upper_bound_over_gamma_times_sales_at_gamma_1e5", round(float(smallest_edge), 4))
    record("max_error_of_growth_rate_of_the_advantage", worst_rate, stable=False)
    assert first is not None and first <= GAMMAS_S[-2]
    assert not holds[:, 0].all()                               # The ladder starts below the threshold of some point.


# ----------------------------------------------------------------------------- Lemma A.2(b)
@pytest.mark.claims("LA2.b")
def test_lemma_a2b_second_period_prices_approach_the_limit_prices_at_rate_one_over_gamma(record):
    """Lemma A.2(b): in Scenario N, given R_1 > 0 and gamma large, the second-period price
    equilibrium is unique and equals 1 / (2 beta) + (2 c_i + c_j) / 3 plus O(1 / gamma).
    Points: 2,000 markets of `draw_market` (seed 5106) for the notation of Online Appendix A.2,
    and 12 markets (seed 5103), one state each with R_1 uniform on [0.1, 1] (mu + sigma), at
    gamma = 10, 100, 1e3, 1e4, 1e5 and 1e6.
    Computed: the solution of the first-order conditions of the price game, a search of each
    price interval and best-response iteration from the four corners (at most 40 sweeps), with
    profits from the primitives, and e(gamma), the larger distance to the limit prices.
    Criterion: at the 2,000 markets nu_A > nu_B > 0, c_A / nu_A < c_B / nu_B,
    p_lo < limit_A < limit_B < p_hi and c_A / limit_A < c_B / limit_B. At the 12 markets e
    shrinks along the ladder, log10(e(gamma) / e(10 gamma)) lies in [0.99, 1.01] over the last
    two decades, gamma e at 1e5 and 1e6 agrees within 0.5% and never exceeds twice its value at
    1e6, and from 1e5 on every market passes: relative gain at most 1e-8, best responses and
    iterations within 2e-5 p_hi."""
    rng = np.random.default_rng(5106)
    for _ in range(2000):
        mk = draw_market(rng)
        limit = claimed_limit_prices(mk)
        nu_a, nu_b = claimed_nu(mk)
        assert nu_a > nu_b > 0.0 and mk.ca / nu_a < mk.cb / nu_b, mk
        assert mk.p_lo < limit[0] < limit[1] < mk.p_hi and mk.ca / limit[0] < mk.cb / limit[1], mk

    rng = np.random.default_rng(5103)
    n = 12
    holds = np.zeros((n, len(GAMMAS_N)), bool)
    worst_order = worst_drift = worst_sup = 0.0
    scaled_at_top, last_orders, from_above = [], [], 0
    for k in range(n):
        mk = draw_market(rng)
        r1 = rng.uniform(0.1, 1.0) * mk.hi
        limit = claimed_limit_prices(mk)
        errors = []
        for j, gamma in enumerate(GAMMAS_N):
            def payoffs(pa, pb):
                return second_period_profits(mk, "N", gamma, pa, pb, r1, 0.0)

            pa, pb = (float(v) for v in price_equilibrium_n(mk, 1.0 / (gamma * r1)))
            gap = price_gap(payoffs, mk, pa, pb)
            good = gap["gain"] <= GAIN_TOL * abs(float(payoffs(pa, pb)[0])) and gap["dist"] <= DIST_TOL * mk.p_hi
            for start in _corners(mk):
                a, b, _ = iterate_best_responses(*price_replies(payoffs, mk), start, sweeps=40, tol=1e-9 * mk.p_hi)
                good &= abs(a - pa) + abs(b - pb) <= DIST_TOL * mk.p_hi
            holds[k, j] = good
            errors.append(max(abs(pa - limit[0]), abs(pb - limit[1])))
        from_above += pa > limit[0] and pb > limit[1]                            # These are the prices at the largest gamma.
        errors = np.array(errors)
        scaled = np.array(GAMMAS_N) * errors / mk.p_hi
        orders = np.log10(errors[:-1] / errors[1:])
        last_orders.extend(float(v) for v in orders[-2:])
        worst_order = max(worst_order, float(np.abs(orders[-2:] - 1.0).max()))
        worst_drift = max(worst_drift, abs(scaled[-1] / scaled[-2] - 1.0))
        worst_sup = max(worst_sup, float(scaled.max() / scaled[-1]))
        scaled_at_top.append(float(scaled[-1]))
        assert np.all(np.diff(errors) < 0.0), (mk, r1, errors)                           # Direction: the distance shrinks.
        assert np.all(np.abs(orders[-2:] - 1.0) <= 0.01), (mk, r1, orders)               # Rate: the order is one.
        assert abs(scaled[-1] / scaled[-2] - 1.0) <= 0.005, (mk, r1, scaled)             # The scaled distance settles.
        assert scaled.max() <= 2.0 * scaled[-1], (mk, r1, scaled)                        # It stays bounded on the ladder.
    first = threshold_on_ladder(GAMMAS_N, list(holds.all(axis=0)))
    record("markets", n)
    record("gamma_ladder", list(GAMMAS_N))
    record("points_where_equilibrium_is_confirmed_and_unique_by_gamma", [int(v) for v in holds.sum(axis=0)])
    record("unique_equilibrium_at_all_points_from_gamma", first)
    record("range_of_observed_order_over_last_two_decades", [round(min(last_orders), 2), round(max(last_orders), 2)])
    record("max_scaled_distance_on_ladder_over_its_value_at_gamma_1e6", round(worst_sup, 2))
    record("max_deviation_of_observed_order_from_1_over_last_two_decades", worst_order, stable=False)
    record("max_relative_change_of_scaled_distance_between_gamma_1e5_and_1e6", worst_drift, stable=False)
    record("range_of_gamma_times_distance_over_upper_price_bound_at_gamma_1e6",
           [round(min(scaled_at_top), 3), round(max(scaled_at_top), 3)])
    record("markets_where_both_prices_approach_the_limit_from_above", int(from_above))
    assert first is not None and first <= GAMMAS_N[-2]
