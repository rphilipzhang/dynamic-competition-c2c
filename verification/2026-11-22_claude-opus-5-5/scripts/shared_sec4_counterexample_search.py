"""Exact counterexample search for the universal claims of Propositions 1 to 6 (those that hold for
every gamma > 0), and a large-gamma check of the threshold claims, in exact rational arithmetic.

Closed forms of Lemmas 1 to 3 under A10, rho = 1 (the same formulas as shared_sec4_closed_forms.py,
written with fractions.Fraction). Points: random admissible markets (A1, A11, I1, I2) including
boundary points: equality in A11 in one or both periods, equal prices, shares close to 1, c_A/c_B
close to 0 and 1, sigma/mu close to 1, equal shares across periods. gamma in {1/1000, 1/10, 1, 10, 1000}
for universal claims; theta on the grid k/40 plus 1 - 10^-6.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5/scripts/shared_sec4_counterexample_search.py
"""
from __future__ import annotations

import random
from fractions import Fraction as Fr


def tails(s, P, th, gm):
    if s == "0":
        return P["ca"] / P["pa1"], P["cb"] / P["pb1"]
    mA, mB = P["pa2"] - P["ca"], P["pb2"] - P["cb"]
    if s == "S":
        return P["ca"] / (P["pa1"] + gm * mA), P["cb"] / (P["pb1"] + gm * mB)
    aB2 = 1 - P["aA2"]
    rA = P["ca"] / (P["pa1"] + P["aA2"] * gm * mA)
    rB = (P["cb"] - aB2 * gm * th * mB * rA) / (P["pb1"] + aB2 * gm * (1 - th) * mB)
    return rA, rB


def first(rA, rB, aA, th, mu, sg):
    aB = 1 - aA
    zA, zB = mu + sg - 2 * sg * rA, mu + sg - 2 * sg * rB
    return dict(yA=(aA + th * aB) * zA - th * aB * zB, yB=aB * zB,
                RA=aA * mu + th * aB * sg * rB**2 - (aA + th * aB) * sg * rA**2, RB=aB * (mu - sg * rB**2), rA=rA, rB=rB)


def q(s, P, th, gm):
    mu, sg = P["mu"], P["sg"]
    d = first(*tails(s, P, th, gm), P["aA1"], th, mu, sg)
    b = first(P["ca"] / P["pa2"], P["cb"] / P["pb2"], P["aA2"], th, mu, sg)
    piA2, piB2 = P["pa2"] * b["RA"] - P["ca"] * b["yA"], P["pb2"] * b["RB"] - P["cb"] * b["yB"]
    mA, mB = P["pa2"] - P["ca"], P["pb2"] - P["cb"]
    if s == "0":
        LA, LB, XA, XB = P["pa1"], P["pb1"], 0, 0
    elif s == "S":
        LA, LB, XA, XB = P["pa1"] + gm * mA, P["pb1"] + gm * mB, 0, 0
    else:
        JA, JB = P["aA2"] * gm * mA, (1 - P["aA2"]) * gm * mB
        LA, LB, XA, XB = P["pa1"] + JA, P["pb1"] + JB, JA, JB
    d["PiA"] = LA * d["RA"] - P["ca"] * d["yA"] + XA * d["RB"] + piA2
    d["PiB"] = LB * d["RB"] - P["cb"] * d["yB"] + XB * d["RA"] + piB2
    return d


def lat(lo, hi, den=1000):
    return Fr(random.randint(int(lo * den), int(hi * den)), den)


def draw(k):
    cb = lat(0.5, 3)
    ratio = random.choice([Fr(1, 1000), Fr(999, 1000), lat(0.05, 0.98)])
    ca = cb * ratio
    mu = lat(5, 20)
    sg = mu * random.choice([Fr(1, 100), Fr(999, 1000), lat(0.1, 0.95)])
    pb = [cb * random.choice([Fr(1001, 1000), Fr(50), lat(1.05, 4)]) for _ in range(2)]
    if k % 3 == 0:                                          # equal shares: same gap in both periods
        if random.random() < 0.3:
            pb[1] = pb[0]
        lam = random.choice([Fr(0), Fr(1), lat(0.001, 0.999)])
        gap = min(pb) * (1 - ratio) * (1 - lam)
        pa = [pb[0] - gap, pb[1] - gap]
    else:
        lams = [random.choice([Fr(0), Fr(1), lat(0.001, 0.999)]) for _ in range(2)]
        pa = [p * (ratio + l * (1 - ratio)) for p, l in zip(pb, lams)]
    gaps = [pb[0] - pa[0], pb[1] - pa[1]]
    G = max(gaps)
    beta = random.choice([Fr(1, 10**6), Fr(499, 1000), lat(0.001, 0.45)]) / G if G > 0 else random.choice([Fr(1, 10**6), Fr(5)])
    P = dict(pa1=pa[0], pb1=pb[0], pa2=pa[1], pb2=pb[1], ca=ca, cb=cb, mu=mu, sg=sg,
             aA1=Fr(1, 2) + beta * gaps[0], aA2=Fr(1, 2) + beta * gaps[1])
    assert 0 < ca < cb and all(cb * a >= ca * b and b >= a > ca and b > cb for a, b in zip(pa, pb))
    assert all(Fr(1, 2) <= P[x] < 1 for x in ("aA1", "aA2")) and mu > sg > 0
    return P


