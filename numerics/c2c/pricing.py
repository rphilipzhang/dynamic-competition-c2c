"""Pure-strategy price equilibria on a finite price menu (Section 5.3 of the paper).

Line-by-line Python port of `numerics/matlab/Figure1_MATLAB/pricing_equilibrium.m`.

The paper's numerical study of the Endogenous Price Model restricts each
retailer to a finite set of prices. The game is solved backward:

  Period 2. For every realized first-period sales state the retailers play a
            price game whose payoffs are the second-period equilibrium profits
            of `c2c.closed_form.period2_profit`. Those payoffs are affine in
            own sales (Scenario S) or in total sales (Scenario N), so a price
            pair that is an equilibrium at the two ends of the feasible range
            is an equilibrium at every state in between. The solver requires
            exactly one price pair to be an equilibrium at EVERY feasible
            sales state ("constant continuation") and stops otherwise.
  Period 1. Given that continuation, each first-period price pair is followed
            by the inventory equilibrium of Lemma 2 or Lemma 3, which gives
            the payoff matrices of a finite price game. All its pure
            equilibria are returned.
"""
from __future__ import annotations

import warnings

import numpy as np

from . import closed_form as cf

__all__ = ["pricing_equilibrium", "PricingError"]


class PricingError(ValueError):
    """Raised where the MATLAB code calls error()."""


def _eps(x: float) -> float:
    """MATLAB eps(x): spacing of double-precision numbers at x."""
    return float(np.spacing(abs(x)))


def _best_response_interval(gain_at_zero, gain_at_upper, tolerance):
    """Port of the local function `best_response_interval`.

    Intersects g0 + (g1 - g0) x >= 0 over all unilateral deviations, where x is
    own sales (S) or aggregate sales (N) divided by the upper demand bound.
    """
    left = np.asarray(gain_at_zero, float).ravel() + tolerance
    right = np.asarray(gain_at_upper, float).ravel() + tolerance
    if np.any((left < 0) & (right < 0)):
        return np.inf, -np.inf
    starts = left < 0
    ends = right < 0
    lower = max([0.0, *(-left[starts] / (right[starts] - left[starts]))])
    upper = min([1.0, *(left[ends] / (left[ends] - right[ends]))])
    return lower, upper


def _pure_equilibria(payoff_a, payoff_b):
    """Port of the local function `pure_equilibria`. Rows are A's prices and
    columns are B's prices. Ties are kept for either retailer."""
    if not (np.all(np.isfinite(payoff_a)) and np.all(np.isfinite(payoff_b))):
        raise PricingError("A price profile produced a nonfinite payoff.")
    tol_a = 64 * _eps(max(1.0, np.max(np.abs(payoff_a))))
    tol_b = 64 * _eps(max(1.0, np.max(np.abs(payoff_b))))
    best_a = payoff_a >= payoff_a.max(axis=0, keepdims=True) - tol_a
    best_b = payoff_b >= payoff_b.max(axis=1, keepdims=True) - tol_b
    return best_a & best_b


def _find(mask):
    """MATLAB [r, c] = find(mask): column-major order."""
    cols, rows = np.nonzero(mask.T)
    return rows, cols


