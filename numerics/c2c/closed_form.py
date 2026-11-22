"""Closed-form equilibrium quantities and profits under uniform seed demand.

This module is a line-by-line Python port of the authors' MATLAB functions in
`numerics/matlab/`. Each function names the MATLAB file it ports and keeps the
order of the arithmetic, so that the two can be compared side by side. The
formulas are the paper's closed forms specialised to

    X_t ~ U[mu - sigma, mu + sigma],   rho = 1          (assumption A10),

for which F^{-1}(q) = mu - sigma + 2 sigma q.

Nothing here is derived independently of the paper. Independent computations
from the model primitives live in `c2c.primitives`, and the tests in
`numerics/tests/` compare the two.

Naming of arguments (identical to the MATLAB code):
    pa1, pb1, pa2, pb2   prices of retailers A and B in periods 1 and 2
    ca, cb               unit ordering costs (c_A < c_B)
    theta                stockout-based substitution rate
    beta                 price sensitivity of the demand split
    mu, sigma            seed demand is uniform on [mu - sigma, mu + sigma]
    gamma                strength of C2C interactions

The functions use only +, -, *, / and comparisons, so they also accept SymPy
symbols. Pass `branch` explicitly in that case, because a comparison of
symbols cannot be evaluated.
"""
from __future__ import annotations

__all__ = [
    "finv_uniform", "pfta_t2_case1", "pftb_t2_case1", "period2_base_profits", "period2_profit",
    "first_period_s", "first_period_n", "spfta_t1", "spftb_t1", "npfta_t1", "npftb_t1",
    "find_general_exo",
]


def finv_uniform(q, mu, sigma):
    """Quantile function of U[mu - sigma, mu + sigma]."""
    return mu - sigma + 2 * sigma * q


def _share(p_own, p_other, beta):
    """Market share 1/2 + beta (p_other - p_own).

    Written as (1 + 2 beta (p_other - p_own)) / 2 so that the function stays
    exact when it is called with rational numbers or symbols. In IEEE
    double-precision arithmetic the two forms give bit-identical results,
    because multiplying or dividing by 2 commutes with rounding.
    """
    return (1 + 2*beta*(p_other - p_own)) / 2


# --------------------------------------------------------------------------- period 2
def pfta_t2_case1(pa2, pb2, theta, ca, cb, beta, mu, sigma):
    """Port of `Figure1_MATLAB/pftaT2Case1.m`.

    Benchmark expected profit pi^0 of the retailer with the HIGHER critical
    fractile (first argument pair), written as one rational function.
    Paper: pi^0_{A,t} at the end of the proof of Lemma 1, under A10.
    """
    numerator = (
        ca**2 * pb2**2 * (1 + 2*pa2*beta*(-1 + theta) - 2*pb2*beta*(-1 + theta) + theta) * sigma
        + pa2**2 * (2*pb2**3*beta*mu + pb2**2*(mu - 2*pa2*beta*mu)
                    - 2*cb**2*pb2*beta*theta*sigma + cb**2*(1 + 2*pa2*beta)*theta*sigma)
        + ca*pa2*pb2 * (pb2*(-1 + 2*pa2*beta)*mu - 2*cb*(1 + 2*pa2*beta)*theta*sigma
                        + pb2*(-1 + 2*pa2*beta + 4*cb*beta*theta)*sigma - 2*pb2**2*beta*(mu + sigma))
    )
    denominator = 2 * pa2 * pb2**2
    return numerator / denominator


def pftb_t2_case1(pa2, pb2, cb, beta, mu, sigma):
    """Port of `Figure1_MATLAB/pftbT2Case1.m`.

    Benchmark expected profit pi^0 of the retailer with the LOWER critical
    fractile. Paper: pi^0_{B,t} at the end of the proof of Lemma 1, under A10.
    """
    numerator = -((cb - pb2) * (-1 - 2*pa2*beta + 2*pb2*beta) * ((-pb2)*mu + cb*sigma))
    denominator = 2 * pb2
    return numerator / denominator


def period2_base_profits(pa2, pb2, theta, ca, cb, beta, mu, sigma, branch=None):
    """Benchmark second-period profits (pi^0_{A,2}, pi^0_{B,2}) for either
    ordering of the critical fractiles. First half of `period2_profit.m`.

    branch: True if c_A / p_{A,2} <= c_B / p_{B,2} (B stocks out first or
    simultaneously). Evaluated from the arguments when None.
    """
    if branch is None:
        branch = ca / pa2 <= cb / pb2
    if branch:
        base_a = pfta_t2_case1(pa2, pb2, theta, ca, cb, beta, mu, sigma)
        base_b = pftb_t2_case1(pa2, pb2, cb, beta, mu, sigma)
    else:
        base_a = pftb_t2_case1(pb2, pa2, ca, beta, mu, sigma)
        base_b = pfta_t2_case1(pb2, pa2, theta, cb, ca, beta, mu, sigma)
    return base_a, base_b


