"""Proposition 9: the steps of its proof that can be checked in closed form.

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5-b/scripts/P9_price_path_steps.py

1. Scenario S. With the orders of Lemma A.1(a) (zeta_A >= zeta_B), expected first-period sales are
   E R_A = (a_A + th a_B) m(zeta_A) - th a_B m(zeta_B), E R_B = a_B m(zeta_B), m(z) = E min(X, z).
   The script checks these against the model (primitives.Uniform.expected_sales), forms
   Pi_i^S = [p_i + gamma(pbar - c_i)] E R_i - c_i y_i + const, differentiates in the own price (SymPy),
   and shows that gamma^-1 dPi_i/dp_i -> -(pbar - c_i) beta mu and that dPi_i/dp_i + gamma(pbar - c_i) beta mu
   stays bounded on the price box and in theta as gamma grows.
2. Scenario N. The own-price derivative of alpha_{i,1}(mu p_{i,1} - c_i(mu+sigma)), the unique equilibrium
   of the limit game, its Jacobian, the Lipschitz constant of the best replies, and p^_{i,1} - p^_{i,2}.
"""
import sys

sys.path.insert(0, "numerics")

import numpy as np
import sympy as sp

from c2c import primitives as pm
from c2c import section5 as s5

pA, pB, cA, cB, b, mu, sg, g, ph = sp.symbols("p_A p_B c_A c_B beta mu sigma gamma pbar", positive=True)
th = sp.Symbol("theta", nonnegative=True)
aA = sp.Rational(1, 2) + b * (pB - pA)
aB = 1 - aA
Finv = lambda x: mu - sg + 2 * sg * x
m = lambda z: mu - (mu + sg - z) ** 2 / (4 * sg)          # E min(X, z) for X ~ U[mu - sigma, mu + sigma], z in the support
PA, PB = pA + g * (ph - cA), pB + g * (ph - cB)
zA, zB = Finv(1 - cA / PA), Finv(1 - cB / PB)
yA = (aA + th * aB) * zA - th * aB * zB
yB = aB * zB
ERA = (aA + th * aB) * m(zA) - th * aB * m(zB)
ERB = aB * m(zB)

# ----------------------------------------------------------------------------- 1a: closed-form sales against the model
f_sales = sp.lambdify((pA, pB, cA, cB, b, mu, sg, g, ph, th), (yA, yB, ERA, ERB), "numpy")
rng = np.random.default_rng(9)
worst = 0.0
for _ in range(3000):
    mk = s5.draw_market(rng)
    gam = 10 ** rng.uniform(0, 6)
    pa1, pb1 = rng.uniform(mk.p_lo, mk.p_hi, 2)
    za_n = float(Finv(1 - cA / PA).subs({cA: mk.ca, pA: pa1, g: gam, ph: mk.p_hi, mu: mk.mu, sg: mk.sigma}))
    zb_n = float(Finv(1 - cB / PB).subs({cB: mk.cb, pB: pb1, g: gam, ph: mk.p_hi, mu: mk.mu, sg: mk.sigma}))
    if za_n < zb_n:                                          # below the ordering threshold of the joint proof
        continue
    ya, yb, era, erb = f_sales(pa1, pb1, mk.ca, mk.cb, mk.beta, mk.mu, mk.sigma, gam, mk.p_hi, mk.theta)
    sa = pm.share(pa1, pb1, mk.beta)
    model = mk.dist.expected_sales(ya, yb, sa, 1 - sa, mk.theta)
    worst = max(worst, abs(model[0][0] - era) / mk.hi, abs(model[1][0] - erb) / mk.hi)
print("1a. closed-form expected sales at the orders of Lemma A.1(a) vs the model, 3,000 points: max error/(mu+sigma) = %.2e" % worst)

# ----------------------------------------------------------------------------- 1b: own-price derivative of Pi^S
PiA = PA * ERA - cA * yA
PiB = PB * ERB - cB * yB
dA, dB = sp.diff(PiA, pA), sp.diff(PiB, pB)
eps = sp.Symbol("epsilon", positive=True)
for name, d, c in (("A", dA, cA), ("B", dB, cB)):
    lead = sp.limit((d / g).subs(g, 1 / eps), eps, 0)
    print(f"1b. retailer {name}: lim gamma^-1 dPi/dp_own = {sp.factor(lead)}")
fd = {k: sp.lambdify((pA, pB, cA, cB, b, mu, sg, g, ph, th), v + g * (ph - c) * b * mu, "numpy")
      for k, v, c in (("A", dA, cA), ("B", dB, cB))}
rng = np.random.default_rng(10)
markets = [s5.draw_market(rng) for _ in range(300)]
print("    sup over 300 markets x 11x11 price grid x theta in {0, 0.5, 1} of |dPi_i/dp_i + gamma(pbar - c_i) beta mu| / (pbar (mu+sigma)):")
for gam in (1e2, 1e3, 1e4, 1e5, 1e6):
    sup = 0.0
    for mk in markets:
        grid = np.linspace(mk.p_lo, mk.p_hi, 11)
        pa1, pb1 = np.meshgrid(grid, grid, indexing="ij")
        for t in (0.0, 0.5, 1.0):
            for k in ("A", "B"):
                v = fd[k](pa1, pb1, mk.ca, mk.cb, mk.beta, mk.mu, mk.sigma, gam, mk.p_hi, t)
                sup = max(sup, float(np.max(np.abs(v))) / (mk.p_hi * mk.hi))
    print(f"    gamma = {gam:8.0e}: {sup:.4f}")

# ----------------------------------------------------------------------------- 2: Scenario N limit game
print("2. Scenario N, limit payoff alpha_{i,1}(mu p_i - c_i(mu+sigma)):")
payA = aA * (mu * pA - cA * (mu + sg))
payB = aB * (mu * pB - cB * (mu + sg))
printed_foc = mu * (sp.Rational(1, 2) + b * pB - 2 * b * pA) + b * cA * (mu + sg)
print("   dpay_A/dp_A minus printed:", sp.simplify(sp.diff(payA, pA) - printed_foc),
      "; second derivative:", sp.diff(payA, pA, 2), "; cross:", sp.diff(payA, pA, pB))
sol = sp.solve([sp.diff(payA, pA), sp.diff(payB, pB)], [pA, pB], dict=True)[0]
hatA1 = 1 / (2 * b) + (mu + sg) * (2 * cA + cB) / (3 * mu)
hatB1 = 1 / (2 * b) + (mu + sg) * (2 * cB + cA) / (3 * mu)
print("   equilibrium minus printed p^_{i,1}:", sp.simplify(sol[pA] - hatA1), sp.simplify(sol[pB] - hatB1))
Jm = sp.Matrix([[sp.diff(payA, pA, 2), sp.diff(payA, pA, pB)], [sp.diff(payB, pB, pA), sp.diff(payB, pB, 2)]])
print("   Jacobian of the first-order system:", Jm, "det =", sp.factor(Jm.det()))
C = sp.Symbol("C", positive=True)
lip = (b * mu + C / g) / (2 * b * mu - C / g)
print("   Lipschitz constant < 1 iff C/gamma < beta mu/2:", sp.solve(sp.Eq(lip, 1), C))
hatA2 = 1 / (2 * b) + (2 * cA + cB) / 3
print("   p^_{A,1} - p^_{A,2} =", sp.factor(sp.simplify(hatA1 - hatA2)))
