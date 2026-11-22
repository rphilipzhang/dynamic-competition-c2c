"""Checks of individual steps of the joint proof of Lemmas A.1 and A.2 (Online Appendix A.2).

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5-b/scripts/LA1_joint_proof_steps.py

Sections (each prints the numbers quoted in proofs/LA1.yaml):
  A  notation: nu_A > nu_B > 0, c_A/nu_A < c_B/nu_B, c_A/p^_A < c_B/p^_B, interiority of the limit prices (SymPy + sampling)
  B  the domination constant delta: every first-period seed-demand share is at least 2 delta
  C  Scenario S critical-ratio ordering for gamma above the stated threshold, and tightness of the threshold
  D  the min-formula for total first-period sales R_1
  E  pi^0_i is C^1 across the fractile switch c_A/p_A = c_B/p_B (its second derivative jumps)
  F  SymPy: the change of variables that gives (A.21), its linear part, q^0, t^0, and the residual formulas
  G  the paper's two first-order conditions (display before (A.21)) against the model's marginal profits
  H  E R_1 = mu - (1-theta) alpha_B sigma t^2 - (alpha_A + theta alpha_B) sigma q^2 in the region s < z
Uses numerics/c2c (primitives and the model part of section5) only; no claimed_* result is assumed
except where a claimed order pair is used as a convenient evaluation point.
"""
import sys

sys.path.insert(0, "numerics")

import numpy as np
import sympy as sp

from c2c import primitives as pm
from c2c import section5 as s5


def admissible_market(rng, edge=True):
    """A market satisfying A1, A10, A12, A13, sampled more widely than section5.draw_market and pushed
    towards the edges of the admissible region when edge is True."""
    while True:
        cb = rng.uniform(0.1, 5.0)
        ca = cb * rng.uniform(0.001, 0.999)
        mu = rng.uniform(1.0, 20.0)
        sigma = mu * rng.uniform(0.001, 0.999)
        beta = 10 ** rng.uniform(-2.3, 0.3)
        theta = rng.choice([0.0, 1.0, rng.uniform()]) if edge else rng.uniform()
        x = 1 / (2 * beta)
        w = (mu + sigma) * (ca + 2 * cb) / (3 * mu)
        p_hi = x + w * (1 + (10 ** rng.uniform(-6, 0.3) if edge else rng.uniform(0.01, 1)))
        lo_min, lo_max = max(cb, p_hi - x), min(x + (2 * ca + cb) / 3, p_hi)
        if lo_min < lo_max:
            u = rng.uniform()
            if edge:
                u = rng.choice([u ** 6, 1 - u ** 6, u])
            p_lo = lo_min + (lo_max - lo_min) * min(max(u, 1e-9), 1 - 1e-9)
            return s5.Market(ca, cb, beta, float(theta), mu, sigma, p_lo, p_hi)


rng = np.random.default_rng(20261122)

# ----------------------------------------------------------------------------- A
print("A. notation of Online Appendix A.2")
b, ca, cb = sp.symbols("beta c_A c_B", positive=True)
pa_hat = 1 / (2 * b) + (2 * ca + cb) / 3
pb_hat = 1 / (2 * b) + (2 * cb + ca) / 3
share_a = sp.Rational(1, 2) + b * (pb_hat - pa_hat)
nu_a = share_a * (pa_hat - ca)
nu_b = (1 - share_a) * (pb_hat - cb)
d = cb - ca
print("  nu_A - beta (1/(2beta) + Delta/3)^2 =", sp.simplify(nu_a - b * (1 / (2 * b) + d / 3) ** 2))
print("  nu_B - beta (1/(2beta) - Delta/3)^2 =", sp.simplify(nu_b - b * (1 / (2 * b) - d / 3) ** 2))
print("  nu_A - nu_B =", sp.factor(sp.simplify(nu_a - nu_b)))
print("  c_A p^_B - c_B p^_A =", sp.factor(sp.simplify(ca * pb_hat - cb * pa_hat)))
p1a = 1 / (2 * b) + sp.Symbol("k") * (2 * ca + cb) / 3   # k = (mu+sigma)/mu
print("  p^_{A,1} - p^_{A,2} with k=(mu+sigma)/mu:", sp.factor(sp.simplify(p1a - pa_hat)))
worst = {"nu_B": np.inf, "lim_lo": np.inf, "lim_hi": np.inf, "ratio": np.inf, "lim1_hi": np.inf}
for _ in range(50000):
    mk = admissible_market(rng)
    la, lb = s5.claimed_limit_prices(mk)
    na, nb = s5.claimed_nu(mk)
    l1a, l1b = s5.proof_first_period_limit_prices(mk)
    assert na > nb > 0 and mk.ca / na < mk.cb / nb and mk.ca / la < mk.cb / lb
    worst["nu_B"] = min(worst["nu_B"], nb / na)
    worst["lim_lo"] = min(worst["lim_lo"], (la - mk.p_lo) / mk.p_hi)
    worst["lim_hi"] = min(worst["lim_hi"], (mk.p_hi - lb) / mk.p_hi)
    worst["lim1_hi"] = min(worst["lim1_hi"], (mk.p_hi - l1b) / mk.p_hi)
    worst["ratio"] = min(worst["ratio"], (mk.cb / nb - mk.ca / na) / (mk.cb / nb))
    assert mk.p_lo < la < l1a and la < lb < l1b < mk.p_hi
