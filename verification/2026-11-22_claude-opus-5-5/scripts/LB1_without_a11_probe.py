"""Lemma B.1 without the price condition A11: is the stated closed form still an equilibrium?

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5/scripts/LB1_without_a11_probe.py

theory.md LB1, difference 1, claims: "Without it the stated closed form is in general not an
equilibrium." This script tests that claim in the model of Section 3.

Points: `section4.draw_without_a11` (seed 7101), mixed scenario G with the lambda_S of the draw,
uniform seed demand. For each point:
  own_a = c_A/(p_A1 + gamma_A2 m_A), own_b = c_B/(p_B1 + gamma_B2 m_B)  (the ordering in the proof),
  the STATED closed form of Lemma B.1 (retailer A's fractile higher), whatever the ordering,
  `primitives.nash_gap` of the stated form for the two-period payoffs of `section4.Game` (G),
  whose continuation uses the true benchmark equilibrium at the second-period prices.
The relative gain is gain / (mu (1 + gamma)). Groups:
  (i)  A11 fails but own_a <= own_b: the stated form should still be an equilibrium;
  (ii) own_a > own_b: the stated form should fail (unless its fractile leaves [0, 1], then it
       is undefined), and the mirror form of `claimed_first_period` should be an equilibrium.
Also period 2: at points with c_A/p_A2 > c_B/p_B2, the A-higher form of Lemma 1 at the
second-period prices (the y^0_{i,2} of Lemma B.1) against the second-period game at a sales state.
"""
import sys
import numpy as np

sys.path.insert(0, "numerics")
from c2c import primitives as pm                                       # noqa: E402
from c2c.section4 import Game, claimed_first_period, draw_without_a11, seeded_rng  # noqa: E402

N = 60
rng = seeded_rng(7101)
rows = []
for _ in range(N):
    prm, mu, sigma = draw_without_a11(rng)
    dist = pm.Uniform(mu - sigma, mu + sigma)
    gA, gB, gcA, gcB = prm.weights("G")
    mA, mB, th = prm.pa2 - prm.ca, prm.pb2 - prm.cb, prm.theta
    own_a = prm.ca / (prm.pa1 + gA * mA)
    own_b = prm.cb / (prm.pb1 + gB * mB)
    qa = 1 - own_a
    qb = 1 - (prm.cb - gcB * th * mB * own_a) / (prm.pb1 + (gB - gcB * th) * mB)
    aA, aB = prm.aa1, 1 - prm.aa1
    game = Game(prm, "G", dist)
    pay_a, pay_b = game.period1_payoffs()
    scale = mu * (1 + prm.gamma)
    a11 = all(pb >= pa >= prm.ca / prm.cb * pb for pa, pb in ((prm.pa1, prm.pb1), (prm.pa2, prm.pb2)))
    stated_gain = None
    if 0 <= qa <= 1 and 0 <= qb <= 1:
        ya, yb = (aA + th * aB) * dist.ppf(qa) - th * aB * dist.ppf(qb), aB * dist.ppf(qb)
        stated_gain = pm.nash_gap(pay_a, pay_b, ya, yb, 1.5 * (mu + sigma))["gain"] / scale
    ya_c, yb_c, *_ = claimed_first_period(prm, "G", dist.ppf)
    claimed_gain = pm.nash_gap(pay_a, pay_b, ya_c, yb_c, 1.5 * (mu + sigma))["gain"] / scale
    rows.append(dict(a11=a11, a_high=own_a <= own_b, stated=stated_gain, claimed=claimed_gain,
                     lam=prm.lam_s, prm=prm))

g1 = [r for r in rows if not r["a11"] and r["a_high"]]
g2 = [r for r in rows if r["a11"]]
g3 = [r for r in rows if not r["a_high"]]
print(f"points {N}: A11 holds {len(g2)}, A11 fails with A higher {len(g1)}, retailer B higher {len(g3)}")
if g1:
    print(f"(i) A11 fails, own_a <= own_b: max relative gain of the stated form {max(r['stated'] for r in g1):.2e}")
defined = [r for r in g3 if r["stated"] is not None]
print(f"(ii) own_a > own_b: stated form defined at {len(defined)} of {len(g3)} points "
      f"(at the others its fractile q^G_B leaves [0, 1])")
if defined:
    gains = sorted(r["stated"] for r in defined)
    print(f"     relative gain of the stated form: min {gains[0]:.2e}, median {gains[len(gains)//2]:.2e}, max {gains[-1]:.2e}; "
          f"above 1e-6 at {sum(g > 1e-6 for g in gains)} of {len(gains)}")
print(f"     mirror form (claimed_first_period, B higher): max relative gain {max(r['claimed'] for r in g3):.2e}")

# second period: Lemma 1 form with A higher at prices with c_A/p_A2 > c_B/p_B2
rng2 = seeded_rng(7102)
bad, tried, gains2 = 0, 0, []
while tried < 15:
    prm, mu, sigma = draw_without_a11(rng2)
    if prm.ca / prm.pa2 <= prm.cb / prm.pb2:
        continue
    tried += 1
    dist = pm.Uniform(mu - sigma, mu + sigma)
    game = Game(prm, "G", dist)
    ra1 = float(rng2.uniform(0, mu + sigma))
    rb1 = float(rng2.uniform(0, mu + sigma - ra1))
    pay_a, pay_b, za, zb = game.period2_payoffs(ra1, rb1)
    a2, b2, th = prm.aa2, 1 - prm.aa2, prm.theta
    zA, zB = dist.ppf(1 - prm.ca / prm.pa2), dist.ppf(1 - prm.cb / prm.pb2)
    ya, yb = (a2 + th * b2) * zA - th * b2 * zB + za, b2 * zB + zb
    g = pm.nash_gap(pay_a, pay_b, ya, yb, game.upper)["gain"] / (mu * (1 + prm.gamma))
    gains2.append(g)
    bad += g > 1e-6
print(f"period 2, c_A/p_A2 > c_B/p_B2: A-higher Lemma 1 form plus Z fails (gain > 1e-6) at {bad} of {tried} points; "
      f"min gain {min(gains2):.2e}, max {max(gains2):.2e}")
