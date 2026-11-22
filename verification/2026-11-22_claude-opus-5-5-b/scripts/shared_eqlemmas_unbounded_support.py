"""L1, L2, L3, LB1 under seed-demand laws with UNBOUNDED support, and L2, L3 with rho < 1.

Run from the repository root, no arguments:
    python verification/2026-11-22_claude-opus-5-5-b/scripts/shared_eqlemmas_unbounded_support.py

Why: the numerical checks in numerics/ use four laws on a bounded support. A3 (the closing
paragraph of Section 3) allows any interval support with a positive interior density, so
also [0, inf). The proofs of L2 and L3 keep a discount factor rho in (0, 1]; the checks use
rho = 1 only.

Everything here is independent of numerics/: the demand system of Section 3 is written
again below, expected sales are integrated by Gauss-Legendre quadrature between the kinks
of the (piecewise linear) sales functions and a ladder of quantiles, plus the exact tail
beyond the last kink (where both retailers sell their whole stock). The claimed orders are
transcribed from the proofs (rho kept), for weights (g_A, g_B, gC_A, gC_B) of
Z_{i,2} = g_i R_{i,1} + gC_i R_{j,1}: S = (gamma, gamma, 0, 0), N = (a gamma, (1-a) gamma,
a gamma, (1-a) gamma) with a = alpha_{A,2}, G = Online Appendix B.

Checks
  (1) period 1: the claimed (y_A, y_B) is a Nash equilibrium of the two-period payoffs
      p_1 E R_i - c_i y_i + rho (p_{i,2} - c_i)(g_i E R_i + gC_i E R_j)   [constant dropped]
      (gain of the best unilateral deviation relative to max price x mean demand, and the
      distance of each best response from the claim);
  (2) period 2 at a random sales state: y^0_{i,2} + Z_{i,2} is a Nash equilibrium, and each
      profit equals pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2};
  (3) uniqueness scan in period 1 (Scenario N and G): sign changes of BR_B(BR_A(y_B)) - y_B.
Points: random points with A11 strict, and edge points (theta = 0 and 1, A11 with equality
in both periods, p_A = p_B, equal shares across periods, gamma = 0.01 and 100, lambda_S at
0 and 1). Laws: exponential, lognormal, gamma (support [0, inf)).
"""
from __future__ import annotations

import time

import numpy as np
from scipy import optimize, stats

NODES, WEIGHTS = np.polynomial.legendre.leggauss(48)
QS = [1e-9, 1e-6, 1e-4, 1e-3, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] + [1 - 10.0 ** -k for k in range(2, 15)]


def sales(x, ya, yb, aa, ab, th, za=0.0, zb=0.0):
    """Section 3: M_i = a_i X + Z_i, D_i = M_i + theta (M_j - y_j)^+, R_i = min(D_i, y_i)."""
    ma, mb = aa * x + za, ab * x + zb
    return np.minimum(ma + th * np.maximum(mb - yb, 0.0), ya), np.minimum(mb + th * np.maximum(ma - ya, 0.0), yb)


class Law:
    def __init__(self, name, dist):
        self.name, self.dist = name, dist
        self.lo = float(dist.support()[0])
        assert np.isinf(dist.support()[1])
        self.fixed = np.unique(dist.ppf(QS))
        self.mean = float(dist.mean())

    def ppf(self, q):
        return float(self.dist.ppf(q))

    def expected_sales(self, ya, yb, aa, ab, th, za=0.0, zb=0.0):
        ya, yb = np.broadcast_arrays(np.atleast_1d(np.asarray(ya, float)), np.atleast_1d(np.asarray(yb, float)))
        k1, k2 = (ya - za) / aa, (yb - zb) / ab
        k3 = (ya - za + th * (yb - zb)) / (aa + th * ab)
        k4 = (yb - zb + th * (ya - za)) / (ab + th * aa)
        top = np.maximum(np.maximum(k1, k2), self.lo)          # beyond it both retailers sell y_i
        pts = np.concatenate([np.broadcast_to(self.fixed, (ya.size, self.fixed.size)),
                              np.stack([k1, k2, k3, k4], axis=1), np.full((ya.size, 1), self.lo), top[:, None]], axis=1)
        pts = np.sort(np.clip(pts, self.lo, top[:, None]), axis=1)
        half, mid = (pts[:, 1:] - pts[:, :-1]) / 2, (pts[:, 1:] + pts[:, :-1]) / 2
        x = mid[:, :, None] + half[:, :, None] * NODES
        w = half[:, :, None] * WEIGHTS * self.dist.pdf(x)
        ra, rb = sales(x, ya[:, None, None], yb[:, None, None], aa, ab, th, za, zb)
        tail = self.dist.sf(top)
        return (ra * w).sum(axis=(1, 2)) + ya * tail, (rb * w).sum(axis=(1, 2)) + yb * tail


