"""Section 4 helpers: the paper's claims on one side, the model computed from its definition on the other.

`claimed_*` functions transcribe what the paper claims (Lemmas 1 to 3 and B.1)
for a general demand distribution, through its quantile function.
`Game` builds the retailers' payoffs from the model primitives only
(`c2c.primitives`). The tests compare the two.

Samplers
    draw_exogenous          floating-point points inside the region of Section 4
    draw_exogenous_exact    the same region on a lattice of rational numbers
    draw_edge_exact         rational points on the edges of the region that Section 4 allows
    draw_without_a11        floating-point points of Section 4 without A11, so that either retailer
                            can have the higher critical fractile
    draw_bounded_prices     floating-point points that satisfy A12 and A13 (Section 5)

`SAMPLED_REGION` states the bounds of every sampler. The bounds of the regular
samplers are narrower than the assumptions of the paper. The edge sampler
exists to reach what the regular samplers cannot: equality in the price
condition A11, equal prices, theta at 0 and at 1, and extreme ratios.

Seeds
    Every test passes a fixed seed to `seeded_rng`, so two runs give the same
    report. A robustness study can shift all seeds at once by setting the
    environment variable C2C_SEED_OFFSET to a positive integer.
"""
from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction

import numpy as np
from scipy import stats

from c2c import primitives as pm

SEED_OFFSET = int(os.environ.get("C2C_SEED_OFFSET", "0"))


def seeded_rng(seed: int):
    """The random generator of a test. The offset is zero unless a robustness
    study sets the environment variable C2C_SEED_OFFSET."""
    return np.random.default_rng(seed + 7919 * SEED_OFFSET)


@dataclass(frozen=True)
class Params:
    pa1: float
    pb1: float
    pa2: float
    pb2: float
    ca: float
    cb: float
    beta: float
    theta: float
    gamma: float
    lam_s: float = 1.0
    lam_n: float = 0.0

    @property
    def aa1(self):
        return pm.share(self.pa1, self.pb1, self.beta)

    @property
    def aa2(self):
        return pm.share(self.pa2, self.pb2, self.beta)

    def weights(self, scenario):
        """(gamma_A, gamma_B, gammaC_A, gammaC_B) with Z_{i,2} = gamma_i R_{i,1} + gammaC_i R_{j,1}.
        This is the notation of Online Appendix B. Scenarios S and N are special cases."""
        g, a = self.gamma, self.aa2
        if scenario == "0":
            return 0.0, 0.0, 0.0, 0.0
        if scenario == "S":
            return g, g, 0.0, 0.0
        if scenario == "N":
            return a * g, (1 - a) * g, a * g, (1 - a) * g
        if scenario == "G":
            return ((self.lam_s + self.lam_n * a) * g, (self.lam_s + self.lam_n * (1 - a)) * g,
                    self.lam_n * g * a, self.lam_n * g * (1 - a))
        raise ValueError(scenario)


# ----------------------------------------------------------------------------- what the paper claims
def claimed_benchmark(p_a, p_b, ca, cb, beta, theta, ppf):
    """Lemma 1 for one period, for either ordering of the critical fractiles.
    Returns (y_A, y_B, q_A, q_B) where q_i = 1 - c_i / p_i."""
    a_a = pm.share(p_a, p_b, beta)
    a_b = 1 - a_a
    q_a, q_b = 1 - ca / p_a, 1 - cb / p_b
    z_a, z_b = ppf(q_a), ppf(q_b)
    if q_a >= q_b:
        return (a_a + theta * a_b) * z_a - theta * a_b * z_b, a_b * z_b, q_a, q_b
    return a_a * z_a, (a_b + theta * a_a) * z_b - theta * a_a * z_a, q_a, q_b


