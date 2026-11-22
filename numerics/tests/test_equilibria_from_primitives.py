"""Lemmas 1, 2, 3 and B.1: the claimed equilibria against payoffs built from the model primitives, and a scan for others.

Nothing here uses the paper's derivations. Each test takes the order
quantities that a lemma claims and builds the retailers' payoffs from the model
primitives of Section 3 (`c2c.primitives`).

Existence (parts L1.eq, L2.first, L2.second and their counterparts)
    Each retailer's whole strategy interval is searched for a profitable
    unilateral deviation. A pass means that no deviation improves a payoff by
    more than 1e-8 relative to the payoff scale and that each best response
    lies within 2e-5 times that scale of the claimed quantity. A relative
    error of 1e-4 in a claimed order quantity fails these tests.

Uniqueness (parts L1.unique, L2.unique, L3.unique, LB1.unique)
    Best responses are single-valued, so (y_A, y_B) is an equilibrium exactly
    when y_B is a fixed point of T(y_B) = BR_B(BR_A(y_B)).
    `section4.scan_fixed_points` evaluates T on the whole strategy interval of
    retailer B and again, more densely, on the range of T, which contains
    every fixed point. A pass means that T(y_B) - y_B is positive at the
    lowest node, negative at the highest, changes sign between exactly one
    pair of neighbouring nodes, and that this pair encloses the claimed y_B
    up to the noise allowance of the scan.
    This is a scan, not a proof: two further equilibria between the same two
    neighbouring nodes would not be seen. The scan is run for the first-period
    game and for the second-period game at a random sales state.

Points
    Regular points come from `section4.draw_exogenous`. Edge points come from
    `section4.draw_edge_exact` and include equality in the price condition A11,
    equal prices, theta at 0 and at 1, gamma at 0.01 and at 1000, and the
    extreme weights of the mixed scenario. `section4.SAMPLED_REGION` states the
    bounds. The lemmas are stated for a general seed-demand distribution, so
    both kinds of test also run under three distributions other than the
    uniform one, on the same support.
"""
from __future__ import annotations

from dataclasses import replace

import pytest

from c2c import primitives as pm

from c2c.section4 import (Game, claimed_benchmark, claimed_first_period, distributions, draw_edge_exact, draw_exogenous,
                   scan_fixed_points, seeded_rng)

GAIN_TOL = 1e-8          # largest admissible payoff gain from a unilateral deviation, relative to payoff scale
DIST_TOL = 2e-5          # largest admissible distance between a best response and the claimed quantity

OTHERS = ("triangular", "beta(2,5)", "truncated normal")
N_UNIFORM = 60           # regular points per test under the uniform distribution
N_OTHER = 6              # regular points per test and per non-uniform distribution
N_EDGE = 30              # edge points per test under the uniform distribution
N_EDGE_OTHER = 1         # edge points per test under one non-uniform distribution

SCAN_UNIFORM = 12        # regular points per scan test under the uniform distribution
SCAN_OTHER = 1           # regular points per scan test and per non-uniform distribution
SCAN_EDGE = 12           # edge points per scan test under the uniform distribution
SCAN_EDGE_OTHER = 1      # edge points per scan test under one non-uniform distribution

FIRST = [pytest.param("S", marks=pytest.mark.claims("L2.first")),
         pytest.param("N", marks=pytest.mark.claims("L3.first")),
         pytest.param("G", marks=pytest.mark.claims("LB1.first"))]
SECOND = [pytest.param("S", marks=pytest.mark.claims("L2.second")),
          pytest.param("N", marks=pytest.mark.claims("L3.second")),
          pytest.param("G", marks=pytest.mark.claims("LB1.second"))]
UNIQUE = [pytest.param("0", marks=pytest.mark.claims("L1.unique")),
          pytest.param("S", marks=pytest.mark.claims("L2.unique")),
          pytest.param("N", marks=pytest.mark.claims("L3.unique")),
          pytest.param("G", marks=pytest.mark.claims("LB1.unique"))]


