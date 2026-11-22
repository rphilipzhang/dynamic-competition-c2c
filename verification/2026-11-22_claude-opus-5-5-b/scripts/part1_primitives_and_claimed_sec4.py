"""Part 1, numerics items 1 and 2 (Section 4 part): primitives.py against Section 3, and the
claimed_* functions of section4.py against Lemmas 1, 2, 3 and B.1.

Run from the repository root, no arguments:
    python verification/2026-11-22_claude-opus-5-5-b/scripts/part1_primitives_and_claimed_sec4.py

(a) primitives.py imports nothing from c2c (so it uses no result of the paper).
(b) primitives.share, sales and c2c_demand against a transcription of Section 3 written here
    (shares, M_i = a_i X + Z_i, D_i = M_i + theta (M_j - y_j)^+, R_i = min(D_i, y_i),
    Z^S_i = gamma R_i, Z^N_i = a_i gamma (R_A + R_B), Z^G = lam_S Z^S + lam_N Z^N), exact
    rational arithmetic at random points (primitives evaluated in floating point), including
    y_i < Z_i and theta in {0, 1}.
(c) primitives.Uniform.expected_sales and Quadrature.expected_sales against scipy.integrate.quad
    of the same sales function (with the kinks as break points).
(d) section4.Params.weights("G") against the definitions of Online Appendix B.
(e) claimed_benchmark and claimed_first_period against the printed formulas of Lemmas 1, 2, 3
    and B.1 (transcribed here), exact rational arithmetic with the uniform quantile function,
    at points satisfying A1, A11 (equality allowed), I1, I2; and their mirror branch against
    the printed formula with the roles of A and B exchanged.
"""
from __future__ import annotations

import ast
import random
import sys
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
from scipy import integrate, stats

sys.path.insert(0, "numerics")
from c2c import primitives as pm  # noqa: E402
from c2c.section4 import Params, claimed_benchmark, claimed_first_period  # noqa: E402


def lat(r, lo, hi, den=1000):
    return Fr(r.randint(round(lo * den), round(hi * den)), den)


def part_a():
    tree = ast.parse(Path("numerics/c2c/primitives.py").read_text())
    mods = sorted({n.module if isinstance(n, ast.ImportFrom) else a.name for n in ast.walk(tree)
                   if isinstance(n, (ast.Import, ast.ImportFrom)) for a in (n.names if isinstance(n, ast.Import) else [None])})
    print(f"(a) modules imported by primitives.py: {mods}")
    assert not any(m and m.startswith("c2c") for m in mods)


def part_b(r):
    n, worst = 0, 0.0
    for _ in range(3000):
        pa, pb, beta = lat(r, 1, 10), lat(r, 1, 10), lat(r, 0, 0.05)
        aa = Fr(1, 2) + beta * (pb - pa)
        assert abs(pm.share(pa, pb, beta) - aa) < 1e-14 and abs(pm.share(pb, pa, beta) - (1 - aa)) < 1e-14
        ab = 1 - aa
        th = r.choice([Fr(0), Fr(1), lat(r, 0, 1)])
        x, ya, yb = lat(r, 0, 20), lat(r, 0, 30), lat(r, 0, 30)
        ra1, rb1, g, lam = lat(r, 0, 10), lat(r, 0, 10), lat(r, 0, 5), lat(r, 0, 1)
        for scn in ("0", "S", "N", "G"):
            za, zb = pm.c2c_demand(scn, g, ra1, rb1, aa, lam, 1 - lam)
            want = {"0": (0, 0), "S": (g * ra1, g * rb1), "N": (aa * g * (ra1 + rb1), ab * g * (ra1 + rb1)),
                    "G": (lam * g * ra1 + (1 - lam) * aa * g * (ra1 + rb1), lam * g * rb1 + (1 - lam) * ab * g * (ra1 + rb1))}[scn]
            assert abs(za - want[0]) < 1e-12 and abs(zb - want[1]) < 1e-12, scn
            ma, mb = aa * x + za, ab * x + zb
            da = ma + th * max(mb - yb, 0)
            db = mb + th * max(ma - ya, 0)
            got = pm.sales(float(x), float(ya), float(yb), float(aa), float(ab), float(th), float(za), float(zb))
            worst = max(worst, abs(float(got[0]) - float(min(da, ya))), abs(float(got[1]) - float(min(db, yb))))
            n += 1
    print(f"(b) share, c2c_demand and sales against the exact transcription of Section 3 at {n} (point, scenario) pairs:"
          f" max abs difference of sales {worst:.2e} (floating point in primitives)")
    assert worst < 1e-12


