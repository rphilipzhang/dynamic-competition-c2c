"""Section 5: the claims that `section5` holds against the text of the paper.

The tests of Section 5 compare the model with the functions `section5.claimed_*`, which
transcribe Lemmas A.1 and A.2 and Propositions 8 and 9. A slip in one of those
transcriptions would go unnoticed there, because the tests would then check a claim other
than the paper's, and no comparison there would reveal it. This file guards against that in
the way `test_port_matches_paper.py` guards the closed forms of Section 4. Every claimed
formula is written a second time, next to the LaTeX string it transcribes. The test asserts
that each string occurs verbatim in the LaTeX source in `paper/`, and that the second
transcription agrees with `section5` at random markets.
"""
from __future__ import annotations

import numpy as np
import pytest

from c2c import paper, section5

APPENDIX = "Online Appendix A.2"
LEMMA_A1 = "Lemma A.1"
LEMMA_A2 = "Lemma A.2"
PROPOSITION_8 = "Proposition 8"
PROPOSITION_9 = "Proposition 9"

# The LaTeX strings that the second transcription below is written from.
QUOTES = {
    APPENDIX: [
        r"\widehat p_{i,2} :=1/(2\beta)+(2c_i+c_j)/3",
        r"\nu_i :=\alpha_{i,2}(\widehat p_{A,2},\widehat p_{B,2})(\widehat p_{i,2}-c_i)",
        r"\sigma\left(c_B-c_A\frac{\nu_B}{\nu_A}\right)(1+2\beta\overline{p}) >\beta(\mu+\sigma)\underline{p}^{\,2}. \label{eq:prop8b2}",
        r"\underline{p}<p_{B,1}< \min\left\{\overline{p},\ \sqrt{\frac{\sigma(c_B-c_A\nu_B/\nu_A)(1+2\beta p_{A,1})}{\beta(\mu+\sigma)}}\right\}. \label{eq:p8region}",
        r"\widehat p_{i,1} = \frac1{2\beta} +\frac{(\mu+\sigma)(2c_i+c_j)}{3\mu}",
    ],
    LEMMA_A1: [
        r"y_{A,1}^S=(\alpha_{A,1}+\theta\alpha_{B,1})\zeta_{A,1}^S -\theta\alpha_{B,1}\zeta_{B,1}^S$ and $y_{B,1}^S=\alpha_{B,1}\zeta_{B,1}^S",
        r"\zeta^S_{i,1} := F^{-1}(1 - \frac{c_i}{p_{i,1} + \gamma (\overline{p}-c_i)})",
        r"(p^S_{A,2}, p^S_{B,2})=(\overline{p},\overline{p})",
    ],
    LEMMA_A2: [
        r"y_{A,1}^N=(\alpha_{A,1}+\theta\alpha_{B,1})\zeta_{A,1}^N -\theta\alpha_{B,1}\zeta_{B,1}^N + O({\gamma^{-2}})$ and $y_{B,1}^N=\alpha_{B,1}\zeta_{B,1}^N + O({\gamma^{-2}})",
        r"\zeta^N_{A,1} = F^{-1}\left( 1- \frac{ c_A}{p_{A,1}+\gamma\nu_A} \right)",
        r"\zeta^N_{B,1} = F^{-1}\left( 1- \frac{c_B-\theta\gamma\nu_Bc_A/(p_{A,1}+\gamma\nu_A)}{p_{B,1}+(1-\theta)\gamma\nu_B} \right)",
    ],
    PROPOSITION_8: [
        r"$y^S_{i,1}$ decreases in $p_{i,1}$ and increases in $p_{j,1}$",
        r"$y^N_{A,1}$ decreases in $p_{A,1}$ and $y^N_{B,1}$ increases in $p_{A,1}$",
        r"$y^N_{A,1}$ decreases in $p_{B,1}$ and $y^N_{B,1}$ increases in $p_{B,1}$, provided that $\gamma>\gamma^D$ and $0\leq\gamma(1-\theta)\leq\ell^D$",
        r"for a fixed $\theta<1$ and sufficiently large $\gamma$, $y^N_{A,1}$ increases in $p_{B,1}$ and $y^N_{B,1}$ decreases in $p_{B,1}$",
    ],
    PROPOSITION_9: [
        r"\underline{p} = p^{S}_{i,1} < p^{S}_{i,2} = \overline{p}",
        r"\underline{p} < p^{N}_{i,2} < p^{N}_{i,1} < \overline{p}",
    ],
}

