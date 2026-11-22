"""Closed forms of Lemmas 1 to 3 under A10 (uniform seed demand, rho = 1), written
independently of numerics/ from the statements and proofs in theory.md.

Used by the P1 to P6 scripts of this run. Run directly, it checks:
  1. the expected first-period sales formula E[R_A] = a_A mu + theta a_B sigma r_B^2
     - (a_A + theta a_B) sigma r_A^2 and E[R_B] = a_B (mu - sigma r_B^2) against a direct
     integration of min(D_i, y_i) over X ~ U[mu - sigma, mu + sigma];
  2. these SymPy closed forms against numerics/c2c/closed_form.py at random exact
     rational admissible points (orders, sales, total profits, scenarios 0, S, N).

Notation: r_i = 1 - F(zeta_i) is the critical tail probability; zeta_i = mu + sigma - 2 sigma r_i.
Shares are aA1, aA2 with aB_t = 1 - aA_t. The profits use
  Pi^S_A = (p_A1 + gamma m_A) E[R^S_A] - c_A y^S_A + pi^0_A2           (A.8)
  Pi^N_A = (p_A1 + J_A) E[R^N_A] - c_A y^N_A + J_A E[R^N_B] + pi^0_A2  (A.12), J_A = aA2 gamma m_A
and the analogues for B, with m_i = p_i2 - c_i.
"""
from __future__ import annotations

import os
import sys
from fractions import Fraction as Fr

import sympy as sp

pa1, pb1, pa2, pb2, cA, cB = sp.symbols("p_A1 p_B1 p_A2 p_B2 c_A c_B", positive=True)
aA1, aA2 = sp.symbols("alpha_A1 alpha_A2", positive=True)
th, g, mu, sg = sp.symbols("theta gamma mu sigma", positive=True)
aB1, aB2 = 1 - aA1, 1 - aA2


def zeta(r):
    return mu + sg - 2 * sg * r


def first_period(rA, rB, aA, theta=th):
    """Orders and expected sales for given tail probabilities (A has the higher fractile)."""
    aB = 1 - aA
    zA, zB = zeta(rA), zeta(rB)
    yA = (aA + theta * aB) * zA - theta * aB * zB
    yB = aB * zB
    RA = aA * mu + theta * aB * sg * rB**2 - (aA + theta * aB) * sg * rA**2
    RB = aB * (mu - sg * rB**2)
    return dict(yA=yA, yB=yB, RA=RA, RB=RB, rA=rA, rB=rB, zA=zA, zB=zB)


def tails(scenario, theta=th, gamma=g):
    if scenario == "0":
        return cA / pa1, cB / pb1
    if scenario == "S":
        return cA / (pa1 + gamma * (pa2 - cA)), cB / (pb1 + gamma * (pb2 - cB))
    if scenario == "N":
        rA = cA / (pa1 + aA2 * gamma * (pa2 - cA))
        rB = (cB - (1 - aA2) * gamma * theta * (pb2 - cB) * rA) / (pb1 + (1 - aA2) * gamma * (1 - theta) * (pb2 - cB))
        return rA, rB
    raise ValueError(scenario)


def period2_benchmark(theta=th):
    """pi^0_{A,2}, pi^0_{B,2}: benchmark profits at second-period prices."""
    q = first_period(cA / pa2, cB / pb2, aA2, theta)
    return pa2 * q["RA"] - cA * q["yA"], pb2 * q["RB"] - cB * q["yB"]


def quantities(scenario, theta=th, gamma=g):
    rA, rB = tails(scenario, theta, gamma)
    q = first_period(rA, rB, aA1, theta)
    piA2, piB2 = period2_benchmark(theta)
    mA, mB = pa2 - cA, pb2 - cB
    if scenario == "0":
        q["PiA"] = pa1 * q["RA"] - cA * q["yA"] + piA2
        q["PiB"] = pb1 * q["RB"] - cB * q["yB"] + piB2
    elif scenario == "S":
        q["PiA"] = (pa1 + gamma * mA) * q["RA"] - cA * q["yA"] + piA2
        q["PiB"] = (pb1 + gamma * mB) * q["RB"] - cB * q["yB"] + piB2
    else:
        JA, JB = aA2 * gamma * mA, (1 - aA2) * gamma * mB
        q["PiA"] = (pa1 + JA) * q["RA"] - cA * q["yA"] + JA * q["RB"] + piA2
        q["PiB"] = (pb1 + JB) * q["RB"] - cB * q["yB"] + JB * q["RA"] + piB2
    return q


# Denominators that the paper prints
P_S = pa1 + g * (pa2 - cA)          # (-gamma c_A + p_A1 + gamma p_A2)
Q_S = pb1 + g * (pb2 - cB)          # -(gamma c_B - p_B1 - gamma p_B2)
P_N = pa1 + aA2 * g * (pa2 - cA)    # -(alpha_A2 gamma c_A - p_A1 - alpha_A2 gamma p_A2)
D_N = pb1 + aB2 * g * (1 - th) * (pb2 - cB)


