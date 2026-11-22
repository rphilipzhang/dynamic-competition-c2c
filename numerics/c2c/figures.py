"""Numbers behind the paper's two figures.

    Figure 1    (Section 5.3)         port of `numerics/matlab/Figure1_MATLAB/Figure1_reproduce.m`
    Figure B.1  (Online Appendix B)   port of `numerics/matlab/Figure2_MATLAB/Exoprice2_Figure2.m`

Figure B.1 is the figure that earlier drafts and the MATLAB code call
"Figure 2". The functions return plain data. Plotting is kept separate in
`numerics/figures/make_figures.py`, because the tests compare numbers, not images.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize

from . import closed_form as cf
from .pricing import pricing_equilibrium

__all__ = ["matlab_colon", "FIG1_PARAMS", "FIG1_PANELS", "FIG1_THETA", "figure1_point", "figure1_data", "figure1_crossings",
           "FIGB1_PARAMS", "FIGB1_SCENARIOS", "FIGB1_PANELS", "FIGB1_THETA", "figureB1_data"]

def matlab_colon(first, step, last):
    """The vector first:step:last as MATLAB builds it.

    MATLAB fills the first half of the vector from the left end
    (first + k step) and the second half from the right end (last - k step).
    The result can differ from a decimal grid in the last bit: 0:0.1:1 has
    3 * 0.1 = 0.30000000000000004 as its fourth element. The grids of both
    figures are built this way so that the port evaluates exactly the points
    that the authors' code evaluates.
    """
    n = int(np.floor((last - first) / step + 1e-10))
    half = n // 2
    return np.array([first + k * step if k <= half else last - (n - k) * step for k in range(n + 1)])


# ----------------------------------------------------------------------------- Figure 1
# Caption: p_{i,t} in {2, 4}, c_B = 1, beta = 0.1, X_t ~ U[5, 15].
FIG1_PARAMS = dict(prices=(2.0, 4.0), cb=1.0, beta=0.1, mu=10.0, sigma=5.0)
# panel: (retailer whose profit is plotted, c_A, gamma)
FIG1_PANELS = {"a": ("A", 0.10, 0.7), "b": ("A", 0.10, 2.0), "c": ("B", 0.95, 0.7), "d": ("B", 0.95, 2.0)}
FIG1_THETA = np.array([0.01, *matlab_colon(0.1, 0.1, 0.9), 0.99])        # MATLAB: [0.01, 0.1:0.1:0.9, 0.99]


def figure1_point(theta, ca, gamma):
    """Equilibrium of the two-price game at one parameter point, in both scenarios.

    Returns {scenario: {"prices": (pa1, pb1, pa2, pb2), "profits": (Pi_A, Pi_B)}}.
    Raises if a scenario does not have exactly one first-period pure equilibrium,
    as the MATLAB code does.
    """
    p = FIG1_PARAMS
    out = {}
    for scenario in ("S", "N"):
        res = pricing_equilibrium(scenario, p["prices"], theta, ca, p["cb"], p["beta"], p["mu"], p["sigma"], gamma)
        if res["total_profits"].shape[0] != 1:
            raise RuntimeError(
                f"The panel requires one pure first-period equilibrium in each scenario at theta={theta:g}.")
        out[scenario] = {"prices": (*res["period1_prices"][0], *res["period2_prices"]),
                         "profits": tuple(res["total_profits"][0])}
    return out


def figure1_data(theta=FIG1_THETA) -> pd.DataFrame:
    """One row per panel and theta: the plotted profits and the equilibrium prices."""
    rows = []
    for panel, (retailer, ca, gamma) in FIG1_PANELS.items():
        k = "AB".index(retailer)
        for th in theta:
            pt = figure1_point(float(th), ca, gamma)
            row = {"panel": panel, "retailer": retailer, "ca": ca, "gamma": gamma, "theta": float(th),
                   "profit_S": pt["S"]["profits"][k], "profit_N": pt["N"]["profits"][k]}
            for s in ("S", "N"):
                for name, val in zip(("pa1", "pb1", "pa2", "pb2"), pt[s]["prices"]):
                    row[f"{name}_{s}"] = val
            rows.append(row)
    return pd.DataFrame(rows)


def figure1_crossings(theta=FIG1_THETA) -> dict[str, list[float]]:
    """Values of theta at which the two plotted profits are equal, per panel.

    As in the MATLAB code, a root is searched between consecutive plotted
    nodes whenever the profit difference changes sign there.
    """
    out = {}
    for panel, (retailer, ca, gamma) in FIG1_PANELS.items():
        k = "AB".index(retailer)

        def gap(th, ca=ca, gamma=gamma, k=k):
            pt = figure1_point(float(th), ca, gamma)
            return pt["N"]["profits"][k] - pt["S"]["profits"][k]

        g = np.array([gap(th) for th in theta])
        roots = [float(th) for th, v in zip(theta, g) if v == 0]
        for j in np.nonzero(g[:-1] * g[1:] < 0)[0]:
            roots.append(float(optimize.brentq(gap, theta[j], theta[j + 1], xtol=1e-14, rtol=1e-14)))
        out[panel] = sorted(roots)
    return out


# ----------------------------------------------------------------------------- Figure B.1
# Caption: p_{i,t} = 2, c_B = 1, beta = 0.1, X_t ~ U[5, 15]. GS: gamma = 2, weights (0.8, 0.2).
# GN: gamma = 2, weights (0.2, 0.8). Benchmark 0: gamma = 0.
FIGB1_PARAMS = dict(pa1=2.0, pb1=2.0, pa2=2.0, pb2=2.0, cb=1.0, beta=0.1, mu=10.0, sigma=5.0)
FIGB1_SCENARIOS = {"GS": (2.0, 0.8, 0.2), "GN": (2.0, 0.2, 0.8), "0": (0.0, 0.8, 0.2)}   # gamma, lam_s, lam_n
# panel: (quantity plotted, c_A, scenarios shown). The quantity indexes the output of find_general_exo.
FIGB1_PANELS = {"a": ("ya1", 0.50, ("GS", "GN")), "b": ("yb1", 0.50, ("GS", "GN", "0")),
                "c": ("profit_a", 0.10, ("GS", "GN")), "d": ("profit_b", 0.92, ("GS", "GN"))}
FIGB1_THETA = matlab_colon(0.0, 0.1, 1.0)                                # MATLAB: (0:0.1:1)
_QUANTITY = {"ya1": 0, "yb1": 1, "profit_a": 2, "profit_b": 3}


def figureB1_data(theta=FIGB1_THETA) -> pd.DataFrame:
    """Wide table with the columns of the authors' reference file:
    theta, a_GS, a_GN, b_GS, b_GN, b_0, c_GS, c_GN, d_GS, d_GN."""
    p = FIGB1_PARAMS
    table = {"theta": [float(t) for t in theta]}
    for panel, (quantity, ca, scenarios) in FIGB1_PANELS.items():
        for s in scenarios:
            gamma, lam_s, lam_n = FIGB1_SCENARIOS[s]
            table[f"{panel}_{s}"] = [
                cf.find_general_exo(p["pa1"], p["pb1"], p["pa2"], p["pb2"], float(t), ca, p["cb"], p["beta"],
                                    p["mu"], p["sigma"], gamma, lam_s, lam_n)[_QUANTITY[quantity]]
                for t in theta]
    return pd.DataFrame(table)
