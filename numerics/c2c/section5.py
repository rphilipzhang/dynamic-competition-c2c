"""Section 5 helpers: the price and inventory game when gamma is large.

The file has three parts.

    claimed_*   What Lemmas A.1 and A.2 and Propositions 8 and 9 claim, transcribed from the
                LaTeX source in `paper/`. `test_section_5_transcription.py` checks the
                transcription. Nothing else in this file uses these functions.
    the model   Payoffs of the game of Section 5, built from `c2c.primitives` only.
    solvers     Numerical tools that locate equilibria of the model. They use no result of
                the paper. A located point counts as evidence only after a test has checked,
                with payoffs from the model, that no unilateral deviation is profitable.

The game (Section 3.3 and the opening of Section 5). In each period the retailers first choose
prices in [p_lo, p_hi] and then order quantities. Backward induction therefore has four steps:
the second-period inventory subgame given second-period prices and first-period sales, the
second-period price game given first-period sales, the first-period inventory subgame given
first-period prices, and the first-period price game.

Seed demand is uniform on [mu - sigma, mu + sigma] and there is no discounting (assumption A10).
Sales are piecewise linear in the seed demand, so every expectation below is exact or is a
Gauss-Legendre rule applied between consecutive kinks of the sales function.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.polynomial import chebyshev

from c2c import primitives as pm

_trapezoid = getattr(np, "trapezoid", None) or np.trapz      # NumPy 2 renamed trapz to trapezoid.


@dataclass(frozen=True)
class Market:
    """Everything that is fixed in one game of Section 5 except gamma and the scenario."""
    ca: float
    cb: float
    beta: float
    theta: float
    mu: float
    sigma: float
    p_lo: float
    p_hi: float

    @property
    def lo(self):
        return self.mu - self.sigma

    @property
    def hi(self):
        return self.mu + self.sigma

    @property
    def dist(self):
        return pm.Uniform(self.lo, self.hi)

    @property
    def smallest_share(self):
        """The smallest market share that any price pair in the box can give a retailer."""
        return 0.5 - self.beta * (self.p_hi - self.p_lo)


def draw_market(rng) -> Market:
    """A random market that satisfies A1, A10, A12 and A13.

    c_B is uniform on [0.5, 3] and c_A / c_B on [0.05, 0.98]. mu is uniform on [5, 20] and
    sigma / mu on [0.1, 0.95]. beta is uniform on [0.02, 0.6] and theta on [0, 1]. The upper
    price bound exceeds its lower limit of A13 by 1% to 100% of (mu + sigma)(c_A + 2 c_B) / (3 mu).
    The lower price bound is uniform on the interval that A12 and A13 leave for it. This is the
    region that `test_proposition_7_shapes.py` samples.
    """
    while True:
        cb = rng.uniform(0.5, 3.0)
        ca = cb * rng.uniform(0.05, 0.98)
        mu = rng.uniform(5.0, 20.0)
        sigma = mu * rng.uniform(0.1, 0.95)
        beta = rng.uniform(0.02, 0.6)
        theta = rng.uniform(0.0, 1.0)
        half = 1.0 / (2.0 * beta)
        excess = (mu + sigma) / (3.0 * mu) * (ca + 2.0 * cb)
        # A13 requires p_hi > 1/(2 beta) + (mu + sigma)(c_A + 2 c_B)/(3 mu) and p_lo < 1/(2 beta) + (2 c_A + c_B)/3.
        # A12 requires p_lo > c_B and beta < 1/(2 (p_hi - p_lo)).
        p_hi = half + excess * (1.0 + rng.uniform(0.01, 1.0))
        lo_min = max(cb, p_hi - half) * 1.001
        lo_max = min(half + (2.0 * ca + cb) / 3.0, p_hi) * 0.999
        if lo_min < lo_max:
            return Market(ca, cb, beta, theta, mu, sigma, rng.uniform(lo_min, lo_max), p_hi)


def threshold_on_ladder(gammas, holds):
    """Smallest gamma on the ladder from which a claim holds at that value and at all larger
    ones. The result is None if the claim fails at the largest value."""
    first = None
    for gamma, good in zip(reversed(gammas), reversed(holds)):
        if not good:
            break
        first = gamma
    return first


# ----------------------------------------------------------------------------- what the paper claims
def claimed_limit_prices(mk: Market):
    r"""Online Appendix A.2, notation: \widehat p_{i,2} := 1/(2\beta) + (2 c_i + c_j)/3."""
    return 1.0 / (2.0 * mk.beta) + (2.0 * mk.ca + mk.cb) / 3.0, 1.0 / (2.0 * mk.beta) + (2.0 * mk.cb + mk.ca) / 3.0


def claimed_nu(mk: Market):
    r"""Online Appendix A.2, notation: \nu_i := \alpha_{i,2}(\widehat p_{A,2}, \widehat p_{B,2}) (\widehat p_{i,2} - c_i)."""
    pa, pb = claimed_limit_prices(mk)
    share_a = pm.share(pa, pb, mk.beta)
    return share_a * (pa - mk.ca), (1.0 - share_a) * (pb - mk.cb)


def claimed_second_period_prices_s(mk: Market):
    """Lemma A.1(b): in Scenario S both second-period prices equal the upper bound."""
    return mk.p_hi, mk.p_hi


def claimed_first_period_prices_s(mk: Market):
    """Proposition 9(a): in Scenario S both first-period prices equal the lower bound."""
    return mk.p_lo, mk.p_lo


def claimed_orders_s(mk: Market, gamma, pa1, pb1):
    r"""Lemma A.1(a): y_A = (\alpha_A + \theta\alpha_B) \zeta_A - \theta\alpha_B \zeta_B and
    y_B = \alpha_B \zeta_B with \zeta_i = F^{-1}(1 - c_i / (p_{i,1} + \gamma (\overline p - c_i)))."""
    share_a = pm.share(pa1, pb1, mk.beta)
    share_b = 1.0 - share_a
    zeta_a = mk.dist.ppf(1.0 - mk.ca / (pa1 + gamma * (mk.p_hi - mk.ca)))
    zeta_b = mk.dist.ppf(1.0 - mk.cb / (pb1 + gamma * (mk.p_hi - mk.cb)))
    return (share_a + mk.theta * share_b) * zeta_a - mk.theta * share_b * zeta_b, share_b * zeta_b


def claimed_orders_n(mk: Market, gamma, pa1, pb1):
    r"""Lemma A.2(a), without its O(\gamma^{-2}) term: the same two expressions with
    \zeta_A = F^{-1}(1 - c_A / (p_{A,1} + \gamma\nu_A)) and
    \zeta_B = F^{-1}(1 - (c_B - \theta\gamma\nu_B c_A / (p_{A,1} + \gamma\nu_A)) / (p_{B,1} + (1-\theta)\gamma\nu_B))."""
    nu_a, nu_b = claimed_nu(mk)
    share_a = pm.share(pa1, pb1, mk.beta)
    share_b = 1.0 - share_a
    zeta_a = mk.dist.ppf(1.0 - mk.ca / (pa1 + gamma * nu_a))
    numerator_b = mk.cb - mk.theta * gamma * nu_b * mk.ca / (pa1 + gamma * nu_a)
    zeta_b = mk.dist.ppf(1.0 - numerator_b / (pb1 + (1.0 - mk.theta) * gamma * nu_b))
    return (share_a + mk.theta * share_b) * zeta_a - mk.theta * share_b * zeta_b, share_b * zeta_b


# Proposition 8: the claimed sign of d y_{i,1} / d p_{j,1} for large gamma. The key is
# (part, retailer whose order it is, retailer whose price moves). Part "b2 bounded" is the
# regime gamma (1 - theta) <= l^D under condition (A.22). Part "b2 fixed" is a fixed theta < 1.
CLAIMED_SLOPE_SIGNS = {
    ("a", "A", "A"): -1, ("a", "A", "B"): +1, ("a", "B", "B"): -1, ("a", "B", "A"): +1,
    ("b1", "A", "A"): -1, ("b1", "B", "A"): +1,
    ("b2 bounded", "A", "B"): -1, ("b2 bounded", "B", "B"): +1,
    ("b2 fixed", "A", "B"): +1, ("b2 fixed", "B", "B"): -1,
}


def claimed_condition_a22(mk: Market):
    r"""Left side of condition (A.22) in Proposition 8(b2) divided by its right side.
    The ratio exceeds 1 exactly when
    \sigma (c_B - c_A \nu_B/\nu_A)(1 + 2\beta\overline p) > \beta(\mu+\sigma)\underline p^2."""
    nu_a, nu_b = claimed_nu(mk)
    return mk.sigma * (mk.cb - mk.ca * nu_b / nu_a) * (1.0 + 2.0 * mk.beta * mk.p_hi) / (mk.beta * mk.hi * mk.p_lo ** 2)


def claimed_bound_a23(mk: Market, pa1):
    r"""The bound on p_{B,1} in (A.23): \sqrt{\sigma (c_B - c_A\nu_B/\nu_A)(1 + 2\beta p_{A,1}) / (\beta(\mu+\sigma))}."""
    nu_a, nu_b = claimed_nu(mk)
    return np.sqrt(mk.sigma * (mk.cb - mk.ca * nu_b / nu_a) * (1.0 + 2.0 * mk.beta * pa1) / (mk.beta * mk.hi))


def claimed_price_path_s(mk: Market, p1, p2):
    r"""Proposition 9(a): \underline p = p_{i,1} < p_{i,2} = \overline p."""
    return bool(p1 == mk.p_lo and p2 == mk.p_hi and p1 < p2)


def claimed_price_path_n(mk: Market, p1, p2):
    r"""Proposition 9(b): \underline p < p_{i,2} < p_{i,1} < \overline p."""
    return bool(mk.p_lo < p2 < p1 < mk.p_hi)


def proof_first_period_limit_prices(mk: Market):
    r"""Proof of Proposition 9, not its statement: \widehat p_{i,1} = 1/(2\beta) + (\mu+\sigma)(2c_i+c_j)/(3\mu).
    Tests report the distance to these prices and assert nothing about it."""
    scale = mk.hi / (3.0 * mk.mu)
    return 1.0 / (2.0 * mk.beta) + scale * (2.0 * mk.ca + mk.cb), 1.0 / (2.0 * mk.beta) + scale * (2.0 * mk.cb + mk.ca)


# ----------------------------------------------------------------------------- the model: one period
def _breakpoints(mk, ya, yb, share_a, za, zb):
    """Sorted seed-demand values between which sales are linear in the seed demand. They are
    the two ends of the support and the four kinks of the sales function, clipped to the support."""
    share_b = 1.0 - share_a
    th = mk.theta
    kinks = [(ya - za) / share_a, (yb - zb) / share_b,
             (ya - za + th * (yb - zb)) / (share_a + th * share_b), (yb - zb + th * (ya - za)) / (share_b + th * share_a)]
    ends = [np.full(ya.shape, mk.lo), np.full(ya.shape, mk.hi)]
    return np.sort(np.clip(np.stack(ends + kinks, axis=-1), mk.lo, mk.hi), axis=-1)


def expected_sales(mk: Market, ya, yb, share_a, za=0.0, zb=0.0):
    """Exact expected sales (E R_A, E R_B) of one period. Every argument broadcasts.

    `c2c.primitives.Uniform.expected_sales` does the same for scalar shares. This version
    evaluates `c2c.primitives.sales` on the kinks and applies the trapezoid rule, which is
    exact for a piecewise linear function. It exists because a price search varies the shares.
    `test_section_5_second_period.py` checks that the two agree.
    """
    ya, yb, share_a, za, zb = np.broadcast_arrays(*(np.asarray(v, float) for v in (ya, yb, share_a, za, zb)))
    x = _breakpoints(mk, ya, yb, share_a, za, zb)
    ra, rb = pm.sales(x, ya[..., None], yb[..., None], share_a[..., None], 1.0 - share_a[..., None], mk.theta,
                      za[..., None], zb[..., None])
    width = mk.hi - mk.lo
    return _trapezoid(ra, x, axis=-1) / width, _trapezoid(rb, x, axis=-1) / width


def benchmark_orders(mk: Market, pa, pb):
    """Equilibrium order quantities of the one-period game without C2C demand, for either
    ordering of the critical fractiles 1 - c_i / p_i. This is Lemma 1 and its mirror image.
    `test_section_5_second_period.py` checks from the primitives that it is an equilibrium at
    every price pair of the box, which Section 5 needs because it drops assumption A11."""
    pa, pb = np.broadcast_arrays(np.asarray(pa, float), np.asarray(pb, float))
    share_a = pm.share(pa, pb, mk.beta)
    share_b = 1.0 - share_a
    zeta_a, zeta_b = mk.dist.ppf(1.0 - mk.ca / pa), mk.dist.ppf(1.0 - mk.cb / pb)
    a_high = zeta_a >= zeta_b
    ya = np.where(a_high, (share_a + mk.theta * share_b) * zeta_a - mk.theta * share_b * zeta_b, share_a * zeta_a)
    yb = np.where(a_high, share_b * zeta_b, (share_b + mk.theta * share_a) * zeta_b - mk.theta * share_a * zeta_a)
    return ya, yb


def second_period_orders(mk: Market, scenario, gamma, pa2, pb2, ra1, rb1):
    """Second-period orders y^0_{i,2} + Z_{i,2} at given prices and first-period sales, and the
    C2C demands Z_{i,2}. Returns (y_A, y_B, Z_A, Z_B)."""
    y0a, y0b = benchmark_orders(mk, pa2, pb2)
    za, zb = pm.c2c_demand(scenario, gamma, np.asarray(ra1, float), np.asarray(rb1, float), pm.share(pa2, pb2, mk.beta))
    return y0a + za, y0b + zb, za, zb


def second_period_profits(mk: Market, scenario, gamma, pa2, pb2, ra1, rb1):
    """Expected second-period profits at the orders of `second_period_orders`, computed from
    the primitives. These are the payoffs of the second-period price game."""
    pa2, pb2 = np.broadcast_arrays(np.asarray(pa2, float), np.asarray(pb2, float))
    ya, yb, za, zb = second_period_orders(mk, scenario, gamma, pa2, pb2, ra1, rb1)
    era, erb = expected_sales(mk, ya, yb, pm.share(pa2, pb2, mk.beta), za, zb)
    return pa2 * era - mk.ca * ya, pb2 * erb - mk.cb * yb


def benchmark_profits(mk: Market, pa, pb):
    """Equilibrium profits pi^0_i of the one-period game without C2C demand."""
    return second_period_profits(mk, "0", 0.0, pa, pb, 0.0, 0.0)


# ----------------------------------------------------------------------------- generic searches
def argmax_on_interval(objective, lo, hi, first=129, points=33, levels=5):
    """Global maximiser of a scalar objective on [lo, hi] from payoff values only.

    `objective` maps an array of candidates to an array of payoffs. A grid of `first` points
    covers the whole interval. Each later level puts `points` points on the two cells around
    the best one. Returns (argmax, max). The result is accurate to about the square root of
    the rounding error of the payoff, like every search that uses values only.
    """
    n = first
    for _ in range(levels):
        grid = np.linspace(lo, hi, n)
        vals = np.asarray(objective(grid), float)
        k = int(np.argmax(vals))
        lo, hi = grid[max(k - 1, 0)], grid[min(k + 1, n - 1)]
        n = points
    return float(grid[k]), float(vals[k])


def price_gap(payoffs, mk: Market, pa, pb, grid=2001):
    """How far the price pair (pa, pb) is from an equilibrium of a price game on the box.

    `payoffs(pa, pb)` returns both payoffs and broadcasts. Each retailer's whole price
    interval is searched with `c2c.primitives.best_response`. The result has the same keys as
    `c2c.primitives.nash_gap`.
    """
    width = mk.p_hi - mk.p_lo
    br_a, max_a = pm.best_response(lambda t: payoffs(mk.p_lo + t, pb)[0], width, grid=grid)
    br_b, max_b = pm.best_response(lambda t: payoffs(pa, mk.p_lo + t)[1], width, grid=grid)
    at_a, at_b = (float(v) for v in payoffs(pa, pb))
    return {"br_a": mk.p_lo + br_a, "br_b": mk.p_lo + br_b,
            "dist": max(abs(mk.p_lo + br_a - pa), abs(mk.p_lo + br_b - pb)),
            "gain": max(max_a - at_a, max_b - at_b)}


def price_replies(payoffs, mk: Market, **search):
    """The two best-reply maps of a price game on the box. A best reply is a global maximiser
    over [p_lo, p_hi], found from payoff values with `argmax_on_interval`."""
    def reply_a(pb):
        return argmax_on_interval(lambda p: payoffs(p, pb)[0], mk.p_lo, mk.p_hi, **search)[0]

    def reply_b(pa):
        return argmax_on_interval(lambda p: payoffs(pa, p)[1], mk.p_lo, mk.p_hi, **search)[0]

    return reply_a, reply_b


def pure_equilibria_on_grid(table_a, table_b):
    """Index pairs of the pure equilibria of a finite two-player game. Rows are retailer A's
    choices and columns are retailer B's. Payoffs must be positive. A choice counts as a best
    reply if it attains the maximum up to a relative rounding allowance of 1e-13."""
    best_a = table_a >= table_a.max(axis=0, keepdims=True) * (1.0 - 1e-13)
    best_b = table_b >= table_b.max(axis=1, keepdims=True) * (1.0 - 1e-13)
    return [tuple(int(v) for v in cell) for cell in np.argwhere(best_a & best_b)]


def iterate_best_responses(reply_a, reply_b, start, sweeps, tol):
    """Alternating best responses. Retailer A replies to B and then B replies to the new value
    of A. Returns the last pair and the number of sweeps that were used."""
    a, b = start
    for sweep in range(1, sweeps + 1):
        a_new = reply_a(b)
        b_new = reply_b(a_new)
        moved = abs(a_new - a) + abs(b_new - b)
        a, b = a_new, b_new
        if moved < tol:
            break
    return a, b, sweep


# ----------------------------------------------------------------------------- second-period price game
class SecondPeriodS:
    """The second-period price game of Scenario S, seen from the first period.

    With C2C demand Z_{i,2} = gamma R_{i,1} the second-period profit of retailer i at prices
    (p_i, p_j) is pi^0_i(p_i, p_j) + gamma R_{i,1} (p_i - c_i). `test_section_5_second_period.py`
    checks this identity from the primitives. The profit is tabulated on a price grid.

    dominance[i]   The upper bound is retailer i's only best reply to every rival price on
                   the grid as soon as gamma R_{i,1} exceeds this number.
    value          Best second-period profit of a retailer whose rival charges the upper
                   bound. It is the retailer's equilibrium continuation value at every sales
                   state in which gamma times the rival's sales exceeds the rival's dominance
                   number, whatever the retailer's own sales are.
    """

    def __init__(self, mk: Market, own=401, rival=41, table=2001):
        self.mk = mk
        own_grid = np.linspace(mk.p_lo, mk.p_hi, own)
        rival_grid = np.linspace(mk.p_lo, mk.p_hi, rival)
        # In both tables the rows are the retailer's own price and the columns are the rival's price.
        profit_a = benchmark_profits(mk, own_grid[:, None], rival_grid[None, :])[0]
        profit_b = benchmark_profits(mk, rival_grid[None, :], own_grid[:, None])[1]
        gap = mk.p_hi - own_grid[:-1]
        self.dominance = tuple(float(((p[:-1] - p[-1:]) / gap[:, None]).max()) for p in (profit_a, profit_b))
        self.base = (float(profit_a[-1, -1]), float(profit_b[-1, -1]))                  # This is pi^0_i at (p_hi, p_hi).
        self._extra = []
        for profit in (profit_a[:, -1], profit_b[:, -1]):                               # The rival charges the upper bound.
            excess = profit[:-1] - profit[-1]
            top = max(float((excess / gap).max()), 0.0)        # The upper bound is the best reply once gamma R exceeds top.
            t = np.linspace(0.0, top, table) if top > 0.0 else np.array([0.0, 1.0])
            self._extra.append((t, np.maximum((excess[None, :] - t[:, None] * gap[None, :]).max(axis=1), 0.0)))

    def value(self, gamma, ra, rb):
        out = []
        for who, (sales, cost) in enumerate(((ra, self.mk.ca), (rb, self.mk.cb))):
            sales = np.asarray(sales, float)
            t, extra = self._extra[who]
            at_upper_bound = self.base[who] + gamma * sales * (self.mk.p_hi - cost)
            out.append(at_upper_bound + np.interp(gamma * sales, t, extra, right=0.0))
        return tuple(out)

    def slopes(self, gamma, ra, rb):
        """Derivatives of each continuation value with respect to own sales and to the rival's
        sales, at states in which both retailers charge the upper bound."""
        return (gamma * (self.mk.p_hi - self.mk.ca), 0.0), (gamma * (self.mk.p_hi - self.mk.cb), 0.0)


_STENCIL = np.array([-2.0, -1.0, 1.0, 2.0])
_STENCIL_WEIGHTS = np.array([1.0, -8.0, 8.0, -1.0]) / 12.0


def _scaled_profits_n(mk, s, pa, pb):
    """Second-period profits of Scenario N divided by gamma R_1, as functions of
    s = 1 / (gamma R_1). With Z_{i,2} = alpha_{i,2} gamma R_1 the profit of retailer i is
    pi^0_i + gamma R_1 alpha_{i,2} (p_{i,2} - c_i)."""
    base_a, base_b = benchmark_profits(mk, pa, pb)
    share_a = pm.share(pa, pb, mk.beta)
    return s * base_a + share_a * (pa - mk.ca), s * base_b + (1.0 - share_a) * (pb - mk.cb)


def _price_foc_n(mk, s, pa, pb, step=1e-3):
    """Own-price derivatives of the scaled profits. The benchmark profit is differentiated
    with a five-point stencil and the quadratic term alpha_i (p_i - c_i) by hand."""
    ha, hb = step * pa, step * pb
    around_a = benchmark_profits(mk, pa[..., None] + _STENCIL * ha[..., None], pb[..., None])[0]
    around_b = benchmark_profits(mk, pa[..., None], pb[..., None] + _STENCIL * hb[..., None])[1]
    slope_a, slope_b = (around_a * _STENCIL_WEIGHTS).sum(-1) / ha, (around_b * _STENCIL_WEIGHTS).sum(-1) / hb
    share_a = pm.share(pa, pb, mk.beta)
    return s * slope_a + share_a - mk.beta * (pa - mk.ca), s * slope_b + (1.0 - share_a) - mk.beta * (pb - mk.cb)


def _newton_2d(residuals, a, b, step, sweeps, tol):
    """Newton iteration for two equations in two unknowns with a forward-difference Jacobian.
    Every array is treated elementwise, so many systems are solved at once."""
    with np.errstate(all="ignore"):
        for _ in range(sweeps):
            fa, fb = residuals(a, b)
            fa_a, fb_a = residuals(a + step, b)
            fa_b, fb_b = residuals(a, b + step)
            j11, j21, j12, j22 = (fa_a - fa) / step, (fb_a - fb) / step, (fa_b - fa) / step, (fb_b - fb) / step
            det = j11 * j22 - j12 * j21
            da, db = -(j22 * fa - j12 * fb) / det, -(j11 * fb - j21 * fa) / det
            a, b = a + da, b + db
            if not np.all(np.isfinite(a + b)) or np.max(np.abs(da) + np.abs(db)) < tol:
                break
    return a, b


def price_equilibrium_n(mk: Market, s, start=None):
    """Solution of the two first-order conditions of the second-period price game of
    Scenario N, for an array of s = 1 / (gamma R_1). At s = 0 the game is the one with payoffs
    alpha_i (p_i - c_i). The solver starts there unless `start` is given. A solution is an
    equilibrium only if it is interior and a global best reply, which the caller must check."""
    s = np.asarray(s, float)
    if start is None:                                              # The solution at s = 0 is found from a corner of the box.
        start = _newton_2d(lambda pa, pb: _price_foc_n(mk, 0.0, pa, pb), np.array(mk.p_lo), np.array(mk.p_hi),
                           1e-6 * mk.p_hi, 20, 1e-14 * mk.p_hi)
    pa, pb = (np.broadcast_to(np.asarray(v, float), s.shape).copy() for v in start)
    return _newton_2d(lambda a, b: _price_foc_n(mk, s, a, b), pa, pb, 1e-6 * mk.p_hi, 40, 1e-13 * mk.p_hi)


class SecondPeriodN:
    """The second-period price game of Scenario N, seen from the first period.

    The game depends on gamma and on total first-period sales R_1 only through s = 1 / (gamma R_1).
    Its equilibrium prices p*(s) are computed at Chebyshev points of consecutive panels of
    [0, s_max] and interpolated. With f_i(s) = pi^0_i(p*(s)) and g_i(s) = alpha_i (p_i - c_i)
    at p*(s), the equilibrium second-period profit is V_i(R_1) = f_i(s) + g_i(s) / s.

    `problems` lists every panel on which the first-order conditions were not solved, the
    solution left the interior of the price box, a retailer had a better price on a grid over
    the whole price interval, or the interpolation did not converge. It is empty when the
    table can be trusted. `test_section_5_first_period.py` compares the table with a direct
    solution of the price game.
    """

    def __init__(self, mk: Market, s_max, first=0.02, ratio=4.0, nodes=24):
        self.mk = mk
        edges = [0.0, min(first, s_max)]
        while edges[-1] < s_max:
            edges.append(min(edges[-1] * ratio, s_max))
        self.edges = np.array(edges)
        self.s_max = float(edges[-1])
        self.problems = []
        self._panels = []
        t = np.cos(np.pi * (np.arange(nodes) + 0.5) / nodes)       # These are Chebyshev points on [-1, 1], largest first.
        grid = np.linspace(mk.p_lo, mk.p_hi, 201)
        start = None
        for left, right in zip(edges[:-1], edges[1:]):
            s = left + 0.5 * (right - left) * (t + 1.0)
            pa, pb = price_equilibrium_n(mk, s, start)
            start = (pa[0], pb[0])                                 # The node next to the right end starts the next panel.
            foc = np.max(np.abs(_price_foc_n(mk, s, pa, pb)))
            at_a, at_b = _scaled_profits_n(mk, s, pa, pb)
            gain_a = _scaled_profits_n(mk, s[:, None], grid[None, :], pb[:, None])[0].max(axis=1) - at_a
            gain_b = _scaled_profits_n(mk, s[:, None], pa[:, None], grid[None, :])[1].max(axis=1) - at_b
            base_a, base_b = benchmark_profits(mk, pa, pb)
            share_a = pm.share(pa, pb, mk.beta)
            fits = [chebyshev.Chebyshev(chebyshev.chebfit(t, v, nodes - 1), domain=[left, right])
                    for v in (pa, pb, base_a, base_b, share_a * (pa - mk.ca), (1.0 - share_a) * (pb - mk.cb))]
            tail = max(np.abs(f.coef[-3:]).max() / np.abs(f.coef).max() for f in fits)
            if not (foc <= 1e-10 and np.all(np.isfinite(pa + pb))):
                self.problems.append(f"first-order conditions not solved on [{left:g}, {right:g}]")
            elif not (pa.min() > mk.p_lo and pb.min() > mk.p_lo and pa.max() < mk.p_hi and pb.max() < mk.p_hi):
                self.problems.append(f"price equilibrium not interior on [{left:g}, {right:g}]")
            elif max(gain_a.max(), gain_b.max()) > 1e-9 * max(at_a.max(), at_b.max()):
                self.problems.append(f"a better price exists on [{left:g}, {right:g}]")
            elif tail > 1e-10:
                self.problems.append(f"interpolation not converged on [{left:g}, {right:g}]")
            self._panels.append(fits + [f.deriv() for f in fits[2:]])

    def _eval(self, s, which):
        s = np.asarray(s, float)
        if s.size and not (s.min() >= 0.0 and s.max() <= self.s_max * (1.0 + 1e-9)):
            raise ValueError("a sales state lies outside the tabulated range of the second-period price game")
        panel = np.clip(np.searchsorted(self.edges, s, side="right") - 1, 0, len(self._panels) - 1)
        out = np.empty(s.shape)
        for k, fits in enumerate(self._panels):
            mask = panel == k
            if mask.any():
                out[mask] = fits[which](s[mask])
        return out

    def prices(self, gamma, r1):
        """Equilibrium second-period prices (p_A, p_B) at total first-period sales r1."""
        s = 1.0 / (gamma * np.asarray(r1, float))
        return self._eval(s, 0), self._eval(s, 1)

    def value(self, gamma, ra, rb):
        """Equilibrium second-period profits (V_A, V_B) at first-period sales (ra, rb)."""
        s = 1.0 / (gamma * (np.asarray(ra, float) + np.asarray(rb, float)))
        return self._eval(s, 2) + self._eval(s, 4) / s, self._eval(s, 3) + self._eval(s, 5) / s

    def slopes(self, gamma, ra, rb):
        """Derivatives of each continuation value with respect to own sales and to the rival's
        sales. They coincide because V_i depends on total sales only. Differentiating
        f_i(s) + g_i(s) / s at s = 1 / (gamma R_1) gives gamma (g_i - s g_i' - s^2 f_i')."""
        s = 1.0 / (gamma * (np.asarray(ra, float) + np.asarray(rb, float)))
        slope_a = gamma * (self._eval(s, 4) - s * self._eval(s, 8) - s * s * self._eval(s, 6))
        slope_b = gamma * (self._eval(s, 5) - s * self._eval(s, 9) - s * s * self._eval(s, 7))
        return (slope_a, slope_a), (slope_b, slope_b)


# ----------------------------------------------------------------------------- first period
_GL_NODES, _GL_WEIGHTS = np.polynomial.legendre.leggauss(16)


def first_period_nodes(mk: Market, ya, yb, share_a):
    """Seed-demand values x and probability weights w for an expectation over first-period
    demand. Sales are linear in the seed demand between consecutive kinks. A 16-point
    Gauss-Legendre rule is used on each of the five pieces, so the expectation of a smooth
    function of sales is accurate to rounding and the probability of an event that is an
    interval of pieces is exact."""
    zero = np.zeros(ya.shape)
    brk = _breakpoints(mk, ya, yb, share_a, zero, zero)
    half = (brk[..., 1:] - brk[..., :-1]) / 2.0
    mid = (brk[..., 1:] + brk[..., :-1]) / 2.0
    x = (mid[..., None] + half[..., None] * _GL_NODES).reshape(*ya.shape, -1)
    w = (half[..., None] * _GL_WEIGHTS).reshape(*ya.shape, -1) / (mk.hi - mk.lo)
    return x, w


def first_period_profits(mk: Market, cont, gamma, pa1, pb1, ya, yb):
    """Expected two-period profits (Pi_A, Pi_B) at first-period prices and orders, when the
    second period is played as `cont` describes: p_{i,1} E R_{i,1} - c_i y_{i,1} + E V_i.
    First-period sales come from `c2c.primitives.sales`. Every argument broadcasts."""
    ya, yb, pa1, pb1 = np.broadcast_arrays(*(np.asarray(v, float) for v in (ya, yb, pa1, pb1)))
    share_a = pm.share(pa1, pb1, mk.beta)
    x, w = first_period_nodes(mk, ya, yb, share_a)
    ra, rb = pm.sales(x, ya[..., None], yb[..., None], share_a[..., None], 1.0 - share_a[..., None], mk.theta)
    va, vb = cont.value(gamma, ra, rb)
    return (w * (pa1[..., None] * ra + va)).sum(-1) - mk.ca * ya, (w * (pb1[..., None] * rb + vb)).sum(-1) - mk.cb * yb


def marginal_profits(mk: Market, cont, gamma, pa1, pb1, ya, yb):
    """Derivatives (d Pi_A / d y_A, d Pi_B / d y_B) of the profits of `first_period_profits`.

    The model of Section 3 is differentiated under the expectation. With M_i = alpha_i x and
    D_i = M_i + theta (M_j - y_j)^+, one more unit of retailer i raises its own sales by one
    exactly when D_i > y_i, and lowers the rival's sales by theta exactly when M_i > y_i and
    the rival has stock left (D_j < y_j). `test_section_5_first_period.py` compares the result
    with finite differences of `first_period_profits`.
    """
    ya, yb, pa1, pb1 = np.broadcast_arrays(*(np.asarray(v, float) for v in (ya, yb, pa1, pb1)))
    share_a = pm.share(pa1, pb1, mk.beta)
    x, w = first_period_nodes(mk, ya, yb, share_a)
    ya_, yb_ = ya[..., None], yb[..., None]
    ma, mb = share_a[..., None] * x, (1.0 - share_a[..., None]) * x
    da = ma + mk.theta * np.maximum(mb - yb_, 0.0)
    db = mb + mk.theta * np.maximum(ma - ya_, 0.0)
    (own_a, cross_a), (own_b, cross_b) = cont.slopes(gamma, np.minimum(da, ya_), np.minimum(db, yb_))
    lost_by_b = mk.theta * ((ma > ya_) & (db < yb_))
    lost_by_a = mk.theta * ((mb > yb_) & (da < ya_))
    return ((w * ((pa1[..., None] + own_a) * (da > ya_) - cross_a * lost_by_b)).sum(-1) - mk.ca,
            (w * ((pb1[..., None] + own_b) * (db > yb_) - cross_b * lost_by_a)).sum(-1) - mk.cb)


def inventory_equilibrium(mk: Market, cont, gamma, pa1, pb1, start):
    """Order quantities at which both marginal profits vanish, by Newton iteration from
    `start`. Every argument broadcasts, so many price pairs are solved at once. The result is
    an equilibrium candidate. Tests confirm it with a search over each retailer's whole
    strategy interval that uses payoff values only."""
    ya, yb = (np.array(v, float) for v in np.broadcast_arrays(*start))
    return _newton_2d(lambda a, b: marginal_profits(mk, cont, gamma, pa1, pb1, a, b), ya, yb,
                      1e-7 * mk.hi / (1.0 + gamma), 30, 1e-14 * mk.hi)