def part_c(r):
    worst = 0.0
    laws = [("uniform", pm.Uniform(2.0, 18.0), stats.uniform(loc=2.0, scale=16.0)),
            ("beta(2,5)", pm.Quadrature(stats.beta(2, 5, loc=2.0, scale=16.0)), stats.beta(2, 5, loc=2.0, scale=16.0)),
            ("truncnorm", pm.Quadrature(stats.truncnorm(-2, 2, loc=10.0, scale=4.0)), stats.truncnorm(-2, 2, loc=10.0, scale=4.0))]
    for name, law, dist in laws:
        for _ in range(8):
            aa = r.uniform(0.5, 0.95); ab = 1 - aa
            th, ya, yb = r.choice([0.0, 1.0, r.uniform(0, 1)]), r.uniform(0, 25), r.uniform(0, 20)
            za, zb = r.choice([(0.0, 0.0), (r.uniform(0, 8), r.uniform(0, 8))])
            ks = [(ya - za) / aa, (yb - zb) / ab, (ya - za + th * (yb - zb)) / (aa + th * ab), (yb - zb + th * (ya - za)) / (ab + th * aa)]
            lo, hi = dist.support()
            pts = sorted(k for k in ks if lo < k < hi)
            ref = [integrate.quad(lambda x, i=i: pm.sales(x, ya, yb, aa, ab, th, za, zb)[i] * dist.pdf(x), lo, hi,
                                  points=pts or None, limit=200, epsabs=1e-13, epsrel=1e-13)[0] for i in (0, 1)]
            got = law.expected_sales(ya, yb, aa, ab, th, za, zb)
            worst = max(worst, abs(got[0][0] - ref[0]), abs(got[1][0] - ref[1]))
    print(f"(c) expected sales of primitives.Uniform / Quadrature against scipy quad: max abs difference {worst:.2e}")
    assert worst < 1e-9


def part_d(r):
    for _ in range(500):
        p = Params(*(float(lat(r, 1, 10)) for _ in range(4)), ca=1.0, cb=1.5, beta=0.05, theta=0.5,
                   gamma=float(lat(r, 0, 10)), lam_s=float(lat(r, 0, 1)), lam_n=0.0)
        p = Params(p.pa1, p.pb1, p.pa2, p.pb2, p.ca, p.cb, p.beta, p.theta, p.gamma, p.lam_s, 1 - p.lam_s)
        a = 0.5 + p.beta * (p.pb2 - p.pa2)
        want = ((p.lam_s + p.lam_n * a) * p.gamma, (p.lam_s + p.lam_n * (1 - a)) * p.gamma, p.lam_n * p.gamma * a, p.lam_n * p.gamma * (1 - a))
        assert np.allclose(p.weights("G"), want, rtol=1e-15, atol=0)
        assert p.weights("S") == (p.gamma, p.gamma, 0.0, 0.0)
        assert np.allclose(p.weights("N"), (a * p.gamma, (1 - a) * p.gamma, a * p.gamma, (1 - a) * p.gamma), rtol=1e-15, atol=0)
    print("(d) Params.weights: S, N and G (gamma_{i,2} = (lam_S + lam_N a_{i,2}) gamma, gammaC_{i,2} = lam_N gamma a_{i,2}) as in Online Appendix B")


def printed(pa1, pb1, pa2, pb2, ca, cb, beta, th, g, lam, scn, finv):
    """Lemma 1 (scn '0', first-period prices), Lemma 2 ('S'), Lemma 3 ('N'), Lemma B.1 ('G'), as printed."""
    a1, a2 = Fr(1, 2) + beta * (pb1 - pa1), Fr(1, 2) + beta * (pb2 - pa2)
    b1, b2 = 1 - a1, 1 - a2
    if scn == "0":
        zA, zB = finv(1 - ca / pa1), finv(1 - cb / pb1)
    elif scn == "S":
        zA, zB = finv(1 - ca / (pa1 + g * (pa2 - ca))), finv(1 - cb / (pb1 + g * (pb2 - cb)))
    elif scn == "N":
        zA = finv(1 - ca / (pa1 + a2 * g * (pa2 - ca)))
        zB = finv(1 - (cb - b2 * g * th * (pb2 - cb) * ca / (pa1 + a2 * g * (pa2 - ca))) / (pb1 + b2 * g * (1 - th) * (pb2 - cb)))
    else:
        lamn = 1 - lam
        gA2, gB2, gCB2 = (lam + lamn * a2) * g, (lam + lamn * b2) * g, lamn * g * b2
        zA = finv(1 - ca / (pa1 + gA2 * (pa2 - ca)))
        zB = finv(1 - (cb - gCB2 * th * (pb2 - cb) * ca / (pa1 + gA2 * (pa2 - ca))) / (pb1 + (gB2 - gCB2 * th) * (pb2 - cb)))
    return (a1 + th * b1) * zA - th * b1 * zB, b1 * zB


