"""Propositions 8 and 9 against the model.

Proposition 8 gives the signs of the derivatives of the first-period equilibrium order
quantities with respect to the first-period prices when gamma is large. Proposition 9 gives
the equilibrium price path of the whole game when gamma is large: in Scenario S the lower
price bound in period 1 and the upper bound in period 2, in Scenario N interior prices that
fall from period 1 to period 2.

The equilibrium objects come from the model. For each first-period price pair the order
quantities are the solution of the model's two first-order conditions, with the second
period played as `section5.SecondPeriodS` or `section5.SecondPeriodN` computes it. In Scenario S
that solution is the closed form of Lemma A.1(a), which is exact, and the tests confirm at
every pair of their price grids that the marginal profits vanish there and that the
continuation is pinned down. In Scenario N the closed form of Lemma A.2(a) is only the
starting point of a Newton iteration on the first-order conditions. A search over each
retailer's whole order interval, with payoff values only, confirms the solution at selected
price pairs. `test_section_5_first_period.py` tests the two lemmas themselves.

The first-period price equilibrium of Proposition 9 is not assumed. It is computed from the
reduced payoffs, which are the two-period profits at the inventory equilibrium of each
first-period price pair, by best-response iteration over continuous prices.

Both propositions hold "for sufficiently large gamma". A test at finite gamma probes them
and does not prove them. Each test runs a ladder of gamma, requires the claim at the two
largest values, and records the smallest value from which it holds at every sampled point.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from c2c import primitives as pm

from c2c.section5 import (CLAIMED_SLOPE_SIGNS, SecondPeriodN, SecondPeriodS, claimed_bound_a23, claimed_condition_a22,
                    claimed_first_period_prices_s, claimed_nu, claimed_orders_n, claimed_orders_s,
                    claimed_price_path_n, claimed_price_path_s, claimed_second_period_prices_s, draw_market,
                    first_period_profits, inventory_equilibrium, iterate_best_responses, marginal_profits, price_gap,
                    price_replies, proof_first_period_limit_prices, pure_equilibria_on_grid, second_period_profits,
                    threshold_on_ladder)

# GAIN_TOL is the largest admissible payoff gain from a unilateral deviation, relative to the payoff scale.
# DIST_TOL is the largest admissible distance between a best response and the tested value, relative to its scale.
GAIN_TOL = 1e-8
DIST_TOL = 2e-5

GAMMAS_S = (1.0, 10.0, 100.0, 1e3, 1e4, 1e5, 1e6)
GAMMAS_N = (10.0, 100.0, 1e3, 1e4, 1e5)
GAMMAS_BOUNDED = (100.0, 1e3, 1e4, 1e5)
GAMMAS_PATH = (100.0, 1e3, 1e4)


def _foc_tol(gamma):
    """Rounding allowance for a marginal profit divided by the unit cost. The stockout
    probability at the equilibrium is of order 1 / gamma and is a difference of numbers of
    order one, so its relative rounding error grows in proportion to gamma."""
    return 1e-12 * (10.0 + gamma)


def _corners(mk):
    """The four corners of the price box."""
    return [(a, b) for a in (mk.p_lo, mk.p_hi) for b in (mk.p_lo, mk.p_hi)]


def _orders_s(mk, cont, gamma, pa1, pb1):
    """First-period equilibrium orders of Scenario S at each price pair, and a flag that is
    true where both marginal profits of the model vanish and where gamma times the smallest
    first-period sales of each retailer exceeds its dominance number, so that both retailers
    charge the upper bound in period 2 at every sales state a unilateral deviation can reach."""
    pa1, pb1 = np.broadcast_arrays(np.asarray(pa1, float), np.asarray(pb1, float))
    ya, yb = claimed_orders_s(mk, gamma, pa1, pb1)
    fa, fb = marginal_profits(mk, cont, gamma, pa1, pb1, ya, yb)
    share = pm.share(pa1, pb1, mk.beta)
    confirmed = ((np.abs(fa) <= _foc_tol(gamma) * mk.ca) & (np.abs(fb) <= _foc_tol(gamma) * mk.cb)
                 & (gamma * np.minimum(share * mk.lo, ya) > cont.dominance[0])
                 & (gamma * np.minimum((1.0 - share) * mk.lo, yb) > cont.dominance[1]))
    return ya, yb, confirmed


def _orders_n(mk, cont, gamma, pa1, pb1):
    """First-period equilibrium orders of Scenario N at each price pair: the solution of the
    two first-order conditions of the model. The flag is true where both marginal profits
    vanish at the solution. A sales state outside the table of `cont` gives a false flag."""
    pa1, pb1 = np.broadcast_arrays(np.asarray(pa1, float), np.asarray(pb1, float))
    try:
        ya, yb = inventory_equilibrium(mk, cont, gamma, pa1, pb1, claimed_orders_n(mk, gamma, pa1, pb1))
        fa, fb = marginal_profits(mk, cont, gamma, pa1, pb1, ya, yb)
    except ValueError:
        return np.full(pa1.shape, np.nan), np.full(pa1.shape, np.nan), np.zeros(pa1.shape, bool)
    return ya, yb, (np.abs(fa) <= _foc_tol(gamma) * mk.ca) & (np.abs(fb) <= _foc_tol(gamma) * mk.cb)


def _no_profitable_order(mk, cont, gamma, pa1, pb1, ya, yb):
    """Search each retailer's whole order interval [0, 1.5 (mu + sigma)], with payoff values
    only, for a profitable deviation from (ya, yb)."""
    upper = 1.5 * mk.hi
    best_a, max_a = pm.best_response(lambda y: first_period_profits(mk, cont, gamma, pa1, pb1, y, yb)[0], upper, grid=1001)
    best_b, max_b = pm.best_response(lambda y: first_period_profits(mk, cont, gamma, pa1, pb1, ya, y)[1], upper, grid=1001)
    at_a, at_b = (float(v) for v in first_period_profits(mk, cont, gamma, pa1, pb1, ya, yb))
    gain = max(max_a - at_a, max_b - at_b) / (mk.p_hi * mk.hi * (1.0 + gamma))
    return bool(gain <= GAIN_TOL and max(abs(best_a - ya), abs(best_b - yb)) <= DIST_TOL * mk.hi)


def _slopes(ya, yb, grid):
    """Difference quotients of the orders between neighbouring points of a price grid. Axis 0
    is retailer A's price and axis 1 is retailer B's. The key is (order of, price of)."""
    step = grid[1] - grid[0]
    return {("A", "A"): np.diff(ya, axis=0) / step, ("A", "B"): np.diff(ya, axis=1) / step,
            ("B", "B"): np.diff(yb, axis=1) / step, ("B", "A"): np.diff(yb, axis=0) / step}


def _signs_hold(part, slopes):
    """True if every slope has the sign that Proposition 8 claims for `part`."""
    keys = [key for key in CLAIMED_SLOPE_SIGNS if key[0] == part]
    return all(bool(np.all(np.sign(slopes[key[1:]]) == CLAIMED_SLOPE_SIGNS[key])) for key in keys)


def _smallest_slope(part, slopes):
    """Smallest absolute value among the slopes that Proposition 8 signs for `part`."""
    return min(float(np.abs(slopes[key[1:]]).min()) for key in CLAIMED_SLOPE_SIGNS if key[0] == part)


def _advantage(table, row, prices):
    """Smallest payoff loss from leaving the price `prices[row]`, per unit of price
    difference. Rows of `table` are own prices and columns are rival prices."""
    others = np.arange(prices.size) != row
    return float(((table[row][None, :] - table[others]) / np.abs(prices[others] - prices[row])[:, None]).min())


# ----------------------------------------------------------------------------- Proposition 8(a)
@pytest.mark.claims("P8.a")
def test_proposition_8a_orders_of_scenario_s_fall_in_own_price_and_rise_in_rival_price(record):
    """Proposition 8(a): in Scenario S, for gamma large, y_{i,1} decreases in p_{i,1} and
    increases in p_{j,1}, for both retailers.
    Points: 20 markets of `draw_market` (seed 5300), a 9 by 9 grid of first-period prices
    that covers the price box, borders included, gamma = 1, 10, 100, 1e3, 1e4, 1e5 and 1e6.
    Computed: the orders of Lemma A.1(a) at all 81 pairs with the flags of `_orders_s` (both
    marginal profits within 1e-12 (10 + gamma) c_i and the continuation of `SecondPeriodS`
    pinned down), the four difference quotients between neighbouring grid points, and at
    gamma = 1e5 and 1e6 a 1001-point search of each order interval at one random grid pair.
    Criterion: the claim holds at a market and gamma if all 81 flags are true, every quotient
    has the claimed sign, and at the two largest gammas the search finds no relative gain
    above 1e-8 and no best response farther than 2e-5 (mu + sigma). It must hold at all
    markets from gamma = 1e5 on, and in each market the largest relative distance of a
    quotient from -beta (mu + sigma) or +beta (mu + sigma), its value when no retailer stocks
    out, must shrink at least fivefold from gamma = 1e5 to 1e6."""
    rng = np.random.default_rng(5300)
    n, points = 20, 9
    holds = np.zeros((n, len(GAMMAS_S)), bool)
    worst_ratio, largest_dev = np.inf, 0.0
    for k in range(n):
        mk = draw_market(rng)
        cont = SecondPeriodS(mk)
        grid = np.linspace(mk.p_lo, mk.p_hi, points)
        pa1, pb1 = np.meshgrid(grid, grid, indexing="ij")
        spot = tuple(rng.integers(0, points, size=2))
        deviation = []
        for j, gamma in enumerate(GAMMAS_S):
            ya, yb, confirmed = _orders_s(mk, cont, gamma, pa1, pb1)
            slopes = _slopes(ya, yb, grid)
            good = bool(confirmed.all()) and _signs_hold("a", slopes)
            if good and j >= len(GAMMAS_S) - 2:
                good = _no_profitable_order(mk, cont, gamma, pa1[spot], pb1[spot], float(ya[spot]), float(yb[spot]))
            holds[k, j] = good
            deviation.append(max(float(np.abs(np.abs(v) / (mk.beta * mk.hi) - 1.0).max()) for v in slopes.values()))
        assert deviation[-1] <= deviation[-2] / 5.0, (mk, deviation)
        worst_ratio = min(worst_ratio, deviation[-2] / deviation[-1])
        largest_dev = max(largest_dev, deviation[-1])
    first = threshold_on_ladder(GAMMAS_S, list(holds.all(axis=0)))
    record("markets", n)
    record("price_pairs_per_market", points * points)
    record("gamma_ladder", list(GAMMAS_S))
    record("markets_where_the_claim_holds_by_gamma", [int(v) for v in holds.sum(axis=0)])
    record("holds_in_all_markets_from_gamma", first)
    record("largest_relative_distance_of_a_slope_from_its_limit_at_gamma_1e6", float(f"{largest_dev:.2g}"))
    record("smallest_factor_by_which_that_distance_shrinks_from_gamma_1e5_to_1e6", round(worst_ratio, 2))
    assert first is not None and first <= GAMMAS_S[-2]


# ----------------------------------------------------------------------------- Proposition 8(b1) and (b2), fixed theta
@pytest.mark.claims("P8.b1", "P8.b2")
def test_proposition_8b_orders_of_scenario_n_at_fixed_theta(record):
    """Proposition 8(b1) and the last sentence of 8(b2), Scenario N, gamma large. (b1) y_{A,1}
    decreases and y_{B,1} increases in p_{A,1}. (b2, fixed theta < 1) y_{A,1} increases and
    y_{B,1} decreases in p_{B,1}.
    Points: 6 markets of `draw_market` (seed 5301), a 7 by 7 grid of first-period prices that
    covers the price box, theta = 0, 0.5, 0.9 and 1 for (b1), whose thresholds Online Appendix
    A.2 announces as uniform in theta, and 0, 0.5 and 0.9 for (b2), gamma = 10, 100, 1e3, 1e4, 1e5.
    Computed: the solutions of the model's first-order conditions at all 49 pairs (`_orders_n`,
    `SecondPeriodN`), the difference quotients between neighbouring grid points, and at
    gamma = 1e4 and 1e5 a 1001-point search of each order interval at one random grid pair.
    Criterion: a part holds at a market, theta and gamma if the conditions are solved within
    1e-12 (10 + gamma) c_i at all 49 pairs, the table reports no problem, every quotient of the
    part has the claimed sign, and at the two largest gammas the search finds no relative gain
    above 1e-8 and no best response farther than 2e-5 (mu + sigma). Each part must hold in
    every case from gamma = 1e4 on."""
    rng = np.random.default_rng(5301)
    n, points = 6, 7
    thetas = {"b1": (0.0, 0.5, 0.9, 1.0), "b2 fixed": (0.0, 0.5, 0.9)}
    holds = {part: np.zeros((n, len(values), len(GAMMAS_N)), bool) for part, values in thetas.items()}
    weakest = {part: np.inf for part in thetas}
    for k in range(n):
        base = draw_market(rng)
        grid = np.linspace(base.p_lo, base.p_hi, points)
        pa1, pb1 = np.meshgrid(grid, grid, indexing="ij")
        spot = tuple(rng.integers(0, points, size=2))
        for t, theta in enumerate(thetas["b1"]):
            mk = replace(base, theta=theta)
            # The table covers the equilibrium states at every gamma, and at the two largest values of
            # gamma also every state that a unilateral deviation at the confirmed pair can reach.
            reach = mk.smallest_share * mk.lo
            cont = SecondPeriodN(mk, max(2.0 / (GAMMAS_N[0] * mk.lo), 1.001 / (GAMMAS_N[-2] * reach)))
            for j, gamma in enumerate(GAMMAS_N):
                ya, yb, solved = _orders_n(mk, cont, gamma, pa1, pb1)
                good = bool(solved.all()) and not cont.problems
                if good and j >= len(GAMMAS_N) - 2:
                    good = _no_profitable_order(mk, cont, gamma, pa1[spot], pb1[spot], float(ya[spot]), float(yb[spot]))
                slopes = _slopes(ya, yb, grid)
                for part in thetas:
                    if theta in thetas[part]:
                        holds[part][k, t, j] = good and _signs_hold(part, slopes)
                        if j == len(GAMMAS_N) - 1:
                            weakest[part] = min(weakest[part], _smallest_slope(part, slopes) / (mk.beta * mk.hi))
    record("markets", n)
    record("price_pairs_per_market", points * points)
    record("gamma_ladder", list(GAMMAS_N))
    for part, label in (("b1", "(b1)"), ("b2 fixed", "(b2) fixed theta")):
        first = threshold_on_ladder(GAMMAS_N, list(holds[part].all(axis=(0, 1))))
        record(f"{label}: values of theta", list(thetas[part]))
        record(f"{label}: cases where the claim holds by gamma", [int(v) for v in holds[part].sum(axis=(0, 1))])
        record(f"{label}: holds in all cases from gamma", first)
        record(f"{label}: smallest slope over beta (mu + sigma) at gamma 1e5", round(weakest[part], 3))
        assert first is not None and first <= GAMMAS_N[-2], part


# ----------------------------------------------------------------------------- Proposition 8(b2), gamma (1 - theta) bounded
def _market_with_condition_a22(rng):
    """A market from `draw_market` that satisfies condition (A.22)."""
    for _ in range(10000):
        mk = draw_market(rng)
        if claimed_condition_a22(mk) > 1.0:
            return mk
    raise AssertionError("no market among 10,000 draws satisfies condition (A.22)")


def _patch_inside_a23(mk):
    """An interior price pair of the set (A.23), a 3 by 3 patch of half-width e around it, and
    a level l with l nu_B = e. The pair has p_{A,1} halfway between the upper price bound and
    the smallest value that leaves room for p_{B,1}, and p_{B,1} halfway between the lower
    price bound and the bound of (A.23). e is one tenth of the distance to the nearest edge."""
    nu_b = claimed_nu(mk)[1]
    c = float(claimed_bound_a23(mk, 0.0)) ** 2                 # The bound of (A.23) is sqrt(c (1 + 2 beta p_A)).
    pa_min = max(mk.p_lo, (mk.p_lo ** 2 / c - 1.0) / (2.0 * mk.beta))
    pa0 = 0.5 * (pa_min + mk.p_hi)
    bound = min(mk.p_hi, float(claimed_bound_a23(mk, pa0)))
    pb0 = 0.5 * (mk.p_lo + bound)
    e = 0.1 * min(mk.p_hi - pa0, pa0 - pa_min, pb0 - mk.p_lo, bound - pb0)
    level = e / nu_b
    assert mk.p_lo < pa0 - e and pa0 + e < mk.p_hi and mk.p_lo < pb0 - e, mk
    assert pb0 + e + level * nu_b < min(mk.p_hi, float(claimed_bound_a23(mk, pa0 - e))), mk     # This is (A.24).
    offsets = e * np.array([-1.0, 0.0, 1.0])
    pa1, pb1 = np.meshgrid(pa0 + offsets, pb0 + offsets, indexing="ij")
    return pa1, pb1, level


def _slopes_in_price_of_b(mk, gamma, pa1, pb1):
    """d y_A / d p_B and d y_B / d p_B of the equilibrium orders of Scenario N at each price
    pair, by central differences with step 1e-4 (p_hi - p_lo). Returns the two slopes, a flag
    that is true if every equilibrium was solved and the price table reports no problem, the
    table, and the orders at the centre pair."""
    h = 1e-4 * (mk.p_hi - mk.p_lo)
    cont = SecondPeriodN(mk, max(2.0 / (gamma * mk.lo), 1.001 / (gamma * mk.smallest_share * mk.lo)))
    up, down, mid = (_orders_n(mk, cont, gamma, pa1, pb1 + d) for d in (h, -h, 0.0))
    solved = bool(up[2].all() and down[2].all() and mid[2].all()) and not cont.problems
    slopes = {("A", "B"): (up[0] - down[0]) / (2.0 * h), ("B", "B"): (up[1] - down[1]) / (2.0 * h)}
    return slopes, solved, cont, (float(mid[0][1, 1]), float(mid[1][1, 1]))


@pytest.mark.claims("P8.b2")
def test_proposition_8b2_reversal_when_gamma_times_one_minus_theta_is_bounded(record):
    """Under condition (A.22) of the Online Appendix, Proposition 8(b2) gives
    an open set of first-period price pairs on which
    y_{A,1} decreases and y_{B,1} increases in p_{B,1}, provided gamma is large and
    0 <= gamma (1 - theta) <= l^D for some l^D > 0.
    Points: 8 markets of `draw_market` that satisfy (A.22) (seed 5302), a 3 by 3 patch of
    prices inside the set (A.23) of the proof, theta = 1 and 1 - l / gamma with one positive l,
    gamma = 100, 1e3, 1e4 and 1e5, and theta = 0.5 at gamma = 1e4 and 1e5.
    Computed: d y_A / d p_B and d y_B / d p_B of the solutions of the first-order conditions
    (`_orders_n`) by central differences of step 1e-4 (p_hi - p_lo), and at gamma = 1e4 and 1e5
    a search of each order interval at the centre pair. The gap to the expansion (A.26) is recorded.
    Criterion: the claim holds at a market and gamma if at both values of theta all equilibria
    are solved, the table reports no problem, the slopes are negative for y_A and positive for
    y_B at all 9 pairs, and at the two largest gammas the search finds no relative gain above
    1e-8 and no best response farther than 2e-5 (mu + sigma). It must hold at all markets from
    gamma = 1e4 on. At theta = 0.5 and gamma = 1e4 and 1e5 both signs are reversed at all 9 pairs."""
    rng = np.random.default_rng(5302)
    n = 8
    holds = np.zeros((n, len(GAMMAS_BOUNDED)), bool)
    weakest, smallest_ratio, largest_level, worst_expansion = np.inf, np.inf, 0.0, 0.0
    for k in range(n):
        base = _market_with_condition_a22(rng)
        nu_a, nu_b = claimed_nu(base)
        pa1, pb1, positive_level = _patch_inside_a23(base)
        smallest_ratio = min(smallest_ratio, claimed_condition_a22(base))
        largest_level = max(largest_level, positive_level)
        for j, gamma in enumerate(GAMMAS_BOUNDED):
            good = True
            for level in (0.0, positive_level):
                mk = replace(base, theta=1.0 - level / gamma)
                slopes, solved, cont, centre = _slopes_in_price_of_b(mk, gamma, pa1, pb1)
                good &= solved and _signs_hold("b2 bounded", slopes)
                if good and j >= len(GAMMAS_BOUNDED) - 2:
                    good = _no_profitable_order(mk, cont, gamma, pa1[1, 1], pb1[1, 1], *centre)
                if j == len(GAMMAS_BOUNDED) - 1:
                    weakest = min(weakest, _smallest_slope("b2 bounded", slopes) / (base.beta * base.hi))
                    shifted = pb1 + level * nu_b                                           # This is expansion (A.26).
                    expansion = -base.beta * base.hi + base.sigma * (base.cb - base.ca * nu_b / nu_a) * (
                        1.0 + 2.0 * base.beta * pa1 + 2.0 * base.beta * level * nu_b) / shifted ** 2
                    gap = float(np.abs(slopes[("B", "B")] - expansion).max()) / (base.beta * base.hi)
                    worst_expansion = max(worst_expansion, gap)
            holds[k, j] = good
            if j >= len(GAMMAS_BOUNDED) - 2:                   # This is the reversal at a fixed theta below one.
                slopes, solved, _, _ = _slopes_in_price_of_b(replace(base, theta=0.5), gamma, pa1, pb1)
                assert solved and _signs_hold("b2 fixed", slopes), (base, gamma)
    first = threshold_on_ladder(GAMMAS_BOUNDED, list(holds.all(axis=0)))
    record("markets", n)
    record("gamma_ladder", list(GAMMAS_BOUNDED))
    record("markets_where_the_claim_holds_by_gamma", [int(v) for v in holds.sum(axis=0)])
    record("holds_in_all_markets_from_gamma", first)
    record("smallest_ratio_of_the_two_sides_of_A22", round(float(smallest_ratio), 3))
    record("largest_tested_value_of_gamma_times_one_minus_theta", float(f"{largest_level:.2g}"))
    record("smallest_slope_over_beta_mu_plus_sigma_at_gamma_1e5", float(f"{weakest:.2g}"))
    record("max_difference_to_expansion_A26_over_beta_mu_plus_sigma_at_gamma_1e5", worst_expansion, stable=False)
    assert first is not None and first <= GAMMAS_BOUNDED[-2]


# ----------------------------------------------------------------------------- Proposition 9(a)
def _check_price_path_of_scenario_s(mk, cont, gamma, first_claim, second_claim):
    """The five steps of the test of Proposition 9(a) at one market and one gamma. Returns
    whether the claimed prices passed them, and for each retailer the advantage of its
    claimed first-period price (see `_advantage`)."""
    own, rival = np.linspace(mk.p_lo, mk.p_hi, 101), np.linspace(mk.p_lo, mk.p_hi, 41)

    def reduced(pa1, pb1):
        ya, yb, _ = _orders_s(mk, cont, gamma, pa1, pb1)
        return first_period_profits(mk, cont, gamma, pa1, pb1, ya, yb)

    # Steps 1 and 2 use the grid. Rows are the own price in both tables.
    confirmed = bool(_orders_s(mk, cont, gamma, own[:, None], rival[None, :])[2].all()
                     and _orders_s(mk, cont, gamma, rival[None, :], own[:, None])[2].all())
    table_a = reduced(own[:, None], rival[None, :])[0]
    table_b = reduced(rival[None, :], own[:, None])[1]
    ia, ib = int(np.argmin(np.abs(own - first_claim[0]))), int(np.argmin(np.abs(own - first_claim[1])))
    dominant = bool(np.all(table_a.argmax(axis=0) == ia) and np.all(table_b.argmax(axis=0) == ib))
    edges = (_advantage(table_a, ia, own), _advantage(table_b, ib, own))
    good = confirmed and dominant
    first, second = [], []                                     # These collect the computed prices of the two periods.
    if good:                                                   # This is step 3.
        gap = price_gap(reduced, mk, *first_claim, grid=501)
        good = gap["gain"] <= GAIN_TOL * abs(float(reduced(*first_claim)[0])) and gap["dist"] <= 1e-12 * mk.p_hi
        replies = price_replies(reduced, mk, first=65, points=17, levels=3)
        first = [iterate_best_responses(*replies, start, sweeps=10, tol=1e-12)[:2] for start in _corners(mk)]
        good &= all(abs(a - first_claim[0]) + abs(b - first_claim[1]) <= 1e-12 * mk.p_hi for a, b in first)
    if good:                                                   # This is step 4.
        small = np.linspace(mk.p_lo, mk.p_hi, 41)
        ya, yb, _ = _orders_s(mk, cont, gamma, *first[0])
        share = pm.share(*first[0], mk.beta)
        for x in (mk.lo, mk.mu, mk.hi):
            ra1, rb1 = pm.sales(x, ya, yb, share, 1.0 - share, mk.theta)
            tables = second_period_profits(mk, "S", gamma, small[:, None], small[None, :], ra1, rb1)
            cells = pure_equilibria_on_grid(*tables)
            second += [(small[i], small[j]) for i, j in cells]
            good &= len(cells) == 1 and second[-1] == second_claim
    if good:                                                   # This is step 5.
        good = all(claimed_price_path_s(mk, p1[i], p2[i]) for p1 in first for p2 in second for i in (0, 1))
    return bool(good), edges


@pytest.mark.claims("P9.a")
def test_proposition_9a_price_path_of_scenario_s(record):
    """Proposition 9(a): in Scenario S, for gamma large, the equilibrium prices are the lower
    bound in period 1 and the upper bound in period 2, for both retailers.
    Points: 20 markets of `draw_market` (seed 5303), gamma = 1, 10, 100, 1e3, 1e4, 1e5 and 1e6.
    Computed: the reduced payoffs (two-period profits at the orders of Lemma A.1(a), continuation
    `SecondPeriodS`) on a grid of 101 own by 41 rival prices, a search of each price interval,
    best-response iteration from the four corners, the second-period price game from the
    primitives on a 41 by 41 grid at the sales for seed demand mu - sigma, mu and mu + sigma,
    and the advantage of p_lo, the smallest loss per unit of price change to another grid price.
    Criterion: the claim holds at a market and gamma if `_orders_s` confirms every grid pair,
    p_lo is each retailer's best reply to every rival grid price, the search finds no relative
    gain above 1e-8, the search and iterations end within 1e-12 p_hi of (p_lo, p_lo), each grid
    game of period 2 has (p_hi, p_hi) as its only pure equilibrium, and
    p_lo = p_{i,1} < p_{i,2} = p_hi. Once it holds it must keep holding, it must hold at all
    markets from 1e5 on and fail at gamma = 1 somewhere, and the advantage must be positive at
    1e5 and grow by a factor in [9.9, 10.1] from 1e5 to 1e6."""
    rng = np.random.default_rng(5303)
    n = 20
    holds = np.zeros((n, len(GAMMAS_S)), bool)
    weakest_edge, worst_growth = np.inf, 0.0
    for k in range(n):
        mk = draw_market(rng)
        cont = SecondPeriodS(mk)
        first_claim, second_claim = claimed_first_period_prices_s(mk), claimed_second_period_prices_s(mk)
        edges = []
        for j, gamma in enumerate(GAMMAS_S):
            holds[k, j], edge = _check_price_path_of_scenario_s(mk, cont, gamma, first_claim, second_claim)
            edges.append(edge)
        for who in (0, 1):
            growth = edges[-1][who] / edges[-2][who]
            worst_growth = max(worst_growth, abs(growth - 10.0))
            weakest_edge = min(weakest_edge, edges[-2][who] / (GAMMAS_S[-2] * mk.p_hi * mk.beta * mk.mu))
            assert edges[-2][who] > 0.0 and abs(growth - 10.0) <= 0.1, (mk, edges)
        assert np.all(np.diff(holds[k].astype(int)) >= 0), (mk, holds[k])           # Once the claim holds, it keeps holding.
    first = threshold_on_ladder(GAMMAS_S, list(holds.all(axis=0)))
    record("markets", n)
    record("gamma_ladder", list(GAMMAS_S))
    record("markets_where_the_claim_holds_by_gamma", [int(v) for v in holds.sum(axis=0)])
    record("holds_in_all_markets_from_gamma", first)
    record("smallest_advantage_of_lower_bound_over_gamma_p_hi_beta_mu_at_gamma_1e5", round(float(weakest_edge), 3))
    record("max_deviation_from_tenfold_growth_of_the_advantage", round(worst_growth, 4))
    assert first is not None and first <= GAMMAS_S[-2]
    assert not holds[:, 0].all()                               # The ladder starts below the threshold of some market.


# ----------------------------------------------------------------------------- Proposition 9(b)
def _price_path_of_scenario_n(mk, gamma):
    """Computes the price path of Scenario N at one market and one gamma, and runs the four
    steps of the test of Proposition 9(b). Returns whether the path passed them, the
    first-period price pair, for each retailer the gap between its first-period price and its
    highest second-period price, and the distance between the two runs relative to p_hi."""
    cont = SecondPeriodN(mk, 2.0 / (gamma * mk.lo))

    def reduced(pa1, pb1):
        ya, yb, _ = _orders_n(mk, cont, gamma, pa1, pb1)
        return first_period_profits(mk, cont, gamma, pa1, pb1, ya, yb)

    replies = price_replies(reduced, mk, first=41, points=17, levels=5)
    runs = [iterate_best_responses(*replies, start, sweeps=10, tol=2e-6 * mk.p_hi)
            for start in ((mk.p_lo, mk.p_hi), (mk.p_hi, mk.p_lo))]
    pa1, pb1 = runs[0][0], runs[0][1]
    apart = (abs(runs[1][0] - pa1) + abs(runs[1][1] - pb1)) / mk.p_hi
    good = apart <= 1e-4 and not cont.problems                                           # These are steps 1 and 3.

    own = np.linspace(mk.p_lo, mk.p_hi, 41)                                               # This is step 2.
    good &= bool(_orders_n(mk, cont, gamma, own, pb1)[2].all() and _orders_n(mk, cont, gamma, pa1, own)[2].all())
    ya, yb, solved = (float(v) for v in _orders_n(mk, cont, gamma, pa1, pb1))
    share = pm.share(pa1, pb1, mk.beta)
    wide = SecondPeriodN(mk, 1.001 / (gamma * min(share * mk.lo, (1.0 - share) * mk.lo, ya, yb)))
    good &= bool(solved) and not wide.problems and _no_profitable_order(mk, wide, gamma, pa1, pb1, ya, yb)

    x = np.linspace(mk.lo, mk.hi, 201)
    ra1, rb1 = pm.sales(x, ya, yb, share, 1.0 - share, mk.theta)
    second = cont.prices(gamma, ra1 + rb1)                    # These are the second-period prices at 201 states.
    mid = len(x) // 2                                                                     # Step 3 uses the mean seed demand.

    def second_period(pa2, pb2):
        return second_period_profits(mk, "N", gamma, pa2, pb2, ra1[mid], rb1[mid])

    at_mid = float(second[0][mid]), float(second[1][mid])
    gap = price_gap(second_period, mk, *at_mid)
    good &= gap["gain"] <= GAIN_TOL * abs(float(second_period(*at_mid)[0])) and gap["dist"] <= DIST_TOL * mk.p_hi

    for who, first_price in enumerate((pa1, pb1)):                                        # This is step 4.
        good &= claimed_price_path_n(mk, first_price, float(second[who].min()))
        good &= claimed_price_path_n(mk, first_price, float(second[who].max()))
    return bool(good), (pa1, pb1), (pa1 - float(second[0].max()), pb1 - float(second[1].max())), apart


@pytest.mark.claims("P9.b")
def test_proposition_9b_price_path_of_scenario_n(record):
    """Proposition 9(b): in Scenario N, for a fixed theta < 1 and gamma large,
    p_lo < p_{i,2} < p_{i,1} < p_hi for both retailers.
    Points: 5 markets of `draw_market` (seed 5304) with theta scaled to 0.9 theta, gamma = 100,
    1e3 and 1e4. Above 1e4 first-period prices are located less accurately.
    Computed: the first-period price equilibrium of the reduced payoffs (`_orders_n`,
    `SecondPeriodN`) by best-response iteration over the price interval from (p_lo, p_hi) and
    (p_hi, p_lo), and the second-period prices at the sales of 201 seed demands on the support.
    Criterion: the claim holds at a market and gamma if the two runs agree within 1e-4 p_hi,
    the tables report no problem, the first-order conditions are solved at 41 own prices of
    each retailer and at the equilibrium, searches of the order intervals there and of the
    second-period price intervals at the mean seed demand find no relative gain above 1e-8 and
    no best response farther than 2e-5 (mu + sigma) or 2e-5 p_hi, and p_lo < min p_{i,2} and
    max p_{i,2} < p_{i,1} < p_hi. It must hold at all markets from gamma = 1e3 on, and the gap
    p_{i,1} - max p_{i,2} must change from 1e3 to 1e4 by at most a quarter of its change from
    100 to 1e3."""
    rng = np.random.default_rng(5304)
    n = 5
    holds = np.zeros((n, len(GAMMAS_PATH)), bool)
    smallest_gap, worst_settle, worst_runs, gap_error = np.inf, 0.0, 0.0, 0.0
    scaled_limit = []
    for k in range(n):
        mk = draw_market(rng)
        mk = replace(mk, theta=0.9 * mk.theta)
        gaps = []
        for j, gamma in enumerate(GAMMAS_PATH):
            holds[k, j], prices, gap, apart = _price_path_of_scenario_n(mk, gamma)
            gaps.append(gap)
            worst_runs = max(worst_runs, apart)
        limit = proof_first_period_limit_prices(mk)            # The measurements below are taken at the largest gamma.
        scaled_limit.append(gamma * max(abs(prices[0] - limit[0]), abs(prices[1] - limit[1])) / mk.p_hi)
        for who, (own_cost, rival_cost) in enumerate(((mk.ca, mk.cb), (mk.cb, mk.ca))):
            limit_gap = mk.sigma * (2.0 * own_cost + rival_cost) / (3.0 * mk.mu)
            gap_error = max(gap_error, abs(gaps[-1][who] - limit_gap) / limit_gap)
            early, late = abs(gaps[1][who] - gaps[0][who]), abs(gaps[2][who] - gaps[1][who])
            worst_settle = max(worst_settle, late / early)
            smallest_gap = min(smallest_gap, gaps[2][who] / mk.p_hi)
            assert late <= 0.25 * early, (mk, gaps)
    first = threshold_on_ladder(GAMMAS_PATH, list(holds.all(axis=0)))
    record("markets", n)
    record("gamma_ladder", list(GAMMAS_PATH))
    record("markets_where_the_claim_holds_by_gamma", [int(v) for v in holds.sum(axis=0)])
    record("holds_in_all_markets_from_gamma", first)
    record("smallest_gap_between_period_prices_over_p_hi_at_gamma_1e4", smallest_gap, stable=False)
    record("largest_ratio_of_late_to_early_change_of_the_gap", worst_settle, stable=False)
    record("max_relative_difference_to_limit_gap_of_the_proof_at_gamma_1e4", gap_error, stable=False)
    record("range_of_gamma_times_distance_to_limit_prices_of_the_proof_over_p_hi_at_gamma_1e4",
           [min(scaled_limit), max(scaled_limit)], stable=False)
    record("max_relative_distance_between_the_two_runs", worst_runs, stable=False)
    assert first is not None and first <= GAMMAS_PATH[-2]