# Proposition 8, written a second time from the four sentences quoted above.
# The key is (part, retailer whose order it is, retailer whose price moves).
SLOPE_SIGNS = {
    ("a", "A", "A"): -1, ("a", "B", "B"): -1, ("a", "A", "B"): +1, ("a", "B", "A"): +1,
    ("b1", "A", "A"): -1, ("b1", "B", "A"): +1,
    ("b2 bounded", "A", "B"): -1, ("b2 bounded", "B", "B"): +1,
    ("b2 fixed", "A", "B"): +1, ("b2 fixed", "B", "B"): -1,
}


def second_transcription(mk, gamma, pa1, pb1):
    """The claimed objects of Section 5, written from the strings in QUOTES without
    looking at `section5`. Uniform seed demand gives F^{-1}(q) = mu - sigma + 2 sigma q."""
    ca, cb, beta, theta, mu, sigma, p_lo, p_hi = mk.ca, mk.cb, mk.beta, mk.theta, mk.mu, mk.sigma, mk.p_lo, mk.p_hi

    def quantile(q):
        return mu - sigma + 2 * sigma * q

    limit_a = 1 / (2 * beta) + (2 * ca + cb) / 3                 # \widehat p_{A,2}
    limit_b = 1 / (2 * beta) + (2 * cb + ca) / 3                 # \widehat p_{B,2}
    share_a2 = 1 / 2 + beta * (limit_b - limit_a)                # \alpha_{A,2} at the limit prices
    nu_a = share_a2 * (limit_a - ca)
    nu_b = (1 - share_a2) * (limit_b - cb)
    share_a1 = 1 / 2 + beta * (pb1 - pa1)
    share_b1 = 1 - share_a1

    zeta_s_a = quantile(1 - ca / (pa1 + gamma * (p_hi - ca)))    # Lemma A.1(a)
    zeta_s_b = quantile(1 - cb / (pb1 + gamma * (p_hi - cb)))
    orders_s = ((share_a1 + theta * share_b1) * zeta_s_a - theta * share_b1 * zeta_s_b, share_b1 * zeta_s_b)

    zeta_n_a = quantile(1 - ca / (pa1 + gamma * nu_a))           # Lemma A.2(a), without its O(gamma^-2) term
    zeta_n_b = quantile(1 - (cb - theta * gamma * nu_b * ca / (pa1 + gamma * nu_a)) / (pb1 + (1 - theta) * gamma * nu_b))
    orders_n = ((share_a1 + theta * share_b1) * zeta_n_a - theta * share_b1 * zeta_n_b, share_b1 * zeta_n_b)

    a22_left = sigma * (cb - ca * nu_b / nu_a) * (1 + 2 * beta * p_hi)            # (A.22)
    a22_right = beta * (mu + sigma) * p_lo ** 2
    a23_bound = np.sqrt(sigma * (cb - ca * nu_b / nu_a) * (1 + 2 * beta * pa1) / (beta * (mu + sigma)))   # (A.23)
    first_limit_a = 1 / (2 * beta) + (mu + sigma) * (2 * ca + cb) / (3 * mu)      # \widehat p_{A,1}, proof of Proposition 9
    first_limit_b = 1 / (2 * beta) + (mu + sigma) * (2 * cb + ca) / (3 * mu)
    return {"limit prices": (limit_a, limit_b), "nu": (nu_a, nu_b), "orders S": orders_s, "orders N": orders_n,
            "A.22 ratio": a22_left / a22_right, "A.23 bound": a23_bound, "first-period limit prices": (first_limit_a, first_limit_b)}