def claimed_first_period(prm: Params, scenario: str, ppf):
    """Lemmas 2, 3 and B.1 (and Lemma 1 for scenario "0"): first-period
    equilibrium order quantities. Returns (y_A, y_B, q_A, q_B, a_has_higher_fractile).

    The lemmas state the case in which retailer A has the higher critical
    fractile, which assumption A11 guarantees. The mirror image is returned in
    the other case. The paper uses it for the Endogenous Price Model.
    """
    g_a, g_b, gc_a, gc_b = prm.weights(scenario)
    a_a, a_b = prm.aa1, 1 - prm.aa1
    th = prm.theta
    m_a, m_b = prm.pa2 - prm.ca, prm.pb2 - prm.cb           # second-period margins
    own_a = prm.ca / (prm.pa1 + g_a * m_a)
    own_b = prm.cb / (prm.pb1 + g_b * m_b)
    if own_a <= own_b:
        q_a = 1 - own_a
        q_b = 1 - (prm.cb - gc_b * th * m_b * own_a) / (prm.pb1 + (g_b - gc_b * th) * m_b)
        z_a, z_b = ppf(q_a), ppf(q_b)
        return (a_a + th * a_b) * z_a - th * a_b * z_b, a_b * z_b, q_a, q_b, True
    q_b = 1 - own_b
    q_a = 1 - (prm.ca - gc_a * th * m_a * own_b) / (prm.pa1 + (g_a - gc_a * th) * m_a)
    z_a, z_b = ppf(q_a), ppf(q_b)
    return a_a * z_a, (a_b + th * a_a) * z_b - th * a_a * z_a, q_a, q_b, False


# ----------------------------------------------------------------------------- the model itself
class Game:
    """Payoffs of the two-period game, computed from the model primitives."""

    def __init__(self, prm: Params, scenario: str, dist):
        self.prm, self.scenario, self.dist = prm, scenario, dist
        self.upper = 1.5 * float(dist.ppf(1.0)) * (1 + prm.gamma)   # generous bound for the search

    # ---- period 2 at a given sales state
    def period2_payoffs(self, ra1, rb1):
        p = self.prm
        za, zb = pm.c2c_demand(self.scenario, p.gamma, ra1, rb1, p.aa2, p.lam_s, p.lam_n)

        def payoff_a(ya, yb):
            era, _ = self.dist.expected_sales(ya, yb, p.aa2, 1 - p.aa2, p.theta, za, zb)
            return p.pa2 * era - p.ca * np.atleast_1d(ya)

        def payoff_b(ya, yb):
            _, erb = self.dist.expected_sales(ya, yb, p.aa2, 1 - p.aa2, p.theta, za, zb)
            return p.pb2 * erb - p.cb * np.atleast_1d(yb)

        return payoff_a, payoff_b, za, zb

    def period2_value(self, ra1, rb1):
        """Second-period profits at the claimed second-period equilibrium
        y_{i,2} = y^0_{i,2} + Z_{i,2}, evaluated from the primitives."""
        p = self.prm
        y0a, y0b, *_ = claimed_benchmark(p.pa2, p.pb2, p.ca, p.cb, p.beta, p.theta, self.dist.ppf)
        payoff_a, payoff_b, za, zb = self.period2_payoffs(ra1, rb1)
        ya, yb = y0a + za, y0b + zb
        return float(payoff_a(ya, yb)[0]), float(payoff_b(ya, yb)[0]), ya, yb

    # ---- period 1
    def period1_payoffs(self):
        """Total two-period payoffs as functions of the first-period orders.

        The continuation value is affine in first-period sales:
        V_i = pi^0_i + (p_{i,2} - c_i) Z_{i,2}. `test_second_period_*` checks
        this from the primitives. Because it is affine, its expectation only
        needs the expected first-period sales.
        """
        p = self.prm
        g_a, g_b, gc_a, gc_b = p.weights(self.scenario)
        pi0_a, pi0_b, *_ = self.period2_value(0.0, 0.0)

        def payoff_a(ya, yb):
            era, erb = self.dist.expected_sales(ya, yb, p.aa1, 1 - p.aa1, p.theta)
            return p.pa1 * era - p.ca * np.atleast_1d(ya) + (p.pa2 - p.ca) * (g_a * era + gc_a * erb) + pi0_a

        def payoff_b(ya, yb):
            era, erb = self.dist.expected_sales(ya, yb, p.aa1, 1 - p.aa1, p.theta)
            return p.pb1 * erb - p.cb * np.atleast_1d(yb) + (p.pb2 - p.cb) * (g_b * erb + gc_b * era) + pi0_b

        return payoff_a, payoff_b


