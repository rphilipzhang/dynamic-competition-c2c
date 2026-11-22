"""Shape predicates used by the tests that compare the paper's statements with the model.

Two families live here and they must not be confused.

Exact predicates
    They take sequences of exact numbers (`fractions.Fraction`) and use no
    tolerance. `test_propositions_exogenous.py` uses them. "Increasing" means
    strictly increasing, and "constant" means equal as rational numbers.

Predicates with a tolerance
    They take floating-point arrays that come out of numerical integration.
    `test_other_distributions.py` uses them. They are weaker than the
    statements of the paper, and their names say how: "non-decreasing" accepts
    a constant function, "increasing overall" accepts a flat stretch, and "at
    most one change of sign" accepts a function that never changes sign.
"""
from __future__ import annotations

import numpy as np


# ----------------------------------------------------------------------------- exact
def strictly_increasing(values) -> bool:
    return all(a < b for a, b in zip(values, values[1:]))


def strictly_decreasing(values) -> bool:
    return all(a > b for a, b in zip(values, values[1:]))


def constant(values) -> bool:
    return all(v == values[0] for v in values)


def sign_runs(values) -> str:
    """The signs of the nonzero entries with repetitions removed, for example
    "+-" for a sequence that is positive first and negative afterwards. Exact
    zeros are skipped. The result is "" if every entry is zero."""
    signs = ["+" if v > 0 else "-" for v in values if v != 0]
    return "".join(s for k, s in enumerate(signs) if k == 0 or s != signs[k - 1])


def increments(values) -> list:
    return [b - a for a, b in zip(values, values[1:])]


# ----------------------------------------------------------------------------- with a tolerance
def _tolerance(v) -> float:
    return 1e-10 * (1.0 + np.abs(v).max())


def non_decreasing(v) -> bool:
    """No step of v falls by more than 1e-10 (1 + max |v|). A constant function passes."""
    return bool(np.all(np.diff(v) >= -_tolerance(v)))


def non_increasing(v) -> bool:
    """No step of v rises by more than 1e-10 (1 + max |v|). A constant function passes."""
    return bool(np.all(np.diff(v) <= _tolerance(v)))


def increasing_overall(v) -> bool:
    """Non-decreasing in the sense above, and the last value exceeds the first
    by more than 1e-10 (1 + max |v|). A constant function fails. A function
    with a flat stretch passes."""
    return non_decreasing(v) and bool(v[-1] - v[0] > _tolerance(v))


def decreasing_overall(v) -> bool:
    """Non-increasing in the sense above, and the last value is below the first
    by more than 1e-10 (1 + max |v|). A constant function fails."""
    return non_increasing(v) and bool(v[0] - v[-1] > _tolerance(v))


def nearly_constant(v) -> bool:
    """The range of v is at most 1e-9 (1 + max |v|)."""
    return bool(np.ptp(v) <= 1e-9 * (1.0 + np.abs(v).max()))


def visible_signs(v, tolerance=None):
    """Signs of the entries of v whose absolute value exceeds the tolerance."""
    tolerance = _tolerance(v) if tolerance is None else tolerance
    s = np.sign(np.where(np.abs(v) <= tolerance, 0.0, v))
    return s[s != 0]


def at_most_one_sign_change_from_positive(d) -> bool:
    """d is not negative first and positive later. Entries below
    1e-9 (1 + max |d|) in absolute value are ignored. A function of one sign
    passes, so this does not show that a change of sign exists."""
    return bool(np.all(np.diff(visible_signs(d, 1e-9 * (1.0 + np.abs(d).max()))) <= 0))


def changes_direction_at_most_once_from_falling(v) -> bool:
    """The steps of v do not rise first and fall later, and they change
    direction at most once. A function that only rises or only falls passes.
    Steps below 1e-12 (1 + max |v|) in absolute value are ignored."""
    s = visible_signs(np.diff(v), 1e-12 * (1.0 + np.abs(v).max()))
    return bool(np.all(np.diff(s) >= 0))


def falls_then_rises(v) -> bool:
    """The steps of v are negative first and positive afterwards, with at least
    one of each. Steps below 1e-12 (1 + max |v|) in absolute value are ignored."""
    s = visible_signs(np.diff(v), 1e-12 * (1.0 + np.abs(v).max()))
    return bool(s.size and np.all(np.diff(s) >= 0) and s[0] < 0 and s[-1] > 0)