def part_e(r):
    mu, sg = Fr(10), Fr(6)
    finv = lambda q: mu - sg + 2 * sg * q          # noqa: E731
    n, n_mirror, n_eq, worst, worst_m = 0, 0, 0, 0.0, 0.0
    for k in range(1500):
        cb = lat(r, 0.5, 3); ratio = lat(r, 0.001, 0.999); ca = cb * ratio
        pb1, pb2 = cb * lat(r, 1.001, 50), cb * lat(r, 1.001, 50)
        pa1, pa2 = (pb * (ratio + r.choice([Fr(0), Fr(1), lat(r, 0, 1)]) * (1 - ratio)) for pb in (pb1, pb2))
        n_eq += pa1 == ratio * pb1
        gap = max(pb1 - pa1, pb2 - pa2)
        beta = lat(r, 0.000001, 0.499, 10**6) / gap if gap > 0 else lat(r, 0.001, 5)
        th, g, lam = r.choice([Fr(0), Fr(1), lat(r, 0, 1)]), lat(r, 0.01, 100), r.choice([Fr(0), Fr(1), lat(r, 0, 1)])
        prm = Params(pa1, pb1, pa2, pb2, ca, cb, beta, th, g, lam, 1 - lam)
        for scn in ("0", "S", "N", "G"):
            ya, yb, qa, qb, a_high = claimed_first_period(prm, scn, finv)
            want = printed(pa1, pb1, pa2, pb2, ca, cb, beta, th, g, lam, scn, finv)
            worst = max(worst, abs(float(ya) - float(want[0])) / float(mu), abs(float(yb) - float(want[1])) / float(mu))
            assert a_high or abs(float(qa) - float(qb)) < 1e-12, (k, scn)
            n += 1
        for pa, pb in ((pa1, pb1), (pa2, pb2)):
            ya, yb, *_ = claimed_benchmark(pa, pb, ca, cb, beta, th, finv)
            want = printed(pa, pb, pa, pb, ca, cb, beta, th, 0, lam, "0", finv)
            worst = max(worst, abs(float(ya) - float(want[0])) / float(mu), abs(float(yb) - float(want[1])) / float(mu))
        # mirror branch: prices that break A11, compared with the printed formula with roles exchanged
        qa1, qb1 = cb * lat(r, 1.001, 10), cb * lat(r, 1.001, 10)
        qa2, qb2 = cb * lat(r, 1.001, 10), cb * lat(r, 1.001, 10)
        beta2 = lat(r, 1, 400) / 1000 / max(abs(qb1 - qa1), abs(qb2 - qa2), Fr(1))
        prm2 = Params(qa1, qb1, qa2, qb2, ca, cb, beta2, th, g, lam, 1 - lam)
        for scn in ("S", "N", "G"):
            ya, yb, _, _, a_high = claimed_first_period(prm2, scn, finv)
            if not a_high:
                yb_sw, ya_sw = printed(qb1, qa1, qb2, qa2, cb, ca, beta2, th, g, lam, scn, finv)
                worst_m = max(worst_m, abs(float(ya) - float(ya_sw)) / float(mu), abs(float(yb) - float(yb_sw)) / float(mu))
                n_mirror += 1
    print(f"(e) claimed_first_period and claimed_benchmark against the printed Lemmas 1, 2, 3, B.1 at {n} "
          f"(point, scenario) pairs ({n_eq} points with A11 equality in period 1): max |difference| / mu = {worst:.2e}; "
          f"the mirror branch against the printed form with A and B exchanged at {n_mirror} pairs: {worst_m:.2e}")
    assert worst < 1e-12 and worst_m < 1e-12


if __name__ == "__main__":
    r = random.Random(2026)
    part_a()
    part_b(r)
    part_c(r)
    part_d(r)
    part_e(r)
    print("all checks passed")
