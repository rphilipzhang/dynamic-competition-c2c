"""Section 5, first-period inventory subgame: Lemmas A.1(a) and A.2(a) against the model.

Given first-period prices, each retailer chooses an order quantity. Its payoff is the
first-period profit plus the expected second-period profit, and the second-period profit is
the equilibrium profit of the second-period price game at the realized first-period sales.
The tests take that continuation from the model, never from the lemmas:

    Scenario S   `section5.SecondPeriodS`. Whenever gamma times a retailer's first-period sales
                 exceeds a number computed from the benchmark profit, the upper price bound is
                 that retailer's only best reply to every rival price. A retailer that deviates
                 to a small order sells little and then prices lower in period 2. Its
                 continuation value is its best profit against the rival's upper bound.
    Scenario N   `section5.SecondPeriodN`. The second-period price equilibrium is computed as a
                 function of total first-period sales, and its profit is the continuation value.

Lemma A.1(a) gives the equilibrium of Scenario S exactly. Lemma A.2(a) gives the equilibrium
of Scenario N up to a term of order gamma^-2. Each claimed order pair is tested in three ways.

    1. A search over each retailer's whole order interval, with payoff values only, for a
       profitable unilateral deviation from the claimed pair.
    2. The exact position of the equilibrium, from the model's first-order conditions.
       In Scenario S they must hold at the claimed pair to rounding error. In Scenario N the
       distance between the claimed pair and their solution must shrink like gamma^-2.
    3. Uniqueness probes: best-response iteration from several starting pairs, and in
       Scenario N a scan of the fixed-point equation of the best-response map.

Both lemmas hold "for sufficiently large gamma". A test at finite gamma probes them and does
not prove them.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from c2c import primitives as pm

from c2c.section5 import (SecondPeriodN, SecondPeriodS, argmax_on_interval, claimed_orders_n, claimed_orders_s, draw_market,
                    first_period_nodes, first_period_profits, inventory_equilibrium, iterate_best_responses,
                    marginal_profits, price_equilibrium_n, second_period_profits, threshold_on_ladder)

# GAIN_TOL is the largest admissible payoff gain from a unilateral deviation, relative to the payoff scale.
# DIST_TOL is the largest admissible distance between a best response and the claimed order, relative to mu + sigma.
# A distance between two order pairs, relative to mu + sigma, is measurable above ERROR_FLOOR.
GAIN_TOL = 1e-8
DIST_TOL = 2e-5
ERROR_FLOOR = 3e-13

# GAMMAS_RATE covers three decades in steps of half a decade. GAMMAS_SEARCH lists the values at which the
# whole order interval is searched. LEVELS lists values of gamma (1 - theta).
GAMMAS_S = (1.0, 10.0, 100.0, 1e3, 1e4, 1e5, 1e6)
GAMMAS_RATE = (10.0, 30.0, 100.0, 300.0, 1e3, 3e3, 1e4)
GAMMAS_SEARCH = (10.0, 100.0, 1e3, 1e4)
GAMMAS_UNIFORM = (300.0, 1e3, 3e3)
LEVELS = (0.0, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0)


def _foc_tol(gamma):
    """Rounding allowance for a marginal profit divided by the unit cost. The stockout
    probability at the equilibrium is of order 1 / gamma and is a difference of numbers of
    order one, so its relative rounding error grows in proportion to gamma."""
    return 1e-12 * (10.0 + gamma)


def _rival_floor(mk, share_a, ya, yb):
    """Smallest first-period sales of each retailer over all seed demands and all orders of
    the other retailer. Retailer i sells at least min(alpha_i (mu - sigma), y_i)."""
    return min(share_a * mk.lo, ya), min((1.0 - share_a) * mk.lo, yb)


def _best_replies(mk, cont, gamma, pa1, pb1, seen=None):
    """The two best-reply maps of the first-period inventory subgame. A best reply is a
    global maximiser over [0, 1.5 (mu + sigma)], found from payoff values. Every rival order
    that a map is asked about is appended to `seen`."""
    upper = 1.5 * mk.hi

    def reply_a(yb):
        if seen is not None:
            seen.append(yb)
        return argmax_on_interval(lambda y: first_period_profits(mk, cont, gamma, pa1, pb1, y, yb)[0], 0.0, upper)[0]

    def reply_b(ya):
        if seen is not None:
            seen.append(ya)
        return argmax_on_interval(lambda y: first_period_profits(mk, cont, gamma, pa1, pb1, ya, y)[1], 0.0, upper)[0]

    return reply_a, reply_b


def _deviation_search(mk, cont, gamma, pa1, pb1, ya, yb, grid=4001):
    """Search each retailer's whole order interval [0, 1.5 (mu + sigma)], with payoff values
    only, for the best unilateral deviation from (ya, yb). Returns the payoff gain of the
    best deviation relative to the payoff scale p_hi (mu + sigma)(1 + gamma), and the
    distance of the best responses from (ya, yb) relative to mu + sigma."""
    upper = 1.5 * mk.hi
    best_a, max_a = pm.best_response(lambda y: first_period_profits(mk, cont, gamma, pa1, pb1, y, yb)[0], upper, grid=grid)
    best_b, max_b = pm.best_response(lambda y: first_period_profits(mk, cont, gamma, pa1, pb1, ya, y)[1], upper, grid=grid)
    at_a, at_b = (float(v) for v in first_period_profits(mk, cont, gamma, pa1, pb1, ya, yb))
    gain = max(max_a - at_a, max_b - at_b) / (mk.p_hi * mk.hi * (1.0 + gamma))
    return gain, max(abs(best_a - ya), abs(best_b - yb)) / mk.hi


def _error_of_closed_form(mk, cont, gamma, pa1, pb1):
    """Distance, relative to mu + sigma, between the closed form of Lemma A.2(a) and the
    solution of the model's two first-order conditions. Returns (distance, solution)."""
    claim = tuple(float(v) for v in claimed_orders_n(mk, gamma, pa1, pb1))
    ya, yb = (float(v) for v in inventory_equilibrium(mk, cont, gamma, pa1, pb1, claim))
    fa, fb = marginal_profits(mk, cont, gamma, pa1, pb1, ya, yb)
    assert max(abs(float(fa)) / mk.ca, abs(float(fb)) / mk.cb) <= _foc_tol(gamma), (mk, pa1, pb1, gamma)
    return max(abs(ya - claim[0]), abs(yb - claim[1])) / mk.hi, (ya, yb)


