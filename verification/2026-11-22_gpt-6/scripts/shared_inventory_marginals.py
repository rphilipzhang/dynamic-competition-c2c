"""Run from the repository root. Exact marginal-payoff checks from substitution events."""

from fractions import Fraction as Q
from itertools import product
from random import Random


def cdf(x, law):
    if law == "uniform":
        return min(Q(1), max(Q(0), (x - 2) / 5))
    x = max(Q(0), x - 2)
    return x / (1 + x)


def quantile(tail, law):
    assert 0 < tail < 1
    return 2 + (5 * (1 - tail) if law == "uniform" else 1 / tail - 1)


def marginal(yi, yj, a, p, c, own, cross, theta, law):
    # D_i(x) reaches yi either before j stocks out, or after substitution starts.
    b = 1 - a
    own_cut = min(yi / a, (yi + theta * yj) / (a + theta * b))
    rival_cut = (yj + theta * yi) / (b + theta * a)
    diversion = theta * max(Q(0), cdf(rival_cut, law) - cdf(yi / a, law))
    return (p + own) * (1 - cdf(own_cut, law)) - c - cross * diversion


def audit(market, scenario, theta, gamma, rho, weight, law):
    ca, cb, pa, pb, pa2, pb2, beta = market
    a = Q(1, 2) + beta * (pb - pa)
    a2 = Q(1, 2) + beta * (pb2 - pa2)
    if scenario == "0":
        gamma = Q(0)
    own, cross = [], []
    for share, cost, price2 in [(a2, ca, pa2), (1 - a2, cb, pb2)]:
        w = {"0": Q(1), "S": Q(1), "N": Q(0), "G": weight}[scenario]
        value = gamma * rho * (price2 - cost)
        own.append(value * (w + (1 - w) * share))
        cross.append(value * (1 - w) * share)
    ta = ca / (pa + own[0])
    tb = (cb - theta * cross[1] * ta) / (pb + own[1] - theta * cross[1])
    za, zb = quantile(ta, law), quantile(tb, law)
    ya, yb = a * za + theta * (1 - a) * (za - zb), (1 - a) * zb
    assert ya / a >= yb / (1 - a) and 0 < ta <= tb < 1
    if scenario == "N":
        assert ya / a > yb / (1 - a)
    for yi, yj, share, price, cost, u, v in [
        (ya, yb, a, pa, ca, own[0], cross[0]),
        (yb, ya, 1 - a, pb, cb, own[1], cross[1]),
    ]:
        for multiplier, expected in [(Q(9999, 10000), 1), (Q(1), 0), (Q(10001, 10000), -1)]:
            d = marginal(yi * multiplier, yj, share, price, cost, u, v, theta, law)
            assert (d > 0) - (d < 0) == expected, (market, scenario, d, expected)
    return min(1 - ta, 1 - tb), max(1 - ta, 1 - tb)


def markets():
    rng = Random(221106)
    for _ in range(32):
        ca = Q(rng.randint(1, 19), 10)
        cb = ca + Q(rng.randint(1, 15), 10)
        pb, pb2 = [cb + Q(rng.randint(1, 80), 10) for _ in range(2)]
        pa, pa2 = [p * ca / cb + Q(rng.randint(0, 8), 8) * p * (1 - ca / cb) for p in (pb, pb2)]
        beta = Q(1, 50)
        yield ca, cb, pa, pb, pa2, pb2, beta
    # Lower A11 equality in both periods, equal retail prices, near-zero fractiles.
    yield tuple(map(Q, (1, 2, 3, 6, 3, 6))) + (Q(1, 12),)
    yield tuple(map(Q, (1, 2, 6, 6, 6, 6))) + (Q(1, 20),)
    eps = Q(1, 10**10)
    yield Q(1), Q(2), 1 + eps, 2 + 2 * eps, 1 + eps, 2 + 2 * eps, Q(1, 20)


if __name__ == "__main__":
    smallest, largest, count = Q(1), Q(0), 0
    for market, theta, gamma, law in product(
        markets(), [Q(0), Q(7, 19), Q(1)], [Q(1, 10**8), Q(7, 3), Q(10**8)], ["uniform", "shifted Lomax"]
    ):
        for scenario, rho, weight in [
            ("0", Q(1), Q(1)), ("S", Q(1), Q(1)), ("S", Q(1, 11), Q(1)),
            ("N", Q(1), Q(0)), ("N", Q(1, 11), Q(0)),
            ("G", Q(1), Q(0)), ("G", Q(1), Q(1, 3)), ("G", Q(1), Q(1)),
        ]:
            lo, hi = audit(market, scenario, theta, gamma, rho, weight, law)
            smallest, largest, count = min(smallest, lo), max(largest, hi), count + 1
    print(f"{count} first-period parameter/law/scenario cases; {6 * count} unilateral marginal checks")
    print(f"minimum CDF fractile {float(smallest):.12g}; maximum {float(largest):.12g}")
