"""Checks of the joint proof of Lemmas A.1 and A.2 (Online Appendix A.2).

Symbolic part (SymPy): nu_i and its ordering, the limit price games, the S-ordering
cross-multiplication, the first-order conditions and the change of variables to (A.21),
the (u, v) Jacobian, the closed forms q^0, t^0 against zeta^N, and the exact expected
total sales used for the expansion of Pi_i^N.

Numerical part (model in numerics/c2c, light): the A.2 notation claims on random markets,
the min-formula for R_1, the two first-order conditions against section5.marginal_profits
with a synthetic continuation, continuity of d pi^0_i / d p_i across the switching boundary
c_A/p_A = c_B/p_B, and the exact expected-total-sales formula against expected_sales.

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5/scripts/LA1_joint_proof_checks.py
"""
from __future__ import annotations

import sys

import numpy as np
import sympy as sp

sys.path.insert(0, "numerics")
from c2c import primitives as pm  # noqa: E402
from c2c import section5 as s5  # noqa: E402


def symbolic():
    print("== symbolic")
    b, cA, cB, mu, sg, th, g = sp.symbols("beta c_A c_B mu sigma theta gamma", positive=True)
    D = cB - cA
    phA = 1 / (2 * b) + (2 * cA + cB) / 3
    phB = 1 / (2 * b) + (2 * cB + cA) / 3
    aA = sp.Rational(1, 2) + b * (phB - phA)
    nuA, nuB = aA * (phA - cA), (1 - aA) * (phB - cB)
    print("nu_A - (1/beta)(1/2 + beta D/3)^2 =", sp.simplify(nuA - (sp.Rational(1, 2) + b * D / 3) ** 2 / b))
    print("nu_B - (1/beta)(1/2 - beta D/3)^2 =", sp.simplify(nuB - (sp.Rational(1, 2) - b * D / 3) ** 2 / b))
    print("nu_A - nu_B =", sp.factor(sp.simplify(nuA - nuB)))
    print("c_B phat_A - c_A phat_B =", sp.factor(sp.simplify(cB * phA - cA * phB)))

    # limit price games: period 2 payoffs alpha_i (p_i - c_i); period 1 payoffs alpha_i (mu p_i - c_i (mu + sigma))
    pA, pB = sp.symbols("p_A p_B")
    al = sp.Rational(1, 2) + b * (pB - pA)
    for name, ua, ub in (("period 2", al * (pA - cA), (1 - al) * (pB - cB)),
                         ("period 1", al * (mu * pA - cA * (mu + sg)), (1 - al) * (mu * pB - cB * (mu + sg)))):
        sol = sp.solve([sp.diff(ua, pA), sp.diff(ub, pB)], [pA, pB], dict=True)[0]
        jac = sp.Matrix([[sp.diff(ua, pA, 2), sp.diff(ua, pA, pB)], [sp.diff(ub, pA, pB), sp.diff(ub, pB, 2)]])
        print(f"{name} limit game: p_A =", sp.simplify(sol[pA]), "; p_B =", sp.simplify(sol[pB]), "; FOC Jacobian =", jac)
        if name == "period 2":
            print("   matches phat_{i,2}:", sp.simplify(sol[pA] - phA) == 0, sp.simplify(sol[pB] - phB) == 0)
            # second-period FOC form printed in the proof (without the pi^0 term)
            print("   d/dp_A [alpha_A (p_A - c_A)] - (1/2 + beta (p_B - 2 p_A + c_A)) =",
                  sp.simplify(sp.diff(ua, pA) - (sp.Rational(1, 2) + b * (pB - 2 * pA + cA))))
        else:
            ph1A = 1 / (2 * b) + (mu + sg) * (2 * cA + cB) / (3 * mu)
            ph1B = 1 / (2 * b) + (mu + sg) * (2 * cB + cA) / (3 * mu)
            print("   matches phat_{i,1}:", sp.simplify(sol[pA] - ph1A) == 0, sp.simplify(sol[pB] - ph1B) == 0)
            print("   phat_{A,1} - phat_{A,2} =", sp.simplify(ph1A - phA), "; phat_{B,1} - phat_{B,2} =", sp.simplify(ph1B - phB))

    # Scenario S: c_A/(p_A + g(ph - c_A)) <= c_B/(p_B + g(ph - c_B)) <=> c_A p_B - c_B p_A <= g ph (c_B - c_A)
    ph = sp.symbols("pbar", positive=True)
    cross = sp.expand(cB * (pA + g * (ph - cA)) - cA * (pB + g * (ph - cB)))
    print("S ordering: c_B(p_A+g(pbar-c_A)) - c_A(p_B+g(pbar-c_B)) =", sp.factor(cross - (cB * pA - cA * pB)), "+ (c_B p_A - c_A p_B)")

    # (A.21): first-order conditions with V_i' = g nu_i + e_i'
    a, s, z, yB, lam = sp.symbols("alpha_A s z y_B lambda")
    nA, nB, eAp, eBQ, I_e = sp.symbols("nu_A nu_B ePrime_A_Q ePrime_B_Q I_eB")   # I_e = int_0^1 e_B'(s + lam (Q - s)) dlam
    aB = 1 - a
    Q = (a + th * aB) * z + (1 - th) * aB * s
    yA = (a + th * aB) * z - th * aB * s
    print("Q - (y_A + y_B) with y_B = alpha_B s:", sp.simplify(Q - (yA + aB * s)))
    x = s + lam * (z - s)
    print("argument identity (alpha_A+theta alpha_B) x + (1-theta) y_B - [s + lam (Q - s)] =",
          sp.simplify((a + th * aB) * x + (1 - th) * aB * s - (s + lam * (Q - s))))
    q = (mu + sg - z) / (2 * sg)
    t = (mu + sg - s) / (2 * sg)
    print("(z - s)/(2 sigma) - (t - q) =", sp.simplify((z - s) / (2 * sg) - (t - q)))
    focA = (pA + g * nA + eAp) * q - cA
    focB = (pB * t + (1 - th) * g * nB * (t - q) + (1 - th) * (t - q) * I_e + (g * nB + eBQ) * q - cB)
    r = (1 - th) * (t - q) * I_e + q * eBQ
    print("A FOC - [(p_A + g nu_A) q + q e_A' - c_A] =", sp.simplify(focA - ((pA + g * nA) * q + q * eAp - cA)))
    print("B FOC - [theta g nu_B q + (p_B + g(1-theta) nu_B) t + r - c_B] =",
          sp.simplify(focB - (th * g * nB * q + (pB + g * (1 - th) * nB) * t + r - cB)))
    # (u, v) system and its Jacobian
    u, v = sp.symbols("u v")
    L = 1 + g * (1 - th)
    sysA = (pA + g * nA) * (u / g)
    sysB = th * g * nB * (u / g) + (pB + g * (1 - th) * nB) * (v / L)
    J = sp.Matrix([[sp.diff(sysA, u), sp.diff(sysA, v)], [sp.diff(sysB, u), sp.diff(sysB, v)]]).applyfunc(sp.simplify)
    print("(u, v) Jacobian:", J)
    q0 = cA / (pA + g * nA)
    t0 = (cB - th * g * nB * q0) / (pB + g * (1 - th) * nB)
    print("linear system solved by (q0, t0):", sp.simplify(sysA.subs(u, g * q0) - cA), sp.simplify(sysB.subs({u: g * q0, v: L * t0}) - cB))
    # F^{-1}(1 - x) = mu + sigma - 2 sigma x for U[mu - sigma, mu + sigma]
    Finv = lambda w: mu - sg + 2 * sg * w  # noqa: E731
    print("z^0 = F^{-1}(1 - q0):", sp.simplify(mu + sg - 2 * sg * q0 - Finv(1 - q0)) == 0,
          "; s^0 = F^{-1}(1 - t0):", sp.simplify(mu + sg - 2 * sg * t0 - Finv(1 - t0)) == 0)
    # exact E R_1 when mu - sigma < s < z < mu + sigma: R_1 = X (X <= s), (a+th aB) X + (1-th) aB s (s<X<=z), Q (X>z)
    X = sp.symbols("X")
    ER1 = (sp.integrate(X, (X, mu - sg, s)) + sp.integrate((a + th * aB) * X + (1 - th) * aB * s, (X, s, z))
           + sp.integrate(Q, (X, z, mu + sg))) / (2 * sg)
    print("E R_1 - [mu - sigma (q^2 + (1-theta) alpha_B (t^2 - q^2))] =",
          sp.simplify(sp.expand(ER1 - (mu - sg * (q ** 2 + (1 - th) * aB * (t ** 2 - q ** 2))))))
    ERA = (sp.integrate(a * X, (X, mu - sg, s)) + sp.integrate((a + th * aB) * X - th * aB * s, (X, s, z))
           + sp.integrate(yA, (X, z, mu + sg))) / (2 * sg)
    print("E R_A - [alpha_A mu - (alpha_A+theta alpha_B) sigma q^2 + theta alpha_B sigma t^2] =",
          sp.simplify(sp.expand(ERA - (a * mu - (a + th * aB) * sg * q ** 2 + th * aB * sg * t ** 2))))