# ----------------------------------------------------------------------------- the machinery
@pytest.mark.supports("LA1", "LA2", "P8", "P9")
def test_first_period_machinery_reproduces_the_model(record):
    """Three numerical tools of `section5` against direct computations (seed 5200).
    Points: (1) 300 markets of `draw_market`, a share uniform on [0.02, 0.98], orders uniform on
    [0, 1.5 (mu + sigma)]. (2) 24 markets, gamma log-uniform on [10, 1e4], total sales R_1
    uniform on [0.2, 1] (mu + sigma). (3) In each of these, 5 order pairs per scenario at prices
    uniform on the box, orders 0.6 to 1.1 times the claimed ones, in Scenario S gamma at least
    100 and only pairs at which both retailers charge p_hi at every sales state.
    Computed: (1) expected sales from `first_period_nodes` and from `primitives.Uniform`.
    (2) prices, profits and slope in R_1 of `SecondPeriodN` and of a direct solution of the price
    game from the primitives, the slope by a central difference of step 1e-3 R_1.
    (3) `marginal_profits` and central differences of `first_period_profits` of step 1e-6 (mu + sigma).
    Criterion: (1) errors at most 1e-13 (mu + sigma), weights summing to 1 within 1e-13. (2) no
    table problem, prices within 1e-10 p_hi, profits within 1e-10 and slopes within 1e-7
    relative. (3) errors at most 1e-6 p_hi (1 + gamma), 120 pairs in Scenario N, 100 or more in S."""
    rng = np.random.default_rng(5200)
    worst_nodes = worst_price = worst_value = worst_slope = worst_marginal = 0.0
    for _ in range(300):
        mk = draw_market(rng)
        share = np.array(rng.uniform(0.02, 0.98))
        ya, yb = (np.array(v) for v in rng.uniform(0.0, 1.5 * mk.hi, size=2))
        x, w = first_period_nodes(mk, ya, yb, share)
        ra, rb = pm.sales(x, ya, yb, share, 1.0 - share, mk.theta)
        exact = mk.dist.expected_sales(ya, yb, share, 1.0 - share, mk.theta)
        worst_nodes = max(worst_nodes, abs((w * ra).sum() - exact[0][0]) / mk.hi,
                          abs((w * rb).sum() - exact[1][0]) / mk.hi, abs(w.sum() - 1.0))
    used = {"S": 0, "N": 0}
    for _ in range(24):
        mk = draw_market(rng)
        gamma = float(10.0 ** rng.uniform(1.0, 4.0))
        r1 = rng.uniform(0.2, 1.0) * mk.hi
        step = 1e-3 * r1
        # The table must cover the states of part (2) and those of part (3), where each retailer sells at
        # least 0.6 times its share of the smallest seed demand.
        table = SecondPeriodN(mk, 1.0 / (gamma * min(r1 - 2.0 * step, 0.59 * mk.lo)))
        assert not table.problems, (mk, table.problems)

        def direct(total):
            pa, pb = price_equilibrium_n(mk, 1.0 / (gamma * total))
            return (float(pa), float(pb)), second_period_profits(mk, "N", gamma, pa, pb, total, 0.0)

        prices, value = direct(r1)
        tab_prices, tab_value = table.prices(gamma, r1), table.value(gamma, r1, 0.0)
        tab_slope = table.slopes(gamma, r1, 0.0)
        up, down = direct(r1 + step)[1], direct(r1 - step)[1]
        for who in (0, 1):
            worst_price = max(worst_price, abs(float(tab_prices[who]) - prices[who]) / mk.p_hi)
            worst_value = max(worst_value, abs(float(tab_value[who]) - float(value[who])) / float(value[who]))
            fd = float(up[who] - down[who]) / (2.0 * step)
            worst_slope = max(worst_slope, abs(float(tab_slope[who][0]) - fd) / fd)

        # Part (3) compares marginal profits with central differences at five order pairs per market and scenario.
        cont_s = SecondPeriodS(mk)
        for scenario, cont, claimed in (("N", table, claimed_orders_n), ("S", cont_s, claimed_orders_s)):
            g = gamma if scenario == "N" else max(gamma, 100.0)
            for _ in range(5):
                pa1, pb1 = rng.uniform(mk.p_lo, mk.p_hi, size=2)
                ya, yb = (float(v) * rng.uniform(0.6, 1.1) for v in claimed(mk, g, pa1, pb1))
                floor = _rival_floor(mk, pm.share(pa1, pb1, mk.beta), ya, yb)
                if scenario == "S" and not (g * floor[0] > cont.dominance[0] and g * floor[1] > cont.dominance[1]):
                    continue
                used[scenario] += 1
                h = 1e-6 * mk.hi

                def profit(who, da, db):
                    return float(first_period_profits(mk, cont, g, pa1, pb1, ya + da, yb + db)[who])

                fa, fb = marginal_profits(mk, cont, g, pa1, pb1, ya, yb)
                fd_a = (profit(0, h, 0.0) - profit(0, -h, 0.0)) / (2.0 * h)
                fd_b = (profit(1, 0.0, h) - profit(1, 0.0, -h)) / (2.0 * h)
                scale = mk.p_hi * (1.0 + g)                    # This is the size of a marginal profit before the unit cost.
                worst_marginal = max(worst_marginal, abs(float(fa) - fd_a) / scale, abs(float(fb) - fd_b) / scale)
    record("node_points", 300)
    record("price_game_states", 24)
    record("order_pairs_scenario_N", used["N"])
    record("order_pairs_scenario_S", used["S"])
    record("max_error_node_quadrature", worst_nodes, stable=False)
    record("max_relative_error_tabulated_price", worst_price, stable=False)
    record("max_relative_error_tabulated_profit", worst_value, stable=False)
    record("max_relative_error_tabulated_slope", worst_slope, stable=False)
    record("max_relative_error_marginal_profit", worst_marginal, stable=False)
    assert worst_nodes <= 1e-13 and worst_price <= 1e-10 and worst_value <= 1e-10
    assert worst_slope <= 1e-7 and worst_marginal <= 1e-6
    assert used["N"] == 120 and used["S"] >= 100


