#!/usr/bin/env python3
"""Recompute the numbers behind Figure 1 and Figure B.1 and redraw both figures.

    python numerics/figures/make_figures.py            # writes reproduced/*.csv and reproduced/*.pdf
    python numerics/figures/make_figures.py --no-plot  # numbers only

Outputs
    reproduced/figure1.csv             one row per panel and theta (profits and equilibrium prices)
    reproduced/figure1_crossings.csv   theta at which the two profit curves of a panel cross
    reproduced/figureB1.csv            same layout as numerics/matlab/Figure2_MATLAB/Figure2_reference.csv
    reproduced/figure1.pdf, reproduced/figureB1.pdf
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "numerics"))

import pandas as pd  # noqa: E402

from c2c import figures as F  # noqa: E402

OUT = ROOT / "numerics" / "figures" / "reproduced"


def plot_figure1(data: pd.DataFrame, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(10, 7.2))
    for ax, (panel, (retailer, ca, gamma)) in zip(axes.ravel(), F.FIG1_PANELS.items()):
        d = data[data.panel == panel]
        ax.plot(d.theta, d.profit_S, "r--", lw=1.4, label="Scenario S")
        ax.plot(d.theta, d.profit_N, "b-", lw=1.4, label="Scenario N")
        ax.set_xlim(0, 1)
        ax.set_xlabel(r"Substitution rate $\theta$")
        ax.set_ylabel(f"Retailer {retailer} profit")
        ax.set_title(rf"({panel}) Retailer {retailer}, $\gamma$ = {gamma:g}, $c_A$ = {ca:g}")
        ax.legend(loc="best", frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_figure_b1(data: pd.DataFrame, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    styles = {"GS": ("r--", "Scenario GS"), "GN": ("b-", "Scenario GN"), "0": ("k-.", "Scenario 0")}
    ylabel = {"ya1": "First-period order quantity", "yb1": "First-period order quantity",
              "profit_a": "Two-period expected profit", "profit_b": "Two-period expected profit"}
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.2))
    for ax, (panel, (quantity, ca, scenarios)) in zip(axes.ravel(), F.FIGB1_PANELS.items()):
        for s in scenarios:
            ax.plot(data.theta, data[f"{panel}_{s}"], styles[s][0], lw=1.7, label=styles[s][1])
        ax.set_xlim(0, 1)
        ax.set_xlabel(r"Substitution rate $\theta$")
        ax.set_ylabel(ylabel[quantity])
        ax.set_title(rf"({panel}) Retailer {'A' if quantity.endswith('a') or quantity == 'ya1' else 'B'}, $c_A$ = {ca:g}")
        ax.legend(loc="best", frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    fig1 = F.figure1_data()
    fig1.to_csv(OUT / "figure1.csv", index=False, float_format="%.15g")
    crossings = F.figure1_crossings()
    pd.DataFrame([{"panel": p, "theta_crossing": t} for p, ts in crossings.items() for t in ts]).to_csv(
        OUT / "figure1_crossings.csv", index=False, float_format="%.12g")
    figb1 = F.figureB1_data()
    figb1.to_csv(OUT / "figureB1.csv", index=False, float_format="%.15g")
    for panel, ts in crossings.items():
        retailer, ca, gamma = F.FIG1_PANELS[panel]
        where = ("the two profits cross at theta = " + ", ".join(f"{t:.9f}" for t in ts) if ts
                 else "the two profits do not cross on the plotted grid")
        print(f"Figure 1({panel}) Retailer {retailer}, gamma = {gamma:g}: {where}")
    if not args.no_plot:
        plot_figure1(fig1, OUT / "figure1.pdf")
        plot_figure_b1(figb1, OUT / "figureB1.pdf")
    print(f"wrote {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
