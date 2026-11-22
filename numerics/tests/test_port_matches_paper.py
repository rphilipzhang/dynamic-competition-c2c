"""The Python port of the authors' MATLAB code in `c2c.closed_form` against the formulas of the paper.

Each test writes a formula of the paper down a second time, independently of
the code, and requires the code to return exactly the same value.

How equality is established
    Both sides are rational functions of the parameters. They are evaluated
    in exact rational arithmetic (no floating point) at random rational
    parameter points and must agree exactly at every point. Two different
    rational functions can agree only on a set of measure zero, so this is a
    randomized identity test with a negligible chance of a false pass. The
    expected-leftover integrals are in addition checked by full symbolic
    simplification.

How the transcription is kept honest
    Every formula taken from the paper is written next to the LaTeX string it
    transcribes, and `quoted` asserts through `c2c.paper` that this string
    occurs verbatim, up to whitespace, in `paper/Manuscript.tex` or
    `paper/OnlineAppendix.tex`. A reviewer only has to compare each LaTeX
    string with the line of Python beneath it.

All expressions use assumption A10: rho = 1 and X ~ U[mu - sigma, mu + sigma],
so that F^{-1}(q) = mu - sigma + 2 sigma q. The case treated is the one of
Section 4: retailer A has the higher critical fractile (assumption A11).
"""
from __future__ import annotations

import random

import pytest
import sympy as sp

from c2c import closed_form as cf
from c2c import paper

N_POINTS = 25
NAMES = ("pa1", "pb1", "pa2", "pb2", "theta", "ca", "cb", "beta", "mu", "sigma", "gamma")


def random_points(seed: int, n: int = N_POINTS):
    """Random rational parameter points. Identities between rational functions
    hold everywhere, so the points need not satisfy the paper's assumptions."""
    rng = random.Random(seed)
    for _ in range(n):
        yield {name: sp.Rational(rng.randint(1, 10**6), rng.randint(1, 10**3)) for name in NAMES}


def args_of(pt):
    return tuple(pt[name] for name in NAMES)


@pytest.fixture(scope="module")
def quoted():
    """Assert that a LaTeX string occurs verbatim in the LaTeX source of the paper.
    The first argument names the result the string comes from, for the reader."""
    def _quoted(result: str, latex: str):
        paper.assert_quoted(latex)
    return _quoted


# ----------------------------------------------------------------------------- the paper, written independently
HALF = sp.Rational(1, 2)


def share(p_own, p_other, beta):
    return HALF + beta * (p_other - p_own)                # alpha_{i,t} = 1/2 + beta (p_{j,t} - p_{i,t})


def finv(q, mu, sigma):
    return mu - sigma + 2 * sigma * q                     # quantile function of U[mu - sigma, mu + sigma]


def order_quantities(a_a, a_b, z_a, z_b, theta):
    """Lemmas 1, 2, 3 and B.1 share this form of the equilibrium order quantities."""
    return (a_a + theta * a_b) * z_a - theta * a_b * z_b, a_b * z_b


# Expected leftovers E[(y_i - D_i)^+] at those order quantities, obtained by
# integrating the demand system of Section 3 over X ~ U[mu - sigma, mu + sigma]
# for mu - sigma <= z_b <= z_a <= mu + sigma. For X < z_b nobody is out of
# stock, so D_A = a_a X and D_B = a_b X. For z_b <= X < z_a retailer B is out of
# stock and A receives the spillover: D_A = a_a X + theta a_b (X - z_b), which
# reaches y_A exactly at X = z_a.
_x, _aa, _ab, _za, _zb, _th, _mu, _sg = sp.symbols("x a_A a_B zeta_A zeta_B theta mu sigma", positive=True)
_ya, _yb = order_quantities(_aa, _ab, _za, _zb, _th)
_LEFT_B = sp.integrate(_yb - _ab * _x, (_x, _mu - _sg, _zb)) / (2 * _sg)
_LEFT_A = (sp.integrate(_ya - _aa * _x, (_x, _mu - _sg, _zb))
           + sp.integrate(_ya - _aa * _x - _th * _ab * (_x - _zb), (_x, _zb, _za))) / (2 * _sg)


def expected_leftovers(a_a, a_b, z_a, z_b, theta, mu, sigma):
    sub = {_aa: a_a, _ab: a_b, _za: z_a, _zb: z_b, _th: theta, _mu: mu, _sg: sigma}
    return _LEFT_A.subs(sub), _LEFT_B.subs(sub)