def nondecr(v):
    return all(b >= a for a, b in zip(v, v[1:]))


def runs(v):
    s = ["+" if x > 0 else "-" for x in v if x != 0]
    return "".join(c for i, c in enumerate(s) if i == 0 or c != s[i - 1])


random.seed(2026)
THETA = [Fr(k, 40) for k in range(41)]
THETA.insert(-1, 1 - Fr(1, 10**6))
GAMMA = [Fr(1, 1000), Fr(1, 10), Fr(1), Fr(10), Fr(1000)]
fails = {k: 0 for k in ("P1.i", "P2.a", "P2.b", "P2.c", "P3.a monotone", "P3.a cutoff", "P3.b", "P4 at large gamma",
                         "P5.a", "P6.a")}
N = 160
patterns_2c, patterns_4 = {}, {}
for k in range(N):
    P = draw(k)
    for gm in GAMMA:
        Z = [q("0", P, t, gm) for t in THETA]
        S = [q("S", P, t, gm) for t in THETA]
        Nn = [q("N", P, t, gm) for t in THETA]
        if not (nondecr([x["yA"] for x in Z]) and nondecr([x["yA"] for x in S]) and nondecr([x["yA"] for x in Nn])):
            fails["P1.i"] += 1
        if not (nondecr([-x["yB"] for x in Nn]) and len({x["yB"] for x in S}) == 1 and len({x["yB"] for x in Z}) == 1):
            fails["P2.a"] += 1
        if not all(z["yB"] < n["yB"] < s["yB"] for z, n, s in zip(Z, Nn, S)):
            fails["P2.b"] += 1
        if not (nondecr([x["RA"] for x in S]) and nondecr([x["RA"] for x in Nn])):
            fails["P3.a monotone"] += 1
        d = [s["RA"] - n["RA"] for s, n in zip(S, Nn)]
        if not (d[0] > 0 and runs(d) in ("+", "+-")):
            fails["P3.a cutoff"] += 1
        if not (nondecr([-x["RB"] for x in Nn]) and len({x["RB"] for x in S}) == 1 and all(n["RB"] < s["RB"] for n, s in zip(Nn, S))):
            fails["P3.b"] += 1
        if not nondecr([x["PiA"] for x in S]):
            fails["P5.a"] += 1
        if not (len({x["PiB"] for x in S}) == 1 and nondecr([x["PiB"] for x in Nn])):
            fails["P6.a"] += 1
    # P2.c: the gap y^S_B - y^N_B rises then falls along a gamma grid, theta < 1
    for t in (Fr(0), Fr(1, 2), Fr(99, 100)):
        grid = [Fr(10) ** e * m for e in range(-4, 12) for m in (1, 2, 5)]
        gap = [q("S", P, t, gm)["yB"] - q("N", P, t, gm)["yB"] for gm in grid]
        pat = runs([b - a for a, b in zip(gap, gap[1:])])
        patterns_2c[pat] = patterns_2c.get(pat, 0) + 1
        if pat not in ("+-", "+"):
            fails["P2.c"] += 1
    # P4 at gamma = 10^12: total sales fall then rise
    gm = Fr(10**12)
    tot = [q("N", P, t, gm)["RA"] + q("N", P, t, gm)["RB"] for t in [Fr(0), Fr(1, 10**20)] + THETA[1:-2] + [1 - Fr(1, 10**10), 1 - Fr(1, 10**20), Fr(1)]]
    pat = runs([b - a for a, b in zip(tot, tot[1:])])
    patterns_4[pat] = patterns_4.get(pat, 0) + 1
    if pat != "-+":
        fails["P4 at large gamma"] += 1

print(f"{N} random admissible markets (one third with equal shares), gamma in {[float(x) for x in GAMMA]}, "
      f"{len(THETA)} theta nodes, exact arithmetic")
for key, v in fails.items():
    print(f"  {key}: violations {v}")
print("  P2.c patterns of increments along gamma (theta = 0, 1/2, 99/100):", patterns_2c,
      "('+' only: peak beyond the grid end 5e11, not a violation)")
print("  P4 patterns of increments along theta at gamma = 1e12:", patterns_4)
