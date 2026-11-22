"""Closed forms against the model, and the price game of Figure 1.

Part 1. Prerequisites of the proposition tests. The proposition tests evaluate
the closed forms of `c2c.closed_form`. Three links tie those closed forms to
the model of Section 3.
    (a) The order quantities of `c2c.closed_form` equal the quantities of
        `section4.claimed_first_period`. `test_equilibria_from_primitives.py`
        shows from the primitives that the latter are equilibria.
    (b) The closed-form expected sales and total two-period profits equal the
        sales and profits obtained by integrating the model at those
        quantities.
    (c) The closed-form second-period profit, as a function of the
        first-period sales state, equals the profit of the model at the
        second-period inventory equilibrium.
Links (a) and (b) are checked at regular points, at edge points, and at points
that violate assumption A11, where retailer B has the higher critical fractile
at some of them. The mixed scenario of Online Appendix B is the exception: the
code implements it only for the ordering of Lemma B.1 and returns order
quantities and profits but no expected sales, so only those are compared, at
regular and edge points. Link (c) is checked at regular points whose
second-period prices are redrawn without A11.

Part 2. The numerical study of Section 5.3 (Figure 1) rests on three things
that the paper does not prove in the main text, because assumption A11 is
dropped there: the inventory equilibrium when retailer B has the higher
critical fractile, the payoff matrices of the first-period price game, and the
claim that one price pair is the second-period equilibrium at every sales
state. All three are checked here from the primitives at the parameter values
of Figure 1.
"""
from __future__ import annotations

import warnings
from dataclasses import replace

import pytest

from c2c import closed_form as cf
from c2c import figures as F
from c2c import primitives as pm
from c2c.pricing import pricing_equilibrium

from c2c.section4 import (Game, Params, claimed_first_period, draw_edge_exact, draw_exogenous, draw_without_a11,
                   seeded_rng)

CLOSED_FORMS = {"S": (cf.first_period_s, cf.spfta_t1, cf.spftb_t1), "N": (cf.first_period_n, cf.npfta_t1, cf.npftb_t1)}

N_REGULAR, N_WITHOUT_A11, N_EDGE = 200, 200, 100

# What rests on the equality of the two transcriptions of each scenario. First the part of the lemma whose
# equilibrium test uses `section4.claimed_*` while `test_port_matches_paper.py` ties the paper's text to
# `c2c.closed_form`. Then the parts whose tests evaluate the closed forms.
ON_BENCHMARK = ("L1.eq", "L4.a", "P1.i", "P2.a", "P2.b", "P5.b", "P6.b")
ON_S = ("L2.first", "L4.b", "P1.i", "P1.ii", "P2.a", "P2.b", "P2.c", "P3.a", "P3.b", "P5.a", "P5.b", "P5.c1", "P5.c2",
        "P6.a", "P6.b", "P6.c1", "P6.c2", "F1")
ON_N = ("L3.first", "L4.b", "P1.i", "P1.ii", "P2.a", "P2.b", "P2.c", "P3.a", "P3.b", "P4", "P5.b", "P5.c1", "P5.c2",
        "P6.a", "P6.b", "P6.c1", "P6.c2", "F1")
ON_G = ("LB1.first", "FB1", "N5")
ON_G_PROFITS = ("FB1", "N5")
SALES_AND_PROFITS_S = ("P3.a", "P3.b", "P5.a", "P5.b", "P5.c1", "P5.c2", "P6.a", "P6.b", "P6.c1", "P6.c2", "F1")
SALES_AND_PROFITS_N = ("P3.a", "P3.b", "P4", "P5.b", "P5.c1", "P5.c2", "P6.a", "P6.b", "P6.c1", "P6.c2", "F1")


def _args(prm, mu, sigma):
    return (prm.pa1, prm.pb1, prm.pa2, prm.pb2, prm.theta, prm.ca, prm.cb, prm.beta, mu, sigma, prm.gamma)


