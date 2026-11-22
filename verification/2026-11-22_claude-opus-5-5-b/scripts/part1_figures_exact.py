"""Part 1: numerics/c2c/pricing.py and figures.py, by an independent exact recomputation of Figure 1 and B.1.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5-b/scripts/part1_figures_exact.py

The script re-implements, in exact rational arithmetic and without the package's formulas:
  - the first-period inventory equilibrium (both fractile orderings) from the first-order conditions,
  - expected sales by exact piecewise integration of the demand system of Section 3 over U[5, 15],
  - the second-period price game at EVERY sales state of the triangle R_A, R_B >= 0, R_A + R_B <= 15,
    solved exactly through the affine dependence of the continuation payoffs on the state,
  - the first-period pure equilibria of the 2x2 price game, with no tolerance,
and compares the result with figures.figure1_data(), figures.figure1_crossings(), figures.figureB1_data()
and the authors' MATLAB values in numerics/matlab/Figure2_MATLAB/Figure2_reference.csv.
It also prints the parameter checks against Section 5 and the captions.
"""
from __future__ import annotations

import sys
from fractions import Fraction as Fr
from functools import lru_cache

sys.path.insert(0, "numerics")
import numpy as np
import pandas as pd

from c2c import figures as F

MU, SG, CB, BETA = Fr(10), Fr(5), Fr(1), Fr(1, 10)
PRICES = (Fr(2), Fr(4))
U = MU + SG


def share(p_own, p_other):
    return Fr(1, 2) + BETA * (p_other - p_own)


def integ(c0, c1, u, v):
    return c0 * (v - u) - c1 * (v * v - u * u) / 2


def leftovers(a_h, a_l, z_h, z_l, th):
    lo = MU - SG
    y_h = (a_h + th * a_l) * z_h - th * a_l * z_l
    y_l = a_l * z_l
    L_l = integ(y_l, a_l, lo, z_l) / (2 * SG)
    L_h = (integ(y_h, a_h, lo, z_l) + integ(y_h + th * y_l, a_h + th * a_l, z_l, z_h)) / (2 * SG)
    return y_h, y_l, L_h, L_l


def equilibrium(pA1, pB1, pA2, pB2, cA, th, w):
    """First-period equilibrium for continuation weights w = (g_A, g_B, gc_A, gc_B)."""
    gA, gB, gcA, gcB = w
    mA, mB = pA2 - cA, pB2 - CB
    kA, kB = cA / (pA1 + gA * mA), CB / (pB1 + gB * mB)
    a_high = kA <= kB
    if a_high:
        qA, qB = 1 - kA, 1 - (CB - gcB * th * mB * kA) / (pB1 + (gB - gcB * th) * mB)
    else:
        qB, qA = 1 - kB, 1 - (cA - gcA * th * mA * kB) / (pA1 + (gA - gcA * th) * mA)
    assert 0 <= qA <= 1 and 0 <= qB <= 1
    zA, zB = MU - SG + 2 * SG * qA, MU - SG + 2 * SG * qB
    a1 = share(pA1, pB1)
    if a_high:
        yA, yB, LA, LB = leftovers(a1, 1 - a1, zA, zB, th)
    else:
        yB, yA, LB, LA = leftovers(1 - a1, a1, zB, zA, th)
    return yA, yB, yA - LA, yB - LB, a_high, abs(kA - kB)


@lru_cache(maxsize=None)
def pi0(pA2, pB2, cA, th):
    yA, yB, RA, RB, *_ = equilibrium(pA2, pB2, pA2, pB2, cA, th, (0, 0, 0, 0))
    return pA2 * RA - cA * yA, pB2 * RB - CB * yB


def total_profits(pA1, pB1, pA2, pB2, cA, th, w):
    yA, yB, RA, RB, a_high, kgap = equilibrium(pA1, pB1, pA2, pB2, cA, th, w)
    gA, gB, gcA, gcB = w
    p0A, p0B = pi0(pA2, pB2, cA, th)
    PiA = pA1 * RA - cA * yA + (pA2 - cA) * (gA * RA + gcA * RB) + p0A
    PiB = pB1 * RB - CB * yB + (pB2 - CB) * (gB * RB + gcB * RA) + p0B
    return PiA, PiB, yA, yB, a_high, kgap