def period2_profit(pa2, pb2, theta, ca, cb, beta, mu, sigma, scenario, gamma, sales_a1, sales_b1,
                   branch=None):
    """Port of `Figure1_MATLAB/period2_profit.m`.

    Expected second-period equilibrium profits given realized first-period
    sales. Paper: proofs of Lemma 2 (Scenario S) and Lemma 3 (Scenario N):
    pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2}, with Z^S_{i,2} = gamma R_{i,1} and
    Z^N_{i,2} = alpha_{i,2} gamma (R_{A,1} + R_{B,1}).
    """
    base_a, base_b = period2_base_profits(pa2, pb2, theta, ca, cb, beta, mu, sigma, branch)
    if scenario == "S":
        extra_a = gamma * sales_a1
        extra_b = gamma * sales_b1
    elif scenario == "N":
        share_a = _share(pa2, pb2, beta)
        expansion = gamma * (sales_a1 + sales_b1)
        extra_a = share_a * expansion
        extra_b = (1 - share_a) * expansion
    else:
        raise ValueError("Use 'S' or 'N' for the C2C scenario.")
    profit_a = base_a + (pa2 - ca) * extra_a
    profit_b = base_b + (pb2 - cb) * extra_b
    return profit_a, profit_b


# --------------------------------------------------------------------------- period 1, expected leftovers
def _leftover_high(a_own, a_other, theta, z_own, z_other, mu, sigma):
    """E[(y - D)^+] of the retailer with the higher critical fractile, whose
    order is (a_own + theta a_other) z_own - theta a_other z_other. The two
    shares are passed separately, as the MATLAB code writes them, so that the
    arithmetic is the same in both branches."""
    return (
        1/(2*sigma) * ((a_own + theta*a_other)*z_own - theta*a_other*z_other) * (z_other - mu + sigma)
        - (1/(2*sigma)) * (a_own/2) * (z_other**2 - (mu - sigma)**2)
        + 1/(2*sigma) * (a_own + theta*a_other) * z_own * (z_own - z_other)
        - 1/(2*sigma) * (a_own + theta*a_other)/2 * (z_own**2 - z_other**2)
    )


def _leftover_low(a_own, z_own, mu, sigma):
    """E[(y - D)^+] of the retailer with the lower critical fractile, whose
    order is a_own z_own."""
    return a_own/2 * (1/(2*sigma)) * (z_own - mu + sigma)**2


def first_period_s(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma, branch=None):
    """First-period equilibrium of Scenario S. Shared body of `SpftaT1.m` and `SpftbT1.m`.

    Returns (ya1, yb1, lefta1, leftb1, za, zb, branch). Paper: Lemma 2.
    branch True means zeta^S_{A,1} >= zeta^S_{B,1}, the case covered by Lemma 2
    under assumption A11. The other case is the mirror image and is needed
    only for the Endogenous Price Model, where A11 is dropped.
    """
    alpha1 = _share(pa1, pb1, beta)
    if branch is None:
        branch = pa1 >= ca/cb*pb1 + gamma/cb*(ca*(pb2 - cb) - cb*(pa2 - ca))
    za = mu - sigma + 2*sigma*(1 - ca/(pa1 + gamma*(pa2 - ca)))
    zb = mu - sigma + 2*sigma*(1 - cb/(pb1 + gamma*(pb2 - cb)))
    if branch:
        ya1 = (alpha1 + theta*(1 - alpha1))*za - theta*(1 - alpha1)*zb
        yb1 = (1 - alpha1)*zb
        lefta1 = _leftover_high(alpha1, 1 - alpha1, theta, za, zb, mu, sigma)
        leftb1 = _leftover_low(1 - alpha1, zb, mu, sigma)
    else:
        ya1 = alpha1*za
        yb1 = (1 - alpha1 + theta*alpha1)*zb - theta*alpha1*za
        lefta1 = _leftover_low(alpha1, za, mu, sigma)
        leftb1 = _leftover_high(1 - alpha1, alpha1, theta, zb, za, mu, sigma)
    return ya1, yb1, lefta1, leftb1, za, zb, branch