# ----------------------------------------------------------------------------- Lemma A.1(a)
@pytest.mark.claims("LA1.a")
def test_lemma_a1a_first_period_inventory_equilibrium_of_scenario_s(record):
    """Lemma A.1(a): for gamma large the first-period inventory subgame of Scenario S has the
    equilibrium y_A = (alpha_A + theta alpha_B) zeta_A - theta alpha_B zeta_B, y_B = alpha_B zeta_B
    with zeta_i = F^-1(1 - c_i / (p_{i,1} + gamma (p_hi - c_i))), and the form is exact.
    Points: 30 markets of `draw_market` (seed 5201), one first-period price pair each,
    uniform on the price box, gamma = 1, 10, 100, 1e3, 1e4, 1e5 and 1e6.
    Computed: at the claimed orders, with the continuation of `SecondPeriodS`, whether gamma
    times each retailer's smallest first-period sales exceeds its dominance number, the best
    deviation found by `primitives.best_response` on 4001 points of [0, 1.5 (mu + sigma)], and
    both marginal profits of the model, whose vanishing detects an error of order 1 / gamma.
    Criterion: the claim holds at a market and gamma if that dominance condition holds, the
    gain is at most 1e-8 p_hi (mu + sigma)(1 + gamma), each best response lies within
    2e-5 (mu + sigma) of the claim and each marginal profit is at most 1e-12 (10 + gamma) c_i.
    Once it holds at a market it must hold at every larger gamma, it must hold at all 30
    markets from gamma = 1e5 on, and it must fail at gamma = 1 at one market or more."""
    rng = np.random.default_rng(5201)
    n = 30
    holds = np.zeros((n, len(GAMMAS_S)), bool)
    worst_gain = worst_dist = worst_foc = 0.0
    for k in range(n):
        mk = draw_market(rng)
        cont = SecondPeriodS(mk)
        pa1, pb1 = rng.uniform(mk.p_lo, mk.p_hi, size=2)
        for j, gamma in enumerate(GAMMAS_S):
            ya, yb = (float(v) for v in claimed_orders_s(mk, gamma, pa1, pb1))
            floor = _rival_floor(mk, pm.share(pa1, pb1, mk.beta), ya, yb)
            pinned = gamma * floor[0] > cont.dominance[0] and gamma * floor[1] > cont.dominance[1]
            gain, dist = _deviation_search(mk, cont, gamma, pa1, pb1, ya, yb)
            fa, fb = marginal_profits(mk, cont, gamma, pa1, pb1, ya, yb)
            foc = max(abs(float(fa)) / mk.ca, abs(float(fb)) / mk.cb) / _foc_tol(gamma)
            holds[k, j] = pinned and gain <= GAIN_TOL and dist <= DIST_TOL and foc <= 1.0
            if j >= len(GAMMAS_S) - 2:
                worst_gain, worst_dist, worst_foc = max(worst_gain, gain), max(worst_dist, dist), max(worst_foc, foc)
        assert np.all(np.diff(holds[k].astype(int)) >= 0), (mk, pa1, pb1, holds[k])    # Once it holds, it keeps holding.
    first = threshold_on_ladder(GAMMAS_S, list(holds.all(axis=0)))
    record("markets", n)
    record("gamma_ladder", list(GAMMAS_S))
    record("points_where_the_claim_holds_by_gamma", [int(v) for v in holds.sum(axis=0)])
    record("holds_at_all_points_from_gamma", first)
    record("tolerance_on_relative_gain_from_deviation", GAIN_TOL)
    record("max_relative_gain_from_deviation_at_top_two_gammas", worst_gain, stable=False)
    record("max_relative_distance_best_response_to_claim_at_top_two_gammas", worst_dist, stable=False)
    record("max_marginal_profit_over_its_rounding_allowance_at_top_two_gammas", worst_foc, stable=False)
    assert first is not None and first <= GAMMAS_S[-2]
    assert not holds[:, 0].all()                               # The ladder starts below the threshold of some point.