def _points(seed, regular_uniform, regular_other, edge_uniform, edge_other):
    """Yields (Params, mu, sigma, name of the distribution, distribution, kind).
    Regular points first, then edge points. Within each kind the points under
    the uniform distribution come first. The non-uniform distribution of the
    edge points depends on the seed, so the tests of this file use all three."""
    rng = seeded_rng(seed)
    for k in range(regular_uniform + 3 * regular_other):
        prm, mu, sigma = draw_exogenous(rng)
        name = "uniform" if k < regular_uniform else OTHERS[(k - regular_uniform) % 3]
        yield prm, mu, sigma, name, distributions(mu, sigma)[name], "regular"
    rng = seeded_rng(seed + 50)
    for k in range(edge_uniform + edge_other):
        prm, mu, sigma = draw_edge_exact(rng).params()
        name = "uniform" if k < edge_uniform else OTHERS[(k - edge_uniform + seed) % 3]
        yield prm, mu, sigma, name, distributions(mu, sigma)[name], "edge"


def _cases(seed):
    return _points(seed, N_UNIFORM, N_OTHER, N_EDGE, N_EDGE_OTHER)


def _scan_cases(seed):
    return _points(seed, SCAN_UNIFORM, SCAN_OTHER, SCAN_EDGE, SCAN_EDGE_OTHER)


def _check(gap, scale, worst):
    worst["gain"] = max(worst["gain"], gap["gain"] / scale)
    worst["dist"] = max(worst["dist"], gap["dist"])
    assert gap["gain"] <= GAIN_TOL * scale, gap
    assert gap["dist"] <= DIST_TOL * max(1.0, scale), gap


def _check_fractiles(q_a, q_b, a_high, kind):
    """Both critical fractiles lie in [0, 1] and retailer A's is the higher
    one. At an edge point with equality in A11 the two fractiles coincide, and
    rounding decides which the code treats as the higher, so the ordering is
    then required up to 1e-12 only."""
    if kind == "regular":
        assert a_high and 0 <= q_b <= q_a <= 1, (q_a, q_b)
    else:
        assert 0 <= q_b <= 1 and 0 <= q_a <= 1 and q_a >= q_b - 1e-12, (q_a, q_b)


def _record_counts(record, cases):
    record("regular_points", sum(c[5] == "regular" for c in cases))
    record("edge_points", sum(c[5] == "edge" for c in cases))
    record("distributions", sorted({c[3] for c in cases}))


# ----------------------------------------------------------------------------- existence
@pytest.mark.claims("L1.eq")
def test_benchmark_equilibrium_of_lemma_1(record):
    """Lemma 1: the claimed order quantities of the single-period game without C2C interactions.
    Points: 109 points (seed 101). 78 regular points of `draw_exogenous`, 60 under the uniform
    distribution and 6 under each of the triangular, beta(2,5) and truncated normal ones,
    and 31 edge points of `draw_edge_exact`, 30 uniform and 1 truncated normal. One game at
    the first-period prices of every point and, under the uniform distribution, one more at
    its second-period prices: 199 games.
    Computed: the quantities of `section4.claimed_benchmark` through the quantile function,
    and `primitives.nash_gap` on [0, 1.5 (mu + sigma)] for the payoffs of `section4.Game`
    with scenario "0", built from the primitives.
    Criterion: both critical fractiles lie in [0, 1] with retailer A's the higher one (up to
    1e-12 at edge points), no deviation gains more than 1e-8 mu, and each best response lies
    within 2e-5 max(1, mu) of the claimed quantity."""
    worst = {"gain": 0.0, "dist": 0.0}
    cases = list(_cases(101))
    games = 0
    for prm, mu, sigma, name, dist, kind in cases:
        price_pairs = [(prm.pa1, prm.pb1)] + ([(prm.pa2, prm.pb2)] if name == "uniform" else [])
        for p_a, p_b in price_pairs:
            p = replace(prm, pa1=p_a, pb1=p_b)
            ya, yb, q_a, q_b = claimed_benchmark(p_a, p_b, p.ca, p.cb, p.beta, p.theta, dist.ppf)
            _check_fractiles(q_a, q_b, q_a >= q_b, kind)      # the ordering that A11 guarantees
            payoff_a, payoff_b = Game(p, "0", dist).period1_payoffs()       # scenario "0": no continuation effect
            _check(pm.nash_gap(payoff_a, payoff_b, ya, yb, 1.5 * (mu + sigma)), mu, worst)
            games += 1
    _record_counts(record, cases)
    record("games_checked", games)
    record("tolerance_on_relative_gain_from_deviation", GAIN_TOL)
    record("max_relative_gain_from_deviation", worst["gain"], stable=False)
    record("max_distance_best_response_to_claim", worst["dist"], stable=False)