def best_response(obj, upper, grid=1201):
    ys = np.linspace(0.0, upper, grid)
    v = obj(ys)
    k = int(np.argmax(v))
    lo, hi = ys[max(k - 1, 0)], ys[min(k + 1, grid - 1)]
    res = optimize.minimize_scalar(lambda y: -obj(np.array([y]))[0], bounds=(lo, hi), method="bounded",
                                   options={"xatol": 1e-11})
    return (float(res.x), float(-res.fun)) if -res.fun >= v[k] else (float(ys[k]), float(v[k]))


def nash_gap(pay_a, pay_b, ya, yb, upper):
    bra, ma = best_response(lambda y: pay_a(y, yb), upper)
    brb, mb = best_response(lambda y: pay_b(ya, y), upper)
    gain = max(ma - pay_a(np.array([ya]), yb)[0], mb - pay_b(ya, np.array([yb]))[0])
    return gain, max(abs(bra - ya), abs(brb - yb))


def weights(scn, g, a2, lam_s=1.0):
    lam_n = 1 - lam_s
    return {"0": (0, 0, 0, 0), "S": (g, g, 0, 0), "N": (a2 * g, (1 - a2) * g, a2 * g, (1 - a2) * g),
            "G": ((lam_s + lam_n * a2) * g, (lam_s + lam_n * (1 - a2)) * g, lam_n * g * a2, lam_n * g * (1 - a2))}[scn]


def claimed(p, scn, law, rho):
    """Lemmas 1-3 (rho kept, as in the proofs) and B.1 (rho = 1) for the ordering A11 gives."""
    a1 = 0.5 + p["beta"] * (p["pb1"] - p["pa1"])
    a2 = 0.5 + p["beta"] * (p["pb2"] - p["pa2"])
    gA, gB, cA, cB = weights(scn, p["gamma"], a2, p["lam_s"])
    mA, mB = p["pa2"] - p["ca"], p["pb2"] - p["cb"]
    r = p["ca"] / (p["pa1"] + rho * gA * mA)
    qA = 1 - r
    qB = 1 - (p["cb"] - rho * cB * p["theta"] * mB * r) / (p["pb1"] + rho * (gB - cB * p["theta"]) * mB)
    assert 0 < qB <= qA + 1e-12 and qA < 1, (qA, qB)
    zA, zB = law.ppf(qA), law.ppf(qB)
    th = p["theta"]
    return (a1 + th * (1 - a1)) * zA - th * (1 - a1) * zB, (1 - a1) * zB, a1, a2, (gA, gB, cA, cB)


def benchmark(pa, pb, ca, cb, beta, th, law):
    a = 0.5 + beta * (pb - pa)
    qA, qB = 1 - ca / pa, 1 - cb / pb
    assert qA >= qB - 1e-15
    zA, zB = law.ppf(qA), law.ppf(qB)
    return (a + th * (1 - a)) * zA - th * (1 - a) * zB, (1 - a) * zB, a


def period1_payoffs(p, law, a1, w, rho):
    gA, gB, cA, cB = w
    mA, mB = p["pa2"] - p["ca"], p["pb2"] - p["cb"]

    def pay_a(ya, yb):
        ra, rb = law.expected_sales(ya, yb, a1, 1 - a1, p["theta"])
        return p["pa1"] * ra - p["ca"] * np.atleast_1d(ya) + rho * mA * (gA * ra + cA * rb)

    def pay_b(ya, yb):
        ra, rb = law.expected_sales(ya, yb, a1, 1 - a1, p["theta"])
        return p["pb1"] * rb - p["cb"] * np.atleast_1d(yb) + rho * mB * (gB * rb + cB * ra)
    return pay_a, pay_b


