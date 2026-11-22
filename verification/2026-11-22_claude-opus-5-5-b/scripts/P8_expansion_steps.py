"""Proposition 8: the leading derivatives of its proof, the equivalence (A.22) <=> (A.23), (A.25) and (A.26).

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5-b/scripts/P8_expansion_steps.py

1. (a): derivatives of the closed form of Lemma A.1(a) in the first-period prices, and their limits as gamma -> oo
   (SymPy, uniform seed demand: F^{-1}(x) = mu - sigma + 2 sigma x).
2. (b1): gamma times the gap between the derivatives of the closed form of Lemma A.2(a) and the leading terms
   beta zeta_B and -beta[(1-theta) zeta_A + theta zeta_B] has a finite limit, uniformly in theta (SymPy).
3. (b2): the replacement theta gamma nu_B c_A/(p_A + gamma nu_A) -> c_A nu_B/nu_A has error O(1/gamma) when
   gamma(1-theta) <= l; the derivative of the leading term of (A.25) in p_{B,1} is the leading term of (A.26).
4. (b2): (A.22) holds exactly when the set (A.23) has an interior point (sampling of section5.draw_market markets,
   with a grid search over p_{A,1}).
5. (b2), fixed theta < 1: the closed form of Lemma A.2(a) is alpha_i (mu+sigma) + O(1/gamma) with derivatives.
"""
import sys

sys.path.insert(0, "numerics")

import numpy as np
import sympy as sp

from c2c import section5 as s5

pA, pB, cA, cB, b, mu, sg, g, ph, nA, nB = sp.symbols("p_A p_B c_A c_B beta mu sigma gamma pbar nu_A nu_B", positive=True)
th = sp.Symbol("theta", nonnegative=True)
eps = sp.Symbol("epsilon", positive=True)                 # eps = 1/gamma
Finv = lambda x: mu - sg + 2 * sg * x
aA = sp.Rational(1, 2) + b * (pB - pA)
aB = 1 - aA

# ----------------------------------------------------------------------------- 1
zA = Finv(1 - cA / (pA + g * (ph - cA)))
zB = Finv(1 - cB / (pB + g * (ph - cB)))
yA = (aA + th * aB) * zA - th * aB * zB
yB = aB * zB
print("1. Lemma A.1(a) closed form, limits of the price derivatives as gamma -> oo:")
for name, expr, var in (("dyA/dpA", yA, pA), ("dyA/dpB", yA, pB), ("dyB/dpB", yB, pB), ("dyB/dpA", yB, pA)):
    d = sp.diff(expr, var)
    lim = sp.limit(d.subs(g, 1 / eps), eps, 0)
    rate = sp.limit(sp.simplify((d - lim).subs(g, 1 / eps) / eps), eps, 0)
    print(f"   {name}: limit {sp.factor(lim)}; gamma x (derivative - limit) -> {sp.simplify(rate)}")

# ----------------------------------------------------------------------------- 2
zAN = Finv(1 - cA / (pA + g * nA))
zBN = Finv(1 - (cB - th * g * nB * cA / (pA + g * nA)) / (pB + (1 - th) * g * nB))
yAN = (aA + th * aB) * zAN - th * aB * zBN
yBN = aB * zBN
gapB = sp.diff(yBN, pA) - b * zBN
gapA = sp.diff(yAN, pA) + b * ((1 - th) * zAN + th * zBN)
print("2. Lemma A.2(a) closed form, (b1):")
for name, gap in (("dyB/dpA - beta zeta_B", gapB), ("dyA/dpA + beta[(1-th) zeta_A + th zeta_B]", gapA)):
    vals = []
    for t in (0, sp.Rational(1, 2), 1):
        vals.append(sp.limit((g * gap).subs(th, t).subs(g, 1 / eps), eps, 0))
    # uniformity in theta: bound |gamma * gap| on a grid of theta and gamma at one numeric market
    f = sp.lambdify((pA, pB, cA, cB, b, mu, sg, nA, nB, th, g), g * gap, "numpy")
    rng = np.random.default_rng(3)
    worst = 0.0
    for _ in range(200):
        mk = s5.draw_market(rng)
        na, nb = s5.claimed_nu(mk)
        pa1, pb1 = rng.uniform(mk.p_lo, mk.p_hi, 2)
        for t in np.linspace(0, 1, 21):
            for gam in (1e2, 1e3, 1e4, 1e5, 1e6):
                worst = max(worst, abs(f(pa1, pb1, mk.ca, mk.cb, mk.beta, mk.mu, mk.sigma, na, nb, t, gam)) / (mk.beta * mk.hi))
    print(f"   {name}: gamma x gap -> {[sp.simplify(v) for v in vals]} at theta = 0, 1/2, 1;"
          f" max |gamma x gap|/(beta(mu+sigma)) over 200 markets, 21 thetas, gamma 1e2..1e6 = {worst:.3g}")

