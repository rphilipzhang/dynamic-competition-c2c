"""Proposition 7: how second-period order quantities respond to second-period prices.

Proposition 7 describes the shape of each retailer's second-period equilibrium
order quantity, for given first-period sales, as a function of its own
second-period price and of the rival's:

    (a) in the own price it either decreases or has one or two interior local maxima,
    (b) in the rival's price it either increases or first decreases and then increases.

The second-period order quantity is y^0_{i,2} + Z_{i,2}: the benchmark quantity
of Lemma 1 for either ordering of the critical fractiles, plus the C2C-induced
demand. `second_period_orders` below writes it out so that it can be evaluated
on a whole price grid at once. The last test of this file ties that function
to the model: it must return the quantities of `section4.claimed_benchmark`, and
those must be a Nash equilibrium of the second-period game built from the
primitives, for both orderings of the critical fractiles.

The shapes are evaluated in floating point on a grid of 1,501 prices between
the price bounds, for random parameters that satisfy the assumptions of
Section 5 (A10, A12, A13), random first-period sales, both scenarios and both
retailers. The sampler is `section4.draw_bounded_prices`. It draws theta equal to
0 and to 1 with probability 1/8 each, and `section4.SAMPLED_REGION` states its
other bounds. A slope whose absolute value is at most 1e-11 (1 + largest
order quantity on the grid) is ignored.

The proposition is stated for all admissible parameters, so one violation
fails the test.
"""
from __future__ import annotations

import numpy as np
import pytest

from c2c import primitives as pm

from c2c.section4 import Game, Params, claimed_benchmark, draw_bounded_prices, region_summary, seeded_rng

N_POINTS = 4000
GRID = 1501
N_TIE = 300


def second_period_orders(pa, pb, q, scenario, ra1, rb1):
    """(y_{A,2}, y_{B,2}) at second-period prices (pa, pb), vectorised in either price."""
    ca, cb, th, beta, mu, sigma = q["ca"], q["cb"], q["theta"], q["beta"], q["mu"], q["sigma"]
    aa = 0.5 + beta * (pb - pa)
    ab = 1.0 - aa
    za = mu - sigma + 2.0 * sigma * (1.0 - ca / pa)
    zb = mu - sigma + 2.0 * sigma * (1.0 - cb / pb)
    a_high = za >= zb
    ya = np.where(a_high, (aa + th * ab) * za - th * ab * zb, aa * za)
    yb = np.where(a_high, ab * zb, (ab + th * aa) * zb - th * aa * za)
    if scenario == "S":
        return ya + q["gamma"] * ra1, yb + q["gamma"] * rb1
    return ya + aa * q["gamma"] * (ra1 + rb1), yb + ab * q["gamma"] * (ra1 + rb1)


def slope_signs(values):
    d = np.diff(values)
    s = np.sign(np.where(np.abs(d) <= 1e-11 * (1.0 + np.abs(values).max()), 0.0, d))
    return s[s != 0]


def own_price_shape(values):
    """"decreasing" if no slope is positive. Otherwise the number of times the
    slope turns from positive to negative, which is the number of interior
    local maxima. One or two are what part (a) allows. Anything else is "other"."""
    s = slope_signs(values)
    if np.all(s < 0):
        return "decreasing"
    maxima = int(np.sum((s[:-1] > 0) & (s[1:] < 0)))
    return f"{maxima} interior local maxima" if maxima in (1, 2) else "other"


def rival_price_shape(values):
    """"increasing" if no slope is negative, "decreasing then increasing" if
    the slope changes sign exactly once, from negative to positive. Anything
    else is "other"."""
    s = slope_signs(values)
    if np.all(s > 0):
        return "increasing"
    turns = int(np.sum(s[:-1] != s[1:]))
    return "decreasing then increasing" if turns == 1 and s[0] < 0 and s[-1] > 0 else "other"


@pytest.fixture(scope="module")
def census():
    """The shape of every curve: two own-price curves and two rival-price
    curves per point and scenario."""
    rng = seeded_rng(1010)
    own, rival, bad_own, bad_rival = {}, {}, [], []
    ends_rising = theta_zero = theta_one = 0
    for _ in range(N_POINTS):
        q = draw_bounded_prices(rng)
        theta_zero += q["theta"] == 0.0
        theta_one += q["theta"] == 1.0
        grid = np.linspace(q["p_lo"], q["p_hi"], GRID)
        ra1 = rng.uniform(0.0, q["mu"] + q["sigma"])
        rb1 = rng.uniform(0.0, q["mu"] + q["sigma"] - ra1)
        other = rng.uniform(q["p_lo"], q["p_hi"])
        for scenario in ("S", "N"):
            curves_own = (second_period_orders(grid, other, q, scenario, ra1, rb1)[0],      # y_A in p_A
                          second_period_orders(other, grid, q, scenario, ra1, rb1)[1])      # y_B in p_B
            curves_rival = (second_period_orders(other, grid, q, scenario, ra1, rb1)[0],    # y_A in p_B
                            second_period_orders(grid, other, q, scenario, ra1, rb1)[1])    # y_B in p_A
            for v in curves_own:
                shape = own_price_shape(v)
                own[shape] = own.get(shape, 0) + 1
                ends_rising += shape != "other" and slope_signs(v)[-1] > 0
                if shape == "other":
                    bad_own.append((q, scenario, ra1, rb1, other))
            for v in curves_rival:
                shape = rival_price_shape(v)
                rival[shape] = rival.get(shape, 0) + 1
                if shape == "other":
                    bad_rival.append((q, scenario, ra1, rb1, other))
    return {"own": own, "rival": rival, "bad_own": bad_own, "bad_rival": bad_rival, "ends_rising": int(ends_rising),
            "theta_zero": int(theta_zero), "theta_one": int(theta_one)}