print("  50,000 edge-sampled admissible markets: nu_A > nu_B > 0, c_A/nu_A < c_B/nu_B, c_A/p^_A < c_B/p^_B,")
print("  p_lo < p^_{A,2} < p^_{A,1}, p^_{A,2} < p^_{B,2} < p^_{B,1} < p_hi at all of them.")
print("  smallest nu_B/nu_A = %.3g, smallest (p^_{A,2}-p_lo)/p_hi = %.3g, smallest (p_hi-p^_{B,1})/p_hi = %.3g"
      % (worst["nu_B"], worst["lim_lo"], worst["lim1_hi"]))

# ----------------------------------------------------------------------------- B
print("\nB. the domination constant delta = [1/2 - beta (p_hi - p_lo)](mu - sigma)/2")
smallest = np.inf
for _ in range(20000):
    mk = admissible_market(rng)
    pa1, pb1 = rng.uniform(mk.p_lo, mk.p_hi, size=2)
    delta = mk.smallest_share * mk.lo / 2
    sa = pm.share(pa1, pb1, mk.beta)
    smallest = min(smallest, min(sa, 1 - sa) * mk.lo / (2 * delta))
    assert delta > 0
print("  min over 20,000 points of alpha_{i,1}(mu - sigma) / (2 delta) = %.6f (>= 1: every unit up to 2 delta sells)" % smallest)

# ----------------------------------------------------------------------------- C
print("\nC. Scenario S ordering zeta^S_A >= zeta^S_B above gamma_0 = (c_A p_hi - c_B p_lo)/(p_hi (c_B - c_A))")
viol_above, tight, positive = 0, 0, 0
for _ in range(5000):
    mk = admissible_market(rng)
    g0 = max(0.0, (mk.ca * mk.p_hi - mk.cb * mk.p_lo) / (mk.p_hi * (mk.cb - mk.ca)))
    grid = np.linspace(mk.p_lo, mk.p_hi, 21)
    pa, pb = np.meshgrid(grid, grid, indexing="ij")
    for g in (g0 * (1 + 1e-9) + 1e-12, 10 * g0 + 1.0):
        ra = mk.ca / (pa + g * (mk.p_hi - mk.ca))
        rb = mk.cb / (pb + g * (mk.p_hi - mk.cb))
        viol_above += int(np.sum(ra > rb * (1 + 1e-12)))
    if g0 > 0:
        positive += 1
        g = 0.99 * g0                                     # just below the threshold, at the worst corner (p_lo, p_hi)
        tight += int(mk.ca / (mk.p_lo + g * (mk.p_hi - mk.ca)) > mk.cb / (mk.p_hi + g * (mk.p_hi - mk.cb)))
print("  5,000 markets, 21x21 price grid: violations of zeta_A >= zeta_B at gamma >= gamma_0:", viol_above)
print("  markets with gamma_0 > 0: %d; of these, ordering fails at the corner (p_lo, p_hi) at 0.99 gamma_0: %d" % (positive, tight))

# ----------------------------------------------------------------------------- D
print("\nD. R_1 = min{X, y_A + y_B, (a_A + th a_B) X + (1-th) y_B, (a_B + th a_A) X + (1-th) y_A}")
x = rng.uniform(0, 30, 400000)
ya, yb = rng.uniform(0, 30, (2, x.size))
aa = rng.uniform(0.01, 0.99, x.size)
th = rng.choice([0.0, 1.0, 0.5], x.size) * rng.uniform(0.5, 1, x.size)
ra, rb = pm.sales(x, ya, yb, aa, 1 - aa, th)
formula = np.minimum.reduce([x, ya + yb, (aa + th * (1 - aa)) * x + (1 - th) * yb, (1 - aa + th * aa) * x + (1 - th) * ya])
print("  400,000 random points: max |R_A + R_B - formula| = %.3g" % np.max(np.abs(ra + rb - formula)))