def _points(seed, with_points_that_violate_a11=True):
    """Yields (Params, mu, sigma, kind): regular points of `draw_exogenous`,
    then points of `draw_without_a11`, then edge points of `draw_edge_exact`."""
    rng = seeded_rng(seed)
    for _ in range(N_REGULAR):
        yield (*draw_exogenous(rng), "regular")
    if with_points_that_violate_a11:
        for _ in range(N_WITHOUT_A11):
            yield (*draw_without_a11(rng), "without A11")
    rng = seeded_rng(seed + 50)
    for _ in range(N_EDGE):
        yield (*draw_edge_exact(rng).params(), "edge")


def _record_points(record, kinds, b_higher):
    for kind in ("regular", "without A11", "edge"):
        if kind in kinds:
            record(f"points_{kind.replace(' ', '_')}", kinds.count(kind))
    record("points_where_retailer_B_has_the_higher_fractile", int(b_higher))


# ----------------------------------------------------------------------------- part 1
@pytest.mark.parametrize("scenario", [pytest.param("0", marks=pytest.mark.supports(*ON_BENCHMARK)),
                                      pytest.param("S", marks=pytest.mark.supports(*ON_S)),
                                      pytest.param("N", marks=pytest.mark.supports(*ON_N)),
                                      pytest.param("G", marks=pytest.mark.supports(*ON_G))])
def test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities(scenario, record):
    """Link (a): the order quantities of `c2c.closed_form` against those of
    `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the
    LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second
    against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
    Points: seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of
    `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points
    only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
    Computed: y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0),
    `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform
    quantile function.
    Criterion: every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has
    the higher critical fractile at one point or more."""
    worst, kinds, b_higher = 0.0, [], 0
    for prm, mu, sigma, kind in _points(1111, with_points_that_violate_a11=(scenario != "G")):
        dist = pm.Uniform(mu - sigma, mu + sigma)
        a = _args(prm, mu, sigma)
        if scenario == "G":
            ya, yb, *_ = cf.find_general_exo(*a, prm.lam_s, prm.lam_n)
        elif scenario == "N":
            ya, yb, *_ = cf.first_period_n(*a)
        else:
            ya, yb, *_ = cf.first_period_s(*a[:-1], prm.gamma if scenario == "S" else 0.0)
        claimed_ya, claimed_yb, _, _, a_high = claimed_first_period(prm, scenario, dist.ppf)
        worst = max(worst, abs(ya - claimed_ya) / mu, abs(yb - claimed_yb) / mu)
        kinds.append(kind)
        b_higher += not a_high
    _record_points(record, kinds, b_higher)
    record("max_relative_difference", worst, stable=False)
    assert worst <= 1e-12
    assert scenario == "G" or b_higher > 0


@pytest.mark.parametrize("scenario", [
    pytest.param("S", marks=[pytest.mark.claims("L2.profits"), pytest.mark.supports(*SALES_AND_PROFITS_S)]),
    pytest.param("N", marks=[pytest.mark.claims("L3.profits"), pytest.mark.supports(*SALES_AND_PROFITS_N)])])
