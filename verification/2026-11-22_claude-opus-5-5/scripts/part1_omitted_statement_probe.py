"""Part 1, item 5: a numerical claim of the paper that numerics/numerical_statements.yaml does not list.

Manuscript.tex, discussion after Proposition 5 (Section 4.2.3):
  "However, when strong cross-brand C2C is present, we find that $\\Pi^N_{A}$ may decrease in
   $\\theta$ when $\\theta$ takes intermediate values."
No proposition states it and no figure shows it. This script probes it: is there an admissible
Section 4 point (A1, A10, A11, I1, I2; uniform demand) at which Pi^N_A, the total two-period
profit of retailer A in Scenario N, strictly decreases on an interior theta interval?

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5/scripts/part1_omitted_statement_probe.py

Pi^N_A is computed twice: from the closed form of the port (closed_form.npfta_t1) and, at the
example printed, from the model primitives (section4.Game, exact uniform integration).
"""
import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, "numerics")
from c2c import closed_form as cf                              # noqa: E402
from c2c.section4 import Game, claimed_first_period, distributions, draw_exogenous, seeded_rng   # noqa: E402

THETA = np.linspace(0.0, 1.0, 101)
rng = seeded_rng(4242)
found = []
n = 0
for k in range(600):
    prm, mu, sigma = draw_exogenous(rng)
    for gamma in (5.0, 20.0, 100.0):
        n += 1
        vals = np.array([cf.npfta_t1(prm.pa1, prm.pb1, prm.pa2, prm.pb2, th, prm.ca, prm.cb, prm.beta, mu, sigma, gamma)
                         for th in THETA])
        d = np.diff(vals)
        tol = 1e-9 * (1 + np.abs(vals).max())
        down = np.nonzero(d < -tol)[0]
        if down.size and down.min() > 0 and down.max() < THETA.size - 2:
            found.append((float(-d.min() / (np.ptp(vals) + 1e-300)), prm, mu, sigma, gamma,
                          float(THETA[down.min()]), float(THETA[down.max() + 1]), vals))

print(f"points x gammas probed: {n}; with a strictly decreasing interior stretch of Pi^N_A: {len(found)}")
if found:
    found.sort(key=lambda t: -t[0])
    rel, prm, mu, sigma, gamma, t0, t1, vals = found[0]
    print(f"example: pa1={prm.pa1:.4f} pb1={prm.pb1:.4f} pa2={prm.pa2:.4f} pb2={prm.pb2:.4f} ca={prm.ca:.4f} cb={prm.cb:.4f} "
          f"beta={prm.beta:.4f} mu={mu:.4f} sigma={sigma:.4f} gamma={gamma}")
    print(f"  Pi^N_A falls on theta in [{t0:.2f}, {t1:.2f}]; values at 0, {t0:.2f}, {t1:.2f}, 1: "
          f"{vals[0]:.6f}, {vals[int(round(t0 * 100))]:.6f}, {vals[int(round(t1 * 100))]:.6f}, {vals[-1]:.6f}")
    dist = distributions(mu, sigma)["uniform"]
    for th in (0.0, t0, t1, 1.0):
        p = replace(prm, theta=th, gamma=gamma)
        ya, yb, *_ = claimed_first_period(p, "N", dist.ppf)
        pay_a, _ = Game(p, "N", dist).period1_payoffs()
        print(f"  theta={th:.2f}: model (primitives) Pi^N_A = {float(np.ravel(pay_a(ya, yb))[0]):.6f}")