def scan_fixed_points(payoff_a, payoff_b, upper, scale, coarse=21, fine=41, grid=801):
    """Scan a two-player game for Nash equilibria.

    Each payoff is concave in the player's own quantity, so best responses are
    single-valued. A pair (y_A, y_B) is then an equilibrium exactly when y_B is
    a fixed point of T(y_B) = BR_B(BR_A(y_B)) and y_A = BR_A(y_B).

    T is evaluated on `coarse` equally spaced values of y_B in [0, upper].
    Every fixed point lies in the range of T. T is therefore evaluated again
    on `fine` equally spaced values in the interval that the coarse values of
    T span, widened on both sides by 5 percent of its length, by at least one
    thousandth of `scale`, and by at least twenty times the noise defined
    below. `scale` is the size of the seed demand.

    A numerical best response is accurate to about 1.5e-8 times its size,
    which is the square root of the machine precision. The noise allowance is
    1e-6 times the larger of `scale` and the largest value of T. A node at
    which |T(y_B) - y_B| is at most the noise counts as lying on the fixed
    point and is skipped.

    Returns the number of evaluations, the noise, the sign of T(y_B) - y_B at
    the lowest and at the highest node, and one bracket (y_low, y_high) for
    every change of sign between neighbouring nodes.
    """
    def composed(yb):
        ya, _ = pm.best_response(lambda y: payoff_a(y, yb), upper, grid=grid)
        return pm.best_response(lambda y: payoff_b(ya, y), upper, grid=grid)[0]

    nodes = np.linspace(0.0, upper, coarse)
    values = np.array([composed(y) for y in nodes])
    noise = 1e-6 * max(scale, float(values.max()))
    pad = max(0.05 * float(np.ptp(values)), 1e-3 * scale, 20 * noise)
    extra = np.linspace(max(0.0, values.min() - pad), min(upper, values.max() + pad), fine)
    nodes = np.concatenate([nodes, extra])
    values = np.concatenate([values, [composed(y) for y in extra]])
    order = np.argsort(nodes, kind="stable")
    nodes, values = nodes[order], values[order]
    gap = values - nodes
    sign = np.sign(np.where(np.abs(gap) <= noise, 0.0, gap))
    keep = sign != 0
    nodes, sign = nodes[keep], sign[keep]
    change = np.nonzero(sign[:-1] != sign[1:])[0]
    return {"evaluations": int(order.size), "noise": noise, "first_sign": float(sign[0]), "last_sign": float(sign[-1]),
            "brackets": [(float(nodes[k]), float(nodes[k + 1])) for k in change]}


# ----------------------------------------------------------------------------- sampling, floating point
REGULAR = {                                                 # the bounds shared by the two regular samplers
    "cb": (0.5, 3.0), "cost_ratio": (0.05, 0.98), "mu": (5.0, 20.0), "sigma_over_mu": (0.1, 0.95),
    "pb_over_cb": (1.05, 4.0), "beta_times_gap": 0.45, "beta_cap": 0.5, "gamma": (0.05, 50.0),
}


def draw_exogenous(rng, scenario="S", equal_shares=False) -> tuple[Params, float, float]:
    """A random floating-point parameter point of Section 4 (A1, A11, I1, I2).
    Returns (Params, mu, sigma). The argument `scenario` is not used.

    The sampled region is narrower than the assumptions allow.
        c_B                  uniform on [0.5, 3]
        c_A / c_B            uniform on [0.05, 0.98]
        mu                   uniform on [5, 20]
        sigma / mu           uniform on [0.1, 0.95]
        p_{B,t} / c_B        uniform on [1.05, 4] in each period
        p_{A,t}              uniform between (c_A / c_B) p_{B,t} and p_{B,t}
        beta                 uniform between 0 and 0.45 / (largest price gap), at most 0.5
        theta                uniform on (0, 1)
        gamma                log-uniform on [0.05, 50]
        lambda_S             uniform on (0, 1)
    With `equal_shares` the price gap p_{B,t} - p_{A,t} is the same in both
    periods, a uniform fraction of the smallest gap that A11 allows.

    Never reached: equality in A11, p_A = p_B, theta equal to 0 or 1, a share
    of retailer B below 0.05. `draw_edge_exact` covers those.
    """
    r = REGULAR
    cb = rng.uniform(*r["cb"])
    ca = cb * rng.uniform(*r["cost_ratio"])
    mu = rng.uniform(*r["mu"])
    sigma = mu * rng.uniform(*r["sigma_over_mu"])
    pb1, pb2 = cb * rng.uniform(*r["pb_over_cb"], size=2)
    pa1 = rng.uniform(ca / cb * pb1, pb1)
    pa2 = rng.uniform(ca / cb * pb2, pb2)
    if equal_shares:                                        # same price gap, hence same shares, in both periods
        gap = min(pb1 - ca / cb * pb1, pb2 - ca / cb * pb2) * rng.uniform(0.0, 1.0)
        pa1, pa2 = pb1 - gap, pb2 - gap
    beta = min(r["beta_cap"], rng.uniform(0.0, r["beta_times_gap"] / max(pb1 - pa1, pb2 - pa2, 1e-9)))
    lam_s = rng.uniform(0.0, 1.0)
    prm = Params(pa1, pb1, pa2, pb2, ca, cb, beta, theta=rng.uniform(0.0, 1.0),
                 gamma=float(np.exp(rng.uniform(np.log(r["gamma"][0]), np.log(r["gamma"][1])))),
                 lam_s=lam_s, lam_n=1 - lam_s)
    return prm, mu, sigma