# ----------------------------------------------------------------------------- E
print("\nE. pi^0_i(p_A, p_B) is C^1 across the switch c_A/p_A = c_B/p_B, with a jump in the second derivative")


def one_sided(f, x0, h, side):
    """Second-order one-sided first and second differences of f at x0."""
    s = 1.0 if side > 0 else -1.0
    f0, f1, f2, f3 = (f(x0 + s * k * h) for k in range(4))
    first = s * (-3 * f0 + 4 * f1 - f2) / (2 * h)
    second = (2 * f0 - 5 * f1 + 4 * f2 - f3) / h ** 2
    return first, second


jump1, jump2, scale1, scale2, found = 0.0, 0.0, 0.0, 0.0, 0
while found < 40:
    mk = admissible_market(rng, edge=False)
    pb = rng.uniform(mk.p_lo, mk.p_hi)
    ps = mk.ca / mk.cb * pb                               # switch point in p_A for this p_B
    if not (mk.p_lo + 0.01 < ps < mk.p_hi - 0.01):
        continue
    found += 1
    h = 1e-4 * ps
    for who in (0, 1):
        f_own = (lambda p, w=who: float(s5.benchmark_profits(mk, p, pb)[w]))      # derivative in p_A
        (dl, sl), (dr, sr) = one_sided(f_own, ps, h, -1), one_sided(f_own, ps, h, +1)
        jump1, scale1 = max(jump1, abs(dl - dr)), max(scale1, abs(dl))
        jump2, scale2 = max(jump2, abs(sl - sr)), max(scale2, abs(sl))
    pa = ps                                                # the same switch, crossed in p_B
    qs = mk.cb / mk.ca * pa
    for who in (0, 1):
        f_cross = (lambda p, w=who: float(s5.benchmark_profits(mk, pa, p)[w]))
        (dl, sl), (dr, sr) = one_sided(f_cross, qs, 1e-4 * qs, -1), one_sided(f_cross, qs, 1e-4 * qs, +1)
        jump1, scale1 = max(jump1, abs(dl - dr)), max(scale1, abs(dl))
        jump2, scale2 = max(jump2, abs(sl - sr)), max(scale2, abs(sl))
print("  40 switch points, both retailers, both price directions:")
print("  max |left - right first derivative| = %.2e (largest |first derivative| %.2f)" % (jump1, scale1))
print("  max |left - right second derivative| = %.2e (largest |second derivative| %.2f)" % (jump2, scale2))

# ----------------------------------------------------------------------------- F
print("\nF. SymPy: change of variables leading to (A.21)")
aA, th, s, z, x_, lam, sg, g, nB, nA, pA, pB, cA, cB = sp.symbols(
    "alpha_A theta s z x lambda sigma gamma nu_B nu_A p_A p_B c_A c_B", real=True)
aB = 1 - aA
Q = (aA + th * aB) * z + (1 - th) * aB * s
R1 = (aA + th * aB) * x_ + (1 - th) * aB * s               # y_B = alpha_B s; total sales for s < X < z
print("  R_1(s) - s =", sp.simplify(R1.subs(x_, s) - s), "; R_1(z) - Q =", sp.simplify(R1.subs(x_, z) - Q))
a0, a1, a2 = sp.symbols("a0 a1 a2")
eprime = lambda r: a0 + a1 * r + a2 * r ** 2              # a polynomial stand-in for e_B'
lhs = (1 - th) / (2 * sg) * sp.integrate(g * nB + eprime(R1), (x_, s, z))
q_, t_ = sp.symbols("q t", positive=True)
mu_ = sp.Symbol("mu")
subs = {z: mu_ + sg - 2 * sg * q_, s: mu_ + sg - 2 * sg * t_}
rhs = (1 - th) * g * nB * (t_ - q_) + (1 - th) * (t_ - q_) * sp.integrate(eprime(s + lam * (Q - s)), (lam, 0, 1))
print("  integral term minus [(1-th) g nu_B (t-q) + (1-th)(t-q) int_0^1 e'(s+lam(Q-s)) dlam] =",
      sp.simplify(sp.expand((lhs - rhs).subs(subs))))
eQ = sp.Symbol("ePrimeB_Q")
focB = pB * t_ + lhs.subs(subs) + (g * nB + eQ) * q_ - cB
r_term = rhs.subs(subs) - (1 - th) * g * nB * (t_ - q_) + q_ * eQ
print("  B's FOC minus [theta g nu_B q + (p_B + g(1-th) nu_B) t + r - c_B] =",
      sp.simplify(sp.expand(focB - (th * g * nB * q_ + (pB + g * (1 - th) * nB) * t_ + r_term - cB))))