def period2_payoffs(p, law, a2, za, zb):
    def pay_a(ya, yb):
        return p["pa2"] * law.expected_sales(ya, yb, a2, 1 - a2, p["theta"], za, zb)[0] - p["ca"] * np.atleast_1d(ya)

    def pay_b(ya, yb):
        return p["pb2"] * law.expected_sales(ya, yb, a2, 1 - a2, p["theta"], za, zb)[1] - p["cb"] * np.atleast_1d(yb)
    return pay_a, pay_b


def random_point(rng):
    cb = rng.uniform(0.5, 3.0)
    ca = cb * rng.uniform(0.05, 0.98)
    pb1, pb2 = cb * rng.uniform(1.05, 4.0, size=2)
    pa1, pa2 = rng.uniform(ca / cb * pb1, pb1), rng.uniform(ca / cb * pb2, pb2)
    beta = min(0.5, rng.uniform(0, 0.45) / max(pb1 - pa1, pb2 - pa2))
    return dict(pa1=pa1, pb1=pb1, pa2=pa2, pb2=pb2, ca=ca, cb=cb, beta=beta, theta=rng.uniform(0, 1),
                gamma=float(np.exp(rng.uniform(np.log(0.05), np.log(50)))), lam_s=rng.uniform(0, 1))


def edge_points(rng):
    out = []
    for tag in ("theta=0", "theta=1", "A11 equality both periods", "A11 equality period 1", "p_A=p_B both periods",
                "equal shares across periods", "gamma=0.01", "gamma=100", "lambda_S=0", "lambda_S=1"):
        p = random_point(rng)
        if tag == "theta=0":
            p["theta"] = 0.0
        elif tag == "theta=1":
            p["theta"] = 1.0
        elif tag.startswith("A11 equality"):
            p["pa1"] = p["ca"] / p["cb"] * p["pb1"]
            if "both" in tag:
                p["pa2"] = p["ca"] / p["cb"] * p["pb2"]
            p["beta"] = min(0.5, 0.45 / max(p["pb1"] - p["pa1"], p["pb2"] - p["pa2"]))
        elif tag == "p_A=p_B both periods":
            p["pa1"], p["pa2"] = p["pb1"], p["pb2"]
        elif tag == "equal shares across periods":
            gap = 0.6 * min(p["pb1"] * (1 - p["ca"] / p["cb"]), p["pb2"] * (1 - p["ca"] / p["cb"]))
            p["pa1"], p["pa2"] = p["pb1"] - gap, p["pb2"] - gap
            p["beta"] = min(0.5, 0.45 / gap)
        elif tag == "gamma=0.01":
            p["gamma"] = 0.01
        elif tag == "gamma=100":
            p["gamma"] = 100.0
        elif tag == "lambda_S=0":
            p["lam_s"] = 0.0
        elif tag == "lambda_S=1":
            p["lam_s"] = 1.0
        out.append((tag, p))
    return out