def spfta_t1(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma, branch=None, branch2=None):
    """Port of `Figure1_MATLAB/SpftaT1.m`. Total two-period profit Pi^S_A
    given the continuation prices (pa2, pb2). Paper: equation (A.8)."""
    pfta2, _ = period2_profit(pa2, pb2, theta, ca, cb, beta, mu, sigma, "S", gamma, 0, 0, branch2)
    ya1, _, lefta1, _, _, _, _ = first_period_s(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma, branch)
    return (pa1 - ca + gamma*(pa2 - ca))*ya1 - (pa1 + gamma*(pa2 - ca))*lefta1 + pfta2


def spftb_t1(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma, branch=None, branch2=None):
    """Port of `Figure1_MATLAB/SpftbT1.m`. Total two-period profit Pi^S_B. Paper: equation (A.10)."""
    _, pftb2 = period2_profit(pa2, pb2, theta, ca, cb, beta, mu, sigma, "S", gamma, 0, 0, branch2)
    _, yb1, _, leftb1, _, _, _ = first_period_s(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma, branch)
    return (pb1 - cb + gamma*(pb2 - cb))*yb1 - (pb1 + gamma*(pb2 - cb))*leftb1 + pftb2


def first_period_n(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma, branch=None):
    """First-period equilibrium of Scenario N. Shared body of `NpftaT1.m` and `NpftbT1.m`.

    Returns (ya1, yb1, lefta1, leftb1, za, zb, branch). Paper: Lemma 3.
    branch True means retailer A has the higher critical fractile, the case
    covered by Lemma 3 under assumption A11.
    """
    alpha2 = _share(pa2, pb2, beta)
    alpha1 = _share(pa1, pb1, beta)
    if branch is None:
        branch = pa1 >= ca/cb*pb1 + gamma/cb*((1 - alpha2)*ca*(pb2 - cb) - alpha2*cb*(pa2 - ca))
    if branch:
        za = mu - sigma + 2*sigma*(1 - ca/(pa1 + alpha2*gamma*(pa2 - ca)))
        zb = mu - sigma + 2*sigma*(1 - (cb - (1 - alpha2)*(pb2 - cb)*gamma*theta*ca/(pa1 + alpha2*gamma*(pa2 - ca)))
                                   / (pb1 + gamma*(1 - alpha2)*(pb2 - cb)*(1 - theta)))
        ya1 = (alpha1 + theta*(1 - alpha1))*za - theta*(1 - alpha1)*zb
        yb1 = (1 - alpha1)*zb
        lefta1 = _leftover_high(alpha1, 1 - alpha1, theta, za, zb, mu, sigma)
        leftb1 = _leftover_low(1 - alpha1, zb, mu, sigma)
    else:
        za = mu - sigma + 2*sigma*(1 - (ca - alpha2*(pa2 - ca)*gamma*theta*cb/(pb1 + (1 - alpha2)*gamma*(pb2 - cb)))
                                   / (pa1 + gamma*alpha2*(pa2 - ca)*(1 - theta)))
        zb = mu - sigma + 2*sigma*(1 - cb/(pb1 + (1 - alpha2)*gamma*(pb2 - cb)))
        ya1 = alpha1*za
        yb1 = (1 - alpha1 + theta*alpha1)*zb - theta*alpha1*za
        lefta1 = _leftover_low(alpha1, za, mu, sigma)
        leftb1 = _leftover_high(1 - alpha1, alpha1, theta, zb, za, mu, sigma)
    return ya1, yb1, lefta1, leftb1, za, zb, branch


def npfta_t1(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma, branch=None, branch2=None):
    """Port of `Figure1_MATLAB/NpftaT1.m`. Total two-period profit Pi^N_A. Paper: equation (A.12)."""
    pfta2, _ = period2_profit(pa2, pb2, theta, ca, cb, beta, mu, sigma, "N", gamma, 0, 0, branch2)
    alpha2 = _share(pa2, pb2, beta)
    ya1, yb1, lefta1, leftb1, _, _, _ = first_period_n(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma, branch)
    return ((pa1 - ca + gamma*alpha2*(pa2 - ca))*ya1 - (pa1 + gamma*alpha2*(pa2 - ca))*lefta1
            + gamma*alpha2*(pa2 - ca)*yb1 - gamma*alpha2*(pa2 - ca)*leftb1 + pfta2)


