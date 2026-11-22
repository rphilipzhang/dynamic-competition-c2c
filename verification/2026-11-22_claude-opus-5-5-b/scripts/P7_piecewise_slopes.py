"""Proposition 7: the derivative formulas of the proof, the kinks, and the two bounds at the upper price.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5-b/scripts/P7_piecewise_slopes.py

1. SymPy: the own- and cross-price derivatives of the benchmark order ybar_{A,2} on both pieces, as printed
   in the proof, and the mirror formulas for retailer B; monotonicity of each derivative on its piece; the
   jump of the derivative at the switch, which equals 2 theta sigma c_j^2 alpha_B / (c_i p_j^2) >= 0 in both directions
   (alpha_B > 0 on the box by A12), so both kinks are convex.
2. The bounds at the upper price p_hi: own-price derivative <= -beta(mu^2 - mu sigma + sigma^2)/(mu+sigma) and
   rival-price derivative >= +beta(mu^2 - mu sigma + sigma^2)/(mu+sigma), for both retailers, on whichever piece
   contains p_hi, for every rival price in [p_lo, p_hi] and theta in {0, 1} (each derivative is affine in theta).
   200,000 admissible markets (A1, A10, A12, A13) pushed towards the edges of the region are searched;
   the largest value of derivative/bound on the wrong side is printed (it must stay below 1 for own prices).
"""
import sys

sys.path.insert(0, "numerics")

import numpy as np
import sympy as sp

# ----------------------------------------------------------------------------- 1. symbolic
pA, pB, cA, cB, b, mu, sg, th = sp.symbols("p_A p_B c_A c_B beta mu sigma theta", positive=True)
aA = sp.Rational(1, 2) + b * (pB - pA)
aB = 1 - aA
zA = mu + sg - 2 * sg * cA / pA          # F^{-1}(1 - c_A/p_A) for U[mu - sigma, mu + sigma]
zB = mu + sg - 2 * sg * cB / pB
yA_low = aA * zA                          # zeta_A <= zeta_B (p_A <= (c_A/c_B) p_B): retailer A has the lower fractile
yA_high = (aA + th * aB) * zA - th * aB * zB
yB_low = aB * zB                          # zeta_B <= zeta_A
yB_high = (aB + th * aA) * zB - th * aA * zA
printed = {
    "dyA/dpA, p_A <= (c_A/c_B) p_B": cA * sg * (2 * b * pB + 1) / pA ** 2 - b * (mu + sg),
    "dyA/dpA, p_A >  (c_A/c_B) p_B": -b * (mu + sg) + cA * sg * (1 + th + 2 * b * (1 - th) * pB) / pA ** 2 + 2 * b * cB * th * sg / pB,
    "dyA/dpB, p_B <  (c_B/c_A) p_A": b * (-2 * cA * (1 - th) * sg / pA + mu + sg) - 2 * cB * b * th * pA * sg / pB ** 2 - cB * th * sg / pB ** 2,
    "dyA/dpB, p_B >= (c_B/c_A) p_A": b * (-2 * cA * sg / pA + mu + sg),
}
computed = {
    "dyA/dpA, p_A <= (c_A/c_B) p_B": sp.diff(yA_low, pA),
    "dyA/dpA, p_A >  (c_A/c_B) p_B": sp.diff(yA_high, pA),
    "dyA/dpB, p_B <  (c_B/c_A) p_A": sp.diff(yA_high, pB),
    "dyA/dpB, p_B >= (c_B/c_A) p_A": sp.diff(yA_low, pB),
}
print("1. printed derivative formulas minus SymPy derivatives:")
for key in printed:
    print("  ", key, ":", sp.simplify(printed[key] - computed[key]))
print("   d/dp_A of the own-price slope, low piece :", sp.factor(sp.diff(computed["dyA/dpA, p_A <= (c_A/c_B) p_B"], pA)))
print("   d/dp_A of the own-price slope, high piece:", sp.factor(sp.diff(computed["dyA/dpA, p_A >  (c_A/c_B) p_B"], pA)))
print("   d/dp_B of the rival-price slope, low piece :", sp.factor(sp.diff(computed["dyA/dpB, p_B <  (c_B/c_A) p_A"], pB)))
sw = {pA: cA * pB / cB}
jump_own = sp.factor(sp.simplify((computed["dyA/dpA, p_A >  (c_A/c_B) p_B"] - computed["dyA/dpA, p_A <= (c_A/c_B) p_B"]).subs(sw)))
print("   own-price slope, right minus left at the switch:", jump_own)
sw2 = {pB: cB * pA / cA}
jump_rival = sp.factor(sp.simplify((computed["dyA/dpB, p_B >= (c_B/c_A) p_A"] - computed["dyA/dpB, p_B <  (c_B/c_A) p_A"]).subs(sw2)))
print("   rival-price slope, right minus left at the switch:", jump_rival)
print("   own jump minus 2 theta sigma c_B^2 alpha_B/(c_A p_B^2) at the switch:",
      sp.simplify(jump_own - (2 * th * sg * cB ** 2 * aB / (cA * pB ** 2)).subs(sw)))