@pytest.mark.parametrize("scenario", SECOND)
def test_second_period_equilibrium_and_continuation_value(scenario, record):
    """Second period of Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
    Points: 109 points (seed 202), 78 regular (60 uniform, 6 under each other distribution)
    and 31 edge (30 uniform, 1 beta(2,5)). One first-period sales state per point, R_A uniform
    on [0, mu + sigma] and R_B uniform on [0, mu + sigma - R_A].
    Computed: the claimed orders y^0_{i,2} + Z_{i,2}, `primitives.nash_gap` on
    [0, 1.5 (mu + sigma)(1 + gamma)] for the second-period payoffs of `section4.Game`, and
    each retailer's profit there, all from the primitives.
    Criterion: with scale mu (1 + gamma), no deviation gains more than 1e-8 times the scale,
    each best response lies within 2e-5 max(1, scale) of the claim, and each profit differs
    from pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2} by at most 1e-9 times the scale."""
    worst = {"gain": 0.0, "dist": 0.0}
    worst_value = 0.0
    rng = seeded_rng(202)
    cases = list(_cases(202))
    for prm, mu, sigma, name, dist, kind in cases:
        game = Game(prm, scenario, dist)
        pi0_a, pi0_b, *_ = game.period2_value(0.0, 0.0)
        ra1 = rng.uniform(0.0, mu + sigma)                # any feasible sales state
        rb1 = rng.uniform(0.0, mu + sigma - ra1)
        va, vb, ya, yb = game.period2_value(ra1, rb1)
        payoff_a, payoff_b, za, zb = game.period2_payoffs(ra1, rb1)
        _check(pm.nash_gap(payoff_a, payoff_b, ya, yb, game.upper), mu * (1 + prm.gamma), worst)
        err = max(abs(va - pi0_a - (prm.pa2 - prm.ca) * za), abs(vb - pi0_b - (prm.pb2 - prm.cb) * zb))
        worst_value = max(worst_value, err / (mu * (1 + prm.gamma)))
        assert err <= 1e-9 * mu * (1 + prm.gamma)
    _record_counts(record, cases)
    record("max_relative_gain_from_deviation", worst["gain"], stable=False)
    record("max_relative_error_of_continuation_value", worst_value, stable=False)


@pytest.mark.parametrize("scenario", FIRST)
def test_first_period_equilibrium(scenario, record):
    """First period of Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
    Points: 109 points (seed 303), 78 regular (60 uniform, 6 under each other distribution)
    and 31 edge (30 uniform, 1 triangular).
    Computed: the claimed orders and critical fractiles of `section4.claimed_first_period`,
    and `primitives.nash_gap` on [0, 1.5 (mu + sigma)] for the two-period payoffs of
    `section4.Game`, built from the primitives with the continuation
    pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2}.
    Criterion: both fractiles lie in [0, 1] with retailer A's the higher one (up to 1e-12 at
    edge points), and with scale mu (1 + gamma) no deviation gains more than 1e-8 times the
    scale and each best response lies within 2e-5 max(1, scale) of the claim."""
    worst = {"gain": 0.0, "dist": 0.0}
    cases = list(_cases(303))
    for prm, mu, sigma, name, dist, kind in cases:
        ya, yb, q_a, q_b, a_high = claimed_first_period(prm, scenario, dist.ppf)
        _check_fractiles(q_a, q_b, a_high, kind)
        payoff_a, payoff_b = Game(prm, scenario, dist).period1_payoffs()
        _check(pm.nash_gap(payoff_a, payoff_b, ya, yb, 1.5 * (mu + sigma)), mu * (1 + prm.gamma), worst)
    _record_counts(record, cases)
    record("tolerance_on_relative_gain_from_deviation", GAIN_TOL)
    record("max_relative_gain_from_deviation", worst["gain"], stable=False)
    record("max_distance_best_response_to_claim", worst["dist"], stable=False)


# ----------------------------------------------------------------------------- uniqueness
def _require_one_fixed_point(payoff_a, payoff_b, upper, scale, name, claimed_yb, context):
    """Run the scan and assert that it finds one change of sign, from positive
    to negative, between two nodes that enclose the claimed y_B up to the
    noise allowance of the scan. The scan uses
    62 nodes and a best-response grid of 801 under the uniform distribution,
    and 24 nodes and a grid of 101 under the other distributions. Every best
    response is refined by a bounded scalar search after the grid search."""
    coarse, fine, grid = (21, 41, 801) if name == "uniform" else (9, 15, 101)
    scan = scan_fixed_points(payoff_a, payoff_b, upper, scale, coarse, fine, grid)
    assert scan["first_sign"] > 0 > scan["last_sign"], (scan, context)
    assert len(scan["brackets"]) == 1, (scan, context)
    lo, hi = scan["brackets"][0]
    assert lo - scan["noise"] <= claimed_yb <= hi + scan["noise"], (scan, claimed_yb, context)
    return scan["evaluations"], (hi - lo) / scale