def interval(gains):
    """{t in [0, 1]: g0 + (g1 - g0) t >= 0 for all (g0, g1)}, exactly. None if empty."""
    lo, hi = Fr(0), Fr(1)
    for g0, g1 in gains:
        if g0 < 0 and g1 < 0:
            return None
        if g0 < 0:
            lo = max(lo, -g0 / (g1 - g0))
        elif g1 < 0:
            hi = min(hi, g0 / (g0 - g1))
    return (lo, hi) if lo <= hi else None


def second_period(scenario, cA, th, gam):
    """Exact solution of the second-period price game over the whole sales triangle.
    Returns (pairs that are equilibria at every state, pairs that are equilibria at some state, min margin)."""
    P = PRICES
    def u(i, j, RA, RB):
        a = share(P[i], P[j])
        p0A, p0B = pi0(P[i], P[j], cA, th)
        if scenario == "S":
            ZA, ZB = gam * RA, gam * RB
        else:
            ZA, ZB = a * gam * (RA + RB), (1 - a) * gam * (RA + RB)
        return p0A + (P[i] - cA) * ZA, p0B + (P[j] - CB) * ZB
    always, some, margins = [], [], []
    for i in range(2):
        for j in range(2):
            # A's gains from deviating to k, at the two ends of its state variable (R_A in S, R_A + R_B in N)
            gA = [(u(i, j, 0, 0)[0] - u(k, j, 0, 0)[0], u(i, j, U, 0)[0] - u(k, j, U, 0)[0]) for k in range(2) if k != i]
            gB = [(u(i, j, 0, 0)[1] - u(i, k, 0, 0)[1], u(i, j, 0, U)[1] - u(i, k, 0, U)[1]) for k in range(2) if k != j]
            iA, iB = interval(gA), interval(gB)
            full = iA == (0, 1) and iB == (0, 1)
            if full:
                always.append((P[i], P[j]))
                margins.append(min(min(g) for g in gA + gB))
            if scenario == "S":
                ok = iA is not None and iB is not None and iA[0] + iB[0] <= 1
            else:
                ok = iA is not None and iB is not None and max(iA[0], iB[0]) <= min(iA[1], iB[1])
            if ok:
                some.append((P[i], P[j]))
    return always, some, (min(margins) if margins else None)


def figure1_point(cA, th, gam):
    out = {}
    for sc in ("S", "N"):
        always, some, m2 = second_period(sc, cA, th, gam)
        assert len(always) == 1, (sc, cA, th, gam, always)
        pA2, pB2 = always[0]
        a2 = share(pA2, pB2)
        w = (gam, gam, 0, 0) if sc == "S" else (a2 * gam, (1 - a2) * gam, a2 * gam, (1 - a2) * gam)
        cells = {(i, j): total_profits(PRICES[i], PRICES[j], pA2, pB2, cA, th, w) for i in range(2) for j in range(2)}
        eq = [(i, j) for (i, j) in cells
              if cells[(i, j)][0] >= max(cells[(k, j)][0] for k in range(2))
              and cells[(i, j)][1] >= max(cells[(i, k)][1] for k in range(2))]
        assert len(eq) == 1, (sc, cA, th, gam, eq)
        i, j = eq[0]
        m1 = min(cells[(i, j)][0] - cells[(1 - i, j)][0], cells[(i, j)][1] - cells[(i, 1 - j)][1])
        out[sc] = dict(prices=(PRICES[i], PRICES[j], pA2, pB2), profits=cells[(i, j)][:2], other2=len(some) - 1,
                       margin2=m2, margin1=m1, b_high=sum(not c[4] for c in cells.values()),
                       kgap=min(c[5] for c in cells.values()))
    return out


