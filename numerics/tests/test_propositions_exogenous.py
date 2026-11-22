"""Lemma 4 and Propositions 1 to 6, part by part, in exact rational arithmetic, and statement N8.

Each test checks one part of one statement and is marked with the ID of that
part. The quantities are the closed forms of `c2c.closed_form`.
`test_port_matches_paper.py` shows that these are the paper's formulas, and
`test_profits_and_price_game.py` shows
that they are the equilibrium quantities, expected sales and profits of the
model.

How signs are decided
    The closed forms use only the four arithmetic operations. They are
    evaluated at parameter points whose coordinates are rational numbers
    (`fractions.Fraction`), so every comparison below is exact. No tolerance
    is used anywhere in this file. "Increasing" means strictly increasing and
    "does not depend on theta" means equal as rational numbers.

Where the points come from
    N_REGULAR points of `section4.draw_exogenous_exact` and N_EDGE points of
    `section4.draw_edge_exact`. The second sampler puts points on the edges of
    the region that the assumptions allow, among them equality in the price
    condition A11. Two thirds of the points have the same market shares in
    both periods. `section4.SAMPLED_REGION` states the bounds of both samplers.
    Parts P5.c2 and P6.c2 make a statement only about points with equal shares
    whose cost difference is on one side of a threshold. Their tests therefore
    add further points of the same two samplers that satisfy that condition.

The grid of theta
    Twenty-one equally spaced values from 0 to 1, the values 1 - t / gamma for
    t from 1/100 to 1000, and two values at a distance delta from 0 and from 1,
    with delta below 1e-30. For large gamma several statements change within a
    distance of order 1 / gamma from theta = 1. The values 1 - t / gamma
    resolve that layer. The two values next to the end points give the sign of
    the slope there. A change of sign or of direction between two neighbouring
    nodes of this grid is seen. Two changes between the same two nodes are not.

Two kinds of statements
    "for all parameters"   The part must hold at every point and at every gamma
                           on the ladder GAMMAS. One counterexample fails the test.
    "for gamma large"      The paper asserts a threshold without giving its
                           value. The part must hold at every point at the two
                           highest rungs of the ladder, 1e50 and 1e60. The test
                           records, for the regular and for the edge points
                           separately, the lowest rung from which the part holds
                           at every point and at every higher rung. A point at
                           which the part fails below that rung is not a
                           counterexample. This probes the statement in the
                           limit. It does not prove it.

Statements that hold only weakly on the boundary of A11
    Where the price condition A11 holds with equality, some quantities that
    the paper calls increasing do not depend on theta at all. The tests encode
    the exact truth: strictly increasing where A11 is strict, and exactly
    constant where it binds. The docstrings of the tests of P1.i, P3.a and P5.a
    say which quantity is constant in which case.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Fr

import numpy as np
import pytest

from c2c import closed_form as cf
from c2c import paper

from c2c.section4 import ExactPoint, draw_edge_exact, draw_exogenous_exact, edge_census, region_summary, seeded_rng
from c2c.predicates import constant, increments, sign_runs, strictly_decreasing, strictly_increasing

N_REGULAR = 120                     # points of draw_exogenous_exact
N_EDGE = 90                         # points of draw_edge_exact
N_FURTHER = 60                      # further regular points per part for P5.c2 and P6.c2, and half as many edge points
GAMMAS = (Fr(1, 20), Fr(1), Fr(10), Fr(100), Fr(10**3), Fr(10**4), Fr(10**6), Fr(10**9), Fr(10**12),
          Fr(10**18), Fr(10**50), Fr(10**60))
TOP = GAMMAS[-2:]                   # "gamma large" for the purpose of these tests
BASE_THETA = tuple(Fr(k, 20) for k in range(21))
LAYER = (Fr(1, 100), Fr(1, 10), Fr(1, 2), Fr(1), Fr(2), Fr(5), Fr(10), Fr(100), Fr(1000))

ALL_PARTS = ("L4.a", "L4.b", "P1.i", "P1.ii", "P2.a", "P2.b", "P2.c", "P3.a", "P3.b", "P4",
             "P5.a", "P5.b", "P5.c1", "P5.c2", "P6.a", "P6.b", "P6.c1", "P6.c2")


def theta_grid(gamma) -> list:
    """The nodes of theta for one gamma, in increasing order. The first node is
    0, the second is delta, the last but one is 1 - delta and the last is 1."""
    delta = Fr(1, 10**30) / (1 + gamma)
    nodes = set(BASE_THETA) | {delta, 1 - delta} | {1 - t / gamma for t in LAYER if t < gamma}
    return sorted(nodes)


def _spread(value, n) -> list:
    """A list of n values. A closed form that does not contain theta returns a
    single number, which is then the value at every node."""
    return list(value) if isinstance(value, np.ndarray) else [value] * n


def curves(pt: ExactPoint, gamma) -> dict:
    """Every quantity of Lemma 4 and Propositions 1 to 6 on the grid of theta,
    for the benchmark ("0"), Scenario S and Scenario N, as exact numbers.

    ya, yb   first-period order quantities       ra, rb   expected first-period sales
    pa, pb   total two-period profits            za, zb   critical values zeta_A, zeta_B
    a_high   the code's own decision that retailer A has the higher critical fractile
    """
    theta = theta_grid(gamma)
    n = len(theta)
    a = (pt.pa1, pt.pb1, pt.pa2, pt.pb2, np.array(theta, dtype=object), pt.ca, pt.cb, pt.beta, pt.mu, pt.sigma)
    out = {"theta": theta}
    for name, first, g in (("0", cf.first_period_s, Fr(0)), ("S", cf.first_period_s, gamma), ("N", cf.first_period_n, gamma)):
        ya, yb, left_a, left_b, za, zb, a_high = first(*a, g)
        out[name] = {"ya": _spread(ya, n), "yb": _spread(yb, n), "ra": _spread(ya - left_a, n), "rb": _spread(yb - left_b, n),
                     "za": _spread(za, n), "zb": _spread(zb, n), "a_high": a_high}
    out["0"]["pa"], out["0"]["pb"] = _spread(cf.spfta_t1(*a, Fr(0)), n), _spread(cf.spftb_t1(*a, Fr(0)), n)
    out["S"]["pa"], out["S"]["pb"] = _spread(cf.spfta_t1(*a, gamma), n), _spread(cf.spftb_t1(*a, gamma), n)
    out["N"]["pa"], out["N"]["pb"] = _spread(cf.npfta_t1(*a, gamma), n), _spread(cf.npftb_t1(*a, gamma), n)
    return out


def second_period_benchmark(pt: ExactPoint) -> dict:
    """The benchmark order quantities at the second-period prices on the base
    grid of theta. By Lemmas 2 and 3 these are the second-period orders of
    Scenarios S and N net of the C2C-induced demand."""
    a = (pt.pa2, pt.pb2, pt.pa2, pt.pb2, np.array(BASE_THETA, dtype=object), pt.ca, pt.cb, pt.beta, pt.mu, pt.sigma, Fr(0))
    ya, yb, *_ = cf.first_period_s(*a)
    n = len(BASE_THETA)
    return {"ya": _spread(ya, n), "yb": _spread(yb, n)}


# ----------------------------------------------------------------------------- expressions taken from the proofs
# Proof of Proposition 5, case alpha_{A,1} = alpha_{A,2}: at theta = 1 the fourth derivative of h_A in gamma
# "has the same sign as" the expression below, and h_A has the sign of Pi^S_A - Pi^N_A. For gamma large the
# difference of the profits at theta = 1 is therefore negative exactly when the expression is negative,
# which the proof writes as c_B > c_B-bar.
P5_SIGN_AT_THETA_ONE = (r"-2 \alpha_{A,1} c_{A}^2 p_{B,1}+\alpha_{B,1} c_{A} p_{A,1} p_{B,2}+2 \alpha_{A,1} c_{A} p_{A,2} p_{B,1} "
                        r"- c_B p_{A,1} (\alpha_{A,1} p_{A,2}-(2 \alpha_{A,1} -1) c_A)")
P5_THRESHOLD_SENTENCE = r"\frac{\partial^4 h_A(1,\gamma)}{\partial \gamma^4} <0$ if $c_B > \overline{c}_B"


def p5_sign_at_theta_one(pt: ExactPoint):
    a, b = pt.aa1, 1 - pt.aa1
    return (-2 * a * pt.ca**2 * pt.pb1 + b * pt.ca * pt.pa1 * pt.pb2 + 2 * a * pt.ca * pt.pa2 * pt.pb1
            - pt.cb * pt.pa1 * (a * pt.pa2 - (2 * a - 1) * pt.ca))


# Proof of Proposition 6, case alpha_{B,1} = alpha_{B,2}: at theta = 0 the second derivative of h_B in gamma is a
# positive factor times the bracket below, and h_B has the sign of Pi^S_B - Pi^N_B. For gamma large the difference
# of the profits at theta = 0 is therefore positive exactly when the bracket is positive, which the proof obtains
# for a cost difference below a threshold.
P6_SIGN_AT_THETA_ZERO = (r"\frac{\partial^2 h_B(0, \gamma)}{\partial \gamma^2} = (1-\alpha_{A,1} ) \alpha_{A,1} \sigma "
                         r"[-2 c_B^2 (p_{A,2}-c_A)^2 \alpha_{A,2}^2 -2 c_A^2 (p_{B,2}-c_B)^2 \alpha_{A,2} + 2 c_A^2 (p_{B,2}-c_B)^2]")


def p6_sign_at_theta_zero(pt: ExactPoint):
    a = pt.aa2
    return (-2 * pt.cb**2 * (pt.pa2 - pt.ca)**2 * a**2 - 2 * pt.ca**2 * (pt.pb2 - pt.cb)**2 * a
            + 2 * pt.ca**2 * (pt.pb2 - pt.cb)**2)


def quoted(result: str, latex: str) -> None:
    """Assert that a LaTeX string occurs verbatim in the LaTeX source of the paper.
    The first argument names the result the string comes from, for the reader."""
    paper.assert_quoted(latex)


# ----------------------------------------------------------------------------- the parts, decided exactly
def _first_failure(*checks) -> str:
    """Each check is a pair (condition, description). Returns "" if every
    condition holds and the description of the first one that fails otherwise."""
    for holds, description in checks:
        if not holds:
            return description
    return ""


def _crossing(difference) -> str:
    """Positive at theta = 0, negative at theta = 1, exactly one change of sign."""
    return _first_failure((difference[0] > 0, "the difference is not positive at theta = 0"),
                          (difference[-1] < 0, "the difference is not negative at theta = 1"),
                          (sign_runs(difference) == "+-", f"the signs along theta are {sign_runs(difference)!r}, not '+-'"))


def _increasing_or_constant(values, binding: bool, name: str) -> str:
    """Strictly increasing where A11 is strict, exactly constant where it binds."""
    if binding:
        return "" if constant(values) else f"{name} is not constant in theta although A11 binds"
    return "" if strictly_increasing(values) else f"{name} is not strictly increasing in theta"


def verdicts(pt: ExactPoint, gamma, c: dict) -> dict:
    """For one point and one gamma: "" if the part holds as stated, a
    description of the first violation otherwise, and None if the part makes no
    statement about this point."""
    Z, S, N = c["0"], c["S"], c["N"]
    a1, a2 = pt.aa1, pt.aa2
    both = pt.binds1 and pt.binds2                          # A11 holds with equality in both periods
    lo, hi = pt.mu - pt.sigma, pt.mu + pt.sigma
    v = {}

    v["region"] = _first_failure(
        (Z["a_high"] and S["a_high"] and N["a_high"], "the code does not place retailer A's fractile above retailer B's"),
        (all(lo <= zb <= za <= hi for s in (Z, S, N) for za, zb in zip(s["za"], s["zb"])),
         "a critical value leaves the support of the seed demand or zeta_A < zeta_B"))

    def per_share(s):                                       # y_A / alpha_A - y_B / alpha_B at every node
        return [ya / a1 - yb / (1 - a1) for ya, yb in zip(s["ya"], s["yb"])]

    e0, eS, eN = per_share(Z), per_share(S), per_share(N)
    v["L4.a"] = _first_failure(
        (all(e >= 0 for e in e0), "y^0_A / alpha_A < y^0_B / alpha_B in period 1"),
        (all(e == 0 for e in e0) if pt.binds1 else all(e > 0 for e in e0), "equality in period 1 does not coincide with equality in A11"))
    v["L4.b"] = _first_failure(
        (all(e >= 0 for e in eS), "y^S_A / alpha_A < y^S_B / alpha_B in period 1"),
        (all(e >= 0 for e in eN), "y^N_A / alpha_A < y^N_B / alpha_B in period 1"),
        (all(e == 0 for e in eS) if both else all(e > 0 for e in eS), "Scenario S: equality does not coincide with equality in A11 in both periods"),
        (all(e > 0 for e in eN), "Scenario N: the inequality is not strict"))

    v["P1.i"] = (_increasing_or_constant(Z["ya"], pt.binds1, "y^0_A") or _increasing_or_constant(S["ya"], both, "y^S_A")
                 or ("" if strictly_increasing(N["ya"]) else "y^N_A is not strictly increasing in theta"))
    d = [s - n for s, n in zip(S["ya"], N["ya"])]
    v["P1.ii"] = _crossing(d)
    v["P1.ii every gamma"] = _first_failure((d[0] > 0, "y^S_A <= y^N_A at theta = 0"),
                                            (sign_runs(d) in ("+", "+-"), f"the signs of y^S_A - y^N_A along theta are {sign_runs(d)!r}"))

    v["P2.a"] = _first_failure((strictly_decreasing(N["yb"]), "y^N_B is not strictly decreasing in theta"),
                               (constant(Z["yb"]), "y^0_B depends on theta"), (constant(S["yb"]), "y^S_B depends on theta"))
    v["P2.b"] = _first_failure((all(z < n for z, n in zip(Z["yb"], N["yb"])), "y^0_B >= y^N_B at some theta"),
                               (all(n < s for n, s in zip(N["yb"], S["yb"])), "y^N_B >= y^S_B at some theta"))

    d = [s - n for s, n in zip(S["ra"], N["ra"])]
    v["P3.a"] = (_increasing_or_constant(S["ra"], both, "E[R^S_A]")
                 or ("" if strictly_increasing(N["ra"]) else "E[R^N_A] is not strictly increasing in theta")
                 or _crossing(d))
    v["P3.a every gamma"] = _first_failure((d[0] > 0, "E[R^S_A] <= E[R^N_A] at theta = 0"),
                                           (sign_runs(d) in ("+", "+-"), f"the signs of E[R^S_A] - E[R^N_A] along theta are {sign_runs(d)!r}"))
    v["P3.a crossing"] = _crossing(d)
    v["P3.b"] = _first_failure((strictly_decreasing(N["rb"]), "E[R^N_B] is not strictly decreasing in theta"),
                               (constant(S["rb"]), "E[R^S_B] depends on theta"),
                               (all(n < s for n, s in zip(N["rb"], S["rb"])), "E[R^N_B] >= E[R^S_B] at some theta"))

    total = [ra + rb for ra, rb in zip(N["ra"], N["rb"])]
    steps = increments(total)
    v["P4"] = _first_failure((steps[0] < 0, "E[R^N_1] does not fall at theta = 0"), (steps[-1] > 0, "E[R^N_1] does not rise at theta = 1"),
                             (sign_runs(steps) == "-+", f"the directions of E[R^N_1] along theta are {sign_runs(steps)!r}, not '-+'"))

    v["P5.a"] = _increasing_or_constant(S["pa"], both, "Pi^S_A")
    v["P5.b"] = _first_failure((all(s > z for s, z in zip(S["pa"], Z["pa"])), "Pi^S_A <= Pi^0_A at some theta"),
                               (all(n > z for n, z in zip(N["pa"], Z["pa"])), "Pi^N_A <= Pi^0_A at some theta"))
    v["P6.a"] = _first_failure((constant(S["pb"]), "Pi^S_B depends on theta"),
                               (strictly_increasing(N["pb"]), "Pi^N_B is not strictly increasing in theta"))
    v["P6.b"] = _first_failure((all(s > z for s, z in zip(S["pb"], Z["pb"])), "Pi^S_B <= Pi^0_B at some theta"),
                               (all(n > z for n, z in zip(N["pb"], Z["pb"])), "Pi^N_B <= Pi^0_B at some theta"))

    da = [s - n for s, n in zip(S["pa"], N["pa"])]
    db = [s - n for s, n in zip(S["pb"], N["pb"])]
    v["P5.c1"] = v["P5.c2"] = v["P6.c1"] = v["P6.c2"] = None
    v["pattern A"], v["pattern B"] = sign_runs(da), sign_runs(db)
    if a1 < a2:                                             # the share of retailer A rises, the share of retailer B falls
        v["P5.c1"] = "" if all(x < 0 for x in da) else "alpha_A1 < alpha_A2 but Pi^S_A >= Pi^N_A at some theta"
        v["P6.c1"] = "" if all(x > 0 for x in db) else "alpha_B1 > alpha_B2 but Pi^S_B <= Pi^N_B at some theta"
    elif a1 > a2:
        v["P5.c1"] = "" if all(x > 0 for x in da) else "alpha_A1 > alpha_A2 but Pi^S_A <= Pi^N_A at some theta"
        v["P6.c1"] = "" if all(x < 0 for x in db) else "alpha_B1 < alpha_B2 but Pi^S_B >= Pi^N_B at some theta"
    else:
        if p5_sign_at_theta_one(pt) < 0:                    # the cost difference is above the threshold of Proposition 5
            v["P5.c2"] = _crossing(da)
        if p6_sign_at_theta_zero(pt) > 0:                   # the cost difference is below the threshold of Proposition 6
            v["P6.c2"] = _crossing(db)
    return v


def second_period_verdicts(pt: ExactPoint) -> dict:
    """Lemma 4 in the second period. It does not depend on gamma."""
    a2 = pt.aa2
    y = second_period_benchmark(pt)
    e = [ya / a2 - yb / (1 - a2) for ya, yb in zip(y["ya"], y["yb"])]
    return {"second period": _first_failure(
        (all(x >= 0 for x in e), "y^0_A / alpha_A < y^0_B / alpha_B in period 2"),
        (all(x == 0 for x in e) if pt.binds2 else all(x > 0 for x in e), "equality in period 2 does not coincide with equality in A11"))}


# ----------------------------------------------------------------------------- the sample
@dataclass
class Entry:
    point: ExactPoint
    fixed: dict                                             # verdicts that do not depend on gamma
    by_gamma: dict                                          # {gamma: verdicts}


def build_sample(n_regular=N_REGULAR, n_edge=N_EDGE) -> list:
    """Two of every three points have the same market shares in both periods."""
    rng_regular, rng_edge = seeded_rng(606), seeded_rng(616)
    points = [draw_exogenous_exact(rng_regular, equal_shares=(k % 3 != 0)) for k in range(n_regular)]
    points += [draw_edge_exact(rng_edge, equal_shares=(k % 3 != 0)) for k in range(n_edge)]
    return [Entry(pt, second_period_verdicts(pt), {g: verdicts(pt, g, curves(pt, g)) for g in GAMMAS}) for pt in points]


@pytest.fixture(scope="module")
def sample():
    return build_sample()


def _violations(sample, part, gammas) -> list:
    return [(e.point, g, e.by_gamma[g][part]) for e in sample for g in gammas if e.by_gamma[g][part]]


def _message(part, bad) -> str:
    point, gamma, reason = bad[0]
    return (f"{part} fails at {len(bad)} pairs of point and gamma. First: gamma = {gamma}, {reason}. {point.describe()}")


def _applicable(sample, part, kind) -> int:
    return sum(e.point.kind == kind and e.by_gamma[TOP[-1]][part] is not None for e in sample)


def _first_rung(sample, part, kind):
    """The lowest rung from which the part holds at every point of one kind and at every higher rung."""
    first = None
    for g in reversed(GAMMAS):
        if any(e.point.kind == kind and e.by_gamma[g][part] for e in sample):
            break
        first = g
    return None if first is None else float(first)


def require_at_every_gamma(sample, part, record) -> None:
    for kind in ("regular", "edge"):
        record(f"{kind}_points", _applicable(sample, part, kind))
    bad = _violations(sample, part, GAMMAS)
    assert not bad, _message(part, bad)


def require_for_large_gamma(sample, part, record) -> None:
    for kind in ("regular", "edge"):
        record(f"{kind}_points", _applicable(sample, part, kind))
        record(f"holds_at_every_{kind}_point_from_gamma", _first_rung(sample, part, kind))
    bad = _violations(sample, part, TOP)
    assert not bad, _message(part, bad)


def profit_difference(pt: ExactPoint, gamma, retailer: str) -> list:
    """Pi^S_i - Pi^N_i on the grid of theta for retailer i, as exact numbers."""
    theta = theta_grid(gamma)
    a = (pt.pa1, pt.pb1, pt.pa2, pt.pb2, np.array(theta, dtype=object), pt.ca, pt.cb, pt.beta, pt.mu, pt.sigma, gamma)
    scenario_s, scenario_n = (cf.spfta_t1, cf.npfta_t1) if retailer == "A" else (cf.spftb_t1, cf.npftb_t1)
    return _spread(scenario_s(*a) - scenario_n(*a), len(theta))


def further_points(seed, condition) -> list:
    """Points with the same shares in both periods that satisfy `condition`:
    the first N_FURTHER such points of `draw_exogenous_exact` and the first
    N_FURTHER / 2 such points of `draw_edge_exact`. Keeping only these points
    does not narrow the region of the test, because the part makes no
    statement about the others."""
    out = []
    for draw, wanted, rng in ((draw_exogenous_exact, N_FURTHER, seeded_rng(seed)), (draw_edge_exact, N_FURTHER // 2, seeded_rng(seed + 10))):
        found = []
        while len(found) < wanted:
            pt = draw(rng, equal_shares=True)
            if condition(pt):
                found.append(pt)
        out += found
    return out


def require_crossing_at_further_points(points, retailer, part, record) -> None:
    bad = [(pt, g, _crossing(profit_difference(pt, g, retailer))) for pt in points for g in TOP]
    bad = [b for b in bad if b[2]]
    record("further_points", len(points))
    assert not bad, _message(part, bad)


# ----------------------------------------------------------------------------- admissibility
@pytest.mark.supports(*ALL_PARTS)
def test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas(sample, record):
    """The sample of this file lies in the region of Lemmas 1 to 3.
    Points: the 210 sample points, 120 of `draw_exogenous_exact` (seed 606) and 90 of
    `draw_edge_exact` (seed 616), two thirds of each with equal shares in both periods, at
    every gamma of the 12-rung ladder from 1/20 to 1e60, on the theta grid of `theta_grid`.
    Computed: `ExactPoint.admissible` (A1, A7, A10, A11, I1 and I2, decided exactly), and
    from the closed forms the code's branch flag and the critical values zeta_A and zeta_B
    of the benchmark and of Scenarios S and N, in exact rational arithmetic. The bounds of
    both samplers and the number of edge points on each edge are recorded.
    Criterion: every point is admissible, and at every point, gamma and theta the code places
    retailer A's fractile above retailer B's and mu - sigma <= zeta_B <= zeta_A <= mu + sigma."""
    assert all(e.point.admissible() for e in sample)
    bad = _violations(sample, "region", GAMMAS)
    assert not bad, _message("the region of the lemmas", bad)
    record("regular_points", sum(e.point.kind == "regular" for e in sample))
    record("edge_points", sum(e.point.kind == "edge" for e in sample))
    record("points_with_the_same_shares_in_both_periods", sum(e.point.equal_shares for e in sample))
    record("gamma_ladder", [float(g) for g in GAMMAS])
    record("theta_nodes_at_the_top_rung", len(theta_grid(TOP[-1])))
    record("region_of_the_regular_points", region_summary("draw_exogenous_exact"))
    record("region_of_the_edge_points", region_summary("draw_edge_exact"))
    for tag, count in edge_census([e.point for e in sample if e.point.kind == "edge"]).items():
        record(f"edge points with {tag}", count)


# ----------------------------------------------------------------------------- Lemma 4
@pytest.mark.claims("L4.a")
def test_lemma_4a_benchmark_order_per_unit_of_share(sample, record):
    """Lemma 4(a): y^0_{A,t} / alpha_{A,t} >= y^0_{B,t} / alpha_{B,t}.
    Points: the 210 sample points (120 regular, 90 edge). Period 1 on the theta grid of
    gamma = 1/20, because the benchmark does not depend on gamma. Period 2 on the 21 values
    k / 20 of theta.
    Computed: e_t = y^0_{A,t} / alpha_{A,t} - y^0_{B,t} / alpha_{B,t} from `first_period_s`
    with gamma = 0, at the first-period prices for t = 1 and at the second-period prices for
    t = 2, in exact rational arithmetic.
    Criterion: e_t >= 0 at every node, and e_t = 0 at every node where A11 holds with
    equality in period t, e_t > 0 at every node otherwise."""
    for kind in ("regular", "edge"):
        record(f"{kind}_points", sum(e.point.kind == kind for e in sample))
    record("points_with_equality_in_period_1", sum(e.point.binds1 for e in sample))
    record("points_with_equality_in_period_2", sum(e.point.binds2 for e in sample))
    bad = _violations(sample, "L4.a", GAMMAS[:1]) + [(e.point, "any", e.fixed["second period"]) for e in sample if e.fixed["second period"]]
    assert not bad, _message("L4.a", bad)


@pytest.mark.claims("L4.b")
def test_lemma_4b_order_per_unit_of_share_in_scenarios_s_and_n(sample, record):
    """Lemma 4(b): y^k_{A,t} / alpha_{A,t} >= y^k_{B,t} / alpha_{B,t} for k = S and N.
    Points: the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder
    and its theta grid in period 1, the 21 values k / 20 of theta in period 2.
    Computed: e^k = y^k_{A,1} / alpha_{A,1} - y^k_{B,1} / alpha_{B,1} from `first_period_s`
    and `first_period_n` in exact rational arithmetic. By Lemmas 2 and 3 the second-period
    orders net of Z_{i,2} are the benchmark quantities at the second-period prices, so
    period 2 is the inequality of part (a) for t = 2. Second-period orders are not computed
    in any other way.
    Criterion: at every node and gamma e^S >= 0 and e^N > 0, e^S = 0 at every node where A11
    holds with equality in both periods and e^S > 0 otherwise, and the period-2 condition
    of the Lemma 4(a) check holds."""
    for kind in ("regular", "edge"):
        record(f"{kind}_points", sum(e.point.kind == kind for e in sample))
    bad = _violations(sample, "L4.b", GAMMAS) + [(e.point, "any", e.fixed["second period"]) for e in sample if e.fixed["second period"]]
    assert not bad, _message("L4.b", bad)


# ----------------------------------------------------------------------------- Proposition 1
@pytest.mark.claims("P1.i")
def test_proposition_1_i_order_quantities_of_retailer_a_increase_in_theta(sample, record):
    """Proposition 1, first sentence: the orders of retailer A increase in theta.
    Points: the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder
    and its theta grid.
    Computed: y^0_{A,1}, y^S_{A,1} and y^N_{A,1} on the grid from `first_period_s` and
    `first_period_n` in exact rational arithmetic.
    Criterion: at every point and gamma y^N_{A,1} is strictly increasing in theta, y^0_{A,1}
    is strictly increasing, or equal at every node where A11 holds with equality in period 1,
    and y^S_{A,1} is strictly increasing, or equal at every node where A11 holds with
    equality in both periods."""
    record("points_where_y0_A_is_constant", sum(e.point.binds1 for e in sample))
    record("points_where_yS_A_is_constant", sum(e.point.binds1 and e.point.binds2 for e in sample))
    require_at_every_gamma(sample, "P1.i", record)


@pytest.mark.claims("P1.ii")
def test_proposition_1_ii_threshold_in_theta_for_large_gamma(sample, record):
    """Proposition 1, second sentence: a threshold in theta for y^S_{A,1} - y^N_{A,1}.
    Points: the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder
    and its theta grid.
    Computed: d = y^S_{A,1} - y^N_{A,1} on the grid in exact rational arithmetic, and for each
    kind of point the lowest rung from which the large-gamma criterion holds at every point.
    Criterion: at gamma = 1e50 and 1e60, at every point, d > 0 at theta = 0, d < 0 at
    theta = 1 and the sign pattern of d along the grid, zeros skipped, is "+-". This is the
    interior threshold of the proof, while the statement also allows one at an end point.
    At every gamma of the ladder, d > 0 at theta = 0 and the pattern is "+" or "+-", which
    is what the proof shows for every gamma."""
    bad = _violations(sample, "P1.ii every gamma", GAMMAS)
    assert not bad, _message("P1.ii at every gamma", bad)
    require_for_large_gamma(sample, "P1.ii", record)


# ----------------------------------------------------------------------------- Proposition 2
@pytest.mark.claims("P2.a")
def test_proposition_2a_order_quantity_of_retailer_b_and_theta(sample, record):
    """Proposition 2(a): the orders of retailer B and theta.
    Points: the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder
    and its theta grid.
    Computed: y^0_{B,1}, y^S_{B,1} and y^N_{B,1} on the grid in exact rational arithmetic.
    The closed forms of y^0_{B,1} and y^S_{B,1} do not contain theta, so that half is a
    statement about the formulas of Lemmas 1 and 2.
    Criterion: at every point and gamma y^N_{B,1} is strictly decreasing in theta, and
    y^0_{B,1} and y^S_{B,1} are each equal at every node."""
    require_at_every_gamma(sample, "P2.a", record)


@pytest.mark.claims("P2.b")
def test_proposition_2b_ordering_of_the_order_quantities_of_retailer_b(sample, record):
    """Proposition 2(b): the ordering of the orders of retailer B across the scenarios.
    Points: the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder
    and its theta grid.
    Computed: y^0_{B,1}, y^N_{B,1} and y^S_{B,1} on the grid in exact rational arithmetic.
    Criterion: y^0_{B,1} < y^N_{B,1} < y^S_{B,1}, both strict, at every node, point and gamma."""
    require_at_every_gamma(sample, "P2.b", record)


C_GAMMA_COARSE = tuple(Fr(10) ** k for k in range(-6, 61))                # one node per decade
C_REFINE = tuple(Fr(m, 10) for m in (13, 18, 24, 32, 42, 56, 75))          # seven more nodes inside a decade
C_THETA = (Fr(0), Fr(1, 2), Fr(9, 10), Fr(999, 1000))
C_REGULAR, C_EDGE = 70, 50


def gap_of_retailer_b(pt: ExactPoint, theta, gammas) -> list:
    """y^S_{B,1} - y^N_{B,1} at one theta for a list of gammas."""
    a = (pt.pa1, pt.pb1, pt.pa2, pt.pb2, theta, pt.ca, pt.cb, pt.beta, pt.mu, pt.sigma, np.array(gammas, dtype=object))
    return list(cf.first_period_s(*a, branch=True)[1] - cf.first_period_n(*a, branch=True)[1])


def rises_then_falls_in_gamma(pt: ExactPoint, theta):
    """The gap on a grid of gamma that is refined in the four decades around
    its largest value. Returns the directions along the grid and the gamma at
    which the gap is largest."""
    coarse = gap_of_retailer_b(pt, theta, C_GAMMA_COARSE)
    k = max(range(len(coarse)), key=coarse.__getitem__)
    decades = C_GAMMA_COARSE[max(k - 2, 0):min(k + 2, len(C_GAMMA_COARSE) - 1)]
    grid = sorted(set(C_GAMMA_COARSE) | {g * m for g in decades for m in C_REFINE})
    values = gap_of_retailer_b(pt, theta, grid)
    return sign_runs(increments(values)), grid[max(range(len(values)), key=values.__getitem__)]


@pytest.mark.claims("P2.c")
def test_proposition_2c_gap_of_retailer_b_rises_then_falls_in_gamma(record):
    """Proposition 2(c): y^S_{B,1} - y^N_{B,1} first rises and then falls in gamma.
    Points: 70 points of `draw_exogenous_exact` (seed 707) and 50 of `draw_edge_exact`
    (seed 717), every second one with equal shares, at theta = 0, 1/2, 9/10 and 999/1000:
    480 curves. The grid of gamma has one node per decade from 1e-6 to 1e60, and seven more
    nodes, at 1.3 to 7.5 times the decade, in the four decades around the largest coarse value.
    Computed: the gap from `first_period_s` and `first_period_n` with the branch of Lemmas 2
    and 3 forced, in exact rational arithmetic, and its increments along the grid.
    Criterion: on every curve the sign pattern of the increments, zeros skipped, is "+-".
    A second rise that begins and ends between two neighbouring nodes would not be seen."""
    rng_regular, rng_edge = seeded_rng(707), seeded_rng(717)
    points = [draw_exogenous_exact(rng_regular, equal_shares=(k % 2 == 1)) for k in range(C_REGULAR)]
    points += [draw_edge_exact(rng_edge, equal_shares=(k % 2 == 1)) for k in range(C_EDGE)]
    largest = Fr(0)
    for pt in points:
        for theta in C_THETA:
            directions, peak = rises_then_falls_in_gamma(pt, theta)
            assert directions == "+-", f"P2.c: directions {directions!r} at theta = {theta}. {pt.describe()}"
            largest = max(largest, peak)
    record("regular_points", C_REGULAR)
    record("edge_points", C_EDGE)
    record("curves_checked", len(points) * len(C_THETA))
    record("gamma_range", [float(C_GAMMA_COARSE[0]), float(C_GAMMA_COARSE[-1])])
    record("largest_gamma_at_which_a_curve_peaks", float(largest))


# ----------------------------------------------------------------------------- Proposition 3
@pytest.mark.claims("P3.a")
def test_proposition_3a_expected_sales_of_retailer_a_for_large_gamma(sample, record):
    """Proposition 3(a): expected sales of retailer A for gamma large.
    Points: the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder
    and its theta grid.
    Computed: E[R^S_{A,1}], E[R^N_{A,1}] and d = E[R^S_{A,1}] - E[R^N_{A,1}] on the grid in
    exact rational arithmetic. For each kind of point two rungs are recorded: the lowest from
    which the large-gamma criterion holds at every point, and the lowest from which the
    change of sign of d exists at every point.
    Criterion: at gamma = 1e50 and 1e60, at every point, E[R^N_{A,1}] is strictly increasing
    in theta, E[R^S_{A,1}] is strictly increasing, or equal at every node where A11 holds
    with equality in both periods, and d > 0 at theta = 0, d < 0 at theta = 1 with sign
    pattern "+-", zeros skipped. At every gamma of the ladder, d > 0 at theta = 0 and the
    pattern is "+" or "+-"."""
    bad = _violations(sample, "P3.a every gamma", GAMMAS)
    assert not bad, _message("P3.a at every gamma", bad)
    for kind in ("regular", "edge"):
        record(f"a_change_of_sign_exists_at_every_{kind}_point_from_gamma", _first_rung(sample, "P3.a crossing", kind))
    require_for_large_gamma(sample, "P3.a", record)


@pytest.mark.claims("P3.b")
def test_proposition_3b_expected_sales_of_retailer_b(sample, record):
    """Proposition 3(b): expected sales of retailer B.
    Points: the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder
    and its theta grid.
    Computed: E[R^S_{B,1}] and E[R^N_{B,1}] on the grid from the closed forms, in exact
    rational arithmetic. The closed form of E[R^S_{B,1}] from Lemma 2 does not contain theta.
    Criterion: at every point and gamma E[R^N_{B,1}] is strictly decreasing in theta,
    E[R^S_{B,1}] is equal at every node, and E[R^N_{B,1}] < E[R^S_{B,1}] at every node."""
    require_at_every_gamma(sample, "P3.b", record)


# ----------------------------------------------------------------------------- Proposition 4
@pytest.mark.claims("P4")
def test_proposition_4_total_sales_fall_then_rise_in_theta(sample, record):
    """Proposition 4: total expected sales E[R^N_1] of Scenario N fall and then rise in theta.
    Points: the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder
    and its theta grid, which contains delta and 1 - delta with delta = 1e-30 / (1 + gamma),
    and the values 1 - t / gamma because the lowest point of E[R^N_1] lies at a distance of
    order 1 / gamma from theta = 1.
    Computed: E[R^N_{A,1}] + E[R^N_{B,1}] and its increments along the grid in exact rational
    arithmetic, and the lowest rung from which the criterion holds at every point of each kind.
    Criterion: at gamma = 1e50 and 1e60, at every point, the increment from 0 to delta is
    negative, the increment from 1 - delta to 1 is positive, and the sign pattern of the
    increments, zeros skipped, is "-+"."""
    require_for_large_gamma(sample, "P4", record)


# ----------------------------------------------------------------------------- Proposition 5
@pytest.mark.claims("P5.a")
def test_proposition_5a_profit_of_retailer_a_in_scenario_s_increases_in_theta(sample, record):
    """Proposition 5(a): the profit Pi^S_A of retailer A in Scenario S increases in theta.
    Points: the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder
    and its theta grid.
    Computed: Pi^S_A on the grid from `spfta_t1` in exact rational arithmetic, and the lowest
    rung from which the criterion holds at every point of each kind.
    Criterion: at gamma = 1e50 and 1e60, at every point, Pi^S_A is strictly increasing in
    theta, or equal at every node where A11 holds with equality in both periods."""
    record("points_where_the_profit_is_constant", sum(e.point.binds1 and e.point.binds2 for e in sample))
    require_for_large_gamma(sample, "P5.a", record)


@pytest.mark.claims("P5.b")
def test_proposition_5b_profit_of_retailer_a_exceeds_the_benchmark(sample, record):
    """Proposition 5(b): the profits of retailer A exceed the benchmark.
    Points: the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder
    and its theta grid.
    Computed: Pi^0_A, Pi^S_A and Pi^N_A on the grid from `spfta_t1` (with gamma = 0 for the
    benchmark) and `npfta_t1` in exact rational arithmetic, and the lowest rung from which
    the criterion holds at every point of each kind.
    Criterion: at gamma = 1e50 and 1e60, at every point, Pi^S_A > Pi^0_A and Pi^N_A > Pi^0_A
    at every node."""
    require_for_large_gamma(sample, "P5.b", record)


@pytest.mark.claims("P5.c1")
def test_proposition_5c1_shares_decide_the_comparison_for_retailer_a(sample, record):
    """Proposition 5(c1): where the shares differ between the periods, they decide the
    comparison of Pi^S_A and Pi^N_A.
    Points: the sample points whose shares alpha_{A,1} and alpha_{A,2} differ, compared
    exactly, so that no point is left out because its shares are close. Every gamma of the
    12-rung ladder and its theta grid.
    Computed: Pi^S_A - Pi^N_A on the grid in exact rational arithmetic, and the lowest rung
    from which the criterion holds at every such point of each kind.
    Criterion: at gamma = 1e50 and 1e60, alpha_{A,1} < alpha_{A,2} gives Pi^S_A < Pi^N_A and
    alpha_{A,1} > alpha_{A,2} gives Pi^S_A > Pi^N_A, at every node of every such point."""
    require_for_large_gamma(sample, "P5.c1", record)


@pytest.mark.claims("P5.c2")
def test_proposition_5c2_threshold_in_theta_above_the_cost_threshold(sample, record, repo_root):
    """Proposition 5(c2): with equal shares and c_B above the threshold c_B-bar of the proof,
    a threshold in theta for Pi^S_A - Pi^N_A.
    Points: the sample points with equal shares at which the expression P5_SIGN_AT_THETA_ONE
    of the proof is negative, which is the condition c_B > c_B-bar, and 90 further points with
    equal shares that satisfy it, 60 of `draw_exogenous_exact` (seed 626) and 30 of
    `draw_edge_exact` (seed 636). Theta grid of each rung of the ladder.
    Computed: Pi^S_A - Pi^N_A on the grid in exact rational arithmetic. The sign patterns at
    the sample points below the cost threshold are recorded and not tested, because the
    statement says nothing about them.
    Criterion: the two LaTeX strings of the proof occur verbatim in the LaTeX source, and at
    gamma = 1e50 and 1e60, at every such point, the difference is positive at theta = 0,
    negative at theta = 1, with sign pattern "+-", zeros skipped."""
    quoted("Proposition 5", P5_SIGN_AT_THETA_ONE)
    quoted("Proposition 5", P5_THRESHOLD_SENTENCE)
    below = [e for e in sample if e.point.equal_shares and p5_sign_at_theta_one(e.point) > 0]
    record("points_below_the_cost_threshold", len(below))
    record("signs_along_theta_below_the_cost_threshold", sorted({e.by_gamma[TOP[-1]]["pattern A"] for e in below}))
    require_for_large_gamma(sample, "P5.c2", record)
    require_crossing_at_further_points(further_points(626, lambda pt: p5_sign_at_theta_one(pt) < 0), "A", "P5.c2", record)


def last_positive_rung_at_theta_one(pt: ExactPoint, ladder) -> Fr | None:
    """The smallest gamma of the ladder from which on Pi^S_A - Pi^N_A < 0 at theta = 1 on every
    larger rung, or None if the difference is not negative on the top rung."""
    negative = [profit_difference_at(pt, Fr(1), g, "A") < 0 for g in ladder]
    if not negative[-1]:
        return None
    k = len(ladder) - 1
    while k > 0 and negative[k - 1]:
        k -= 1
    return ladder[k]


def profit_difference_at(pt: ExactPoint, theta, gamma, retailer: str):
    """Pi^S_i - Pi^N_i at one value of theta, as an exact number."""
    a = (pt.pa1, pt.pb1, pt.pa2, pt.pb2, np.array([theta], dtype=object), pt.ca, pt.cb, pt.beta, pt.mu, pt.sigma, gamma)
    scenario_s, scenario_n = (cf.spfta_t1, cf.npfta_t1) if retailer == "A" else (cf.spftb_t1, cf.npftb_t1)
    return _spread(scenario_s(*a) - scenario_n(*a), 1)[0]


@pytest.mark.supports("P5")
def test_threshold_gamma_a4_of_proposition_5c2_depends_on_c_b(record):
    """Under the fixed-market interpretation of Proposition 5(c2) in theory.md,
    the threshold gamma^A_4 in the proof can depend on c_B. It grows without bound as c_B increases to p_{B,2}
    when p_{B,2} < p_{B,1}, and it can stay bounded as c_B increases to the end of its range
    when that end is p_{B,1}.
    Points: equal shares (alpha_{A,1} = alpha_{A,2} = 13/25), c_A = 1, beta = 1/10, mu = 10,
    sigma = 4. Prices p_A = (7/2, 3), p_B = (37/10, 16/5), where the range of c_B ends at
    p_{B,2} = 16/5, and the mirrored prices p_A = (3, 7/2), p_B = (16/5, 37/10), where it ends
    at p_{B,1} = 16/5. In each case c_B = 16/5 - eps for eps in {1/10, 1/100, 1/1000}, every
    point admissible and above c_B-bar. Gamma on the ladder 2^0, 2^1, ..., 2^30.
    Computed: Pi^S_A - Pi^N_A at theta = 1 from the closed forms of Lemmas 2 and 3 in exact
    rational arithmetic, and the smallest rung from which on it is negative on every larger
    rung. Pi^S_A - Pi^N_A at theta = 0 is positive at every rung used.
    Criterion: with p_{B,2} < p_{B,1} that rung rises by a factor of at least 10 with each
    tenfold decrease of eps. With p_{B,1} < p_{B,2} it is the same at every eps and at most 2^8."""
    ladder = [Fr(2) ** k for k in range(31)]
    common = dict(ca=Fr(1), beta=Fr(1, 10), mu=Fr(10), sigma=Fr(4), theta=Fr(1), gamma=Fr(1), lam_s=Fr(1, 2))
    cases = {"p_B2 < p_B1": (Fr(7, 2), Fr(37, 10), Fr(3), Fr(16, 5)), "p_B1 < p_B2": (Fr(3), Fr(16, 5), Fr(7, 2), Fr(37, 10))}
    rungs = {}
    for name, (pa1, pb1, pa2, pb2) in cases.items():
        rungs[name] = []
        for eps in (Fr(1, 10), Fr(1, 100), Fr(1, 1000)):
            pt = ExactPoint(pa1=pa1, pb1=pb1, pa2=pa2, pb2=pb2, cb=Fr(16, 5) - eps, **common)
            assert pt.admissible() and pt.equal_shares and p5_sign_at_theta_one(pt) < 0, pt.describe()
            rung = last_positive_rung_at_theta_one(pt, ladder)
            assert rung is not None, f"{name}, eps = {eps}: Pi^S_A - Pi^N_A at theta = 1 is not negative at gamma = 2^30"
            assert all(profit_difference_at(pt, Fr(0), g, "A") > 0 for g in ladder[ladder.index(rung):]), pt.describe()
            rungs[name].append(rung)
        record(f"rungs {name}", [int(r) for r in rungs[name]])
    rising = rungs["p_B2 < p_B1"]
    assert all(b >= 10 * a for a, b in zip(rising, rising[1:])), rising
    flat = rungs["p_B1 < p_B2"]
    assert len(set(flat)) == 1 and flat[0] <= 2 ** 8, flat


# ----------------------------------------------------------------------------- Proposition 6
@pytest.mark.claims("P6.a")
def test_proposition_6a_profit_of_retailer_b_and_theta(sample, record):
    """Proposition 6(a): the profits of retailer B and theta.
    Points: the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder
    and its theta grid.
    Computed: Pi^S_B and Pi^N_B on the grid from `spftb_t1` and `npftb_t1` in exact rational
    arithmetic, and the lowest rung from which the criterion holds at every point of each kind.
    The closed form of Pi^S_B from Lemma 2 does not contain theta.
    Criterion: at gamma = 1e50 and 1e60, at every point, Pi^S_B is equal at every node and
    Pi^N_B is strictly increasing in theta."""
    require_for_large_gamma(sample, "P6.a", record)


@pytest.mark.claims("P6.b")
def test_proposition_6b_profit_of_retailer_b_exceeds_the_benchmark(sample, record):
    """Proposition 6(b): the profits of retailer B exceed the benchmark.
    Points: the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder
    and its theta grid.
    Computed: Pi^0_B, Pi^S_B and Pi^N_B on the grid from `spftb_t1` (with gamma = 0 for the
    benchmark) and `npftb_t1` in exact rational arithmetic, and the lowest rung from which
    the criterion holds at every point of each kind.
    Criterion: at gamma = 1e50 and 1e60, at every point, Pi^S_B > Pi^0_B and Pi^N_B > Pi^0_B
    at every node."""
    require_for_large_gamma(sample, "P6.b", record)


@pytest.mark.claims("P6.c1")
def test_proposition_6c1_shares_decide_the_comparison_for_retailer_b(sample, record):
    """Proposition 6(c1): where the shares differ between the periods, they decide the
    comparison of Pi^S_B and Pi^N_B.
    Points: the sample points whose shares differ between the periods, compared exactly.
    Every gamma of the 12-rung ladder and its theta grid.
    Computed: Pi^S_B - Pi^N_B on the grid in exact rational arithmetic, and the lowest rung
    from which the criterion holds at every such point of each kind.
    Criterion: at gamma = 1e50 and 1e60, alpha_{B,1} > alpha_{B,2} gives Pi^S_B > Pi^N_B and
    alpha_{B,1} < alpha_{B,2} gives Pi^S_B < Pi^N_B, at every node of every such point."""
    require_for_large_gamma(sample, "P6.c1", record)


@pytest.mark.claims("P6.c2")
def test_proposition_6c2_threshold_in_theta_below_the_cost_threshold(sample, record, repo_root):
    """Proposition 6(c2): with equal shares and a cost difference below the threshold of the
    proof, a threshold in theta for Pi^S_B - Pi^N_B.
    Points: the sample points with equal shares at which the bracket in
    P6_SIGN_AT_THETA_ZERO of the proof is positive, which is the cost condition, and 90
    further points with equal shares that satisfy it, 60 of `draw_exogenous_exact` (seed
    636) and 30 of `draw_edge_exact` (seed 646). Theta grid of each rung of the ladder.
    Computed: Pi^S_B - Pi^N_B on the grid in exact rational arithmetic. The sign patterns at
    the sample points above the cost threshold are recorded and not tested, because the
    statement says nothing about them.
    Criterion: the LaTeX string of the proof occurs verbatim in the LaTeX source, and at
    gamma = 1e50 and 1e60, at every such point, the difference is positive at theta = 0,
    negative at theta = 1, with sign pattern "+-", zeros skipped."""
    quoted("Proposition 6", P6_SIGN_AT_THETA_ZERO)
    above = [e for e in sample if e.point.equal_shares and p6_sign_at_theta_zero(e.point) < 0]
    record("points_above_the_cost_threshold", len(above))
    record("signs_along_theta_above_the_cost_threshold", sorted({e.by_gamma[TOP[-1]]["pattern B"] for e in above}))
    require_for_large_gamma(sample, "P6.c2", record)
    require_crossing_at_further_points(further_points(636, lambda pt: p6_sign_at_theta_zero(pt) > 0), "B", "P6.c2", record)


# ----------------------------------------------------------------------------- statement N8 of Section 4.2.3
N8_GAMMAS = (Fr(1), Fr(10), Fr(50), Fr(100), Fr(1000))
N8_TESTED = (Fr(50), Fr(100))           # "strong cross-brand C2C" for the purpose of the test


def rise_fall_rise(values) -> tuple[int, int] | None:
    """The first and the last step at which the sequence falls, if it rises over its first and
    its last step and falls over some step in between. None otherwise."""
    steps = [b - a for a, b in zip(values, values[1:])]
    falls = [k for k, s in enumerate(steps) if s < 0]
    if falls and steps[0] > 0 and steps[-1] > 0:
        return falls[0], falls[-1]
    return None


@pytest.mark.claims("N8")
def test_profit_of_retailer_a_in_scenario_n_can_fall_at_intermediate_theta(record):
    """N8, Section 4.2.3: when strong cross-brand C2C is present, Pi^N_A may decrease in theta
    when theta takes intermediate values. The sentence says that such markets exist.
    Points: the 120 regular points of the sample (`draw_exogenous_exact`, seed 606, two of
    every three with equal shares), gamma in {1, 10, 50, 100, 1000}, and theta = 0, 1/20, ..., 1.
    Computed: Pi^N_A on the grid from `npfta_t1` in exact rational arithmetic, and for each
    gamma the number of points at which Pi^N_A rises over the first and the last step of the
    grid and falls over some step in between.
    Criterion: at gamma = 50 and at gamma = 100 at least one point has this pattern."""
    theta = [Fr(k, 20) for k in range(21)]
    rng = seeded_rng(606)
    points = [draw_exogenous_exact(rng, equal_shares=(k % 3 != 0)) for k in range(N_REGULAR)]
    found = {}
    for gamma in N8_GAMMAS:
        found[gamma] = []
        for pt in points:
            a = (pt.pa1, pt.pb1, pt.pa2, pt.pb2, np.array(theta, dtype=object), pt.ca, pt.cb, pt.beta,
                 pt.mu, pt.sigma, gamma)
            pattern = rise_fall_rise(_spread(cf.npfta_t1(*a), len(theta)))
            if pattern:
                found[gamma].append((pt, pattern))
        record(f"points_with_a_fall_at_intermediate_theta_at_gamma_{gamma}", len(found[gamma]))
    if found[N8_TESTED[0]]:
        _, (first, last) = found[N8_TESTED[0]][0]
        record("first_example_at_gamma_50_falls_between_theta", f"{theta[first]} and {theta[last + 1]}")
    missing = [str(g) for g in N8_TESTED if not found[g]]
    assert not missing, f"no point with a fall of Pi^N_A at intermediate theta at gamma = {', '.join(missing)}"