def draw_without_a11(rng) -> tuple[Params, float, float]:
    """A point of `draw_exogenous` whose four prices are replaced by
    independent uniform draws on [1.05 c_B, 4 c_B]. No ordering of the prices
    is imposed, so assumption A11 fails at most of these points and retailer B
    has the higher critical fractile at some of them. beta is reduced where
    necessary so that the share of each retailer stays above 0.05."""
    prm, mu, sigma = draw_exogenous(rng)
    lo, hi = REGULAR["pb_over_cb"]
    pa1, pb1, pa2, pb2 = prm.cb * rng.uniform(lo, hi, size=4)
    beta = min(prm.beta, REGULAR["beta_times_gap"] / max(abs(pb1 - pa1), abs(pb2 - pa2), 1e-9))
    return Params(pa1, pb1, pa2, pb2, prm.ca, prm.cb, beta, prm.theta, prm.gamma, prm.lam_s, prm.lam_n), mu, sigma


def draw_bounded_prices(rng) -> dict:
    """A random floating-point parameter point of Section 5 (A1, A10, A12, A13).

    Returns a dictionary with the costs, mu, sigma, beta, the price bounds
    p_lo and p_hi, theta and gamma.
        c_B, c_A / c_B, mu, sigma / mu   as in `draw_exogenous`
        beta                 uniform on [0.02, 0.6]
        p_hi                 the lower bound of A13 plus 1 to 100 percent of
                             w = (mu + sigma) (c_A + 2 c_B) / (3 mu), so that
                             1/(2 beta) + 1.01 w <= p_hi <= 1/(2 beta) + 2 w
        p_lo                 uniform on the interval that A12 and A13 leave,
                             shrunk by one thousandth at both ends
        theta                0 with probability 1/8, 1 with probability 1/8,
                             otherwise uniform on (0, 1)
        gamma                log-uniform on [0.05, 50]
    Draws for which A12 and A13 leave no room for p_lo are rejected.
    """
    r = REGULAR
    while True:
        cb = rng.uniform(*r["cb"])
        ca = cb * rng.uniform(*r["cost_ratio"])
        mu = rng.uniform(*r["mu"])
        sigma = mu * rng.uniform(*r["sigma_over_mu"])
        beta = rng.uniform(0.02, 0.6)
        u = 1.0 / (2.0 * beta)
        w = (mu + sigma) / (3.0 * mu) * (ca + 2.0 * cb)
        p_hi = u + w * (1.0 + rng.uniform(0.01, 1.0))                  # p_hi > 1/(2 beta) + (mu+sigma)(c_A+2c_B)/(3 mu)
        lo_min = max(cb, p_hi - u) * 1.001                              # p_lo > c_B and beta < 1/(2 (p_hi - p_lo))
        lo_max = min(u + (2.0 * ca + cb) / 3.0, p_hi) * 0.999           # p_lo < 1/(2 beta) + (2c_A+c_B)/3
        if lo_min < lo_max:
            p_lo = rng.uniform(lo_min, lo_max)
            pick = rng.uniform()
            theta = 0.0 if pick < 0.125 else 1.0 if pick < 0.25 else rng.uniform(0.0, 1.0)
            gamma = float(np.exp(rng.uniform(np.log(r["gamma"][0]), np.log(r["gamma"][1]))))
            return dict(ca=ca, cb=cb, mu=mu, sigma=sigma, beta=beta, p_lo=p_lo, p_hi=p_hi, theta=theta, gamma=gamma)


