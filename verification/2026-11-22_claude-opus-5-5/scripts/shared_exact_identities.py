"""Exact rational checks of the algebraic steps of Lemmas 1-4 and B.1 (theory.md L1, L2, L3, L4, LB1).

Run from the repository root:
    python verification/2026-11-22_claude-opus-5-5/scripts/shared_exact_identities.py

Independent of numerics/: own sampler, own formulas, Python Fractions only. The steps are
statements about critical ratios q (arguments of F^{-1}) and about the piecewise-linear best
responses, so they hold for every F of the A3 class once they hold for the ratios; F enters
only through a strictly increasing F^{-1} on (0, 1), which preserves every ordering below.

Points: rational points with A1 (0 < c_A < c_B), A11 (p_B,t >= p_A,t >= (c_A/c_B) p_B,t),
I1 (p_i,t > c_i), I2 (shares in (0, 1)), theta in [0, 1], gamma > 0, lambda_S in [0, 1].
Each coordinate is drawn regular or at an edge (A11 equality, p_A = p_B, theta 0 or 1,
lambda 0 or 1, c_A/c_B near 0 or 1, p_B/c_B near 1, small and huge gamma).

Checks (each printed with the number of points and failures):
 C1  L2: c_A/(p_A1+g m_A) <= c_B/(p_B1+g m_B), equality iff A11 binds in both periods.
 C2  L3: c_A/(p_A1+a_A2 g m_A) < c_B/(p_B1+a_B2 g m_B) strictly (gamma > 0, A1).
 C3  L3: q^N_B in (0,1), q^N_A in (0,1), q^N_A > q^N_B; and q^N_A >= q^N_B <=> C2-ordering
         (tested also at points violating A11).
 C4  L3: (A.17) holds at the closed form: F(u) = q^N_A, F(b) = q^N_B solve both equations.
 C5  L3: zeta^N_A < zeta^S_A (q^N_A < q^S_A).
 C6  LB1: for each lambda, c_A/(p_A1+gamma_A2 m_A) <= c_B/(p_B1+gamma_B2 m_B); q^G_B in (0,1);
          q^G_A >= q^G_B; the first-period system of the proof holds at the closed form;
          lambda = (1,0) gives L2 and lambda = (0,1) gives L3.
 C7  L1/L2 'by combining (A.2) and (A.3)': with z_A >= z_B the four branch pairs of the piecewise
     linear best responses have exactly one consistent solution, the claimed one (exact).
 C8  L4: y_A/a_A - y_B/a_B = (a_A + theta a_B)(z_A - z_B)/a_A >= 0 (exact), with z = F^{-1}(q)
     for the uniform law; equality iff q_A = q_B.
 C9  L2/L3/LB1 second period: pathwise, with y_i = y0_i + Z_i, R_i = Z_i + R0_i(X), so the
     period-2 profit is pi0_i(X) + (p_i2 - c_i) Z_i at every X (exact at random X).
 C10 L3 contradiction step: in the region a < b (a = y_A/a_A, b = y_B/a_B), w = (y_B+th y_A)/(a_B+th a_A)
     satisfies a < w <= b, and the first equation of (A.16) with F(a) < F(w) forces
     1 - c_A/(p_A1+K_A) < F(w) (checked as an identity on the coefficients, exact).
"""
from fractions import Fraction as Fr
import random

rng = random.Random(20261122)
N = 4000


def lat(lo, hi, den=1000):
    return Fr(rng.randint(round(lo * den), round(hi * den)), den)


def pick(edges, regular):
    u = rng.random()
    return edges[0] if u < 0.2 else edges[1] if u < 0.4 else regular()


def draw(a11=True):
    cb = lat(0.5, 3)
    ratio = pick((Fr(1, 1000), Fr(999, 1000)), lambda: lat(0.05, 0.98))
    ca = cb * ratio
    pb = [cb * pick((Fr(1001, 1000), Fr(50)), lambda: lat(1.05, 4)) for _ in range(2)]
    if a11:
        pa = [p * (ratio + pick((Fr(0), Fr(1)), lambda: lat(0.001, 0.999)) * (1 - ratio)) for p in pb]
    else:
        pa = [cb * lat(1.05, 4) for _ in range(2)]
        pa = [max(p, ca * Fr(1001, 1000)) for p in pa]
    gap = max(abs(pb[0] - pa[0]), abs(pb[1] - pa[1]))
    beta = (lat(0.001, 0.499) / gap) if gap > 0 else lat(0.001, 5)
    theta = pick((Fr(0), Fr(1)), lambda: lat(0.001, 0.999))
    gamma = pick((Fr(1, 100), Fr(10**6)), lambda: lat(0.05, 50))
    lam = pick((Fr(0), Fr(1)), lambda: lat(0.001, 0.999))
    aa = [Fr(1, 2) + beta * (pb[t] - pa[t]) for t in range(2)]
    return dict(pa1=pa[0], pa2=pa[1], pb1=pb[0], pb2=pb[1], ca=ca, cb=cb, beta=beta, theta=theta,
                gamma=gamma, lam=lam, aa1=aa[0], aa2=aa[1], ab1=1 - aa[0], ab2=1 - aa[1])