def benchmark_profits(p_a, p_b, pt):
    """pi^0_{A,t} and pi^0_{B,t} as defined at the end of the proof of Lemma 1."""
    a_a = share(p_a, p_b, pt["beta"])
    a_b = 1 - a_a
    z_a = finv(1 - pt["ca"] / p_a, pt["mu"], pt["sigma"])
    z_b = finv(1 - pt["cb"] / p_b, pt["mu"], pt["sigma"])
    y_a, y_b = order_quantities(a_a, a_b, z_a, z_b, pt["theta"])
    left_a, left_b = expected_leftovers(a_a, a_b, z_a, z_b, pt["theta"], pt["mu"], pt["sigma"])
    return (p_a - pt["ca"]) * y_a - p_a * left_a, (p_b - pt["cb"]) * y_b - p_b * left_b


def lemma_b1(pt, lam_s, lam_n):
    """Lemma B.1 with weights (lam_s, lam_n). Returns fractiles, quantities,
    expected leftovers and total two-period profits. Lemma 2 is the case
    (1, 0) and Lemma 3 is the case (0, 1)."""
    pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma = args_of(pt)
    a_a1, a_a2 = share(pa1, pb1, beta), share(pa2, pb2, beta)
    a_b1, a_b2 = 1 - a_a1, 1 - a_a2
    g_a, g_b = (lam_s + lam_n * a_a2) * gamma, (lam_s + lam_n * a_b2) * gamma     # gamma_{i,2}
    gc_a, gc_b = lam_n * gamma * a_a2, lam_n * gamma * a_b2                       # gamma^C_{i,2}
    z_a = finv(1 - ca / (pa1 + g_a * (pa2 - ca)), mu, sigma)
    z_b = finv(1 - (cb - gc_b * theta * (pb2 - cb) * ca / (pa1 + g_a * (pa2 - ca)))
               / (pb1 + (g_b - gc_b * theta) * (pb2 - cb)), mu, sigma)
    y_a, y_b = order_quantities(a_a1, a_b1, z_a, z_b, theta)
    left_a, left_b = expected_leftovers(a_a1, a_b1, z_a, z_b, theta, mu, sigma)
    pi0_a, pi0_b = benchmark_profits(pa2, pb2, pt)
    # first-period margin, plus (p_2 - c) E[Z_{i,2}], plus the benchmark second-period profit
    total_a = ((pa1 - ca + g_a * (pa2 - ca)) * y_a - (pa1 + g_a * (pa2 - ca)) * left_a
               + gc_a * (pa2 - ca) * (y_b - left_b) + pi0_a)
    total_b = ((pb1 - cb + g_b * (pb2 - cb)) * y_b - (pb1 + g_b * (pb2 - cb)) * left_b
               + gc_b * (pb2 - cb) * (y_a - left_a) + pi0_b)
    return dict(z_a=z_a, z_b=z_b, y_a=y_a, y_b=y_b, left_a=left_a, left_b=left_b, total_a=total_a, total_b=total_b)


# ----------------------------------------------------------------------------- tests
@pytest.mark.supports("L1", "L2", "L3", "LB1")
def test_expected_leftovers_in_the_code_follow_from_the_model():
    """The two expected-leftover expressions used throughout `c2c.closed_form`.
    Points: none. The check is symbolic in the positive symbols a_A, a_B, zeta_A,
    zeta_B, theta, mu and sigma.
    Computed: E[(y_i - D_i)^+] at the order quantities of Lemmas 1, 2, 3 and B.1, by
    SymPy integration of the demand system of Section 3 over X ~ U[mu - sigma, mu + sigma]
    for mu - sigma <= zeta_B <= zeta_A <= mu + sigma, and `_leftover_high` and
    `_leftover_low` of `c2c.closed_form` in the same symbols.
    Criterion: each of the two differences expands to exactly 0."""
    assert sp.expand(cf._leftover_high(_aa, _ab, _th, _za, _zb, _mu, _sg) - _LEFT_A) == 0
    assert sp.expand(cf._leftover_low(_ab, _zb, _mu, _sg) - _LEFT_B) == 0


