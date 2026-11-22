"""Closed forms of Lemmas 1-3 under the uniform law (A10, rho = 1), derived independently
for the audit of P1-P6 (run 2026-11-22_claude-opus-5-5-b).

The expressions below are written from the statements of Lemmas 1-3 and from the
definitions of leftovers and profits in their proofs (theory.md), not copied from
numerics/c2c/closed_form.py.  Under X ~ U[mu - sigma, mu + sigma] and z_A >= z_B:

  y_A = (a_A + th a_B) z_A - th a_B z_B,  y_B = a_B z_B
  E L_A = [ y_A (z_B - lo) - a_A (z_B^2 - lo^2)/2 + (a_A + th a_B)(z_A - z_B)^2 / 2 ] / (2 sigma)
  E L_B = a_B (z_B - lo)^2 / (4 sigma)

(derived by splitting X at z_B and z_A).  Shares are free symbols aA1, aA2 with
aB = 1 - aA; the sampler below ties them to prices via a_A = 1/2 + beta (p_B - p_A).

Run from the repository root:  python verification/2026-11-22_claude-opus-5-5-b/scripts/shared_sec4_closed_forms.py
Running it compares these expressions with numerics/c2c/closed_form.py at random exact
rational admissible points (agreement, not independence, of the two transcriptions).
"""
from __future__ import annotations

import sys
from fractions import Fraction as Fr
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[3]

pa1, pb1, pa2, pb2, ca, cb, aA1, aA2, mu, sg, th, g = sp.symbols(
    "p_A1 p_B1 p_A2 p_B2 c_A c_B alpha_A1 alpha_A2 mu sigma theta gamma", positive=True)
aB1, aB2 = 1 - aA1, 1 - aA2
lo = mu - sg


def finv(q):
    return mu - sg + 2 * sg * q


def first_period(aA, qA, qB, theta):
    """Equilibrium objects of the period game with A's fractile above B's."""
    aB = 1 - aA
    zA, zB = finv(qA), finv(qB)
    yA = (aA + theta * aB) * zA - theta * aB * zB
    yB = aB * zB
    ELA = (yA * (zB - lo) - aA * (zB**2 - lo**2) / 2 + (aA + theta * aB) * (zA - zB)**2 / 2) / (2 * sg)
    ELB = aB * (zB - lo)**2 / (4 * sg)
    return dict(zA=zA, zB=zB, yA=yA, yB=yB, ELA=ELA, ELB=ELB, RA=yA - ELA, RB=yB - ELB,
                qA=qA, qB=qB)


def benchmark(t=1, theta=th):
    p_a, p_b, aA = (pa1, pb1, aA1) if t == 1 else (pa2, pb2, aA2)
    return first_period(aA, 1 - ca / p_a, 1 - cb / p_b, theta)


def pi0(t, theta=th):
    p_a, p_b = (pa1, pb1) if t == 1 else (pa2, pb2)
    e = benchmark(t, theta)
    return (p_a - ca) * e["yA"] - p_a * e["ELA"], (p_b - cb) * e["yB"] - p_b * e["ELB"]


PS_A = pa1 + g * (pa2 - ca)            # effective first-period price of A in S
PS_B = pb1 + g * (pb2 - cb)
PN_A = pa1 + aA2 * g * (pa2 - ca)      # in N
J = aB2 * g * (pb2 - cb)
K = J * ca / PN_A


def r_N(theta=th):
    """1 - critical ratio of B in Scenario N (Lemma 3)."""
    return (cb - K * theta) / (pb1 + J * (1 - theta))


def scen_S(theta=th):
    return first_period(aA1, 1 - ca / PS_A, 1 - cb / PS_B, theta)


def scen_N(theta=th):
    return first_period(aA1, 1 - ca / PN_A, 1 - r_N(theta), theta)


def profits(theta=th):
    """Total two-period equilibrium profits (Pi^0_i, Pi^S_i, Pi^N_i) from the proofs of L1-L3."""
    p0A1, p0B1 = pi0(1, theta)
    p0A2, p0B2 = pi0(2, theta)
    S, N = scen_S(theta), scen_N(theta)
    PiS_A = (pa1 - ca + g * (pa2 - ca)) * S["yA"] - PS_A * S["ELA"] + p0A2
    PiS_B = (pb1 - cb + g * (pb2 - cb)) * S["yB"] - PS_B * S["ELB"] + p0B2
    mA, mB = aA2 * g * (pa2 - ca), aB2 * g * (pb2 - cb)
    PiN_A = (pa1 - ca + mA) * N["yA"] - (pa1 + mA) * N["ELA"] + mA * N["RB"] + p0A2
    PiN_B = (pb1 - cb + mB) * N["yB"] - (pb1 + mB) * N["ELB"] + mB * N["RA"] + p0B2
    return dict(Pi0_A=p0A1 + p0A2, Pi0_B=p0B1 + p0B2, PiS_A=PiS_A, PiS_B=PiS_B, PiN_A=PiN_A, PiN_B=PiN_B)


SYMS = (pa1, pb1, pa2, pb2, ca, cb, aA1, aA2, mu, sg)


