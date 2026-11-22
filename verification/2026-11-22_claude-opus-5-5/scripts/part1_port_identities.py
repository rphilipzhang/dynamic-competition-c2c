"""Part 1, item 3: independent identities for the MATLAB port in numerics/c2c/closed_form.py.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5/scripts/part1_port_identities.py

1. pfta_t2_case1 / pftb_t2_case1 (ports of pftaT2Case1.m / pftbT2Case1.m) equal
   pi^0 = (p - c) y^0 - p E[L^0] of the proof of Lemma 1 under U[mu-sigma, mu+sigma],
   by full symbolic simplification (the repo test uses 25 rational points).
2. The branches that the repo's transcription tests do not force (retailer B has the
   higher critical fractile) are the mirror image of the Lemma 2 / Lemma 3 branch:
   swapping the roles of A and B in the arguments must swap the outputs. Exact rationals.
3. _share((1 + 2 b d)/2) is bit-identical to MATLAB's 1/2 + b d in IEEE doubles.
4. matlab_colon grids used for both figures.
5. Figure2_reference.csv against the port, and the stored reproduced/ CSVs against a fresh run.
"""
import random
import sys

import numpy as np
import pandas as pd
import sympy as sp

sys.path.insert(0, "numerics")
from c2c import closed_form as cf          # noqa: E402
from c2c import figures as F               # noqa: E402

# ---------------------------------------------------------------- 1. benchmark profit polynomials
pa, pb, ca, cb, be, th, mu, sg, x = sp.symbols("p_A p_B c_A c_B beta theta mu sigma x", positive=True)
aa = sp.Rational(1, 2) + be * (pb - pa)
ab = 1 - aa
za = mu - sg + 2 * sg * (1 - ca / pa)
zb = mu - sg + 2 * sg * (1 - cb / pb)
ya = (aa + th * ab) * za - th * ab * zb
yb = ab * zb
# E[(y_A - D_A)^+] with D_A = a_A X + theta (a_B X - y_B)^+, A has the higher fractile (za >= zb):
# for X < zb nobody stocks out; for zb <= X < za, D_A = a_A X + theta (a_B X - a_B zb) and reaches y_A at X = za.
LA = (sp.integrate(ya - aa * x, (x, mu - sg, zb)) + sp.integrate(ya - aa * x - th * ab * (x - zb), (x, zb, za))) / (2 * sg)
LB = sp.integrate(yb - ab * x, (x, mu - sg, zb)) / (2 * sg)
pi0a = (pa - ca) * ya - pa * LA
pi0b = (pb - cb) * yb - pb * LB
d_a = sp.simplify(sp.together(cf.pfta_t2_case1(pa, pb, th, ca, cb, be, mu, sg) - pi0a))
d_b = sp.simplify(sp.together(cf.pftb_t2_case1(pa, pb, cb, be, mu, sg) - pi0b))
print("1. pftaT2Case1 - pi0_A simplifies to:", d_a)
print("   pftbT2Case1 - pi0_B simplifies to:", d_b)

# ---------------------------------------------------------------- 2. mirror identities for the B-high branches
rng = random.Random(2026)
NAMES = ("pa1", "pb1", "pa2", "pb2", "theta", "ca", "cb", "beta", "mu", "sigma", "gamma")


def rpt():
    return {n: sp.Rational(rng.randint(1, 10**5), rng.randint(1, 10**3)) for n in NAMES}


def swapped(p):
    q = dict(p)
    q["pa1"], q["pb1"], q["pa2"], q["pb2"] = p["pb1"], p["pa1"], p["pb2"], p["pa2"]
    q["ca"], q["cb"] = p["cb"], p["ca"]
    return q


def args(p):
    return tuple(p[n] for n in NAMES)


bad = 0
n_pts = 40
for _ in range(n_pts):
    p = rpt()
    q = swapped(p)
    for fp in (cf.first_period_s, cf.first_period_n):
        lo = fp(*args(p), branch=False)     # B has the higher fractile
        hi = fp(*args(q), branch=True)      # same game with the names swapped
        # outputs: ya1, yb1, lefta1, leftb1, za, zb
        if not (lo[0] == hi[1] and lo[1] == hi[0] and lo[2] == hi[3] and lo[3] == hi[2] and lo[4] == hi[5] and lo[5] == hi[4]):
            bad += 1
    for scen, (fa, fb) in (("S", (cf.spfta_t1, cf.spftb_t1)), ("N", (cf.npfta_t1, cf.npftb_t1))):
        if not (fa(*args(p), branch=False, branch2=False) == fb(*args(q), branch=True, branch2=True)
                and fb(*args(p), branch=False, branch2=False) == fa(*args(q), branch=True, branch2=True)):
            bad += 1
    ba, bb = cf.period2_base_profits(p["pa2"], p["pb2"], p["theta"], p["ca"], p["cb"], p["beta"], p["mu"], p["sigma"], branch=False)
    qa, qb = cf.period2_base_profits(q["pa2"], q["pb2"], q["theta"], q["ca"], q["cb"], q["beta"], q["mu"], q["sigma"], branch=True)
    if not (ba == qb and bb == qa):
        bad += 1
print(f"2. mirror identities (B-high branch = A-high branch with A and B swapped): {n_pts} exact rational points, failures = {bad}")

# ---------------------------------------------------------------- 3. share formula, bit identity
r = np.random.default_rng(7)
b = r.uniform(0, 0.5, 200000)
d = r.uniform(-10, 10, 200000)
port = (1 + 2 * b * d) / 2
matlab = 0.5 + b * d
print("3. share: (1+2bd)/2 vs 1/2+bd, doubles differing:", int(np.sum(port != matlab)), "of", b.size)

# ---------------------------------------------------------------- 4. grids
print("4. FIG1_THETA:", [repr(float(t)) for t in F.FIG1_THETA])
print("   FIGB1_THETA:", [repr(float(t)) for t in F.FIGB1_THETA])

# ---------------------------------------------------------------- 5. Figure B.1 against the authors' MATLAB values
ref = pd.read_csv("numerics/matlab/Figure2_MATLAB/Figure2_reference.csv")
mine = F.figureB1_data()
lines = open("numerics/matlab/Figure2_MATLAB/Figure2_reference.csv").read().strip().split("\n")[1:]
same = sum(f"{mine[c][i]:.15g}" == cell for i, line in enumerate(lines) for c, cell in zip(ref.columns[1:], line.split(",")[1:]))
print("5. Figure2_reference.csv: columns equal:", list(ref.columns) == list(mine.columns),
      "| max abs diff:", float((mine - ref).abs().to_numpy().max()),
      "| equal at 15 significant digits:", same, "of", ref.shape[0] * (ref.shape[1] - 1))
stored_b1 = pd.read_csv("numerics/figures/reproduced/figureB1.csv")
print("   reproduced/figureB1.csv vs fresh: max abs diff", float((stored_b1 - mine).abs().to_numpy().max()))
fresh1 = F.figure1_data()
stored1 = pd.read_csv("numerics/figures/reproduced/figure1.csv")
num = [c for c in fresh1.columns if c not in ("panel", "retailer")]
print("   reproduced/figure1.csv vs fresh: same shape", stored1.shape == fresh1.shape,
      "| max abs diff", float((stored1[num] - fresh1[num]).abs().to_numpy().max()))