@pytest.mark.supports("L1.eq")
def test_benchmark_profit_polynomials_match_lemma_1(quoted, record):
    """Benchmark profits pi^0 = (p - c) y^0 - p E[L^0] at the equilibrium of Lemma 1.
    Points: 25 random rational parameter points (seed 1), at their second-period prices.
    The points need not satisfy the assumptions of the paper.
    Computed: pi^0_A and pi^0_B from this file's transcription of Lemma 1 and of the end of
    its proof, and `pfta_t2_case1` and `pftb_t2_case1` of `c2c.closed_form`, all in exact
    rational arithmetic. Three LaTeX strings of Lemma 1 and its proof are quoted.
    Criterion: both profits are equal as rational numbers at every point, and every quoted
    string occurs verbatim, up to whitespace, in the LaTeX source in `paper/`."""
    quoted("Lemma 1", r"\zeta_{i,t}^0= F^{-1}(1 - \frac{c_i}{p_{i,t}})")
    quoted("Lemma 1",
           r"y^{0}_{A,t} = (\alpha_{A,t} + \theta \alpha_{B,t}) \zeta_{A,t}^0 - \theta \alpha_{B,t} \zeta_{B,t}^0")
    quoted("Lemma 1, proof", r"\pi^{0}_{A,t} := (p_{A,t}-c_A)y^0_{A,t} - p_{A,t} \mathbb{E}[L^0_{A,t}]")
    for pt in random_points(1):
        pi_a, pi_b = benchmark_profits(pt["pa2"], pt["pb2"], pt)
        assert cf.pfta_t2_case1(pt["pa2"], pt["pb2"], pt["theta"], pt["ca"], pt["cb"], pt["beta"], pt["mu"], pt["sigma"]) == pi_a
        assert cf.pftb_t2_case1(pt["pa2"], pt["pb2"], pt["cb"], pt["beta"], pt["mu"], pt["sigma"]) == pi_b
    record("exact_rational_points", N_POINTS)


@pytest.mark.claims("L2.first", "L2.profits")
def test_scenario_s_code_matches_lemma_2(quoted, record):
    """Scenario S: Lemma 2 and equations (A.8) and (A.10) with rho = 1.
    Points: 25 random rational parameter points (seed 2).
    Computed: critical values, order quantities and expected leftovers of the first period
    and total two-period profits of both retailers, from this file's transcription of
    Lemma 2, (A.8) and (A.10), and from `first_period_s`, `spfta_t1` and `spftb_t1` of
    `c2c.closed_form` with the branch of Lemma 2 forced, all in exact rational arithmetic.
    Three LaTeX strings of Lemma 2 and its proof are quoted.
    Criterion: the six first-period values and both profits are equal as rational numbers
    at every point, and every quoted string occurs verbatim, up to whitespace, in the LaTeX
    source in `paper/`."""
    quoted("Lemma 2",
           r"\zeta^S_{i,1} = F^{-1}\left( 1 - \frac{c_i}{p_{i,1} + \gamma (p_{i,2}-c_i)}\right)")
    quoted("Lemma 2",
           r"y^{S}_{A,1} = (\alpha_{A,1} + \theta \alpha_{B,1}) \zeta_{A,1}^S - \theta \alpha_{B,1} \zeta_{B,1}^S")
    quoted("Lemma 2, proof, (A.8)",
           r"[p_{A,1} -c_A + \rho (p_{A,2} -c_A)\gamma]y_{A,1} - [p_{A,1}+\rho (p_{A,2} -c_A)\gamma] "
           r"\mathbb{E} \left[y_{A,1} - D_{A,1} \right]^+ + \rho \pi^{0}_{A,2},")
    for pt in random_points(2):
        pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma = a = args_of(pt)
        # Lemma 2, written out directly
        z_a = finv(1 - ca / (pa1 + gamma * (pa2 - ca)), mu, sigma)
        z_b = finv(1 - cb / (pb1 + gamma * (pb2 - cb)), mu, sigma)
        a_a1 = share(pa1, pb1, beta)
        y_a, y_b = order_quantities(a_a1, 1 - a_a1, z_a, z_b, theta)
        left_a, left_b = expected_leftovers(a_a1, 1 - a_a1, z_a, z_b, theta, mu, sigma)
        pi0_a, pi0_b = benchmark_profits(pa2, pb2, pt)
        total_a = (pa1 - ca + (pa2 - ca) * gamma) * y_a - (pa1 + (pa2 - ca) * gamma) * left_a + pi0_a   # (A.8)
        total_b = (pb1 - cb + (pb2 - cb) * gamma) * y_b - (pb1 + (pb2 - cb) * gamma) * left_b + pi0_b   # (A.10)
        code = cf.first_period_s(*a, branch=True)
        assert code[:6] == (y_a, y_b, left_a, left_b, z_a, z_b)
        assert cf.spfta_t1(*a, branch=True, branch2=True) == total_a
        assert cf.spftb_t1(*a, branch=True, branch2=True) == total_b
    record("exact_rational_points", N_POINTS)