def as_poly(expr, *gens):
    return sp.Poly(sp.expand(expr), *gens)


# ----------------------------------------------------------------------------- self-checks
def _check_sales_by_integration():
    x = sp.symbols("x", real=True)
    aA = sp.symbols("a_A", positive=True)
    zA, zB = sp.symbols("z_A z_B", real=True)
    aB = 1 - aA
    yA = (aA + th * aB) * zA - th * aB * zB
    yB = aB * zB
    dens = 1 / (2 * sg)
    lo, hi = mu - sg, mu + sg
    # region mu - sigma <= zB <= zA <= mu + sigma; D_A = aA x for x <= zB, (aA + th aB) x - th aB zB beyond; R_A = min(D_A, y_A)
    ERA = (sp.integrate(aA * x * dens, (x, lo, zB)) + sp.integrate(((aA + th * aB) * x - th * aB * zB) * dens, (x, zB, zA))
           + sp.integrate(yA * dens, (x, zA, hi)))
    ERB = sp.integrate(aB * x * dens, (x, lo, zB)) + sp.integrate(yB * dens, (x, zB, hi))
    rA, rB = (mu + sg - zA) / (2 * sg), (mu + sg - zB) / (2 * sg)
    q = first_period(rA, rB, aA)
    ok1 = sp.simplify(ERA - q["RA"].subs(aA1, aA)) == 0
    ok2 = sp.simplify(ERB - q["RB"].subs(aA1, aA)) == 0
    # the ordering y_A at x = zA: D_A(zA) = y_A (continuity of the kink)
    ok3 = sp.simplify(((aA + th * aB) * zA - th * aB * zB) - yA) == 0
    print(f"E[R_A] closed form equals direct integration: {ok1}")
    print(f"E[R_B] closed form equals direct integration: {ok2}")
    print(f"D_A reaches y_A exactly at X = zeta_A: {ok3}")
    return ok1 and ok2 and ok3


def _check_against_port(n=40, seed=11):
    sys.path.insert(0, "numerics")
    import numpy as np
    from c2c import closed_form as cf
    rng = np.random.default_rng(seed)
    worst = Fr(0)
    for k in range(n):
        cb = Fr(int(rng.integers(500, 3000)), 1000)
        ca = cb * Fr(int(rng.integers(50, 980)), 1000)
        PB = [cb * Fr(int(rng.integers(1050, 4000)), 1000) for _ in range(2)]
        lam = [Fr(int(rng.integers(0, 1001)), 1000) for _ in range(2)]
        if k % 3 == 0:
            lam = [Fr(0), Fr(0)]                      # equality in A11 in both periods
        PA = [pb * (ca + (cb - ca) * l) / cb for pb, l in zip(PB, lam)]
        gap = max(PB[0] - PA[0], PB[1] - PA[1])
        beta = Fr(int(rng.integers(1, 499)), 1000) / gap if gap > 0 else Fr(1, 3)
        m = Fr(int(rng.integers(5000, 20000)), 1000)
        s = m * Fr(int(rng.integers(10, 999)), 1000)
        theta = Fr(int(rng.integers(0, 1001)), 1000)
        gam = Fr(int(rng.integers(1, 10**6)), 1000)
        sub = {pa1: PA[0], pb1: PB[0], pa2: PA[1], pb2: PB[1], cA: ca, cB: cb, mu: m, sg: s, th: theta, g: gam,
               aA1: Fr(1, 2) + beta * (PB[0] - PA[0]), aA2: Fr(1, 2) + beta * (PB[1] - PA[1])}
        args = (PA[0], PB[0], PA[1], PB[1], theta, ca, cb, beta, m, s)
        port = {}
        for scen, first in (("0", cf.first_period_s), ("S", cf.first_period_s), ("N", cf.first_period_n)):
            gg = Fr(0) if scen == "0" else gam
            ya, yb, la, lb, *_ = first(*args, gg)
            port[scen] = dict(yA=ya, yB=yb, RA=ya - la, RB=yb - lb)
        port["0"]["PiA"], port["0"]["PiB"] = cf.spfta_t1(*args, Fr(0)), cf.spftb_t1(*args, Fr(0))
        port["S"]["PiA"], port["S"]["PiB"] = cf.spfta_t1(*args, gam), cf.spftb_t1(*args, gam)
        port["N"]["PiA"], port["N"]["PiB"] = cf.npfta_t1(*args, gam), cf.npftb_t1(*args, gam)
        for scen in ("0", "S", "N"):
            mine = quantities(scen)
            for key in ("yA", "yB", "RA", "RB", "PiA", "PiB"):
                v = sp.Rational(mine[key].subs(sub))
                d = abs(Fr(int(v.p), int(v.q)) - Fr(port[scen][key]))
                worst = max(worst, d)
    print(f"largest |SymPy closed form - numerics port| over {n} exact points, 3 scenarios, 6 quantities: {worst}")
    return worst == 0


if __name__ == "__main__":
    a = _check_sales_by_integration()
    b = _check_against_port()
    print("ALL OK" if a and b else "MISMATCH")