def pricing_equilibrium(scenario, prices, theta, ca, cb, beta, mu, sigma, gamma):
    """Pure price equilibria for a finite price menu and uniform seed demand.

    Returns a dict with
        period2_prices        (pa2, pb2), the constant continuation
        other_period2_prices  price pairs that are equilibria at some but not all sales states
        period1_prices        array (k, 2), one row per first-period pure equilibrium
        total_profits         array (k, 2), two-period profits (A, B) at those equilibria
        payoff_a, payoff_b    first-period payoff matrices (rows: A's price, columns: B's price)
    """
    prices = np.asarray(prices)
    if not np.isrealobj(prices):
        raise PricingError("Use distinct finite prices above both unit costs.")
    prices = prices.astype(float).ravel(order="F")           # MATLAB prices(:) is column-major
    if (prices.size == 0 or not np.all(np.isfinite(prices)) or np.unique(prices).size != prices.size
            or np.any(prices <= max(ca, cb))):
        raise PricingError("Use distinct finite prices above both unit costs.")
    if (not np.all(np.isfinite([theta, ca, cb, beta, mu, sigma, gamma])) or theta < 0 or theta > 1
            or min(ca, cb) <= 0 or sigma <= 0 or mu < sigma or gamma < 0 or beta < 0
            or beta * (prices.max() - prices.min()) >= 0.5):
        raise PricingError("Check costs, positive demand shares, and the uniform-demand and C2C parameters.")
    if scenario not in ("S", "N"):
        raise PricingError("Use S or N for the C2C scenario.")

    # Feasible sales satisfy RA >= 0, RB >= 0, RA + RB <= mu + sigma.
    upper_demand = mu + sigma
    n = prices.size
    base_a, base_b = np.zeros((n, n)), np.zeros((n, n))
    upper_a, upper_b = np.zeros((n, n)), np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            args = (prices[i], prices[j], theta, ca, cb, beta, mu, sigma, scenario, gamma)
            base_a[i, j], base_b[i, j] = cf.period2_profit(*args, 0.0, 0.0)
            upper_a[i, j], _ = cf.period2_profit(*args, upper_demand, 0.0)
            _, upper_b[i, j] = cf.period2_profit(*args, 0.0, upper_demand)
    tol_a = 64 * _eps(max(1.0, np.abs(base_a).max(), np.abs(upper_a).max()))
    tol_b = 64 * _eps(max(1.0, np.abs(base_b).max(), np.abs(upper_b).max()))
    common = np.zeros((n, n), bool)
    possible = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(n):
            a = _best_response_interval(base_a[i, j] - base_a[:, j], upper_a[i, j] - upper_a[:, j], tol_a)
            b = _best_response_interval(base_b[i, j] - base_b[i, :], upper_b[i, j] - upper_b[i, :], tol_b)
            common[i, j] = a[0] == 0 and a[1] == 1 and b[0] == 0 and b[1] == 1
            if scenario == "S":
                possible[i, j] = a[0] <= a[1] and b[0] <= b[1] and a[0] + b[0] <= 1
            else:
                possible[i, j] = max(a[0], b[0]) <= min(a[1], b[1])

    a2, b2 = _find(common)
    if a2.size == 0:
        raise PricingError(
            f"No constant pure continuation was certified over the sales triangle in scenario {scenario}. "
            "A sales-dependent continuation analysis is needed for these parameters.")
    if a2.size > 1:
        raise PricingError(
            f"Several price pairs are equilibria at every sales state in scenario {scenario}: "
            f"{np.column_stack([prices[a2], prices[b2]]).tolist()}. "
            "Specify a continuation selection to evaluate period 1.")
    pa2, pb2 = float(prices[a2[0]]), float(prices[b2[0]])
    other_a, other_b = _find(possible & ~common)
    other = np.column_stack([prices[other_a], prices[other_b]])
    if other.size:
        warnings.warn(
            f"Using the constant continuation ({pa2:g}, {pb2:g}) in scenario {scenario}. Other pure price "
            f"pairs are supported at some sales states within the bound: {other.tolist()}.", stacklevel=2)

    # Every first-period price deviation gets its own inventory equilibrium.
    profit_a1, profit_b1 = (cf.spfta_t1, cf.spftb_t1) if scenario == "S" else (cf.npfta_t1, cf.npftb_t1)
    payoff_a, payoff_b = np.zeros((n, n)), np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            payoff_a[i, j] = profit_a1(prices[i], prices[j], pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma)
            payoff_b[i, j] = profit_b1(prices[i], prices[j], pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma)
    a1, b1 = _find(_pure_equilibria(payoff_a, payoff_b))
    return {
        "period2_prices": (pa2, pb2),
        "other_period2_prices": other,
        "period1_prices": np.column_stack([prices[a1], prices[b1]]),
        "total_profits": np.column_stack([payoff_a[a1, b1], payoff_b[a1, b1]]),
        "payoff_a": payoff_a,
        "payoff_b": payoff_b,
    }