u, v = sp.symbols("u v")
lin = sp.Matrix([(pA + g * nA) * u / g, th * g * nB * u / g + (pB + g * (1 - th) * nB) * v / (1 + g * (1 - th))])
J = lin.jacobian([u, v])
print("  Jacobian of the linear part in (u, v):", [sp.simplify(e) for e in J])
sol = sp.solve([sp.Eq(cA, (pA + g * nA) * q_), sp.Eq(cB, th * g * nB * q_ + (pB + g * (1 - th) * nB) * t_)], [q_, t_])
print("  q^0 =", sp.simplify(sol[q_]), "; t^0 - stated =",
      sp.simplify(sol[t_] - (cB - th * g * nB * cA / (pA + g * nA)) / (pB + g * (1 - th) * nB)))
dd = sp.Symbol("d", positive=True)
print("  (p_B + G nu_B)/(1 + G) - min(p_B, nu_B) >= 0: weighted average; d/dG =",
      sp.simplify(sp.diff((pB + dd * nB) / (1 + dd), dd)))

# ----------------------------------------------------------------------------- G
print("\nG. the paper's first-order conditions (display before (A.21)) against the model's marginal profits")
gl_x, gl_w = np.polynomial.legendre.leggauss(40)
worst_a = worst_b = 0.0
pairs = 0
for _ in range(6):
    mk = admissible_market(rng, edge=False)
    for gamma in (50.0, 500.0):
        pa1, pb1 = rng.uniform(mk.p_lo, mk.p_hi, size=2)
        sa = pm.share(pa1, pb1, mk.beta)
        base = s5.claimed_orders_n(mk, gamma, pa1, pb1)
        cont = s5.SecondPeriodN(mk, 1.01 / (gamma * min(sa, 1 - sa) * mk.lo * 0.9))
        assert not cont.problems
        for scale in (0.97, 1.0, 1.02):
            ya, yb = float(base[0]) * scale, float(base[1]) * (2 - scale)
            ss, zz = yb / (1 - sa), (ya + mk.theta * yb) / (sa + mk.theta * (1 - sa))
            if not (mk.lo < ss < zz < mk.hi and ya / sa > yb / (1 - sa)):
                continue
            pairs += 1
            Qv = ya + yb
            slope = lambda r: cont.slopes(gamma, np.asarray(r, float), 0.0)
            vA_Q, vB_Q = float(slope(Qv)[0][0]), float(slope(Qv)[1][0])
            xs = 0.5 * (zz - ss) * gl_x + 0.5 * (zz + ss)
            integral = 0.5 * (zz - ss) * np.sum(gl_w * slope((sa + mk.theta * (1 - sa)) * xs + (1 - mk.theta) * yb)[1][0])
            paper_a = (pa1 + vA_Q) * (mk.hi - zz) / (2 * mk.sigma) - mk.ca
            paper_b = (pb1 * (mk.hi - ss) / (2 * mk.sigma) + (1 - mk.theta) / (2 * mk.sigma) * integral
                       + vB_Q * (mk.hi - zz) / (2 * mk.sigma) - mk.cb)
            fa, fb = s5.marginal_profits(mk, cont, gamma, pa1, pb1, ya, yb)
            worst_a = max(worst_a, abs(paper_a - float(fa)) / (mk.p_hi * (1 + gamma)))
            worst_b = max(worst_b, abs(paper_b - float(fb)) / (mk.p_hi * (1 + gamma)))
print("  %d order pairs with mu - sigma < s < z < mu + sigma: max relative difference A %.2e, B %.2e" % (pairs, worst_a, worst_b))

# ----------------------------------------------------------------------------- H
print("\nH. E R_1 in the region mu - sigma < s < z < mu + sigma")
worst, n = 0.0, 0
while n < 5000:
    mk = admissible_market(rng, edge=False)
    sa = rng.uniform(0.05, 0.95)
    ss, zz = np.sort(rng.uniform(mk.lo, mk.hi, 2))
    yb = (1 - sa) * ss
    ya = (sa + mk.theta * (1 - sa)) * zz - mk.theta * yb
    if ya / sa <= yb / (1 - sa):
        continue
    n += 1
    era, erb = mk.dist.expected_sales(ya, yb, sa, 1 - sa, mk.theta)
    q, t = (mk.hi - zz) / (2 * mk.sigma), (mk.hi - ss) / (2 * mk.sigma)
    formula = mk.mu - (1 - mk.theta) * (1 - sa) * mk.sigma * t ** 2 - (sa + mk.theta * (1 - sa)) * mk.sigma * q ** 2
    worst = max(worst, abs(era[0] + erb[0] - formula) / mk.hi)
print("  5,000 random points: max |E R_1 - formula| / (mu + sigma) = %.2e" % worst)