# ----------------------------------------------------------------------------- sampling, exact rational numbers
@dataclass(frozen=True)
class ExactPoint:
    """A parameter point of Section 4 whose coordinates are rational numbers.

    The closed forms of `c2c.closed_form` use only the four arithmetic
    operations, so they can be evaluated at such a point without rounding.
    Signs, orderings and equalities are then decided exactly.
    """
    pa1: Fraction
    pb1: Fraction
    pa2: Fraction
    pb2: Fraction
    ca: Fraction
    cb: Fraction
    beta: Fraction
    mu: Fraction
    sigma: Fraction
    theta: Fraction
    gamma: Fraction
    lam_s: Fraction
    kind: str = "regular"

    @property
    def aa1(self):
        return Fraction(1, 2) + self.beta * (self.pb1 - self.pa1)

    @property
    def aa2(self):
        return Fraction(1, 2) + self.beta * (self.pb2 - self.pa2)

    @property
    def binds1(self):
        """Equality in the price condition A11 in period 1: p_A = (c_A / c_B) p_B."""
        return self.cb * self.pa1 == self.ca * self.pb1

    @property
    def binds2(self):
        return self.cb * self.pa2 == self.ca * self.pb2

    @property
    def equal_shares(self):
        """The market shares are the same in the two periods."""
        return self.pb1 - self.pa1 == self.pb2 - self.pa2

    def admissible(self) -> bool:
        """A1, A7, A10, A11 and the implicit conditions I1 and I2, decided exactly."""
        prices = all(self.cb * pa >= self.ca * pb and pb >= pa > self.ca and pb > self.cb
                     for pa, pb in ((self.pa1, self.pb1), (self.pa2, self.pb2)))
        shares = all(Fraction(1, 2) <= a < 1 for a in (self.aa1, self.aa2))
        return bool(0 < self.ca < self.cb and prices and shares and self.beta > 0 and self.mu > self.sigma > 0
                    and 0 <= self.theta <= 1 and self.gamma > 0 and 0 <= self.lam_s <= 1)

    def tags(self) -> tuple[str, ...]:
        """The edges of the admissible region on which this point lies."""
        out = []
        for t, pa, pb, binds in ((1, self.pa1, self.pb1, self.binds1), (2, self.pa2, self.pb2, self.binds2)):
            if binds:
                out.append(f"equality in A11 in period {t}")
            if pa == pb:
                out.append(f"p_A = p_B in period {t}")
            if pb / self.cb in EDGE["pb_over_cb"]:
                out.append(f"p_B / c_B = {pb / self.cb} in period {t}")
        if self.binds1 and self.binds2:
            out.append("equality in A11 in both periods")
        if self.equal_shares:
            out.append("same shares in both periods")
        if self.ca / self.cb in EDGE["cost_ratio"]:
            out.append(f"c_A / c_B = {self.ca / self.cb}")
        if self.sigma / self.mu in EDGE["sigma_over_mu"]:
            out.append(f"sigma / mu = {self.sigma / self.mu}")
        largest_gap = max(self.pb1 - self.pa1, self.pb2 - self.pa2)
        if largest_gap > 0 and self.beta * largest_gap in EDGE["beta_times_gap"]:
            out.append(f"beta x largest price gap = {self.beta * largest_gap}")
        if largest_gap == 0 and self.beta in EDGE["beta_without_gap"]:
            out.append(f"beta = {self.beta} without a price gap")
        if self.theta in (0, 1):
            out.append(f"theta = {self.theta}")
        if self.gamma in EDGE["gamma"]:
            out.append(f"gamma = {self.gamma}")
        if self.lam_s in (0, 1):
            out.append(f"lambda_S = {self.lam_s}")
        return tuple(out)

    def params(self) -> tuple[Params, float, float]:
        """The point in floating point, in the form the primitives take: (Params, mu, sigma)."""
        prm = Params(float(self.pa1), float(self.pb1), float(self.pa2), float(self.pb2), float(self.ca), float(self.cb),
                     float(self.beta), float(self.theta), float(self.gamma), float(self.lam_s), float(1 - self.lam_s))
        return prm, float(self.mu), float(self.sigma)

    def describe(self) -> str:
        """All coordinates as exact fractions, for the message of a failing assertion."""
        names = ("pa1", "pb1", "pa2", "pb2", "ca", "cb", "beta", "mu", "sigma")
        return f"{self.kind} point " + ", ".join(f"{n}={getattr(self, n)}" for n in names)