# --------------------------------------------------------------------------------------- Figure 1
THETA1 = [Fr(1, 100)] + [Fr(k, 10) for k in range(1, 10)] + [Fr(99, 100)]
PANELS1 = {"a": ("A", Fr(1, 10), Fr(7, 10)), "b": ("A", Fr(1, 10), Fr(2)),
           "c": ("B", Fr(95, 100), Fr(7, 10)), "d": ("B", Fr(95, 100), Fr(2))}
port = F.figure1_data()
worst_profit, price_mismatch, other2, b_high_cells = 0.0, 0, 0, 0
min_m1, min_m2, min_kgap = None, None, None
for panel, (ret, cA, gam) in PANELS1.items():
    k = "AB".index(ret)
    for th in THETA1:
        pt = figure1_point(cA, th, gam)
        row = port[(port.panel == panel) & np.isclose(port.theta, float(th), atol=1e-12)].iloc[0]
        for sc in ("S", "N"):
            worst_profit = max(worst_profit, abs(float(pt[sc]["profits"][k]) - row[f"profit_{sc}"]))
            price_mismatch += tuple(float(v) for v in pt[sc]["prices"]) != tuple(row[[f"{n}_{sc}" for n in ("pa1", "pb1", "pa2", "pb2")]])
            other2 += pt[sc]["other2"]
            b_high_cells += pt[sc]["b_high"]
            min_m1 = pt[sc]["margin1"] if min_m1 is None else min(min_m1, pt[sc]["margin1"])
            min_m2 = pt[sc]["margin2"] if min_m2 is None else min(min_m2, pt[sc]["margin2"])
            min_kgap = pt[sc]["kgap"] if min_kgap is None else min(min_kgap, pt[sc]["kgap"])
print("Figure 1: 44 points x 2 scenarios recomputed exactly")
print("  max |exact plotted profit - figure1_data|:", f"{worst_profit:.3e}")
print("  equilibrium price paths (pa1, pb1, pa2, pb2) differing from figure1_data:", price_mismatch)
print("  second-period price pairs that are an equilibrium at SOME sales state besides the constant one:", other2)
print("  first-period cells (of 352) where retailer B has the higher critical fractile:", b_high_cells)
print("  smallest |kappa_A - kappa_B| over the 352 cells (distance from the branch switch):", f"{float(min_kgap):.4f}")
print("  smallest second-period equilibrium margin (gain of the best deviation, any state):", f"{float(min_m2):.4f}")
print("  smallest first-period pure-equilibrium margin:", f"{float(min_m1):.6f}")
for panel in "abcd":
    sub = port[port.panel == panel]
    print(f"  panel {panel}: price paths S", sorted(set(zip(sub.pa1_S, sub.pb1_S, sub.pa2_S, sub.pb2_S))),
          "N", sorted(set(zip(sub.pa1_N, sub.pb1_N, sub.pa2_N, sub.pb2_N))))

# crossings: bisection on the exact gap, compared with figures.figure1_crossings
port_cross = F.figure1_crossings()
for panel, (ret, cA, gam) in PANELS1.items():
    k = "AB".index(ret)
    gap = lambda th: (lambda p: p["N"]["profits"][k] - p["S"]["profits"][k])(figure1_point(cA, th, gam))
    vals = [gap(th) for th in THETA1]
    roots = []
    for a, b, va, vb in zip(THETA1[:-1], THETA1[1:], vals[:-1], vals[1:]):
        if va * vb < 0:
            lo, hi, vlo = a, b, va
            for _ in range(45):
                mid = (lo + hi) / 2
                vm = gap(mid)
                if (vm < 0) == (vlo < 0):
                    lo, vlo = mid, vm
                else:
                    hi = mid
            roots.append(float((lo + hi) / 2))
    print(f"  crossings panel {panel}: exact bisection {[round(r, 10) for r in roots]}, "
          f"figure1_crossings {[round(r, 10) for r in port_cross[panel]]}")

