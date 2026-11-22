"""The model of Section 3, computed directly from its definition.

Nothing in this module uses a result of the paper. It implements the demand
system, sales, and expected profits exactly as Section 3 defines them, and a
generic best-response search. The tests in `numerics/tests/` use it to test the
paper's lemmas and propositions against the model itself rather than against
the paper's own formulas.

Model (Section 3), for retailers i, j in {A, B}, i != j, and period t:
    share              alpha_{i,t} = 1/2 + beta (p_{j,t} - p_{i,t})
    pre-stockout       M_{i,t} = alpha_{i,t} X_t + Z_{i,t}
    effective demand   D_{i,t} = M_{i,t} + theta (M_{j,t} - y_{j,t})^+
    sales              R_{i,t} = min(D_{i,t}, y_{i,t})
    period profit      p_{i,t} R_{i,t} - c_i y_{i,t}
C2C-induced demand in period 2:
    Scenario S   Z_{i,2} = gamma R_{i,1}
    Scenario N   Z_{i,2} = alpha_{i,2} gamma (R_{A,1} + R_{B,1})
    Mixed        Z_{i,2} = lam_s gamma R_{i,1} + lam_n alpha_{i,2} gamma (R_{A,1} + R_{B,1})
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import optimize

_trapezoid = getattr(np, "trapezoid", None) or np.trapz      # NumPy 2 renamed trapz

__all__ = ["share", "sales", "Uniform", "Quadrature", "c2c_demand", "best_response", "nash_gap"]


def share(p_own, p_other, beta):
    """Market share of the seed demand."""
    return 0.5 + beta * (p_other - p_own)


def sales(x, ya, yb, aa, ab, theta, za=0.0, zb=0.0):
    """Realized sales (R_A, R_B) at seed demand x. All arguments broadcast."""
    ma, mb = aa * x + za, ab * x + zb
    da = ma + theta * np.maximum(mb - yb, 0.0)
    db = mb + theta * np.maximum(ma - ya, 0.0)
    return np.minimum(da, ya), np.minimum(db, yb)


def _kinks(ya, yb, aa, ab, theta, za, zb):
    """Seed-demand values at which sales can change slope. Sales are piecewise
    linear in x, and every kink is one of these four candidates."""
    return [(ya - za) / aa, (yb - zb) / ab,
            (ya - za + theta * (yb - zb)) / (aa + theta * ab),
            (yb - zb + theta * (ya - za)) / (ab + theta * aa)]


@dataclass(frozen=True)
class Uniform:
    """Seed demand X ~ U[lo, hi]. Expectations of sales are exact: sales are
    piecewise linear in X, so the trapezoid rule on the kinks has no error."""
    lo: float
    hi: float

    def ppf(self, q):
        return self.lo + (self.hi - self.lo) * q

    def expected_sales(self, ya, yb, aa, ab, theta, za=0.0, zb=0.0):
        ya, yb = np.broadcast_arrays(np.atleast_1d(np.asarray(ya, float)), np.atleast_1d(np.asarray(yb, float)))
        cand = np.stack([np.full_like(ya, self.lo), np.full_like(ya, self.hi),
                         *[np.broadcast_to(k, ya.shape) for k in _kinks(ya, yb, aa, ab, theta, za, zb)]], axis=1)
        x = np.sort(np.clip(cand, self.lo, self.hi), axis=1)
        ra, rb = sales(x, ya[:, None], yb[:, None], aa, ab, theta, za, zb)
        width = self.hi - self.lo
        return _trapezoid(ra, x, axis=1) / width, _trapezoid(rb, x, axis=1) / width


_QUANTILE_BREAKS = (0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999)


class Quadrature:
    """Seed demand with any frozen `scipy.stats` distribution on a bounded support.

    Expected sales are integrated by 64-point Gauss-Legendre quadrature on
    every interval between consecutive break points. The break points are the
    kinks of the sales function (which depend on the order quantities), a fixed
    set of quantiles of the distribution, and any `breaks` supplied by the
    caller (for example the mode of a triangular density). Between break points
    the integrand is a linear function times the density, so the rule is exact
    for polynomial densities and accurate to rounding for smooth ones.
    """

    def __init__(self, dist, breaks=()):
        self.dist = dist
        self.lo, self.hi = (float(v) for v in dist.support())
        if not (np.isfinite(self.lo) and np.isfinite(self.hi)):
            raise ValueError("Quadrature needs a distribution with bounded support.")
        fixed = [self.lo, self.hi, *dist.ppf(_QUANTILE_BREAKS), *breaks]
        self._fixed = np.unique(np.clip(np.asarray(fixed, float), self.lo, self.hi))
        self._nodes, self._weights = np.polynomial.legendre.leggauss(64)

    def ppf(self, q):
        return self.dist.ppf(q)

    def expected_sales(self, ya, yb, aa, ab, theta, za=0.0, zb=0.0):
        ya, yb = np.broadcast_arrays(np.atleast_1d(np.asarray(ya, float)), np.atleast_1d(np.asarray(yb, float)))
        kinks = np.stack([np.broadcast_to(k, ya.shape) for k in _kinks(ya, yb, aa, ab, theta, za, zb)], axis=1)
        pts = np.concatenate([np.broadcast_to(self._fixed, (ya.size, self._fixed.size)),
                              np.clip(kinks, self.lo, self.hi)], axis=1)
        pts.sort(axis=1)
        half = (pts[:, 1:] - pts[:, :-1]) / 2
        mid = (pts[:, 1:] + pts[:, :-1]) / 2
        x = mid[:, :, None] + half[:, :, None] * self._nodes
        w = half[:, :, None] * self._weights * self.dist.pdf(x)
        ra, rb = sales(x, ya[:, None, None], yb[:, None, None], aa, ab, theta, za, zb)
        return (ra * w).sum(axis=(1, 2)), (rb * w).sum(axis=(1, 2))


def c2c_demand(scenario, gamma, ra, rb, alpha_a2, lam_s=None, lam_n=None):
    """C2C-induced second-period demand (Z_{A,2}, Z_{B,2}) from first-period sales."""
    if scenario == "0":
        return 0.0 * ra, 0.0 * rb
    if scenario == "S":
        return gamma * ra, gamma * rb
    if scenario == "N":
        return alpha_a2 * gamma * (ra + rb), (1 - alpha_a2) * gamma * (ra + rb)
    if scenario == "G":
        return (lam_s * gamma * ra + lam_n * alpha_a2 * gamma * (ra + rb),
                lam_s * gamma * rb + lam_n * (1 - alpha_a2) * gamma * (ra + rb))
    raise ValueError(f"unknown scenario {scenario!r}")


def best_response(objective, upper, grid=4001, xatol=1e-12):
    """Global maximiser of a scalar objective on [0, upper].

    `objective` maps an array of candidate order quantities to an array of
    payoffs. A grid search locates the best cell and a bounded scalar search
    refines it. Returns (argmax, max).
    """
    ys = np.linspace(0.0, upper, grid)
    vals = np.asarray(objective(ys), float)
    k = int(np.argmax(vals))
    lo, hi = ys[max(k - 2, 0)], ys[min(k + 2, grid - 1)]
    res = optimize.minimize_scalar(lambda y: -float(np.asarray(objective(np.array([y])))[0]),
                                   bounds=(lo, hi), method="bounded", options={"xatol": xatol})
    if -res.fun >= vals[k]:
        return float(res.x), float(-res.fun)
    return float(ys[k]), float(vals[k])


def nash_gap(payoff_a, payoff_b, ya, yb, upper):
    """How far (ya, yb) is from a Nash equilibrium of a two-player game.

    payoff_a(ya_array, yb) and payoff_b(ya, yb_array) return arrays of payoffs.
    Returns a dict with each player's best response to the other's quantity,
    the distance of the candidate from that best response, and the payoff gain
    of the best unilateral deviation (zero at an equilibrium).
    """
    br_a, max_a = best_response(lambda y: payoff_a(y, yb), upper)
    br_b, max_b = best_response(lambda y: payoff_b(ya, y), upper)
    at_a = float(np.asarray(payoff_a(np.array([ya]), yb))[0])
    at_b = float(np.asarray(payoff_b(ya, np.array([yb])))[0])
    return {"br_a": br_a, "br_b": br_b,
            "dist": max(abs(br_a - ya), abs(br_b - yb)),
            "gain": max(max_a - at_a, max_b - at_b)}