def npftb_t1(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma, branch=None, branch2=None):
    """Port of `Figure1_MATLAB/NpftbT1.m`. Total two-period profit Pi^N_B. Paper: equation (A.14)."""
    _, pftb2 = period2_profit(pa2, pb2, theta, ca, cb, beta, mu, sigma, "N", gamma, 0, 0, branch2)
    alpha2 = _share(pa2, pb2, beta)
    ya1, yb1, lefta1, leftb1, _, _, _ = first_period_n(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma, branch)
    return ((pb1 - cb + gamma*(1 - alpha2)*(pb2 - cb))*yb1 - (pb1 + gamma*(1 - alpha2)*(pb2 - cb))*leftb1
            + gamma*(1 - alpha2)*(pb2 - cb)*ya1 - gamma*(1 - alpha2)*(pb2 - cb)*lefta1 + pftb2)


# --------------------------------------------------------------------------- mixed scenario (Online Appendix B)
def find_general_exo(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma, lam_s, lam_n):
    """Port of `Figure2_MATLAB/FindGeneral_exo.m`.

    Returns (ya1, yb1, profit_a, profit_b): first-period equilibrium order
    quantities and total two-period profits when within-brand and cross-brand
    C2C interactions are mixed with weights lam_s and lam_n. Paper: Lemma B.1.
    Only the case covered by Lemma B.1 (retailer A has the higher critical
    fractile, assumption A11) is implemented, as in the MATLAB code.
    """
    alpha_a1 = _share(pa1, pb1, beta)
    alpha_b1 = 1 - alpha_a1
    alpha_a2 = _share(pa2, pb2, beta)
    alpha_b2 = 1 - alpha_a2

    gamma_a2 = gamma*(lam_s + lam_n*alpha_a2)
    gamma_b2 = gamma*(lam_s + lam_n*alpha_b2)
    gamma_c_a2 = gamma*lam_n*alpha_a2
    gamma_c_b2 = gamma*lam_n*alpha_b2

    fa = 1 - ca/(pa1 + gamma_a2*(pa2 - ca))
    za = mu - sigma + 2*sigma*fa
    fb = 1 - (cb - gamma_c_b2*theta*(pb2 - cb)*ca/(pa1 + gamma_a2*(pa2 - ca))) / (pb1 + (gamma_b2 - gamma_c_b2*theta)*(pb2 - cb))
    zb = mu - sigma + 2*sigma*fb

    ya1 = (alpha_a1 + theta*alpha_b1)*za - theta*alpha_b1*zb
    yb1 = alpha_b1*zb

    lefta1 = (1/(2*sigma)*((alpha_a1 + theta*alpha_b1)*za - theta*alpha_b1*zb)*(zb - mu + sigma)
              - (1/(2*sigma))*(alpha_a1/2)*(zb**2 - (mu - sigma)**2)
              + 1/(2*sigma)*(alpha_a1 + theta*alpha_b1)*za*(za - zb)
              - 1/(2*sigma)*(alpha_a1 + theta*alpha_b1)/2*(za**2 - zb**2))
    leftb1 = alpha_b1/2*(1/(2*sigma))*(zb - mu + sigma)**2

    za2 = mu - sigma + 2*sigma*(1 - ca/pa2)
    zb2 = mu - sigma + 2*sigma*(1 - cb/pb2)
    ya2 = (alpha_a2 + theta*alpha_b2)*za2 - theta*alpha_b2*zb2
    yb2 = alpha_b2*zb2
    lefta2 = (1/(2*sigma)*((alpha_a2 + theta*alpha_b2)*za2 - theta*alpha_b2*zb2)*(zb2 - mu + sigma)
              - (1/(2*sigma))*(alpha_a2/2)*(zb2**2 - (mu - sigma)**2)
              + 1/(2*sigma)*(alpha_a2 + theta*alpha_b2)*za2*(za2 - zb2)
              - 1/(2*sigma)*(alpha_a2 + theta*alpha_b2)/2*(za2**2 - zb2**2))
    leftb2 = alpha_b2/2*(1/(2*sigma))*(zb2 - mu + sigma)**2

    pfta2 = (pa2 - ca)*ya2 - pa2*lefta2
    pftb2 = (pb2 - cb)*yb2 - pb2*leftb2

    profit_a = ((pa1 - ca + gamma_a2*(pa2 - ca))*ya1 - (pa1 + gamma_a2*(pa2 - ca))*lefta1
                + gamma_c_a2*(pa2 - ca)*yb1 - gamma_c_a2*(pa2 - ca)*leftb1 + pfta2)
    profit_b = ((pb1 - cb + gamma_b2*(pb2 - cb))*yb1 - (pb1 + gamma_b2*(pb2 - cb))*leftb1
                + gamma_c_b2*(pb2 - cb)*ya1 - gamma_c_b2*(pb2 - cb)*lefta1 + pftb2)
    return ya1, yb1, profit_a, profit_b