@pytest.mark.claims("LA1.a")
def test_lemma_a1a_best_response_iteration_returns_to_the_claimed_orders(record):
    """Uniqueness probe for Lemma A.1(a): alternating best responses from several starts.
    Points: 10 markets of `draw_market` (seed 5202), one first-period price pair each,
    gamma = 1e3 and 1e5, 3 starting pairs per case: 60 runs. A starting order of retailer i
    is uniform on [L_i / gamma, 1.5 (mu + sigma)], with L_i the dominance number of
    `SecondPeriodS`. Below L_i / gamma the rival of a deviating retailer could sell so little
    that it would not charge the upper bound in period 2, and the continuation used here
    would not apply.
    Computed: alternating best replies over [0, 1.5 (mu + sigma)], found from payoff values
    with `argmax_on_interval`, for at most 30 sweeps or until a sweep moves less than
    1e-9 (mu + sigma). The width of the excluded strip is recorded.
    Criterion: L_i / gamma < alpha_i (mu - sigma) for both retailers, every run ends within
    1e-4 (mu + sigma) of the claimed pair in the sum of the two distances, and every rival
    order at which a best reply was evaluated lies above that rival's strip."""
    rng = np.random.default_rng(5202)
    worst, runs, widest_strip, most_sweeps = 0.0, 0, 0.0, 0
    for _ in range(10):
        mk = draw_market(rng)
        cont = SecondPeriodS(mk)
        pa1, pb1 = rng.uniform(mk.p_lo, mk.p_hi, size=2)
        share = pm.share(pa1, pb1, mk.beta)
        upper = 1.5 * mk.hi
        for gamma in (1e3, 1e5):
            claim = tuple(float(v) for v in claimed_orders_s(mk, gamma, pa1, pb1))
            strip = (cont.dominance[0] / gamma, cont.dominance[1] / gamma)
            assert strip[0] < share * mk.lo and strip[1] < (1.0 - share) * mk.lo, (mk, pa1, pb1, gamma)
            widest_strip = max(widest_strip, max(strip) / upper)
            seen = []
            reply_a, reply_b = _best_replies(mk, cont, gamma, pa1, pb1, seen)
            for _ in range(3):
                start = (rng.uniform(strip[0], upper), rng.uniform(strip[1], upper))
                a, b, sweeps = iterate_best_responses(reply_a, reply_b, start, sweeps=30, tol=1e-9 * mk.hi)
                runs += 1
                most_sweeps = max(most_sweeps, sweeps)
                away = (abs(a - claim[0]) + abs(b - claim[1])) / mk.hi
                worst = max(worst, away)
                assert away <= 5.0 * DIST_TOL, (mk, pa1, pb1, gamma, start, (a, b), claim)
            # `seen` alternates between orders of retailer B and orders of retailer A.
            assert min(seen[1::2]) > strip[0] and min(seen[0::2]) > strip[1], (mk, pa1, pb1, gamma)
    record("runs", runs)
    record("widest_excluded_strip_over_order_interval", float(f"{widest_strip:.1g}"))
    record("largest_number_of_sweeps", most_sweeps, stable=False)
    record("max_relative_distance_to_claimed_orders", worst, stable=False)