EDGE = {                                                    # the extreme values that the edge sampler uses
    "cost_ratio": (Fraction(1, 1000), Fraction(999, 1000)),
    "sigma_over_mu": (Fraction(1, 100), Fraction(999, 1000)),
    "pb_over_cb": (Fraction(1001, 1000), Fraction(50)),
    "beta_times_gap": (Fraction(1, 10**6), Fraction(499, 1000)),
    "beta_without_gap": (Fraction(1, 10**6), Fraction(5)),
    "gamma": (Fraction(1, 100), Fraction(1000)),
}


def _lattice(rng, lo, hi, den=1000) -> Fraction:
    """A uniformly drawn multiple of 1/den between lo and hi, both included."""
    return Fraction(int(rng.integers(round(lo * den), round(hi * den), endpoint=True)), den)


def _regular_gamma(rng) -> Fraction:
    lo, hi = REGULAR["gamma"]
    return max(Fraction(round(float(np.exp(rng.uniform(np.log(lo), np.log(hi)))) * 1000), 1000), Fraction(lo).limit_denominator(1000))


def draw_exogenous_exact(rng, equal_shares=False) -> ExactPoint:
    """A random rational parameter point in the region of `draw_exogenous`.

    Every ratio is a multiple of 1/1000.
        c_B                  [0.5, 3]
        c_A / c_B            [0.05, 0.98]
        mu                   [5, 20]
        sigma / mu           [0.1, 0.95]
        p_{B,t} / c_B        [1.05, 4] in each period
        p_{A,t}              (c_A / c_B) p_{B,t} plus 0.001 to 0.999 of the
                             distance to p_{B,t}, so A11 holds strictly and
                             p_A < p_B
        beta                 0.001 to 0.45 divided by the largest price gap,
                             at most 1/2
        theta                [0.001, 0.999]
        gamma                log-uniform on [0.05, 50], rounded to 1/1000
        lambda_S             [0.001, 0.999]
    With `equal_shares` the price gap is the same in both periods, 0.001 to
    0.999 of the smallest gap that A11 allows, so the shares are exactly equal.
    """
    r = REGULAR
    cb = _lattice(rng, *r["cb"])
    ratio = _lattice(rng, *r["cost_ratio"])
    mu = _lattice(rng, *r["mu"])
    sigma = mu * _lattice(rng, *r["sigma_over_mu"])
    pb1, pb2 = (cb * _lattice(rng, *r["pb_over_cb"]) for _ in range(2))
    pa1, pa2 = (pb * (ratio + _lattice(rng, 0.001, 0.999) * (1 - ratio)) for pb in (pb1, pb2))
    if equal_shares:
        gap = min(pb1, pb2) * (1 - ratio) * _lattice(rng, 0.001, 0.999)
        pa1, pa2 = pb1 - gap, pb2 - gap
    beta = min(Fraction(r["beta_cap"]), _lattice(rng, 0.001, r["beta_times_gap"]) / max(pb1 - pa1, pb2 - pa2))
    point = ExactPoint(pa1, pb1, pa2, pb2, cb * ratio, cb, beta, mu, sigma, theta=_lattice(rng, 0.001, 0.999),
                       gamma=_regular_gamma(rng), lam_s=_lattice(rng, 0.001, 0.999), kind="regular")
    assert point.admissible(), point.describe()
    return point