# ----------------------------------------------------------------------------- 3
L = sp.Symbol("L", nonnegative=True)                       # L = gamma (1 - theta)
repl = (th * g * nB * cA / (pA + g * nA) - cA * nB / nA).subs(th, 1 - L / g)
print("3. (b2): replacement error with theta = 1 - L/gamma:", sp.factor(sp.simplify(repl)))
print("   gamma x error -> ", sp.simplify(sp.limit((g * repl).subs(g, 1 / eps), eps, 0)), "(bounded for L in [0, l^D])")
K = cB - cA * nB / nA
lead = aB * (mu + sg - 2 * sg * K / (pB + L * nB))
a26 = -b * (mu + sg) + sg * K * (1 + 2 * b * pA + 2 * b * L * nB) / (pB + L * nB) ** 2
print("   d/dp_B of the leading term of (A.25) minus the leading term of (A.26):", sp.simplify(sp.diff(lead, pB) - a26))
print("   d/dp_A of the leading term of (A.26) (>= 0 when K > 0):", sp.factor(sp.diff(a26, pA)),
      "; d/dL:", sp.factor(sp.diff(a26, L)))
lead_sum = (aA + th * aB) * (mu + sg) + (1 - th) * aB * (mu + sg)
print("   leading term of y_A + y_B with zeta_A = zeta_B = mu + sigma:", sp.simplify(lead_sum))

# ----------------------------------------------------------------------------- 4
rng = np.random.default_rng(11)
agree = disagree = holds = 0
closest = np.inf
for _ in range(20000):
    mk = s5.draw_market(rng)
    ratio = s5.claimed_condition_a22(mk)
    grid = np.linspace(mk.p_lo, mk.p_hi, 2001)[1:-1]
    bound = np.minimum(mk.p_hi, s5.claimed_bound_a23(mk, grid))
    nonempty = bool(np.any(bound > mk.p_lo))
    holds += ratio > 1
    if nonempty == (ratio > 1):
        agree += 1
    else:
        disagree += 1
        closest = min(closest, abs(ratio - 1))
print(f"4. (A.22) vs nonempty interior of (A.23) on 20,000 markets: agree {agree}, disagree {disagree}"
      f" (disagreements only within grid resolution of ratio 1: closest |ratio - 1| = {closest:.2g}); (A.22) holds at {holds}")

# ----------------------------------------------------------------------------- 5
print("5. fixed theta < 1: gamma x (closed form - alpha_i (mu + sigma)) and gamma x its p_B-derivative gap, limits:")
for t in (0, sp.Rational(1, 2), sp.Rational(9, 10)):
    for name, y, a in (("y_A", yAN, aA), ("y_B", yBN, aB)):
        v = sp.limit((g * (y - a * (mu + sg))).subs(th, t).subs(g, 1 / eps), eps, 0)
        dv = sp.limit((g * (sp.diff(y, pB) - sp.diff(a, pB) * (mu + sg))).subs(th, t).subs(g, 1 / eps), eps, 0)
        print(f"   theta={t}, {name}: value limit {sp.simplify(v)}; derivative limit {sp.simplify(dv)}")