def test_closed_form_sales_and_profits_equal_the_model(scenario, record):
    """Link (b) for Scenario S (Lemma 2) or Scenario N (Lemma 3).
    Points: 500 points (seed 505), 200 of `draw_exogenous`, 200 of `draw_without_a11` and
    100 of `draw_edge_exact`, under the uniform distribution.
    Computed: at the closed-form orders, expected first-period sales y_i - E[(y_i - D_i)^+]
    and total two-period profits of both retailers from `c2c.closed_form`, and the same
    quantities from the exact integration of `primitives.Uniform` and the payoffs of
    `section4.Game`.
    Criterion: sales differ by at most 1e-11 mu, profits by at most 1e-9 mu (1 + gamma)
    times the largest of the four prices, and retailer B has the higher critical fractile at
    one point or more. The closed-form profits cancel to a much smaller value, so their
    rounding error grows with the terms. Over 117 alternative seeds it reached 7e-11 of the
    scale, at edge points. A wrong term in one of the closed forms changes a profit by far more."""
    worst_sales = worst_profit = 0.0
    kinds, b_higher = [], 0
    first, total_a, total_b = CLOSED_FORMS[scenario]
    for prm, mu, sigma, kind in _points(505):
        dist = pm.Uniform(mu - sigma, mu + sigma)
        payoff_a, payoff_b = Game(prm, scenario, dist).period1_payoffs()
        a = _args(prm, mu, sigma)
        ya, yb, left_a, left_b, _, _, a_high = first(*a)
        era, erb = dist.expected_sales(ya, yb, prm.aa1, 1 - prm.aa1, prm.theta)
        worst_sales = max(worst_sales, abs(ya - left_a - era[0]) / mu, abs(yb - left_b - erb[0]) / mu)
        scale = mu * (1 + prm.gamma) * max(prm.pa1, prm.pb1, prm.pa2, prm.pb2)
        worst_profit = max(worst_profit, abs(total_a(*a) - payoff_a(ya, yb)[0]) / scale, abs(total_b(*a) - payoff_b(ya, yb)[0]) / scale)
        kinds.append(kind)
        b_higher += not a_high
    _record_points(record, kinds, b_higher)
    record("max_relative_error_expected_sales", worst_sales, stable=False)
    record("max_relative_error_profit", worst_profit, stable=False)
    assert worst_sales <= 1e-11 and worst_profit <= 1e-9
    assert b_higher > 0


@pytest.mark.supports(*ON_G_PROFITS)
def test_closed_form_profits_of_the_mixed_scenario_equal_the_model(record):
    """Link (b) for the mixed scenario of Online Appendix B (Lemma B.1).
    Points: 300 points (seed 506), 200 of `draw_exogenous` and 100 of `draw_edge_exact`,
    all of which satisfy A11, because the code implements only the ordering of Lemma B.1.
    Computed: total two-period profits of both retailers at the orders of
    `find_general_exo`, from that function and from the payoffs of `section4.Game`
    (scenario G) integrated exactly under the uniform distribution. The code returns no
    expected sales for this scenario, so sales are not compared.
    Criterion: every difference is at most 1e-9 mu (1 + gamma) max(p_{B,1}, p_{B,2})."""
    worst_profit = 0.0
    kinds = []
    for prm, mu, sigma, kind in _points(506, with_points_that_violate_a11=False):
        dist = pm.Uniform(mu - sigma, mu + sigma)
        payoff_a, payoff_b = Game(prm, "G", dist).period1_payoffs()
        ya, yb, profit_a, profit_b = cf.find_general_exo(*_args(prm, mu, sigma), prm.lam_s, prm.lam_n)
        scale = mu * (1 + prm.gamma) * max(prm.pb1, prm.pb2)
        worst_profit = max(worst_profit, abs(profit_a - payoff_a(ya, yb)[0]) / scale, abs(profit_b - payoff_b(ya, yb)[0]) / scale)
        kinds.append(kind)
    _record_points(record, kinds, 0)
    record("max_relative_error_profit", worst_profit, stable=False)
    assert worst_profit <= 1e-9


@pytest.mark.parametrize("scenario", [
    pytest.param("S", marks=[pytest.mark.claims("L2.profits"), pytest.mark.supports("F1")]),
    pytest.param("N", marks=[pytest.mark.claims("L3.profits"), pytest.mark.supports("F1")])])