@pytest.mark.supports("LA1", "LA2", "P8", "P9")
def test_claims_of_section_5_are_transcribed_from_the_paper(repo_root, record):
    """`section5.claimed_*` against a second transcription of Lemmas A.1 and A.2 and
    Propositions 8 and 9.
    Points: 500 markets of `draw_market` (seed 5400), each with first-period prices uniform on
    the price box, gamma log-uniform on [1, 1e6], and two sorted prices uniform on the box for
    the price-path predicates.
    Computed: the 17 LaTeX strings of `QUOTES` against the LaTeX source in `paper/`, and both
    transcriptions of the limit prices, nu_i, the claimed first-period orders of Scenarios S
    and N, the ratio of the two sides of (A.22), the bound in (A.23) and the first-period
    limit prices of the proof of Proposition 9.
    Criterion: every string occurs verbatim, up to whitespace, every difference is at most
    1e-12 max(1, |value|), the claimed Scenario S prices are (p_lo, p_lo) and (p_hi, p_hi),
    the predicates of Proposition 9 accept and reject the test pairs as its inequalities
    require, and `CLAIMED_SLOPE_SIGNS` equals the table written from Proposition 8."""
    n_quotes = 0
    for result, strings in QUOTES.items():
        for latex in strings:
            paper.assert_quoted(latex)
            n_quotes += 1

    rng = np.random.default_rng(5400)
    n, worst = 500, 0.0
    for _ in range(n):
        mk = section5.draw_market(rng)
        gamma = float(np.exp(rng.uniform(0.0, np.log(1e6))))
        pa1, pb1 = rng.uniform(mk.p_lo, mk.p_hi, size=2)
        second = second_transcription(mk, gamma, pa1, pb1)
        first = {"limit prices": section5.claimed_limit_prices(mk), "nu": section5.claimed_nu(mk),
                 "orders S": section5.claimed_orders_s(mk, gamma, pa1, pb1),
                 "orders N": section5.claimed_orders_n(mk, gamma, pa1, pb1),
                 "A.22 ratio": section5.claimed_condition_a22(mk), "A.23 bound": section5.claimed_bound_a23(mk, pa1),
                 "first-period limit prices": section5.proof_first_period_limit_prices(mk)}
        for name, value in second.items():
            a, b = np.atleast_1d(np.asarray(first[name], float)), np.atleast_1d(np.asarray(value, float))
            error = float(np.max(np.abs(a - b) / np.maximum(1.0, np.abs(b))))
            worst = max(worst, error)
            assert error <= 1e-12, (name, mk, gamma, pa1, pb1, first[name], value)
        assert section5.claimed_second_period_prices_s(mk) == (mk.p_hi, mk.p_hi)
        assert section5.claimed_first_period_prices_s(mk) == (mk.p_lo, mk.p_lo)
        inside = np.sort(rng.uniform(mk.p_lo, mk.p_hi, size=2))
        if mk.p_lo < inside[0] < inside[1] < mk.p_hi:
            assert section5.claimed_price_path_n(mk, inside[1], inside[0])          # the first-period price is the higher one
            assert not section5.claimed_price_path_n(mk, inside[0], inside[1])
        assert section5.claimed_price_path_s(mk, mk.p_lo, mk.p_hi)
        assert not section5.claimed_price_path_s(mk, mk.p_hi, mk.p_lo)
        assert not section5.claimed_price_path_s(mk, mk.p_lo, inside[0])
    assert section5.CLAIMED_SLOPE_SIGNS == SLOPE_SIGNS
    record("latex_strings_found_in_the_paper", n_quotes)
    record("random_points", n)
    record("largest_relative_difference", worst, stable=False)