@pytest.mark.claims("L3.first", "L3.profits")
def test_scenario_n_code_matches_lemma_3(quoted, record):
    """Scenario N: Lemma 3 and equations (A.12) and (A.14) with rho = 1.
    Points: 25 random rational parameter points (seed 3).
    Computed: critical values, order quantities and expected leftovers of the first period
    and total two-period profits of both retailers, from this file's transcription of
    Lemma 3, (A.12) and (A.14), and from `first_period_n`, `npfta_t1` and `npftb_t1` of
    `c2c.closed_form` with the branch of Lemma 3 forced, all in exact rational arithmetic.
    Three LaTeX strings of Lemma 3 and its proof are quoted.
    Criterion: the six first-period values and both profits are equal as rational numbers
    at every point, and every quoted string occurs verbatim, up to whitespace, in the LaTeX
    source in `paper/`."""
    quoted("Lemma 3",
           r"\zeta^N_{A,1} = F^{-1} \bigg( 1- \frac{c_A}{p_{A,1} + \alpha_{A,2} \gamma (p_{A,2} -c_A)} \bigg)")
    quoted("Lemma 3",
           r"\zeta^N_{B,1}= F^{-1} \bigg( 1- \frac{c_B - \alpha_{B,2} \gamma \theta (p_{B,2} -c_B) "
           r"\frac{c_A}{p_{A,1} + \alpha_{A,2} \gamma (p_{A,2}-c_A)}}{p_{B,1} + \alpha_{B,2} \gamma (1-\theta)(p_{B,2} -c_B)} \bigg);")
    quoted("Lemma 3, proof, (A.12)",
           r"+ \rho (p_{A,2} -c_A)\alpha_{A,2} \gamma y_{B,1} - \rho (p_{A,2} -c_A)\alpha_{A,2} \gamma "
           r"\mathbb{E} \left[y_{B,1} - D_{B,1} \right]^+ + \rho \pi^{0}_{A,2},")
    for pt in random_points(3):
        pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma = a = args_of(pt)
        a_a1, a_a2 = share(pa1, pb1, beta), share(pa2, pb2, beta)
        a_b2 = 1 - a_a2
        # Lemma 3, written out directly
        z_a = finv(1 - ca / (pa1 + a_a2 * gamma * (pa2 - ca)), mu, sigma)
        z_b = finv(1 - (cb - a_b2 * gamma * theta * (pb2 - cb) * ca / (pa1 + a_a2 * gamma * (pa2 - ca)))
                   / (pb1 + a_b2 * gamma * (1 - theta) * (pb2 - cb)), mu, sigma)
        y_a, y_b = order_quantities(a_a1, 1 - a_a1, z_a, z_b, theta)
        left_a, left_b = expected_leftovers(a_a1, 1 - a_a1, z_a, z_b, theta, mu, sigma)
        pi0_a, pi0_b = benchmark_profits(pa2, pb2, pt)
        ga, gb = (pa2 - ca) * a_a2 * gamma, (pb2 - cb) * a_b2 * gamma
        total_a = (pa1 - ca + ga) * y_a - (pa1 + ga) * left_a + ga * y_b - ga * left_b + pi0_a          # (A.12)
        total_b = (pb1 - cb + gb) * y_b - (pb1 + gb) * left_b + gb * y_a - gb * left_a + pi0_b          # (A.14)
        code = cf.first_period_n(*a, branch=True)
        assert code[:6] == (y_a, y_b, left_a, left_b, z_a, z_b)
        assert cf.npfta_t1(*a, branch=True, branch2=True) == total_a
        assert cf.npftb_t1(*a, branch=True, branch2=True) == total_b
    record("exact_rational_points", N_POINTS)


