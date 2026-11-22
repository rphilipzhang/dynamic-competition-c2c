"""N6, one part that numerics/ leaves out: Proposition 2(c) under the three other distributions.

Proposition 2(c): for theta < 1, y^S_{B,1} - y^N_{B,1} is first increasing then decreasing in gamma.
Lemmas 2 and 3 give the orders for a general distribution through F^{-1}; the repository's checks
confirm them as equilibria under these distributions (test_equilibria_from_primitives.py).
Points: 16 markets of `section4.draw_exogenous` per distribution (seed 2027), theta in
{0, 0.3, 0.7, 0.95}, gamma on 241 log-spaced values in [1e-3, 1e4]. The uniform distribution is
included as a control.
Criterion reported: the difference d(gamma) rises and then falls, with exactly one change of
direction (steps smaller than 1e-12 (1 + max|d|) are ignored), rising first.
Run from the repository root: python verification/2026-11-22_claude-opus-5-5-b/scripts/N6_prop2c_other_distributions.py
"""
from __future__ import annotations

import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, "numerics")
from c2c.section4 import claimed_first_period, distributions, draw_exogenous, seeded_rng  # noqa: E402

GAMMAS = np.logspace(-3, 4, 241)
THETAS = (0.0, 0.3, 0.7, 0.95)
NAMES = ("uniform", "triangular", "beta(2,5)", "truncated normal")


def shape(d):
    tol = 1e-12 * (1 + np.abs(d).max())
    steps = np.diff(d)
    s = np.sign(np.where(np.abs(steps) <= tol, 0.0, steps))
    s = s[s != 0]
    if s.size == 0:
        return "flat"
    changes = int(np.sum(np.diff(s) != 0))
    return f"{'rise' if s[0] > 0 else 'fall'}-first, {changes} change(s)"


def main():
    rng = seeded_rng(2027)
    markets = [draw_exogenous(rng) for _ in range(16)]
    for name in NAMES:
        tally = {}
        for prm, mu, sigma in markets:
            ppf = distributions(mu, sigma)[name].ppf
            for th in THETAS:
                d = []
                for g in GAMMAS:
                    p = replace(prm, theta=th, gamma=float(g))
                    ys = claimed_first_period(p, "S", ppf)
                    yn = claimed_first_period(p, "N", ppf)
                    assert ys[4] and yn[4]                       # A11: retailer A has the higher fractile
                    d.append(ys[1] - yn[1])
                key = shape(np.array(d))
                tally[key] = tally.get(key, 0) + 1
        print(f"{name:>16}: {sum(tally.values())} curves (16 markets x 4 theta): {tally}")


if __name__ == "__main__":
    main()