print("   rival jump minus 2 theta sigma c_A^2 alpha_B/(c_B p_A^2) at the switch:",
      sp.simplify(jump_rival - (2 * th * sg * cA ** 2 * aB / (cB * pA ** 2)).subs(sw2)))
print("   continuity of y_A at the switch:", sp.simplify((yA_high - yA_low).subs(sw)))
# retailer B: the mirror formulas
dB_own_low, dB_own_high = sp.diff(yB_low, pB), sp.diff(yB_high, pB)
dB_riv_low, dB_riv_high = sp.diff(yB_high, pA), sp.diff(yB_low, pA)   # in p_A: low p_A gives zeta_B > zeta_A
print("   B: d/dp_B of own slope (both pieces):", sp.factor(sp.diff(dB_own_low, pB)), "|", sp.factor(sp.diff(dB_own_high, pB)))
print("   B: d/dp_A of rival slope, low piece:", sp.factor(sp.diff(dB_riv_low, pA)), "; high piece slope:", sp.simplify(dB_riv_high))

# ----------------------------------------------------------------------------- 2. the bounds at p_hi
f = {k: sp.lambdify((pA, pB, cA, cB, b, mu, sg, th), v, "numpy") for k, v in
     {"A_own_hi": computed["dyA/dpA, p_A >  (c_A/c_B) p_B"], "A_riv_lo": computed["dyA/dpB, p_B <  (c_B/c_A) p_A"],
      "A_riv_hi": computed["dyA/dpB, p_B >= (c_B/c_A) p_A"], "B_own_lo": dB_own_low, "B_own_hi": dB_own_high,
      "B_riv_hi": dB_riv_high}.items()}

rng = np.random.default_rng(77)
N = 200000
cb_ = rng.uniform(0.05, 5.0, N)
ca_ = cb_ * np.where(rng.uniform(size=N) < 0.3, rng.uniform(0.0005, 0.02, N), np.where(rng.uniform(size=N) < 0.5, rng.uniform(0.98, 0.9995, N), rng.uniform(0.0005, 0.9995, N)))
mu_ = rng.uniform(1.0, 20.0, N)
sg_ = mu_ * np.where(rng.uniform(size=N) < 0.5, rng.uniform(0.95, 0.9999, N), rng.uniform(0.0005, 0.9999, N))
b_ = 10 ** rng.uniform(-2.5, 0.5, N)
x_ = 1 / (2 * b_)
w_ = (mu_ + sg_) * (ca_ + 2 * cb_) / (3 * mu_)
phi = x_ + w_ * (1 + 10 ** rng.uniform(-7, 0.3, N))
lo_min, lo_max = np.maximum(cb_, phi - x_), np.minimum(x_ + (2 * ca_ + cb_) / 3, phi)
ok = lo_min < lo_max
u = rng.uniform(size=N)
u = np.where(rng.uniform(size=N) < 0.5, u ** 8, u)
plo = lo_min + (lo_max - lo_min) * np.clip(u, 1e-12, 1 - 1e-12)
cb_, ca_, mu_, sg_, b_, phi, plo = (v[ok] for v in (cb_, ca_, mu_, sg_, b_, phi, plo))
n = ok.sum()
bound = b_ * (mu_ ** 2 - mu_ * sg_ + sg_ ** 2) / (mu_ + sg_)
worst_own, worst_riv = -np.inf, np.inf
for frac in np.linspace(0.0, 1.0, 41):
    rival = plo + frac * (phi - plo)
    for t in (0.0, 1.0):
        # retailer A at p_A = p_hi (always on its high piece since c_A < c_B and p_B <= p_hi)
        worst_own = max(worst_own, np.max(f["A_own_hi"](phi, rival, ca_, cb_, b_, mu_, sg_, t) / bound))
        # retailer B at p_B = p_hi: low piece if p_hi <= (c_B/c_A) p_A, else high piece
        own_b = np.where(phi <= cb_ / ca_ * rival, f["B_own_lo"](rival, phi, ca_, cb_, b_, mu_, sg_, t),
                         f["B_own_hi"](rival, phi, ca_, cb_, b_, mu_, sg_, t))
        worst_own = max(worst_own, np.max(own_b / bound))
        # retailer A in the rival price at p_B = p_hi, given p_A = rival
        riv_a = np.where(phi < cb_ / ca_ * rival, f["A_riv_lo"](rival, phi, ca_, cb_, b_, mu_, sg_, t),
                         f["A_riv_hi"](rival, phi, ca_, cb_, b_, mu_, sg_, t))
        worst_riv = min(worst_riv, np.min(riv_a / bound))
        # retailer B in the rival price at p_A = p_hi (always the piece zeta_A >= zeta_B), given p_B = rival
        worst_riv = min(worst_riv, np.min(f["B_riv_hi"](phi, rival, ca_, cb_, b_, mu_, sg_, t) / bound))
print(f"\n2. {n} admissible markets, 41 rival prices, theta in {{0, 1}}:")
print(f"   own-price slope at p_hi: claim slope <= -bound. max of slope/bound + 1 = {worst_own + 1:.3e} (must be <= 0)")
print(f"   rival-price slope at p_hi: claim slope >= +bound. min of slope/bound - 1 = {worst_riv - 1:.3e} (must be >= 0)")