def test_second_period_profit_function_equals_the_model(scenario, record):
    """Link (c) for Scenario S or Scenario N: the second-period profit that the appendix
    states and that the price game uses, as a function of prices and first-period sales.
    Points: 400 points of `draw_exogenous` (seed 909) with p_{A,2} and p_{B,2} redrawn
    independently on [1.05 c_B, 4 c_B], so that A11 is not imposed, and beta reduced to at
    most 0.45 / |p_{B,2} - p_{A,2}|. One sales state per point, R_A uniform on
    [0, mu + sigma] and R_B uniform on [0, mu + sigma - R_A].
    Computed: `closed_form.period2_profit`, and the profits that `section4.Game` computes
    from the primitives at the orders y^0_{i,2} + Z_{i,2}.
    Criterion: each difference is at most 1e-11 mu (1 + gamma) p_{i,2}, and
    c_A / p_{A,2} > c_B / p_{B,2} at one point or more."""
    rng = seeded_rng(909)
    worst, mirrored, n = 0.0, 0, 400
    for _ in range(n):
        prm, mu, sigma = draw_exogenous(rng, scenario)
        pa2 = rng.uniform(prm.cb * 1.05, prm.cb * 4.0)                       # above both costs, no ordering imposed
        pb2 = rng.uniform(prm.cb * 1.05, prm.cb * 4.0)
        beta = min(prm.beta, 0.45 / max(abs(pb2 - pa2), 1e-9))
        prm = replace(prm, pa2=pa2, pb2=pb2, beta=beta)
        dist = pm.Uniform(mu - sigma, mu + sigma)
        ra1 = rng.uniform(0.0, mu + sigma)
        rb1 = rng.uniform(0.0, mu + sigma - ra1)
        va, vb, *_ = Game(prm, scenario, dist).period2_value(ra1, rb1)
        ca_, cb_ = cf.period2_profit(pa2, pb2, prm.theta, prm.ca, prm.cb, beta, mu, sigma, scenario, prm.gamma, ra1, rb1)
        mirrored += prm.ca / pa2 > prm.cb / pb2
        worst = max(worst, abs(ca_ - va) / (mu * (1 + prm.gamma) * pa2), abs(cb_ - vb) / (mu * (1 + prm.gamma) * pb2))
    record("parameter_points", n)
    record("points_where_retailer_B_has_the_higher_fractile", int(mirrored))
    record("max_relative_error", worst, stable=False)
    assert worst <= 1e-11 and mirrored > 0


# ----------------------------------------------------------------------------- part 2
def _figure1_points(thetas):
    p = F.FIG1_PARAMS
    for panel, (_, ca, gamma) in F.FIG1_PANELS.items():
        for theta in thetas:
            for scenario in ("S", "N"):
                with warnings.catch_warnings():
                    warnings.simplefilter("error")           # an ambiguous continuation would be a failure
                    res = pricing_equilibrium(scenario, p["prices"], float(theta), ca, p["cb"], p["beta"],
                                              p["mu"], p["sigma"], gamma)
                yield panel, float(theta), scenario, ca, gamma, res