def main():
    t0 = time.time()
    rng = np.random.default_rng(20261122)
    laws = [Law("exponential(scale 10)", stats.expon(scale=10.0)),
            Law("lognormal(s 0.6, scale 10)", stats.lognorm(s=0.6, scale=10.0)),
            Law("gamma(a 2.5, scale 4)", stats.gamma(a=2.5, scale=4.0))]
    configs = [("0", 1.0), ("S", 1.0), ("N", 1.0), ("G", 1.0), ("S", 0.6), ("N", 0.6)]
    worst = {}
    n_games = 0
    for law in laws:
        pts = [("random", random_point(rng)) for _ in range(2)] + edge_points(rng)
        for tag, p in pts:
            for scn, rho in configs:
                ya, yb, a1, a2, w = claimed(p, scn, law, rho)
                upper = 1.3 * max(law.ppf(1 - 1e-7), 1.5 * ya / a1)
                gain, dist = nash_gap(*period1_payoffs(p, law, a1, w, rho), ya, yb, upper)
                scale = max(p["pa1"], p["pb1"], p["pa2"], p["pb2"]) * (1 + p["gamma"]) * law.mean
                key = (scn, rho)
                g_rel = gain / scale
                worst[key] = max(worst.get(key, (0, 0, "")), (g_rel, dist / law.mean, f"{law.name} {tag}"))
                n_games += 1
                assert g_rel < 1e-8 and dist < 2e-5 * law.mean, (law.name, tag, scn, rho, g_rel, dist)
    print(f"(1) period-1 equilibrium, {n_games} games ({len(laws)} unbounded laws x 12 points x {len(configs)} configs)")
    for (scn, rho), (g, d, where) in sorted(worst.items()):
        print(f"    scenario {scn} rho={rho}: max relative deviation gain {g:.2e}, max |BR - claim|/mean {d:.2e}  [{where}]")

    # (2) second period at a random state
    worst2 = (0.0, 0.0, 0.0)
    n2 = 0
    for law in laws:
        for tag, p in [("random", random_point(rng))] + edge_points(rng)[:4]:
            a2 = 0.5 + p["beta"] * (p["pb2"] - p["pa2"])
            y0a, y0b, _ = benchmark(p["pa2"], p["pb2"], p["ca"], p["cb"], p["beta"], p["theta"], law)
            ra1, rb1 = rng.uniform(0, 2 * law.mean), rng.uniform(0, 2 * law.mean)
            pi0 = [f(np.array([y0a]), y0b)[0] if k == 0 else f(y0a, np.array([y0b]))[0]
                   for k, f in enumerate(period2_payoffs(p, law, a2, 0.0, 0.0))]
            for scn in ("S", "N", "G"):
                gA, gB, cA, cB = weights(scn, p["gamma"], a2, p["lam_s"])
                za, zb = gA * ra1 + cA * rb1, gB * rb1 + cB * ra1
                pay_a, pay_b = period2_payoffs(p, law, a2, za, zb)
                ya, yb = y0a + za, y0b + zb
                upper = 1.3 * (law.ppf(1 - 1e-7) + za + zb)
                gain, dist = nash_gap(pay_a, pay_b, ya, yb, upper)
                va, vb = pay_a(np.array([ya]), yb)[0], pay_b(ya, np.array([yb]))[0]
                verr = max(abs(va - pi0[0] - (p["pa2"] - p["ca"]) * za), abs(vb - pi0[1] - (p["pb2"] - p["cb"]) * zb))
                scale = max(p["pa2"], p["pb2"]) * (1 + p["gamma"]) * law.mean
                worst2 = tuple(max(u, v) for u, v in zip(worst2, (gain / scale, dist / law.mean, verr / scale)))
                n2 += 1
                assert gain / scale < 1e-8 and dist < 2e-5 * law.mean * (1 + p["gamma"]) and verr / scale < 1e-10
    print(f"(2) period-2 equilibrium y0 + Z at a random state, {n2} games: max relative gain {worst2[0]:.2e}, "
          f"max |BR - claim|/mean {worst2[1]:.2e}, max relative error of pi0 + (p2 - c) Z {worst2[2]:.2e}")

    # (3) uniqueness scan of period 1, scenarios N and G
    print("(3) period-1 uniqueness scan of T(y_B) = BR_B(BR_A(y_B)) on 30 nodes")
    for law, scn in zip(laws, ("N", "G", "N")):
        p = random_point(rng)
        ya, yb, a1, a2, w = claimed(p, scn, law, 1.0)
        pay_a, pay_b = period1_payoffs(p, law, a1, w, 1.0)
        upper = 1.3 * max(law.ppf(1 - 1e-7), 1.5 * ya / a1)
        nodes = np.linspace(0, upper, 30)
        gaps = []
        for y in nodes:
            bra = best_response(lambda u: pay_a(u, y), upper, grid=401)[0]
            gaps.append(best_response(lambda u: pay_b(bra, u), upper, grid=401)[0] - y)
        s = np.sign(gaps)
        changes = [(nodes[k], nodes[k + 1]) for k in range(len(s) - 1) if s[k] != s[k + 1]]
        print(f"    {law.name}, scenario {scn}: sign changes {len(changes)} at {[(round(a, 3), round(b, 3)) for a, b in changes]}, "
              f"claimed y_B = {yb:.4f}")
        assert len(changes) == 1 and changes[0][0] <= yb <= changes[0][1]
    print(f"all checks passed in {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