# ----------------------------------------------------------------------------- Lemma A.2(a)
@pytest.mark.claims("LA2.a")
def test_lemma_a2a_first_period_inventory_equilibrium_of_scenario_n(record):
    """Lemma A.2(a): for gamma large the first-period inventory subgame of Scenario N has an
    equilibrium that equals the stated closed form up to a term of order gamma^-2.
    Points: 16 markets of `draw_market` (seed 5203), one price pair each on the price box, theta
    set to 1 in every fourth market, to 0 in every fourth and to 0.9 theta in the others (theta
    just below 1 is left to the next check), gamma = 10, 30, 100, 300, 1e3, 3e3 and 1e4.
    Computed: with the continuation of `SecondPeriodN`, the solution y* of the model's two
    first-order conditions, e(gamma) = max_i |y_i* - y_i| / (mu + sigma) for the closed form y,
    the order -d log e / d log gamma between neighbouring values, and at gamma = 10, 100, 1e3
    and 1e4 a 1001-point search of [0, 1.5 (mu + sigma)] from y, at 1e4 also from y*.
    Criterion: the conditions hold at y* within 1e-12 (10 + gamma) c_i, e shrinks on every step
    with e > 3e-13 at both ends, the order is at least 1.75 on such steps from gamma = 100 on
    (an error of order 1 / gamma gives 1), with 16 or more such steps in all, and from 1e3 on
    every search passes at every market: table without problem, relative gain at most 1e-8,
    best responses within 2e-5 (mu + sigma)."""
    rng = np.random.default_rng(5203)
    n = 16
    gammas = np.array(GAMMAS_RATE)
    searched = np.zeros((n, len(GAMMAS_SEARCH)), bool)
    worst_gain = worst_dist = sup_scaled = 0.0
    lowest_order, usable_steps = np.inf, 0
    last_order = {"theta = 1": [], "theta < 1": []}
    for k in range(n):
        mk = draw_market(rng)
        mk = replace(mk, theta={0: 1.0, 1: 0.0}.get(k % 4, 0.9 * mk.theta))
        pa1, pb1 = rng.uniform(mk.p_lo, mk.p_hi, size=2)
        share = pm.share(pa1, pb1, mk.beta)
        claims = [tuple(float(v) for v in claimed_orders_n(mk, gamma, pa1, pb1)) for gamma in GAMMAS_RATE]
        reach = min(min(_rival_floor(mk, share, *claim)) for claim in claims)
        cont = SecondPeriodN(mk, 1.001 / (GAMMAS_RATE[0] * reach))                  # The table covers every reachable state.
        errors = []
        for gamma, claim in zip(GAMMAS_RATE, claims):
            error, solution = _error_of_closed_form(mk, cont, gamma, pa1, pb1)
            errors.append(error)
            if gamma in GAMMAS_SEARCH:
                good = not cont.problems
                for pair in (claim, solution) if gamma == GAMMAS_SEARCH[-1] else (claim,):
                    gain, dist = _deviation_search(mk, cont, gamma, pa1, pb1, *pair, grid=1001)
                    good &= gain <= GAIN_TOL and dist <= DIST_TOL
                    if gamma == GAMMAS_SEARCH[-1]:
                        worst_gain, worst_dist = max(worst_gain, gain), max(worst_dist, dist)
                searched[k, GAMMAS_SEARCH.index(gamma)] = good
        errors = np.array(errors)
        orders = -np.diff(np.log(np.maximum(errors, 1e-300))) / np.diff(np.log(gammas))
        usable = (errors[:-1] > ERROR_FLOOR) & (errors[1:] > ERROR_FLOOR)
        asserted = usable & (gammas[:-1] >= 100.0)
        assert np.all(np.diff(errors)[usable] < 0.0), (mk, pa1, pb1, errors)             # Direction: the error shrinks.
        assert np.all(orders[asserted] >= 1.75), (mk, pa1, pb1, errors, orders)       # Rate: the order is about two or more.
        usable_steps += int(asserted.sum())
        if asserted.any():
            last = int(np.flatnonzero(asserted)[-1])
            lowest_order = min(lowest_order, float(orders[asserted].min()))
            sup_scaled = max(sup_scaled, float((gammas ** 2 * errors)[2:last + 2].max()))
            last_order["theta = 1" if mk.theta == 1.0 else "theta < 1"].append(float(orders[last]))
    first = threshold_on_ladder(GAMMAS_SEARCH, list(searched.all(axis=0)))
    record("markets", n)
    record("gamma_ladder", list(GAMMAS_RATE))
    record("gammas_with_search_of_the_whole_order_interval", list(GAMMAS_SEARCH))
    record("points_without_profitable_deviation_by_gamma", [int(v) for v in searched.sum(axis=0)])
    record("no_profitable_deviation_at_all_points_from_gamma", first)
    for label, values in last_order.items():
        if values:
            rounded = sorted({int(round(v)) for v in values})
            record(f"observed_order_on_last_usable_step_rounded_to_integer, {label}", rounded)
            record(f"range_of_observed_order_on_last_usable_step, {label}", [min(values), max(values)], stable=False)
    record("usable_steps_from_gamma_100", usable_steps, stable=False)
    record("lowest_observed_order_from_gamma_100", lowest_order, stable=False)
    record("largest_gamma_squared_times_relative_error_from_gamma_100", sup_scaled, stable=False)
    record("max_relative_gain_from_deviation_at_gamma_1e4", worst_gain, stable=False)
    record("max_relative_distance_best_response_at_gamma_1e4", worst_dist, stable=False)
    assert first is not None and first <= GAMMAS_SEARCH[-2]
    assert usable_steps >= n                                   # Enough steps lie above rounding level to show a rate.


