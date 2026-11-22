"""Compact profit forms and the polynomials h_A, h_B, h^N_B of the proofs of P5 and P6.

Compact forms (mine, from L2/L3 profits with E[L] = y - E[R]):
  Pi^S_A = P^S_A E[R^S_A] - c_A y^S_A + pi^0_A2,   Pi^N_A = P^N_A E[R^N_A] - c_A y^N_A + gamma a_A2 v E[R^N_B] + pi^0_A2
  Pi^S_B = P^S_B E[R^S_B] - c_B y^S_B + pi^0_B2,   Pi^N_B = P^N_B E[R^N_B] - c_B y^N_B + gamma a_B2 w E[R^N_A] + pi^0_B2
with E[R_A] = a_A mu - sigma[(a_A + th a_B) tA^2 - th a_B tB^2], E[R_B] = a_B (mu - sigma tB^2),
y_A = (a_A + th a_B) zA - th a_B zB, y_B = a_B zB, z = mu + sigma - 2 sigma t, t = tail 1 - F(zeta).
Tails: tA^S = c_A/X1, tB^S = c_B/X2, tA^N = c_A/X3, tB^N = Nr/(X3 X4), with
X1 = P^S_A, X2 = P^S_B, X3 = P^N_A, X4 = den = p_B1 + a_B2 gamma w (1-theta), Nr = c_B X3 - th a_B2 gamma w c_A.
Clearing denominators is done with X1..X4 as symbols, so no rational cancellation is needed.

Run from the repository root (prints a consistency check against shared_sec4_closed_forms):
    python verification/2026-11-22_claude-opus-5-5-b/scripts/shared_profit_polys.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from random import Random

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared_sec4_closed_forms import (PN_A, PS_A, PS_B, aA1, aA2, aB1, aB2, ca, cb, g, mu, pa1, pa2, pb1, pb2,
                                      profits, random_point, sg, subs_point, th)

X1, X2, X3, X4 = sp.symbols("X1 X2 X3 X4", positive=True)
v, w = pa2 - ca, pb2 - cb
DEN4 = pb1 + aB2 * g * w * (1 - th)
Nr_X = cb * X3 - th * aB2 * g * w * ca
XDEF = {X1: PS_A, X2: PS_B, X3: PN_A, X4: DEN4}
GENS = (g, th, pa1, pb1, pa2, pb2, ca, cb, aA1, aA2, mu, sg)


def ER_A(tA, tB):
    return aA1 * mu - sg * ((aA1 + th * aB1) * tA**2 - th * aB1 * tB**2)


def ER_B(tB):
    return aB1 * (mu - sg * tB**2)


def zz(t):
    return mu + sg - 2 * sg * t


def y_A(tA, tB):
    return (aA1 + th * aB1) * zz(tA) - th * aB1 * zz(tB)


def y_B(tB):
    return aB1 * zz(tB)


tAS, tBS, tAN, tBN = ca / X1, cb / X2, ca / X3, Nr_X / (X3 * X4)
PiS_A_X = X1 * ER_A(tAS, tBS) - ca * y_A(tAS, tBS)                 # without pi^0_A2 (common to S and N)
PiN_A_X = X3 * ER_A(tAN, tBN) - ca * y_A(tAN, tBN) + g * aA2 * v * ER_B(tBN)
PNB_X = X4 + th * aB2 * g * w                                        # = P^N_B = p_B1 + a_B2 gamma w
PiS_B_X = X2 * ER_B(tBS) - cb * y_B(tBS)                              # without pi^0_B2
PiN_B_X = PNB_X * ER_B(tBN) - cb * y_B(tBN) + g * aB2 * w * ER_A(tAN, tBN)


def clear(expr_X, mult_X):
    """expand(expr * mult) in the X symbols, then substitute their polynomial definitions."""
    e = sp.expand(expr_X * mult_X)
    PX = sp.Poly(e, X1, X2, X3, X4)     # raises if a negative power of an X survived
    gens = GENS
    base = [sp.Poly(XDEF[x], *gens) for x in (X1, X2, X3, X4)]
    powers = {}
    total = sp.Poly(0, *gens)
    for monom, coeff in PX.terms():
        term = sp.Poly(coeff, *gens)
        for i, k in enumerate(monom):
            if k:
                if (i, k) not in powers:
                    powers[(i, k)] = base[i] ** k
                term = term * powers[(i, k)]
        total = total + term
    return total


def h_A():
    """h_A = (Pi^S_A - Pi^N_A) X1 X2^2 X3^2 X4^2 / gamma (polynomial)."""
    P = clear(PiS_A_X - PiN_A_X, X1 * X2**2 * X3**2 * X4**2)
    q, r = sp.div(P, sp.Poly(g, *GENS))
    assert r.is_zero
    return q                            # a Poly over GENS


def h_B():
    """h_B = (Pi^S_B - Pi^N_B) X2 X3^2 X4 / ((p_B2 - c_B) gamma) (polynomial)."""
    P = clear(PiS_B_X - PiN_B_X, X2 * X3**2 * X4)
    q, r = sp.div(P, sp.Poly(g * w, *GENS))
    assert r.is_zero
    return q                            # a Poly over GENS


def compact_profits():
    sub = lambda e: e.xreplace(XDEF)
    return dict(PiS_A=sub(PiS_A_X), PiN_A=sub(PiN_A_X), PiS_B=sub(PiS_B_X), PiN_B=sub(PiN_B_X))


if __name__ == "__main__":
    from shared_sec4_closed_forms import pi0
    full = profits(th)
    cp = compact_profits()
    p0A2, p0B2 = pi0(2)
    rng = Random(7)
    ok = 0
    for k in range(10):
        pt = random_point(rng, equal_shares=(k % 2 == 0), bind=(k % 3 == 0, k % 4 == 0))
        rep = {th: sp.Rational(rng.randint(0, 20), 20), g: sp.Rational(rng.randint(1, 9999), 13)}
        ok += all(subs_point(full[k_] - cp[k_] - (p0A2 if k_.endswith("A") else p0B2), pt, rep) == 0 for k_ in cp)
    print(f"compact profit forms equal the full closed forms (minus pi^0_i2) exactly at {ok}/10 points")
    hA, hB = h_A(), h_B()
    print("h_A built; degree in theta:", hA.degree(th), "; degree in gamma:", hA.degree(g))
    print("h_B built; degree in theta:", hB.degree(th), "; degree in gamma:", hB.degree(g))