@pytest.mark.parametrize("scenario", UNIQUE)
def test_first_period_equilibrium_is_the_only_fixed_point_found_by_a_scan(scenario, record):
    """Uniqueness in the first period of Lemma 1 (case 0), Lemma 2 (case S),
    Lemma 3 (case N) or Lemma B.1 (case G).
    Points: 28 points (seed 404), 15 regular (12 uniform, 1 under each other distribution)
    and 13 edge (12 uniform, 1 truncated normal).
    Computed: `section4.scan_fixed_points` for T(y_B) = BR_B(BR_A(y_B)) of the two-period
    payoffs on [0, 1.5 (mu + sigma)], with 21 coarse and 41 fine nodes and a best-response
    grid of 801 under the uniform distribution, 9, 15 and 101 under the others.
    Criterion: T(y_B) - y_B is positive at the lowest node and negative at the highest, its
    sign changes between exactly one pair of neighbouring nodes, and that pair encloses the
    claimed y_B up to the noise allowance 1e-6 max(mu + sigma, max T). Two equilibria
    between the same two neighbouring nodes would not be seen."""
    cases = list(_scan_cases(404))
    evaluations, widest = 0, 0.0
    for prm, mu, sigma, name, dist, kind in cases:
        _, claimed_yb, *_ = claimed_first_period(prm, scenario, dist.ppf)
        payoff_a, payoff_b = Game(prm, scenario, dist).period1_payoffs()
        n, width = _require_one_fixed_point(payoff_a, payoff_b, 1.5 * (mu + sigma), mu + sigma, name, claimed_yb, (prm, mu, sigma, name))
        evaluations, widest = evaluations + n, max(widest, width)
    _record_counts(record, cases)
    record("evaluations_of_the_composed_best_response", evaluations)
    record("widest_bracket_of_the_fixed_point_relative_to_demand", widest, stable=False)


@pytest.mark.parametrize("scenario", UNIQUE)
def test_second_period_equilibrium_is_the_only_fixed_point_found_by_a_scan(scenario, record):
    """Uniqueness in the second period of Lemma 1 (case 0, the benchmark game
    at the second-period prices), Lemma 2 (case S), Lemma 3 (case N) or Lemma
    B.1 (case G).
    Points: 28 points (seed 505), 15 regular (12 uniform, 1 under each other distribution)
    and 13 edge (12 uniform, 1 beta(2,5)), each with one random first-period sales state
    (seed 405) drawn as in the second-period equilibrium check.
    Computed: `section4.scan_fixed_points` for the composed best-response map of the
    second-period payoffs on [0, 1.5 (mu + sigma)(1 + gamma)], with the nodes and grids of
    the first-period scan.
    Criterion: as in the first-period scan, with the claimed y^0_{B,2} + Z_{B,2} in place of
    y_B: one change of sign, from positive to negative, between two neighbouring nodes that
    enclose the claim up to the noise allowance 1e-6 max(mu + sigma, max T)."""
    rng = seeded_rng(405)
    cases = list(_scan_cases(505))
    evaluations, widest = 0, 0.0
    for prm, mu, sigma, name, dist, kind in cases:
        game = Game(prm, scenario, dist)
        ra1 = rng.uniform(0.0, mu + sigma)
        rb1 = rng.uniform(0.0, mu + sigma - ra1)
        _, _, _, claimed_yb = game.period2_value(ra1, rb1)
        payoff_a, payoff_b, *_ = game.period2_payoffs(ra1, rb1)
        n, width = _require_one_fixed_point(payoff_a, payoff_b, game.upper, mu + sigma, name, claimed_yb, (prm, mu, sigma, name, ra1, rb1))
        evaluations, widest = evaluations + n, max(widest, width)
    _record_counts(record, cases)
    record("evaluations_of_the_composed_best_response", evaluations)
    record("widest_bracket_of_the_fixed_point_relative_to_demand", widest, stable=False)