@pytest.mark.claims("LA2.a")
def test_lemma_a2a_error_bound_is_uniform_in_theta_near_one(record):
    """Lemma A.2(a) with the uniformity that Online Appendix A.2 announces for its bounds:
    the error of the closed form is of order gamma^-2 uniformly in theta, including theta
    close to 1, where the error changes regime.
    Points: 8 markets of `draw_market` (seed 5205), one first-period price pair each,
    uniform on the price box, gamma = 300, 1e3 and 3e3, and theta = 1 - l / gamma for
    l = 0, 0.03, 0.1, 0.3, 1, 3, 10 and 30.
    Computed: the scaled error gamma^2 e(gamma), with e as in the previous check, and for each
    gamma its largest value over l. Also recorded: the growth of that maximum, its ratio to
    the value at theta = 1, and how closely the scaled errors at gamma = 1e3 and 3e3 agree at
    fixed l <= 3 where they are ten times above rounding level.
    Criterion: `SecondPeriodN` reports no problem, the first-order conditions hold at y*
    within 1e-12 (10 + gamma) c_i, and the maximum grows by at most 10% plus 3e-14 gamma^2
    from one gamma to the next. An error of order 1 / gamma would multiply it by about 3 at
    each step."""
    rng = np.random.default_rng(5205)
    n = 8
    growth, hump, collapse, compared = [], 0.0, 0.0, 0
    for _ in range(n):
        base = draw_market(rng)
        pa1, pb1 = rng.uniform(base.p_lo, base.p_hi, size=2)
        scaled = np.zeros((len(GAMMAS_UNIFORM), len(LEVELS)))
        for i, gamma in enumerate(GAMMAS_UNIFORM):
            for j, level in enumerate(LEVELS):
                mk = replace(base, theta=1.0 - level / gamma)
                cont = SecondPeriodN(mk, 2.0 / (gamma * mk.lo))                    # The table covers the equilibrium states.
                assert not cont.problems, (mk, cont.problems)
                scaled[i, j] = gamma ** 2 * _error_of_closed_form(mk, cont, gamma, pa1, pb1)[0]
        largest = scaled.max(axis=1)
        for i in (0, 1):
            allowance = 3e-14 * GAMMAS_UNIFORM[i + 1] ** 2
            assert largest[i + 1] <= 1.1 * largest[i] + allowance, (base, pa1, pb1, scaled)
            growth.append(float(largest[i + 1] / largest[i]))
        hump = max(hump, float(largest[-1] / scaled[-1, 0]))
        usable = (scaled[-1] > 10.0 * ERROR_FLOOR * GAMMAS_UNIFORM[-1] ** 2) & (np.array(LEVELS) <= 3.0)
        compared += int(usable.sum())
        collapse = max(collapse, float(np.abs(scaled[-1] / scaled[-2] - 1.0)[usable].max(initial=0.0)))
    record("markets", n)
    record("gammas", list(GAMMAS_UNIFORM))
    record("values_of_gamma_times_one_minus_theta", list(LEVELS))
    record("range_of_growth_of_largest_scaled_error_per_step_of_gamma_to_one_decimal",
           [round(min(growth), 1), round(max(growth), 1)])
    record("range_of_growth_of_largest_scaled_error_per_step_of_gamma", [min(growth), max(growth)], stable=False)
    record("largest_ratio_of_maximal_scaled_error_to_its_value_at_theta_1", hump, stable=False)
    record("entries_compared_between_gamma_1e3_and_3e3", compared, stable=False)
    record("max_relative_change_from_gamma_1e3_to_3e3_at_fixed_level_up_to_3", collapse, stable=False)