def _record_sample(record, census):
    record("curves", 4 * N_POINTS)
    record("points_with_theta_equal_to_0", census["theta_zero"])
    record("points_with_theta_equal_to_1", census["theta_one"])
    record("sampled_region", region_summary("draw_bounded_prices"))


@pytest.mark.claims("P7.a")
def test_proposition_7a_shape_in_the_own_price(census, record):
    """Proposition 7(a), read literally: y_{i,2} as a function of the own second-period price.
    Points: 4,000 points of `draw_bounded_prices` (seed 1010), each with one sales state
    (R_A uniform on [0, mu + sigma], R_B on [0, mu + sigma - R_A]) and one rival price
    uniform on [p_lo, p_hi], Scenarios S and N, both retailers: 16,000 curves on a grid of
    1,501 own prices between the price bounds.
    Computed: the orders of `second_period_orders` (Lemma 1 for either ordering of the
    fractiles plus Z_{i,2}) and the signs of their steps, ignoring steps of absolute value at
    most 1e-11 (1 + largest order on the grid). The number of accepted curves that end with a
    positive step is recorded. The proof implies that there are none.
    Criterion: every curve has no positive step, or its steps turn from positive to negative
    exactly once or exactly twice."""
    _record_sample(record, census)
    for shape, count in sorted(census["own"].items()):
        record(shape, count)
    record("accepted_curves_that_end_with_a_positive_slope", census["ends_rising"])
    assert not census["bad_own"], census["bad_own"][0]


@pytest.mark.claims("P7.b")
def test_proposition_7b_shape_in_the_rival_price(census, record):
    """Proposition 7(b): y_{i,2} as a function of the rival's second-period price.
    Points: the 4,000 points, sales states and fixed prices of the 7(a) check, Scenarios S
    and N, both retailers: 16,000 curves on a grid of 1,501 rival prices.
    Computed: the orders of `second_period_orders` and the signs of their steps, ignoring
    steps of absolute value at most 1e-11 (1 + largest order on the grid).
    Criterion: every curve has no negative step, or its steps are negative first and
    positive afterwards, with exactly one change of sign."""
    _record_sample(record, census)
    for shape, count in sorted(census["rival"].items()):
        record(shape, count)
    assert not census["bad_rival"], census["bad_rival"][0]


@pytest.mark.supports("P7.a", "P7.b")
def test_second_period_orders_of_this_file_are_the_equilibrium_of_the_model(record):
    """Prerequisite of both parts: `second_period_orders` against the model.
    Points: 300 points of `draw_bounded_prices` (seed 1020), each with a pair of
    second-period prices uniform on [p_lo, p_hi] and one sales state drawn as above,
    Scenarios S and N: 600 second-period games.
    Computed: `second_period_orders`, the quantities of `section4.claimed_benchmark` plus the
    C2C-induced demand Z_{i,2}, and `primitives.nash_gap` on [0, 1.5 (mu + sigma)(1 + gamma)]
    for the second-period payoffs of `section4.Game`, built from the primitives.
    Criterion: the orders agree with the claimed ones within 1e-12 relative to the order,
    with scale mu (1 + gamma) no deviation gains more than 1e-8 times the scale and each best
    response lies within 2e-5 max(1, scale) of the order, and retailer B has the higher
    critical fractile at some but not all of the 300 points."""
    rng = seeded_rng(1020)
    worst_gain = worst_tie = 0.0
    b_higher = games = 0
    for _ in range(N_TIE):
        q = draw_bounded_prices(rng)
        pa, pb = rng.uniform(q["p_lo"], q["p_hi"], size=2)
        top = q["mu"] + q["sigma"]
        ra1 = rng.uniform(0.0, top)
        rb1 = rng.uniform(0.0, top - ra1)
        dist = pm.Uniform(q["mu"] - q["sigma"], top)
        prm = Params(pa, pb, pa, pb, q["ca"], q["cb"], q["beta"], q["theta"], q["gamma"])
        y0a, y0b, q_a, q_b = claimed_benchmark(pa, pb, q["ca"], q["cb"], q["beta"], q["theta"], dist.ppf)
        b_higher += q_b > q_a
        scale = q["mu"] * (1 + q["gamma"])
        for scenario in ("S", "N"):
            ya, yb = (float(v) for v in second_period_orders(pa, pb, q, scenario, ra1, rb1))
            game = Game(prm, scenario, dist)
            payoff_a, payoff_b, za, zb = game.period2_payoffs(ra1, rb1)
            worst_tie = max(worst_tie, abs(ya - y0a - za) / ya, abs(yb - y0b - zb) / yb)
            gap = pm.nash_gap(payoff_a, payoff_b, ya, yb, game.upper)
            worst_gain = max(worst_gain, gap["gain"] / scale)
            assert gap["gain"] <= 1e-8 * scale and gap["dist"] <= 2e-5 * max(1.0, scale), (q, pa, pb, scenario, gap)
            games += 1
    record("second_period_games", games)
    record("points_where_retailer_B_has_the_higher_fractile", int(b_higher))
    record("max_relative_difference_to_claimed_benchmark", worst_tie, stable=False)
    record("max_relative_gain_from_deviation", worst_gain, stable=False)
    assert worst_tie <= 1e-12
    assert 0 < b_higher < N_TIE
