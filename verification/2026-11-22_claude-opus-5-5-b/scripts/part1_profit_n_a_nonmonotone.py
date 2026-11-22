"""A sentence of Section 4 (Profits) that neither theory.md nor numerics/numerical_statements.yaml lists:

    "However, when strong cross-brand C2C is present, we find that $\\Pi^N_{A}$ may decrease in
    $\\theta$ when $\\theta$ takes intermediate values."

No proposition states it. It is an existence claim: for some admissible markets with gamma large,
Pi^N_A falls on an interval of intermediate theta. This script looks for such markets.
Points: 300 markets of `section4.draw_exogenous` (seed 2026; A1, A11 strict, I1, I2, uniform demand),
gamma in {5, 50, 500, 5000}, theta = 0, 0.01, ..., 1. Pi^N_A from `closed_form.npfta_t1`, which the
repository's checks tie to the model (test_closed_form_sales_and_profits_equal_the_model[N]).
A market counts when Pi^N_A falls by more than 1e-9 (1 + |Pi|) over some step, and the falling steps
all lie strictly inside (0, 1) with Pi^N_A rising both before the first and after the last falling step.
Run from the repository root: python verification/2026-11-22_claude-opus-5-5-b/scripts/part1_profit_n_a_nonmonotone.py
"""
from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, "numerics")
from c2c import closed_form as cf  # noqa: E402
from c2c.section4 import draw_exogenous, seeded_rng  # noqa: E402

THETA = np.round(np.linspace(0.0, 1.0, 101), 12)
GAMMAS = (5.0, 50.0, 500.0, 5000.0)


def profile(prm, mu, sigma, gamma):
    return np.array([cf.npfta_t1(prm.pa1, prm.pb1, prm.pa2, prm.pb2, float(t), prm.ca, prm.cb, prm.beta, mu, sigma, gamma)
                     for t in THETA])


def main():
    rng = seeded_rng(2026)
    markets = [draw_exogenous(rng) for _ in range(300)]
    for gamma in GAMMAS:
        found, any_fall, example = 0, 0, None
        for prm, mu, sigma in markets:
            pi = profile(prm, mu, sigma, gamma)
            d = np.diff(pi)
            tol = 1e-9 * (1 + np.abs(pi).max())
            falls = np.nonzero(d < -tol)[0]
            if falls.size == 0:
                continue
            any_fall += 1
            first, last = falls[0], falls[-1]
            if first > 0 and last < len(d) - 1 and np.all(d[:first] > tol) and np.all(d[last + 1:] > tol):
                found += 1
                if example is None:
                    example = (prm, mu, sigma, THETA[first], THETA[last + 1], float(-d[falls].sum()))
        print(f"gamma = {gamma:g}: markets with some fall of Pi^N_A in theta {any_fall}/300; "
              f"with a fall only at intermediate theta (rise, fall, rise) {found}/300")
        if example:
            prm, mu, sigma, t0, t1, drop = example
            print(f"   example: pa1={prm.pa1:.4f} pb1={prm.pb1:.4f} pa2={prm.pa2:.4f} pb2={prm.pb2:.4f} ca={prm.ca:.4f} "
                  f"cb={prm.cb:.4f} beta={prm.beta:.4f} mu={mu:.3f} sigma={sigma:.3f}: falls on [{t0:.2f}, {t1:.2f}], total drop {drop:.4g}")


if __name__ == "__main__":
    main()