# --------------------------------------------------------------------------------------- Figure B.1
THETAB = [Fr(k, 10) for k in range(11)]
SCEN = {"GS": (Fr(2), Fr(8, 10)), "GN": (Fr(2), Fr(2, 10)), "0": (Fr(0), Fr(8, 10))}
PANELSB = {"a": (0, Fr(1, 2), ("GS", "GN")), "b": (1, Fr(1, 2), ("GS", "GN", "0")),
           "c": (2, Fr(1, 10), ("GS", "GN")), "d": (3, Fr(92, 100), ("GS", "GN"))}
p2 = Fr(2)
mine = {"theta": [float(t) for t in THETAB]}
for panel, (q, cA, scs) in PANELSB.items():
    for s in scs:
        gam, lam_s = SCEN[s]
        a2 = share(p2, p2)
        w = ((lam_s + (1 - lam_s) * a2) * gam, (lam_s + (1 - lam_s) * (1 - a2)) * gam,
             (1 - lam_s) * gam * a2, (1 - lam_s) * gam * (1 - a2))
        col = []
        for th in THETAB:
            PiA, PiB, yA, yB, a_high, _ = total_profits(p2, p2, p2, p2, cA, th, w)
            assert a_high
            col.append(float((yA, yB, PiA, PiB)[q]))
        mine[f"{panel}_{s}"] = col
mine = pd.DataFrame(mine)
portB = F.figureB1_data()
ref = pd.read_csv("numerics/matlab/Figure2_MATLAB/Figure2_reference.csv")
cols = [c for c in ref.columns if c != "theta"]
print("Figure B.1: columns", cols)
print("  columns of figureB1_data equal to the reference file's:", list(portB.columns) == list(ref.columns))
print("  max |exact - figureB1_data|:", f"{np.abs(mine[cols].values - portB[cols].values).max():.3e}")
print("  max |exact - MATLAB reference csv|:", f"{np.abs(mine[cols].values - ref[cols].values).max():.3e}")
print("  max |figureB1_data - MATLAB reference csv|:", f"{np.abs(portB[cols].values - ref[cols].values).max():.3e}")

# --------------------------------------------------------------------------------------- parameters vs paper
print("Parameters against the paper")
print("  figures.FIG1_PARAMS:", F.FIG1_PARAMS, " FIG1_PANELS:", F.FIG1_PANELS)
print("  figures.FIGB1_PARAMS:", F.FIGB1_PARAMS, " FIGB1_SCENARIOS:", F.FIGB1_SCENARIOS)
print("  figures.FIGB1_PANELS:", {k: (v[0], v[1], v[2]) for k, v in F.FIGB1_PANELS.items()})
dec1 = np.array([0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99])
decB = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
print("  FIG1_THETA entries that differ in the last bits from the decimal literals:",
      [(float(d), repr(float(t))) for t, d in zip(F.FIG1_THETA, dec1) if t != d])
print("  FIGB1_THETA entries that differ in the last bits from the decimal literals:",
      [(float(d), repr(float(t))) for t, d in zip(F.FIGB1_THETA, decB) if t != d])
plo, phi = min(PRICES), max(PRICES)
print("  Section 5: p_lower > c_B:", plo > CB, "; beta (p_upper - p_lower) =", float(BETA * (phi - plo)), "< 1/2:",
      BETA * (phi - plo) < Fr(1, 2))
for cA in (Fr(1, 10), Fr(95, 100)):
    lo_b = 1 / (2 * BETA) + (2 * cA + CB) / 3
    hi_b = 1 / (2 * BETA) + (MU + SG) * (cA + 2 * CB) / (3 * MU)
    print(f"  Section 5 footnote at c_A = {float(cA)}: needs p_lower < {float(lo_b):.4f} (p_lower = 2: {plo < lo_b}), "
          f"p_upper > {float(hi_b):.4f} (p_upper = 4: {phi > hi_b})")
for cA in (Fr(1, 2), Fr(1, 10), Fr(92, 100)):
    print(f"  Figure B.1 at c_A = {float(cA)}: A11 p_B >= p_A >= (c_A/c_B) p_B with all prices 2:",
          p2 >= p2 >= cA / CB * p2)