@pytest.mark.claims("LB1.first")
def test_mixed_scenario_code_matches_lemma_b1(quoted, record):
    """Mixed scenario of Online Appendix B: Lemma B.1.
    Points: 25 random rational parameter points (seed 4), each with a weight lambda_S drawn
    from the multiples of 1/1000 in [0, 1] (seed 40) and lambda_N = 1 - lambda_S.
    Computed: first-period order quantities and total two-period profits of both retailers
    from this file's transcription of Lemma B.1, and from `find_general_exo` of
    `c2c.closed_form`, in exact rational arithmetic. Four LaTeX strings of Online
    Appendix B are quoted.
    Criterion: the four values are equal as rational numbers at every point, and every
    quoted string occurs verbatim, up to whitespace, in the LaTeX source in `paper/`."""
    quoted("Lemma B.1",
           r"\zeta^G_{A,1} = F^{-1} \bigg( 1- \frac{c_A}{p_{A,1} + \gamma_{A,2} (p_{A,2} -c_A)} \bigg)")
    quoted("Lemma B.1",
           r"\zeta^G_{B,1}= F^{-1} \bigg( 1- \frac{c_B - \gamma^C_{B,2} \theta (p_{B,2} -c_B) "
           r"\frac{c_A}{p_{A,1} + \gamma_{A,2} (p_{A,2}-c_A)}}{p_{B,1} + (\gamma_{B,2}-\gamma^C_{B,2}\theta )(p_{B,2} -c_B)} \bigg);")
    quoted("Online Appendix B", r"\gamma_{i,t}:=(\lambda^S + \lambda^N \alpha_{i,t}) \gamma")
    quoted("Online Appendix B", r"\gamma^C_{i,t} := \lambda^N \gamma \alpha_{i,t}")
    rng = random.Random(40)
    for pt in random_points(4):
        lam_s = sp.Rational(rng.randint(0, 1000), 1000)
        paper = lemma_b1(pt, lam_s, 1 - lam_s)
        code = cf.find_general_exo(*args_of(pt), lam_s, 1 - lam_s)
        assert code == (paper["y_a"], paper["y_b"], paper["total_a"], paper["total_b"])
    record("exact_rational_points", N_POINTS)


@pytest.mark.claims("LB1.first")
@pytest.mark.supports("L2", "L3")
def test_mixed_scenario_reduces_to_scenarios_s_and_n(quoted, record):
    """Online Appendix B: Scenario S is the mixed scenario with weights (1, 0) and
    Scenario N is the mixed scenario with weights (0, 1).
    Points: 25 random rational parameter points (seed 5).
    Computed: `find_general_exo` with weights (1, 0) and (0, 1), and the order quantities
    and total profits of `first_period_s`, `spfta_t1`, `spftb_t1` and of `first_period_n`,
    `npfta_t1`, `npftb_t1`, with the branch of the lemmas forced, in exact rational
    arithmetic. The sentence of Online Appendix B on the Scenario S case is quoted.
    Criterion: both pairs of four-value tuples are equal as rational numbers at every point,
    and the quoted sentence occurs verbatim, up to whitespace, in the LaTeX source in `paper/`."""
    quoted("Online Appendix B",
           r"Note that Scenario S is a special case of Scenario G if $\lambda^S = 1$ and $\lambda^N = 0$")
    for pt in random_points(5):
        a = args_of(pt)
        as_s, as_n = cf.find_general_exo(*a, 1, 0), cf.find_general_exo(*a, 0, 1)
        s, n = cf.first_period_s(*a, branch=True), cf.first_period_n(*a, branch=True)
        assert as_s == (s[0], s[1], cf.spfta_t1(*a, branch=True, branch2=True), cf.spftb_t1(*a, branch=True, branch2=True))
        assert as_n == (n[0], n[1], cf.npfta_t1(*a, branch=True, branch2=True), cf.npftb_t1(*a, branch=True, branch2=True))
    record("exact_rational_points", N_POINTS)


@pytest.mark.claims("L2.first", "L3.first")
def test_branch_conditions_in_the_code_are_the_fractile_orderings(record):
    """Which retailer has the higher critical fractile, as the code decides it.
    Points: 25 random rational parameter points (seed 6).
    Computed: the branch flag that `first_period_s` and `first_period_n` derive from an
    inequality in prices, and the comparison of the fractiles of Lemmas 2 and 3,
    c_B (p_{A,1} + g_A (p_{A,2} - c_A)) >= c_A (p_{B,1} + g_B (p_{B,2} - c_B)), with g_i = gamma
    in Scenario S and g_i = alpha_{i,2} gamma in Scenario N, in exact rational arithmetic.
    Criterion: the flag equals the comparison at every point, in both scenarios."""
    for pt in random_points(6):
        pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma = a = args_of(pt)
        a_a2 = share(pa2, pb2, beta)
        # Scenario S: zeta_A >= zeta_B  <=>  c_B (p_A1 + gamma (p_A2 - c_A)) >= c_A (p_B1 + gamma (p_B2 - c_B))
        paper_s = cb * (pa1 + gamma * (pa2 - ca)) >= ca * (pb1 + gamma * (pb2 - cb))
        # Scenario N: the same comparison with gamma replaced by alpha_{i,2} gamma
        paper_n = cb * (pa1 + a_a2 * gamma * (pa2 - ca)) >= ca * (pb1 + (1 - a_a2) * gamma * (pb2 - cb))
        assert cf.first_period_s(*a)[6] == paper_s
        assert cf.first_period_n(*a)[6] == paper_n
    record("exact_rational_points", N_POINTS)