def random_point(rng, equal_shares=False, bind=(False, False), equal_prices=False):
    """A random exact admissible point of Section 4 (A1, A10, A11, I1, I2, mu > sigma > 0).
    Returns a dict symbol -> Fraction for SYMS plus 'beta'."""
    from random import Random
    assert isinstance(rng, Random)
    def fr(lo_, hi_, den=97):
        return Fr(rng.randint(max(1, int(lo_ * den)), int(hi_ * den)), den)
    while True:
        cB = fr(0.5, 3)
        ratio = fr(0.05, 0.97)
        cA = cB * ratio
        m = fr(5, 20)
        s = m * fr(0.05, 0.95)
        PB1, PB2 = cB * fr(1.05, 4), cB * fr(1.05, 4)
        if equal_shares or equal_prices:
            gapmax = min(PB1, PB2) * (1 - ratio)
            gap = Fr(0) if equal_prices else (gapmax if bind[0] else gapmax * fr(0.02, 0.98))
            PA1, PA2 = PB1 - gap, PB2 - gap
        else:
            PA1 = PB1 * (ratio if bind[0] else ratio + fr(0.02, 0.98) * (1 - ratio))
            PA2 = PB2 * (ratio if bind[1] else ratio + fr(0.02, 0.98) * (1 - ratio))
        gapm = max(PB1 - PA1, PB2 - PA2)
        beta = fr(0.01, 3) if gapm == 0 else fr(0.01, 0.49) / gapm
        a1, a2 = Fr(1, 2) + beta * (PB1 - PA1), Fr(1, 2) + beta * (PB2 - PA2)
        ok = (beta > 0 and 0 < cA < cB and all(cB * pa >= cA * pb and pb >= pa > cA and pb > cB
                                  for pa, pb in ((PA1, PB1), (PA2, PB2))) and Fr(1, 2) <= a1 < 1
              and Fr(1, 2) <= a2 < 1 and m > s > 0)
        if ok:
            return {pa1: PA1, pb1: PB1, pa2: PA2, pb2: PB2, ca: cA, cb: cB, aA1: a1, aA2: a2, mu: m, sg: s,
                    "beta": beta}


def subs_point(expr, pt, extra=None):
    """Exact substitution of a point (and optionally theta, gamma) by structural replacement."""
    rep = {k: sp.Rational(v.numerator, v.denominator) for k, v in pt.items() if k != "beta"}
    if extra:
        rep.update({k: sp.Rational(v) for k, v in extra.items()})
    return sp.sympify(expr).xreplace(rep)


def _compare_with_numerics(n=12):
    from random import Random
    sys.path.insert(0, str(ROOT / "numerics"))
    from c2c import closed_form as cf
    rng = Random(20261122)
    worst = 0
    for k in range(n):
        pt = random_point(rng, equal_shares=(k % 2 == 0), bind=(k % 3 == 0, k % 4 == 0))
        thv, gv = Fr(rng.randint(0, 20), 20), Fr(rng.randint(1, 4000), 40)
        args = (pt[pa1], pt[pb1], pt[pa2], pt[pb2], thv, pt[ca], pt[cb], pt["beta"], pt[mu], pt[sg], gv)
        mine = profits(th)
        S, N = scen_S(), scen_N()
        repl = {th: sp.Rational(thv.numerator, thv.denominator), g: sp.Rational(gv.numerator, gv.denominator)}
        def ev(e):
            v = subs_point(e, pt, repl)
            return Fr(int(sp.numer(v)), int(sp.denom(v)))
        ref = {"PiS_A": cf.spfta_t1(*args), "PiS_B": cf.spftb_t1(*args), "PiN_A": cf.npfta_t1(*args),
               "PiN_B": cf.npftb_t1(*args), "Pi0_A": cf.spfta_t1(*args[:-1], Fr(0)), "Pi0_B": cf.spftb_t1(*args[:-1], Fr(0))}
        ya, yb, la, lb, *_ = cf.first_period_n(*args)
        ref.update(N_yA=ya, N_yB=yb, N_RA=ya - la, N_RB=yb - lb)
        ya, yb, la, lb, *_ = cf.first_period_s(*args)
        ref.update(S_yA=ya, S_yB=yb, S_RA=ya - la, S_RB=yb - lb)
        got = {**{key: ev(mine[key]) for key in ("PiS_A", "PiS_B", "PiN_A", "PiN_B", "Pi0_A", "Pi0_B")},
               "N_yA": ev(N["yA"]), "N_yB": ev(N["yB"]), "N_RA": ev(N["RA"]), "N_RB": ev(N["RB"]),
               "S_yA": ev(S["yA"]), "S_yB": ev(S["yB"]), "S_RA": ev(S["RA"]), "S_RB": ev(S["RB"])}
        diffs = {key: got[key] - ref[key] for key in ref}
        bad = {key: v for key, v in diffs.items() if v != 0}
        worst = max(worst, len(bad))
        print(f"point {k}: theta={thv}, gamma={gv}, equal shares={pt[aA1] == pt[aA2]}, "
              f"exact mismatches with closed_form.py: {len(bad)}")
    print("all quantities agree exactly at every point:", worst == 0)


if __name__ == "__main__":
    _compare_with_numerics()