def draw_edge_exact(rng, equal_shares=False) -> ExactPoint:
    """A random rational parameter point on the edges of the region that the
    assumptions of Section 4 allow.

    Each coordinate below takes one of its two extreme values with probability
    1/2 (1/4 each) and a regular value, drawn as in `draw_exogenous_exact`,
    otherwise. The coordinates are drawn independently, so most points lie on
    several edges at once.
        c_A / c_B            1/1000 or 999/1000
        sigma / mu           1/100 or 999/1000
        p_{B,t} / c_B        1001/1000 or 50, in each period
        p_{A,t}              (c_A / c_B) p_{B,t}, which is equality in A11,
                             or p_{B,t}, which gives equal shares 1/2,
                             in each period
        beta                 1/1000000 or 499/1000 divided by the largest
                             price gap, which gives a share of retailer B of
                             1/1000. If both price gaps are zero, beta is
                             1/1000000 or 5.
        theta                0 or 1
        gamma                1/100 or 1000
        lambda_S             0 or 1
    With `equal_shares` the price gap is the same in both periods: zero, the
    smallest gap at which A11 binds, or a regular fraction of it. In addition
    p_{B,2} is set equal to p_{B,1} with probability 1/4, so that equality in
    A11 in both periods occurs together with equal shares.

    The proposition tests use the nine price, cost and demand coordinates and
    replace theta and gamma by their own grids. The equilibrium tests use all
    twelve coordinates.
    """
    def pick(low_high, regular):
        u = rng.uniform()
        return low_high[0] if u < 0.25 else low_high[1] if u < 0.5 else regular()

    r = REGULAR
    cb = _lattice(rng, *r["cb"])
    ratio = pick(EDGE["cost_ratio"], lambda: _lattice(rng, *r["cost_ratio"]))
    mu = _lattice(rng, *r["mu"])
    sigma = mu * pick(EDGE["sigma_over_mu"], lambda: _lattice(rng, *r["sigma_over_mu"]))
    pb1, pb2 = (cb * pick(EDGE["pb_over_cb"], lambda: _lattice(rng, *r["pb_over_cb"])) for _ in range(2))
    if equal_shares:
        if rng.uniform() < 0.25:
            pb2 = pb1
        gap = min(pb1, pb2) * (1 - ratio) * pick((Fraction(0), Fraction(1)), lambda: _lattice(rng, 0.001, 0.999))
        pa1, pa2 = pb1 - gap, pb2 - gap
    else:
        pa1, pa2 = (pb * (ratio + pick((Fraction(0), Fraction(1)), lambda: _lattice(rng, 0.001, 0.999)) * (1 - ratio))
                    for pb in (pb1, pb2))
    largest_gap = max(pb1 - pa1, pb2 - pa2)
    if largest_gap == 0:
        beta = pick(EDGE["beta_without_gap"], lambda: _lattice(rng, 0.001, r["beta_cap"]))
    else:
        beta = pick(EDGE["beta_times_gap"], lambda: _lattice(rng, 0.001, r["beta_times_gap"])) / largest_gap
    point = ExactPoint(pa1, pb1, pa2, pb2, cb * ratio, cb, beta, mu, sigma,
                       theta=pick((Fraction(0), Fraction(1)), lambda: _lattice(rng, 0.001, 0.999)),
                       gamma=pick(EDGE["gamma"], lambda: _regular_gamma(rng)),
                       lam_s=pick((Fraction(0), Fraction(1)), lambda: _lattice(rng, 0.001, 0.999)), kind="edge")
    assert point.admissible(), point.describe()
    return point


def edge_census(points) -> dict[str, int]:
    """How many of the given exact points lie on each edge."""
    return dict(sorted(Counter(tag for p in points for tag in p.tags()).items()))