@pytest.mark.claims("LA2.a")
def test_lemma_a2a_uniqueness_probes(record):
    """Uniqueness probes for Lemma A.2(a) at gamma = 1e3 (seed 5204).
    Points: probe 1, 6 markets of `draw_market` with theta scaled to 0.8 theta, 3 starting pairs
    uniform on [d, 1.5 (mu + sigma)]^2. Probe 2, 4 markets with theta = 0.5, 0.95, 1 and the
    theta of `draw_market`, 121 values of y_B on [d, 1.5 (mu + sigma)]. One price pair per market.
    d = min(alpha_A, alpha_B, [1/2 - beta (p_hi - p_lo)] / 2) (mu - sigma). Below d total sales
    can approach zero, where the second-period price game leaves its large-gamma regime.
    Computed: best replies A and B over [0, 1.5 (mu + sigma)] from payoff values, continuation
    `SecondPeriodN`. Probe 1 alternates them, at most 60 sweeps, until a sweep moves less than
    1e-7 (mu + sigma), and records the predicted contraction per sweep, which tends to 1 as
    theta tends to 1. Probe 2 evaluates the residual B(A(y_B)) - y_B.
    Criterion: no table problem and every rival order evaluated at least d. Probe 1: fewer than
    60 sweeps, end point within 1e-4 (mu + sigma) of the closed form. Probe 2: residual positive
    at d and negative at 1.5 (mu + sigma), with a change of sign (product of signs at most 0)
    between exactly one pair of neighbours, which encloses the claimed y_B."""
    rng = np.random.default_rng(5204)
    gamma = 1e3
    worst, runs, most_sweeps, largest_factor = 0.0, 0, 0, 0.0
    scans = []
    cases = [(None, "iteration")] * 6 + [(0.5, "scan"), (0.95, "scan"), (1.0, "scan"), (None, "scan")]
    for theta, probe in cases:
        mk = draw_market(rng)
        mk = replace(mk, theta=0.8 * mk.theta if probe == "iteration" else (mk.theta if theta is None else theta))
        pa1, pb1 = rng.uniform(mk.p_lo, mk.p_hi, size=2)
        share = pm.share(pa1, pb1, mk.beta)
        upper = 1.5 * mk.hi
        d = min(share * mk.lo, (1.0 - share) * mk.lo, mk.smallest_share * mk.lo / 2.0)
        cont = SecondPeriodN(mk, 1.001 / (gamma * d))
        assert not cont.problems, (mk, cont.problems)
        claim = tuple(float(v) for v in claimed_orders_n(mk, gamma, pa1, pb1))
        seen = []
        reply_a, reply_b = _best_replies(mk, cont, gamma, pa1, pb1, seen)
        if probe == "iteration":
            k = mk.theta ** 2 * (1.0 - share) / ((1.0 - mk.theta) * (share + mk.theta * (1.0 - share)))
            largest_factor = max(largest_factor, k / (1.0 + k))
            for _ in range(3):
                start = tuple(rng.uniform(d, upper, size=2))
                a, b, sweeps = iterate_best_responses(reply_a, reply_b, start, sweeps=60, tol=1e-7 * mk.hi)
                runs += 1
                most_sweeps = max(most_sweeps, sweeps)
                away = (abs(a - claim[0]) + abs(b - claim[1])) / mk.hi
                worst = max(worst, away)
                assert sweeps < 60, (mk, pa1, pb1, start)
                assert away <= 5.0 * DIST_TOL, (mk, pa1, pb1, start, (a, b), claim)
        else:
            grid = np.linspace(d, upper, 121)
            residual = np.array([reply_b(reply_a(y)) - y for y in grid])
            crossings = np.flatnonzero(np.sign(residual[:-1]) * np.sign(residual[1:]) <= 0.0)
            scans.append(int(crossings.size))
            assert crossings.size == 1, (mk, pa1, pb1, residual)
            assert grid[crossings[0]] <= claim[1] <= grid[crossings[0] + 1], (mk, pa1, pb1, grid[crossings[0]], claim)
            assert residual[0] > 0.0 > residual[-1], (mk, pa1, pb1)
        assert min(seen) >= d, (mk, pa1, pb1)                  # Every sales state stayed inside the tabulated range.
    record("gamma", gamma)
    record("iteration_runs", runs)
    record("largest_predicted_contraction_factor_per_sweep", round(largest_factor, 2))
    record("sign_changes_of_the_fixed_point_residual_per_scanned_market", scans)
    record("largest_number_of_sweeps", most_sweeps, stable=False)
    record("max_relative_distance_to_claimed_orders_after_iteration", worst, stable=False)
