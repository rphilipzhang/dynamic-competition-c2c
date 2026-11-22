"""Exact rational checks of two formulas used in the proof of Lemmas A.1 and A.2."""

from fractions import Fraction as F
from itertools import product


def realized_sales(x, a, b, theta, ya, yb):
    ra = min(ya, a * x + theta * max(b * x - yb, 0))
    rb = min(yb, b * x + theta * max(a * x - ya, 0))
    total = min(x, ya + yb, (a + theta * b) * x + (1 - theta) * yb,
                (b + theta * a) * x + (1 - theta) * ya)
    assert ra + rb == total
    return ra, rb


def integrate_sales(low, high, a, b, theta, ya, yb):
    switches = (low, high, ya / a, yb / b,
                (ya + theta * yb) / (a + theta * b),
                (yb + theta * ya) / (b + theta * a))
    nodes = sorted({x for x in switches if low <= x <= high})
    values = [realized_sales(x, a, b, theta, ya, yb) for x in nodes]
    return tuple(sum((right - left) * (vi[i] + vj[i]) / (2 * (high - low))
                     for left, right, vi, vj in zip(nodes, nodes[1:], values, values[1:]))
                 for i in (0, 1))


low, high, mu = F(6), F(14), F(10)
width = high - low
ca, cb, beta = F(3, 2), F(2), F(1, 6)
prices = [F(14 + j, 4) for j in range(11)]
rates = [F(0), F(1, 3), F(2, 3), F(999, 1000), F(1)]
static_pairs = tie_pairs = stock_pairs = 0
for pa, pb, theta in product(prices, prices, rates):
    a = F(1, 2) + beta * (pb - pa)
    b = 1 - a
    za, zb = high - width * ca / pa, high - width * cb / pb
    ya = a * za + theta * b * max(za - zb, 0)
    yb = b * zb + theta * a * max(zb - za, 0)
    era, erb = integrate_sales(low, high, a, b, theta, ya, yb)
    for p, c, share, z, other_z, er, y in (
            (pa, ca, a, za, zb, era, ya), (pb, cb, b, zb, za, erb, yb)):
        base = share * (p * mu - c * high + width * c**2 / (2 * p))
        spill = theta * (1 - share) * p * max(z - other_z, 0)**2 / (2 * width)
        assert p * er - c * y == base + spill
    static_pairs += 1
    tie_pairs += za == zb

    # Equilibrium-shaped stocks need only satisfy low <= s <= z <= high
    # for the exact sales integrals used in the fixed-theta profit expansion.
    for s, z in ((low, high), (F(8), F(9)), (F(13), F(27, 2)), (F(12), F(12))):
        h = a + theta * b
        ya = h * z - theta * b * s
        yb = b * s
        era, erb = integrate_sales(low, high, a, b, theta, ya, yb)
        tail_s, tail_z = (high - s)**2 / (2 * width), (high - z)**2 / (2 * width)
        assert erb == b * (mu - tail_s)
        assert era == a * mu + theta * b * tail_s - h * tail_z
        assert era + erb == mu - (1 - theta) * b * tail_s - h * tail_z
        stock_pairs += 1

print(f"Static payoff pairs: {static_pairs}, including {tie_pairs} fractile ties.")
print(f"Ordered first-period stock pairs and exact sales integrals: {stock_pairs}.")