def binds(P, t):
    return P["cb"] * P[f"pa{t}"] == P["ca"] * P[f"pb{t}"]


def weights(P, lam_s):
    g, a, b = P["gamma"], P["aa2"], P["ab2"]
    lam_n = 1 - lam_s
    return (lam_s + lam_n * a) * g, (lam_s + lam_n * b) * g, lam_n * g * a, lam_n * g * b


def ratios(P, gA, gB, gcB):
    mA, mB, th = P["pa2"] - P["ca"], P["pb2"] - P["cb"], P["theta"]
    own_a = P["ca"] / (P["pa1"] + gA * mA)
    own_b = P["cb"] / (P["pb1"] + gB * mB)
    qa = 1 - own_a
    qb = 1 - (P["cb"] - gcB * th * mB * own_a) / (P["pb1"] + (gB - gcB * th) * mB)
    return own_a, own_b, qa, qb


fails = {k: 0 for k in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10")}
counts = dict.fromkeys(fails, 0)
c1_equal = 0
c3_reverse = 0
for k in range(N):
    P = draw(a11=True)
    th, g = P["theta"], P["gamma"]
    mA, mB = P["pa2"] - P["ca"], P["pb2"] - P["cb"]
    # C1
    oa, ob, qa_s, qb_s = ratios(P, g, g, 0)
    counts["C1"] += 1
    both = binds(P, 1) and binds(P, 2)
    c1_equal += both
    if not (oa <= ob and ((oa == ob) == both)):
        fails["C1"] += 1
    # C2, C3, C4, C5: Scenario N
    gA, gB, gcA, gcB = P["aa2"] * g, P["ab2"] * g, P["aa2"] * g, P["ab2"] * g
    oa, ob, qa, qb = ratios(P, gA, gB, gcB)
    counts["C2"] += 1
    fails["C2"] += not (oa < ob)
    counts["C3"] += 1
    fails["C3"] += not (0 < qb < 1 and 0 < qa < 1 and qa > qb)
    KA, KB = mA * gA, mB * gB
    eq1 = (P["pa1"] - P["ca"] + KA) - (P["pa1"] + KA) * qa
    eq2 = (P["pb1"] - P["cb"] + KB) - ((P["pb1"] + KB * (1 - th)) * qb + KB * th * qa)
    counts["C4"] += 1
    fails["C4"] += not (eq1 == 0 and eq2 == 0)
    counts["C5"] += 1
    fails["C5"] += not (qa < qa_s)
    # C6: mixed scenario, several weights
    for lam_s in (Fr(0), Fr(1), Fr(1, 3), Fr(1, 2), P["lam"]):
        gA, gB, gcA, gcB = weights(P, lam_s)
        oa, ob, qa, qb = ratios(P, gA, gB, gcB)
        e1 = (P["pa1"] - P["ca"] + mA * gA) - (P["pa1"] + mA * gA) * qa
        e2 = (P["pb1"] - P["cb"] + mB * gB) - ((P["pb1"] + mB * (gB - gcB * th)) * qb + mB * gcB * th * qa)
        ok = oa <= ob and 0 < qb < 1 and 0 < qa < 1 and qa >= qb and e1 == 0 and e2 == 0
        if lam_s == 1:
            ok = ok and (qa, qb) == (qa_s, qb_s)
        if lam_s == 0:
            ok = ok and (qa, qb) == ratios(P, P["aa2"] * g, P["ab2"] * g, P["ab2"] * g)[2:]
        counts["C6"] += 1
        fails["C6"] += not ok
    # C7: branch combinations of (A.2)/(A.3) with z_A >= z_B (any F: only zeta values matter)
    za = lat(0, 30)
    zb = za - pick((Fr(0), za), lambda: lat(0, float(za)))
    aA, aB = P["aa1"], P["ab1"]
    sols = set()
    # A branch 1: yA = (aA+th aB) za - th yB if yB <= aB za ; branch 2: yA = aA za if yB > aB za
    # B branch 1: yB = (aB+th aA) zb - th yA if yA <= aA zb ; branch 2: yB = aB zb if yA > aA zb
    for ba in (1, 2):
        for bb in (1, 2):
            if ba == 1 and bb == 1:
                det = 1 - th * th
                if det == 0:          # theta = 1: both lines y_A + y_B = const; consistent only if constants agree
                    ca_, cb_ = (aA + aB) * za, (aB + aA) * zb
                    if ca_ != cb_:
                        continue
                    # a segment: points with yB <= aB za and yA <= aA zb on yA + yB = za (za = zb here)
                    # it contains the claimed point; any other point would need yA/aA, yB/aB both <= z, so equal
                    yA, yB = aA * za, aB * zb
                else:
                    yA = ((aA + th * aB) * za - th * (aB + th * aA) * zb) / det
                    yB = (aB + th * aA) * zb - th * yA
                if yB <= aB * za and yA <= aA * zb and yA >= 0 and yB >= 0:
                    sols.add((yA, yB))
            elif ba == 1 and bb == 2:
                yB = aB * zb
                yA = (aA + th * aB) * za - th * yB
                if yB <= aB * za and yA > aA * zb:
                    sols.add((yA, yB))
            elif ba == 2 and bb == 1:
                yA = aA * za
                yB = (aB + th * aA) * zb - th * yA
                if yB > aB * za and yA <= aA * zb:
                    sols.add((yA, yB))
            else:
                yA, yB = aA * za, aB * zb
                if yB > aB * za and yA > aA * zb:
                    sols.add((yA, yB))
    claimed = ((aA + th * aB) * za - th * aB * zb, aB * zb)
    counts["C7"] += 1
    fails["C7"] += not (sols == {claimed})
    # C8: Lemma 4 identity under the uniform law F^{-1}(q) = mu - sigma + 2 sigma q
    mu = lat(5, 20)
    sigma = mu * lat(0.01, 0.999)
    for qa_, qb_ in ((qa_s, qb_s), ratios(P, P["aa2"] * g, P["ab2"] * g, P["ab2"] * g)[2:],
                     (1 - P["ca"] / P["pa1"], 1 - P["cb"] / P["pb1"])):
        zA, zB = mu - sigma + 2 * sigma * qa_, mu - sigma + 2 * sigma * qb_
        yA, yB = (aA + th * aB) * zA - th * aB * zB, aB * zB
        lhs = yA / aA - yB / aB
        rhs = (aA + th * aB) * (zA - zB) / aA
        counts["C8"] += 1
        fails["C8"] += not (lhs == rhs and lhs >= 0 and ((lhs == 0) == (qa_ == qb_)))
    # C9: pathwise second-period identity
    a2, b2 = P["aa2"], P["ab2"]
    zA2, zB2 = mu - sigma + 2 * sigma * (1 - P["ca"] / P["pa2"]), mu - sigma + 2 * sigma * (1 - P["cb"] / P["pb2"])
    y0A, y0B = (a2 + th * b2) * zA2 - th * b2 * zB2, b2 * zB2
    for _ in range(3):
        X = mu - sigma + 2 * sigma * Fr(rng.randint(0, 1000), 1000)
        ZA, ZB = lat(0, 40), lat(0, 40)
        def sales(yA, yB, zA_, zB_):
            mA_, mB_ = a2 * X + zA_, b2 * X + zB_
            return min(mA_ + th * max(mB_ - yB, 0), yA), min(mB_ + th * max(mA_ - yA, 0), yB)
        RA, RB = sales(y0A + ZA, y0B + ZB, ZA, ZB)
        R0A, R0B = sales(y0A, y0B, 0, 0)
        piA = P["pa2"] * RA - P["ca"] * (y0A + ZA)
        piB = P["pb2"] * RB - P["cb"] * (y0B + ZB)
        counts["C9"] += 1
        fails["C9"] += not (piA == P["pa2"] * R0A - P["ca"] * y0A + (P["pa2"] - P["ca"]) * ZA
                            and piB == P["pb2"] * R0B - P["cb"] * y0B + (P["pb2"] - P["cb"]) * ZB)
    # C10: region a < b
    a_ = lat(0, 20)
    b_ = a_ + lat(0.001, 10)
    yA, yB = aA * a_, aB * b_
    w = (yB + th * yA) / (aB + th * aA)
    KA = mA * P["aa2"] * g
    FA, Fw = Fr(rng.randint(0, 999), 1000), None
    Fw = FA + (1 - FA) * Fr(rng.randint(1, 1000), 1000)     # any value with F(a) < F(w) <= 1
    lhs = (P["pa1"] + KA * (1 - th)) * FA + KA * th * Fw    # RHS of the first equation of (A.16)
    counts["C10"] += 1
    fails["C10"] += not (a_ < w <= b_ and lhs < (P["pa1"] + KA) * Fw)

# C3 second half: equivalence of the fractile ordering with the ratio ordering at points without A11
eq_fail = 0
for k in range(N):
    P = draw(a11=False)
    g = P["gamma"]
    oa, ob, qa, qb = ratios(P, P["aa2"] * g, P["ab2"] * g, P["ab2"] * g)
    c3_reverse += oa > ob
    eq_fail += ((qa >= qb) != (oa <= ob))
for key in fails:
    print(f"{key}: points {counts[key]}, failures {fails[key]}")
print(f"C1 points with A11 binding in both periods: {c1_equal}")
print(f"C3 equivalence q_A >= q_B <=> own_a <= own_b at {N} points without A11: failures {eq_fail}; "
      f"points with retailer B higher: {c3_reverse}")
