"""The last paragraph of the joint proof of Lemmas A.1-A.2, used by Proposition 9(b):
Pi_i^N(p_1) = gamma nu_i mu + K_i(theta) + alpha_{i,1}(mu p_{i,1} - c_i(mu+sigma)) + O_{C^2}(gamma^-1), "for each fixed theta < 1".

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5-b/scripts/P9_profit_expansion_fixed_theta.py

Pi_i^N is computed from the model: the inventory equilibrium of Scenario N solved from the model's first-order
conditions (section5.inventory_equilibrium) with the continuation section5.SecondPeriodN, and the two-period profit
section5.first_period_profits. K_i(theta) = lim (V_i(R_1) - gamma nu_i R_1) as gamma R_1 -> oo is read from the
same table: with V_i = f_i(s) + g_i(s)/s and s = 1/(gamma R_1), K_i = f_i(0) + g_i'(0).
Printed for gamma = 1e2, 1e3, 1e4 at theta = 0.5 (fixed), theta = 1 - 1/gamma and theta = 1:
  rem_i     = gamma x [Pi_i^N - gamma nu_i mu - K_i - alpha_i(mu p_i - c_i(mu+sigma))]      (bounded if O(1/gamma))
  drem_i    = gamma x [dPi_i^N/dp_i - mu(1/2 + beta p_j - 2 beta p_i) - beta c_i(mu+sigma)]  (central difference)
"""
import sys
from dataclasses import replace

sys.path.insert(0, "numerics")

import numpy as np

from c2c import primitives as pm
from c2c import section5 as s5


def total_profit(mk, cont, gamma, pa1, pb1):
    claim = tuple(float(v) for v in s5.claimed_orders_n(mk, gamma, pa1, pb1))
    ya, yb = (float(v) for v in s5.inventory_equilibrium(mk, cont, gamma, pa1, pb1, claim))
    fa, fb = s5.marginal_profits(mk, cont, gamma, pa1, pb1, ya, yb)
    assert max(abs(float(fa)) / mk.ca, abs(float(fb)) / mk.cb) <= 1e-12 * (10 + gamma)
    return np.array([float(v) for v in s5.first_period_profits(mk, cont, gamma, pa1, pb1, ya, yb)])


rng = np.random.default_rng(21)
for k in range(3):
    base = s5.draw_market(rng)
    pa1 = base.p_lo + rng.uniform(0.3, 0.7) * (base.p_hi - base.p_lo)
    pb1 = base.p_lo + rng.uniform(0.3, 0.7) * (base.p_hi - base.p_lo)
    h = 1e-3 * (base.p_hi - base.p_lo)
    nu = np.array(s5.claimed_nu(base))
    print(f"market {k}: c=({base.ca:.3f}, {base.cb:.3f}) beta={base.beta:.3f} mu={base.mu:.2f} sigma={base.sigma:.2f} "
          f"p_1=({pa1:.3f}, {pb1:.3f})")
    print("    gamma    theta      rem_A       rem_B      drem_A      drem_B")
    for gamma in (1e2, 1e3, 1e4):
        for label, theta in (("0.5", 0.5), ("1-1/g", 1 - 1 / gamma), ("1", 1.0)):
            mk = replace(base, theta=theta)
            cont = s5.SecondPeriodN(mk, 2.0 / (gamma * mk.lo))
            assert not cont.problems, cont.problems
            zero = np.array([0.0])
            K = np.array([cont._eval(zero, 2)[0] + cont._eval(zero, 8)[0], cont._eval(zero, 3)[0] + cont._eval(zero, 9)[0]])
            assert abs(cont._eval(zero, 4)[0] - nu[0]) < 1e-9 * nu[0] and abs(cont._eval(zero, 5)[0] - nu[1]) < 1e-9 * nu[1]
            sa = pm.share(pa1, pb1, mk.beta)
            shares = np.array([sa, 1 - sa])
            own = np.array([pa1, pb1])
            costs = np.array([mk.ca, mk.cb])
            lead = gamma * nu * mk.mu + K + shares * (mk.mu * own - costs * mk.hi)
            pi = total_profit(mk, cont, gamma, pa1, pb1)
            rem = gamma * (pi - lead)
            d_a = (total_profit(mk, cont, gamma, pa1 + h, pb1)[0] - total_profit(mk, cont, gamma, pa1 - h, pb1)[0]) / (2 * h)
            d_b = (total_profit(mk, cont, gamma, pa1, pb1 + h)[1] - total_profit(mk, cont, gamma, pa1, pb1 - h)[1]) / (2 * h)
            lim_a = mk.mu * (0.5 + mk.beta * pb1 - 2 * mk.beta * pa1) + mk.beta * mk.ca * mk.hi
            lim_b = mk.mu * (0.5 + mk.beta * pa1 - 2 * mk.beta * pb1) + mk.beta * mk.cb * mk.hi
            print(f"   {gamma:7.0f}  {label:>6}  {rem[0]:10.4g}  {rem[1]:10.4g}  {gamma * (d_a - lim_a):10.4g}  {gamma * (d_b - lim_b):10.4g}")
