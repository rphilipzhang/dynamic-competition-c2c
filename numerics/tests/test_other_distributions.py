"""The comparisons of Section 4 under other demand distributions.

Section 3.3 states that the authors tested numerically that all results remain
qualitatively the same with other distributions. The code behind that sentence
was not provided. This file is an independent re-implementation of such a test
for the results of Section 4. It is not the authors' experiment, and it bears
on claim N6 only.

For three non-uniform distributions on the support of the uniform one, and for
random regular parameters (`section4.draw_exogenous`), the equilibrium of Lemmas 1
to 3 is evaluated through the quantile function, and expected sales and
two-period profits are integrated from the model primitives. The sample is
small: 48 parameter points, a 41-point grid of theta and four values of gamma.

What is tested is weaker than the propositions
    The quantities come out of numerical integration, so the tests use the
    predicates with a tolerance of `predicates.py`. Their docstrings say what
    each accepts. In particular "non-decreasing" accepts a constant function,
    and "at most one change of sign" accepts a function without any change of
    sign. Proposition 2(c), the cost thresholds of Propositions 5(c2) and
    6(c2), the edge points and Section 5 are not covered.

Statements for gamma large
    In floating point gamma cannot be pushed far, because several quantities
    then vary by less than the rounding error. Patterns of such quantities
    are therefore tested at gamma = 1e3 and 1e4 only in forms that also hold
    below the threshold of the statement, and the number of points at which
    the full pattern is visible is recorded. Comparisons that are decided by
    terms of order gamma are tested at gamma = 1e8.

Propositions 1 to 6 are proved in the paper for the uniform distribution only.
A pattern that fails here would not contradict a theorem of the paper. It
would qualify the sentence of Section 3.3.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from c2c.section4 import Game, claimed_first_period, distributions, draw_exogenous, seeded_rng
from c2c.predicates import (at_most_one_sign_change_from_positive, changes_direction_at_most_once_from_falling,
                        decreasing_overall, falls_then_rises, increasing_overall, nearly_constant, non_decreasing)

THETA = np.linspace(0.0, 1.0, 41)
GAMMAS = (2.0, 1e3, 1e4)
LEADING = 1e8                      # for comparisons that are decided by terms of order gamma
N_POINTS = 16                      # per distribution, half of them with equal market shares
NAMES = ("triangular", "beta(2,5)", "truncated normal")


def curves(prm, dist, gamma):
    out = {s: {k: np.empty(THETA.size) for k in ("ya", "yb", "ra", "rb", "pa", "pb")} for s in "0SN"}
    for k, theta in enumerate(THETA):
        p = replace(prm, theta=float(theta), gamma=gamma)
        for s in "0SN":
            ya, yb, q_a, q_b, a_high = claimed_first_period(p, s, dist.ppf)
            assert a_high and 0 <= q_b <= q_a <= 1
            era, erb = dist.expected_sales(ya, yb, p.aa1, 1 - p.aa1, p.theta)
            payoff_a, payoff_b = Game(p, s, dist).period1_payoffs()
            c = out[s]
            c["ya"][k], c["yb"][k], c["ra"][k], c["rb"][k] = ya, yb, era[0], erb[0]
            c["pa"][k], c["pb"][k] = payoff_a(ya, yb)[0], payoff_b(ya, yb)[0]
    return out


@pytest.fixture(scope="module")
def sample():
    rng = seeded_rng(808)
    points = []
    for name in NAMES:
        for k in range(N_POINTS):
            prm, mu, sigma = draw_exogenous(rng, equal_shares=(k % 2 == 1))
            dist = distributions(mu, sigma)[name]
            points.append((name, prm, {g: curves(prm, dist, g) for g in (*GAMMAS, LEADING)}))
    return points


def _all(sample, predicate, gammas=GAMMAS):
    return [(name, g) for name, prm, by_gamma in sample for g in gammas if not predicate(prm, by_gamma[g])]


@pytest.mark.claims("N6")
def test_order_quantities_and_sales_patterns_under_other_distributions(sample, record):
    """Patterns of the parts of Propositions 1 to 3 that the paper states for every gamma.
    Points: 48 points of `draw_exogenous` (seed 808), 16 for each of the triangular,
    beta(2,5) and truncated normal distributions on [mu - sigma, mu + sigma], every second
    one with equal shares in both periods, 41 values of theta on [0, 1], gamma = 2, 1e3, 1e4.
    Computed: for the benchmark and Scenarios S and N, the orders of `claimed_first_period`
    through the quantile function and expected first-period sales by quadrature.
    Criterion: retailer A has the higher fractile at every evaluation, y^0_A and y^N_A are
    increasing overall, y^S_A is increasing overall at gamma = 2 and non-decreasing at the
    larger values, y^N_B and E[R^N_B] are decreasing overall, y^0_B, y^S_B and E[R^S_B] are
    nearly constant, and y^0_B < y^N_B < y^S_B and E[R^N_B] < E[R^S_B] at every theta. With
    t = 1e-10 (1 + max |v|), "increasing overall" means no step below -t and a total rise
    above t, and "nearly constant" means a range of at most 10 t."""
    def patterns(prm, c, gamma):
        y_s_a = increasing_overall(c["S"]["ya"]) if gamma == GAMMAS[0] else non_decreasing(c["S"]["ya"])
        return (increasing_overall(c["0"]["ya"]) and y_s_a and increasing_overall(c["N"]["ya"])
                and decreasing_overall(c["N"]["yb"]) and nearly_constant(c["0"]["yb"]) and nearly_constant(c["S"]["yb"])
                and bool(np.all(c["0"]["yb"] < c["N"]["yb"]) and np.all(c["N"]["yb"] < c["S"]["yb"]))
                and decreasing_overall(c["N"]["rb"]) and nearly_constant(c["S"]["rb"]) and bool(np.all(c["N"]["rb"] < c["S"]["rb"])))

    failures = [(name, g) for name, prm, by_gamma in sample for g in GAMMAS if not patterns(prm, by_gamma[g], g)]
    record("parameter_points", len(sample))
    record("distributions", list(NAMES))
    record("gammas", list(GAMMAS))
    assert not failures, failures


@pytest.mark.claims("N6")
def test_large_gamma_patterns_under_other_distributions(sample, record):
    """Weak forms of the parts of Propositions 1 and 3 to 6 that the paper states for gamma large.
    Points: the 48 points and 41 values of theta of the previous check, gamma = 1e3, 1e4, 1e8.
    Computed: orders and expected sales as there, and two-period profits from the payoffs of
    `section4.Game`. The number of points at which E[R^N_1] visibly falls and then rises is
    recorded.
    Criterion: at gamma = 1e3 and 1e4, y^S_A - y^N_A and E[R^S_A] - E[R^N_A] change sign at
    most once, from positive to negative, E[R^S_A] is non-decreasing and E[R^N_A] increasing
    overall, E[R^N_1] changes direction at most once, from falling to rising, Pi^S_A is
    non-decreasing, all four profits exceed the benchmark at every theta, Pi^S_B is nearly
    constant and Pi^N_B increasing overall, and where the shares agree within 1e-6 each
    Pi^S_i - Pi^N_i changes sign at most once, from positive to negative. At gamma = 1e8,
    alpha_{A,1} < alpha_{A,2} - 1e-6 gives Pi^S_A < Pi^N_A and Pi^S_B > Pi^N_B at every theta,
    and alpha_{A,1} > alpha_{A,2} + 1e-6 the reverse. Sign checks ignore entries below
    1e-9 (1 + max |d|), and none of the "at most once" checks requires a change to exist."""
    large = GAMMAS[1:]

    def ordering_by_shares(prm, c, key, sign):
        if prm.aa1 < prm.aa2 - 1e-6:
            return bool(np.all(sign * (c["S"][key] - c["N"][key]) < 0))
        if prm.aa1 > prm.aa2 + 1e-6:
            return bool(np.all(sign * (c["S"][key] - c["N"][key]) > 0))
        return True

    def one_change_where_shares_are_equal(prm, c, key):
        return abs(prm.aa1 - prm.aa2) > 1e-6 or at_most_one_sign_change_from_positive(c["S"][key] - c["N"][key])

    checks = {
        "P1 at most one crossing of y_A": lambda prm, c: at_most_one_sign_change_from_positive(c["S"]["ya"] - c["N"]["ya"]),
        "P3a sales of A": lambda prm, c: non_decreasing(c["S"]["ra"]) and increasing_overall(c["N"]["ra"]),
        "P3a at most one crossing of sales of A": lambda prm, c: at_most_one_sign_change_from_positive(c["S"]["ra"] - c["N"]["ra"]),
        "P4 at most one change of direction": lambda prm, c: changes_direction_at_most_once_from_falling(c["N"]["ra"] + c["N"]["rb"]),
        "P5a": lambda prm, c: non_decreasing(c["S"]["pa"]),
        "P5b": lambda prm, c: bool(np.all(c["S"]["pa"] > c["0"]["pa"]) and np.all(c["N"]["pa"] > c["0"]["pa"])),
        "P5c2 weak": lambda prm, c: one_change_where_shares_are_equal(prm, c, "pa"),
        "P6a": lambda prm, c: nearly_constant(c["S"]["pb"]) and increasing_overall(c["N"]["pb"]),
        "P6b": lambda prm, c: bool(np.all(c["S"]["pb"] > c["0"]["pb"]) and np.all(c["N"]["pb"] > c["0"]["pb"])),
        "P6c2 weak": lambda prm, c: one_change_where_shares_are_equal(prm, c, "pb"),
    }
    leading = {
        "P5c1": lambda prm, c: ordering_by_shares(prm, c, "pa", +1),
        "P6c1": lambda prm, c: ordering_by_shares(prm, c, "pb", -1),
    }
    failed = {}
    for group, gammas in ((checks, large), (leading, (LEADING,))):
        for name, predicate in group.items():
            bad = _all(sample, predicate, gammas)
            record(f"{name}: failures", len(bad))
            if bad:
                failed[name] = bad
    for g in large:
        visible = sum(falls_then_rises(by_gamma[g]["N"]["ra"] + by_gamma[g]["N"]["rb"]) for _, _, by_gamma in sample)
        record(f"P4 visibly falls then rises at gamma = {g:g}: points", visible)
    assert not failed, failed