@pytest.mark.claims("F1")
def test_figure_1_payoff_matrices_equal_the_model(record):
    """Figure 1: the payoff matrices of the first-period price game.
    Points: the 44 parameter points of Figure 1 (4 panels, 11 values of theta), Scenarios S
    and N, and the 4 first-period price pairs of {2, 4}: 352 cells.
    Computed: `pricing.pricing_equilibrium` with warnings turned into errors, and at its
    second-period prices the two-period profits from the primitives (`section4.Game`) at the
    orders of `section4.claimed_first_period`, for either ordering of the fractiles.
    Criterion: no warning, both fractiles in [0, 1] in every cell, every payoff of the solver
    within 1e-9 (absolute) of the model's, and retailer B has the higher fractile in one cell
    or more."""
    p = F.FIG1_PARAMS
    dist = pm.Uniform(p["mu"] - p["sigma"], p["mu"] + p["sigma"])
    worst, cells, mirrored = 0.0, 0, 0
    for panel, theta, scenario, ca, gamma, res in _figure1_points(F.FIG1_THETA):
        pa2, pb2 = res["period2_prices"]
        for i, pa1 in enumerate(p["prices"]):
            for j, pb1 in enumerate(p["prices"]):
                prm = Params(pa1, pb1, pa2, pb2, ca, p["cb"], p["beta"], theta, gamma)
                ya, yb, q_a, q_b, a_high = claimed_first_period(prm, scenario, dist.ppf)
                assert 0 <= min(q_a, q_b) and max(q_a, q_b) <= 1
                mirrored += not a_high
                payoff_a, payoff_b = Game(prm, scenario, dist).period1_payoffs()
                err = max(abs(res["payoff_a"][i, j] - payoff_a(ya, yb)[0]), abs(res["payoff_b"][i, j] - payoff_b(ya, yb)[0]))
                worst = max(worst, err)
                cells += 1
    record("payoff_cells_compared", cells)
    record("cells_where_retailer_B_has_the_higher_fractile", int(mirrored))
    record("max_abs_error", worst, stable=False)
    assert worst <= 1e-9
    assert mirrored > 0


@pytest.mark.claims("F1")
def test_figure_1_inventory_equilibria_hold_in_the_model(record):
    """Figure 1: the first-period inventory equilibria behind the payoff matrices, including
    the price pairs that violate assumption A11.
    Points: the 4 panels of Figure 1 at theta = 0.01, 0.5 and 0.99, Scenarios S and N, and
    the 4 first-period price pairs of {2, 4}: 96 inventory games.
    Computed: the orders of `section4.claimed_first_period` at the second-period prices of
    `pricing.pricing_equilibrium`, and `primitives.nash_gap` on [0, 1.5 (mu + sigma)] for the
    two-period payoffs of `section4.Game`, built from the primitives.
    Criterion: the solver issues no warning, and in every game no deviation gains more than
    1e-7 and each best response lies within 2e-5 of the claimed order, both absolute."""
    p = F.FIG1_PARAMS
    dist = pm.Uniform(p["mu"] - p["sigma"], p["mu"] + p["sigma"])
    worst_gain = worst_dist = 0.0
    games = 0
    for panel, theta, scenario, ca, gamma, res in _figure1_points((0.01, 0.5, 0.99)):
        pa2, pb2 = res["period2_prices"]
        for pa1 in p["prices"]:
            for pb1 in p["prices"]:
                prm = Params(pa1, pb1, pa2, pb2, ca, p["cb"], p["beta"], theta, gamma)
                ya, yb, *_ = claimed_first_period(prm, scenario, dist.ppf)
                payoff_a, payoff_b = Game(prm, scenario, dist).period1_payoffs()
                gap = pm.nash_gap(payoff_a, payoff_b, ya, yb, 1.5 * (p["mu"] + p["sigma"]))
                worst_gain, worst_dist = max(worst_gain, gap["gain"]), max(worst_dist, gap["dist"])
                games += 1
    record("inventory_games_checked", games)
    record("max_gain_from_deviation", worst_gain, stable=False)
    record("max_distance_best_response_to_claim", worst_dist, stable=False)
    assert worst_gain <= 1e-7 and worst_dist <= 2e-5