def _regular_region(exact: bool) -> dict[str, str]:
    r = REGULAR
    grid = ", multiples of 1/1000" if exact else ""
    return {
        "assumptions": "A1, A11 with strict inequalities, I1, I2",
        "c_B": f"[{r['cb'][0]:g}, {r['cb'][1]:g}]{grid}",
        "c_A / c_B": f"[{r['cost_ratio'][0]:g}, {r['cost_ratio'][1]:g}]{grid}",
        "mu": f"[{r['mu'][0]:g}, {r['mu'][1]:g}]{grid}",
        "sigma / mu": f"[{r['sigma_over_mu'][0]:g}, {r['sigma_over_mu'][1]:g}]{grid}",
        "p_B,t / c_B": f"[{r['pb_over_cb'][0]:g}, {r['pb_over_cb'][1]:g}]{grid}",
        "p_A,t": ("(c_A / c_B) p_B,t plus 0.001 to 0.999 of the distance to p_B,t" if exact
                  else "uniform between (c_A / c_B) p_B,t and p_B,t, end points have probability zero"),
        "beta": f"at most {r['beta_times_gap']:g} / (largest price gap) and at most {r['beta_cap']:g}, so the share of B is at least 0.05",
        "equal_shares option": "the same price gap in both periods, a fraction of the smallest gap that A11 allows",
        "theta": "[0.001, 0.999]" if exact else "uniform on (0, 1)",
        "gamma": f"log-uniform on [{r['gamma'][0]:g}, {r['gamma'][1]:g}]",
        "lambda_S": "[0.001, 0.999]" if exact else "uniform on (0, 1)",
        "never reached": "equality in A11, p_A = p_B, theta at 0 or 1, a share of B below 0.05",
    }


SAMPLED_REGION = {
    "draw_exogenous": _regular_region(exact=False),
    "draw_exogenous_exact": _regular_region(exact=True),
    "draw_edge_exact": {
        "assumptions": "A1, A11 with equality allowed, I1, I2",
        "rule": "each coordinate takes an extreme value with probability 1/2, otherwise a value of draw_exogenous_exact",
        "c_A / c_B": " or ".join(str(v) for v in EDGE["cost_ratio"]),
        "sigma / mu": " or ".join(str(v) for v in EDGE["sigma_over_mu"]),
        "p_B,t / c_B": " or ".join(str(v) for v in EDGE["pb_over_cb"]),
        "p_A,t": "(c_A / c_B) p_B,t (equality in A11) or p_B,t (shares 1/2)",
        "beta x largest price gap": " or ".join(str(v) for v in EDGE["beta_times_gap"]) + ", the latter gives a share of B of 1/1000",
        "beta when both price gaps are zero": " or ".join(str(v) for v in EDGE["beta_without_gap"]),
        "theta": "0 or 1",
        "gamma": " or ".join(str(v) for v in EDGE["gamma"]),
        "lambda_S": "0 or 1",
        "equal_shares option": "a common price gap that is zero, binding in A11, or regular. p_B,2 = p_B,1 with probability 1/4",
    },
    "draw_without_a11": {
        "assumptions": "A1, I1, I2. A11 is not imposed",
        "prices": f"all four uniform on [{REGULAR['pb_over_cb'][0]:g} c_B, {REGULAR['pb_over_cb'][1]:g} c_B], independent",
        "other coordinates": "as in draw_exogenous, beta reduced so that both shares are at least 0.05",
    },
    "draw_bounded_prices": {
        "assumptions": "A1, A10, A12, A13",
        "c_B, c_A / c_B, mu, sigma / mu": "as in draw_exogenous",
        "beta": "uniform on [0.02, 0.6]",
        "p_hi": "between 1/(2 beta) + 1.01 w and 1/(2 beta) + 2 w, with w = (mu + sigma)(c_A + 2 c_B)/(3 mu)",
        "p_lo": "uniform on the interval that A12 and A13 leave, shrunk by one thousandth at both ends",
        "theta": "0 with probability 1/8, 1 with probability 1/8, otherwise uniform on (0, 1)",
        "gamma": f"log-uniform on [{REGULAR['gamma'][0]:g}, {REGULAR['gamma'][1]:g}]",
    },
}


def region_summary(name: str) -> str:
    """The bounds of one sampler on one line, for a report."""
    return ". ".join(f"{key}: {value}" for key, value in SAMPLED_REGION[name].items())


def distributions(mu, sigma):
    """The uniform distribution of the paper and three other distributions on
    the same support, used to test the lemmas that are stated for a general F."""
    lo, hi = mu - sigma, mu + sigma
    width = hi - lo
    mode = lo + 0.3 * width
    return {
        "uniform": pm.Uniform(lo, hi),
        "triangular": pm.Quadrature(stats.triang(c=0.3, loc=lo, scale=width), breaks=(mode,)),
        "beta(2,5)": pm.Quadrature(stats.beta(2, 5, loc=lo, scale=width)),
        "truncated normal": pm.Quadrature(stats.truncnorm(-2.0, 2.0, loc=mu, scale=sigma / 2)),
    }