class SyntheticCont:
    """A continuation with V_i'(R) = gamma nu_i + eps_i(R), to test the FOC formulas of the proof."""

    def __init__(self, nu, eps):
        self.nu, self.eps = nu, eps

    def slopes(self, gamma, ra, rb):
        r = ra + rb
        da = gamma * self.nu[0] + self.eps * np.cos(r)
        db = gamma * self.nu[1] + self.eps * np.sin(r)
        return (da, da), (db, db)


def numerical():
    print("== numerical")
    rng = np.random.default_rng(20261122)
    worst = {"nuA-nuB": np.inf, "nuB": np.inf, "cA/nuA vs cB/nuB": np.inf, "p_lo - phatA2": -np.inf,
             "phatB1 - p_hi": -np.inf, "alphaB(phat)": np.inf, "2delta - min alpha (mu-sigma)": -np.inf}
    for _ in range(2000):
        mk = s5.draw_market(rng)
        nua, nub = s5.claimed_nu(mk)
        pa2, pb2 = s5.claimed_limit_prices(mk)
        pa1, pb1 = s5.proof_first_period_limit_prices(mk)
        worst["nuA-nuB"] = min(worst["nuA-nuB"], nua - nub)
        worst["nuB"] = min(worst["nuB"], nub)
        worst["cA/nuA vs cB/nuB"] = min(worst["cA/nuA vs cB/nuB"], mk.cb / nub - mk.ca / nua)
        worst["p_lo - phatA2"] = max(worst["p_lo - phatA2"], mk.p_lo - min(pa2, pb2, pa1, pb1))
        worst["phatB1 - p_hi"] = max(worst["phatB1 - p_hi"], max(pa2, pb2, pa1, pb1) - mk.p_hi)
        worst["alphaB(phat)"] = min(worst["alphaB(phat)"], 1.0 - pm.share(pa2, pb2, mk.beta))
        delta = mk.smallest_share * mk.lo / 2.0
        worst["2delta - min alpha (mu-sigma)"] = max(worst["2delta - min alpha (mu-sigma)"], 2 * delta - mk.smallest_share * mk.lo)
    print("2000 markets of draw_market (min of quantities that must be > 0, max of those that must be < 0):")
    for k, val in worst.items():
        print(f"   {k}: {val:.4g}")

    # R_1 = min{X, yA+yB, (aA+th aB)X+(1-th)yB, (aB+th aA)X+(1-th)yA}
    err = 0.0
    for _ in range(2000):
        mk = s5.draw_market(rng)
        aa = rng.uniform(0.02, 0.98)
        ya, yb = rng.uniform(0, 1.2 * mk.hi, size=2)
        x = rng.uniform(mk.lo, mk.hi, size=50)
        ra, rb = pm.sales(x, ya, yb, aa, 1 - aa, mk.theta)
        th = mk.theta
        formula = np.minimum.reduce([x, np.full_like(x, ya + yb), (aa + th * (1 - aa)) * x + (1 - th) * yb,
                                     ((1 - aa) + th * aa) * x + (1 - th) * ya])
        err = max(err, np.max(np.abs(ra + rb - formula)))
    print(f"R_1 min-formula vs primitives.sales, 100,000 points: max |error| = {err:.2e}")

    # FOCs of the proof against marginal_profits with a synthetic continuation
    worst_a = worst_b = 0.0
    n = 0
    for _ in range(300):
        mk = s5.draw_market(rng)
        gamma = 10 ** rng.uniform(1, 3)
        nua, nub = s5.claimed_nu(mk)
        cont = SyntheticCont((nua, nub), eps=0.3)
        pa1, pb1 = rng.uniform(mk.p_lo, mk.p_hi, size=2)
        aa = pm.share(pa1, pb1, mk.beta)
        ab = 1 - aa
        th = mk.theta
        s = rng.uniform(mk.lo + 0.05 * mk.sigma, mk.hi - 0.2 * mk.sigma)
        z = rng.uniform(s + 0.01 * mk.sigma, mk.hi - 0.01 * mk.sigma)
        yb = ab * s
        ya = (aa + th * ab) * z - th * yb
        if ya / aa <= yb / ab:
            continue
        Q = ya + yb
        fa, fb = s5.marginal_profits(mk, cont, gamma, np.array(pa1), np.array(pb1), np.array(ya), np.array(yb))
        dva = lambda r: gamma * nua + 0.3 * np.cos(r)  # noqa: E731
        dvb = lambda r: gamma * nub + 0.3 * np.sin(r)  # noqa: E731
        q, t = (mk.hi - z) / (2 * mk.sigma), (mk.hi - s) / (2 * mk.sigma)
        paper_a = (pa1 + dva(Q)) * q - mk.ca
        xs, ws = np.polynomial.legendre.leggauss(40)
        xm = 0.5 * (z - s) * xs + 0.5 * (z + s)
        integral = 0.5 * (z - s) * np.sum(ws * dvb((aa + th * ab) * xm + (1 - th) * yb))
        paper_b = pb1 * t + (1 - th) / (2 * mk.sigma) * integral + dvb(Q) * q - mk.cb
        worst_a = max(worst_a, abs(float(fa) - paper_a) / (1 + gamma))
        worst_b = max(worst_b, abs(float(fb) - paper_b) / (1 + gamma))
        n += 1
    print(f"proof FOCs vs section5.marginal_profits (synthetic V' = gamma nu + 0.3 cos/sin), {n} points: "
          f"max error / (1 + gamma) A = {worst_a:.2e}, B = {worst_b:.2e}")

    # pi^0_i is C^1 across the switching boundary: one-sided derivatives in the own price at p_A = (c_A/c_B) p_B
    steps = (1e-3, 1e-4, 1e-5)
    jumps, kinks_y = {h: [] for h in steps}, {h: [] for h in steps}
    second = 0.0
    for _ in range(400):
        mk = s5.draw_market(rng)
        pb = rng.uniform(mk.p_lo, mk.p_hi)
        pa_star = mk.ca / mk.cb * pb
        if not (mk.p_lo + 1e-2 < pa_star < mk.p_hi - 1e-2):
            continue
        f = lambda pa: float(s5.benchmark_profits(mk, np.array(pa), np.array(pb))[0])  # noqa: E731
        ya = lambda pa: float(s5.benchmark_orders(mk, np.array(pa), np.array(pb))[0])  # noqa: E731
        for rel in steps:
            h = rel * pa_star
            # second-order one-sided differences: f'(x) ~ (-3 f(x) + 4 f(x +- h) - f(x +- 2h)) / (+- 2h)
            right = (-3 * f(pa_star) + 4 * f(pa_star + h) - f(pa_star + 2 * h)) / (2 * h)
            left = (3 * f(pa_star) - 4 * f(pa_star - h) + f(pa_star - 2 * h)) / (2 * h)
            jumps[rel].append(abs(right - left) / (1 + abs(left)))
            right_y = (-3 * ya(pa_star) + 4 * ya(pa_star + h) - ya(pa_star + 2 * h)) / (2 * h)
            left_y = (3 * ya(pa_star) - 4 * ya(pa_star - h) + ya(pa_star - 2 * h)) / (2 * h)
            kinks_y[rel].append(abs(right_y - left_y))
        grid = np.linspace(mk.p_lo, mk.p_hi, 2001)
        vals = s5.benchmark_profits(mk, grid, np.full_like(grid, pb))[0]
        dd = np.diff(vals, 2) / (grid[1] - grid[0]) ** 2
        second = max(second, float(np.max(np.abs(dd))) / (mk.hi * (1 + mk.p_hi)))
    n_m = len(jumps[steps[0]])
    print(f"pi^0_A across c_A/p_A = c_B/p_B, {n_m} markets, one-sided second-order differences of step h p_A:")
    for rel in steps:
        print(f"   h = {rel:g}: max relative jump of d pi^0_A/d p_A = {max(jumps[rel]):.2e}; "
              f"max jump of d y^0_A/d p_A = {max(kinks_y[rel]):.3g}")
    print("   (the pi^0 jump shrinks like h^2, i.e. it is discretisation error: pi^0 is C^1; the y^0 jump does not: y^0 has a kink)")
    print(f"   max |second difference of pi^0_A in p_A| / ((mu+sigma)(1+p_hi)) on a 2001-grid = {second:.3g} (bounded: M exists)")

    # exact E R_1 and E R_A formulas against expected_sales
    err1 = errA = 0.0
    for _ in range(2000):
        mk = s5.draw_market(rng)
        aa = rng.uniform(0.05, 0.95)
        ab, th = 1 - aa, mk.theta
        s = rng.uniform(mk.lo, mk.hi)
        z = rng.uniform(s, mk.hi)
        yb = ab * s
        ya = (aa + th * ab) * z - th * yb
        era, erb = s5.expected_sales(mk, ya, yb, aa)
        q, t = (mk.hi - z) / (2 * mk.sigma), (mk.hi - s) / (2 * mk.sigma)
        err1 = max(err1, abs(float(era + erb) - (mk.mu - mk.sigma * (q * q + (1 - th) * ab * (t * t - q * q)))) / mk.hi)
        errA = max(errA, abs(float(era) - (aa * mk.mu - (aa + th * ab) * mk.sigma * q * q + th * ab * mk.sigma * t * t)) / mk.hi)
    print(f"exact E R_1 and E R_A formulas vs section5.expected_sales, 2000 points: max rel. error {err1:.2e}, {errA:.2e}")


if __name__ == "__main__":
    symbolic()
    numerical()