@pytest.mark.claims("F1")
def test_figure_1_second_period_prices_are_an_equilibrium_at_every_sales_state(record):
    """Figure 1: the solver's second-period price pair is the equilibrium whatever the
    first-period sales.
    Points: the 4 panels of Figure 1 at theta = 0.01, 0.3, 0.6 and 0.99, Scenarios S and N
    (32 cases), the 10 first-period sales states listed in the code, among them the corners
    (0, 0), (15, 0) and (0, 15) of the sales triangle, and the 4 price pairs of {2, 4}.
    Computed: second-period profits of both retailers from the primitives (`section4.Game`)
    at the orders y^0_{i,2} + Z_{i,2}, and at each state the price pairs from which no
    unilateral price change gains more than 1e-9.
    Criterion: in each case the solver runs without warning, its pair is such a pair at all
    10 states, and it is the only price pair that is."""
    p = F.FIG1_PARAMS
    lo, hi = p["mu"] - p["sigma"], p["mu"] + p["sigma"]
    dist = pm.Uniform(lo, hi)
    states = [(0.0, 0.0), (hi, 0.0), (0.0, hi), (hi / 2, hi / 2), (hi / 3, hi / 3), (hi / 4, hi / 2),
              (hi / 2, hi / 4), (0.1 * hi, 0.1 * hi), (0.6 * hi, 0.1 * hi), (0.1 * hi, 0.6 * hi)]
    prices = p["prices"]
    checked = 0
    for panel, theta, scenario, ca, gamma, res in _figure1_points((0.01, 0.3, 0.6, 0.99)):
        star = res["period2_prices"]
        always = {(a, b): True for a in prices for b in prices}
        for ra1, rb1 in states:
            value = {}
            for pa2 in prices:
                for pb2 in prices:
                    prm = Params(prices[0], prices[0], pa2, pb2, ca, p["cb"], p["beta"], theta, gamma)
                    game = Game(prm, scenario, dist)
                    va, vb, ya, yb = game.period2_value(ra1, rb1)
                    value[(pa2, pb2)] = (va, vb)
            for (pa2, pb2) in always:
                is_eq = (all(value[(pa2, pb2)][0] >= value[(q, pb2)][0] - 1e-9 for q in prices)
                         and all(value[(pa2, pb2)][1] >= value[(pa2, q)][1] - 1e-9 for q in prices))
                always[(pa2, pb2)] &= is_eq
            checked += 1
        assert always[star], (panel, theta, scenario, star)
        assert sum(always.values()) == 1, (panel, theta, scenario, always)
    record("price_games_solved", checked)


@pytest.mark.claims("F1")
def test_second_period_inventory_equilibrium_for_all_price_pairs_of_figure_1(record):
    """Figure 1: the second-period inventory equilibrium y^0_{i,2} + Z_{i,2} that the
    profits above use, at every price pair, including pairs at which retailer B has the
    higher critical fractile.
    Points: (c_A, gamma) = (0.10, 0.7) and (0.95, 2.0), Scenarios S and N, theta = 0.01,
    0.5 and 0.99, the 4 second-period price pairs of {2, 4}, and the sales state
    (R_A, R_B) = (5, 3.75): 48 games.
    Computed: `primitives.nash_gap` on [0, 1.5 (mu + sigma)(1 + gamma)] for the
    second-period payoffs of `section4.Game` at the claimed orders.
    Criterion: no unilateral deviation gains more than 1e-7 (absolute) in any game."""
    p = F.FIG1_PARAMS
    lo, hi = p["mu"] - p["sigma"], p["mu"] + p["sigma"]
    dist = pm.Uniform(lo, hi)
    worst_gain = 0.0
    games = 0
    for ca, gamma in ((0.10, 0.7), (0.95, 2.0)):
        for scenario in ("S", "N"):
            for theta in (0.01, 0.5, 0.99):
                for pa2 in p["prices"]:
                    for pb2 in p["prices"]:
                        prm = Params(2.0, 2.0, pa2, pb2, ca, p["cb"], p["beta"], theta, gamma)
                        game = Game(prm, scenario, dist)
                        _, _, ya, yb = game.period2_value(hi / 3, hi / 4)
                        payoff_a, payoff_b, *_ = game.period2_payoffs(hi / 3, hi / 4)
                        gap = pm.nash_gap(payoff_a, payoff_b, ya, yb, game.upper)
                        worst_gain = max(worst_gain, gap["gain"])
                        games += 1
    record("inventory_games_checked", games)
    record("max_gain_from_deviation", worst_gain, stable=False)
    assert worst_gain <= 1e-7
