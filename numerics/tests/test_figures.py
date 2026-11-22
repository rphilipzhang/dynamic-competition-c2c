"""Figure 1 and Figure B.1: the code reproduces the numbers of the paper.

Three references are used.
  numerics/matlab/Figure2_MATLAB/Figure2_reference.csv   values the authors computed with MATLAB for Figure B.1
  numerics/figures/published_data.csv                    values read back from the published vector figures
  the text of the paper                                  qualitative statements about both figures

`published_data.csv` is produced by `numerics/figures/extract_published_data.py` from
the EPS files in `paper/`. `published_data_calibration.json` gives, for each
panel, a bound on the error of that extraction. Every comparison with a published
figure uses that bound as its tolerance, plus 1e-9 for floating-point slack.
"""
from __future__ import annotations

import json
import warnings

import numpy as np
import pandas as pd
import pytest

from c2c import figures as F

MATLAB_B1 = "numerics/matlab/Figure2_MATLAB/Figure2_reference.csv"

FIG1_FILES = {"a": "figure1.eps", "b": "figure2.eps", "c": "figure3.eps", "d": "figure4.eps"}
FIGB1_FILES = {"a": "yaG.eps", "b": "ybG.eps", "c": "piaG.eps", "d": "pibG.eps"}


@pytest.fixture(scope="module")
def published(repo_root):
    table = pd.read_csv(repo_root / "numerics/figures/published_data.csv", dtype={"figure": str})
    calib = json.loads((repo_root / "numerics/figures/published_data_calibration.json").read_text())["files"]
    return table, calib


@pytest.fixture(scope="module")
def fig1():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        data = F.figure1_data()
    return data, caught


@pytest.fixture(scope="module")
def figb1():
    return F.figureB1_data()


def _bound(calib, file):
    return calib[file]["y_axis"]["resolution"]["abs_error_bound_vs_plotted_double"]


def _series(table, figure, panel, label):
    sub = table[(table.figure == figure) & (table.panel == panel) & (table.series == label)].sort_values("theta")
    assert len(sub) == 11, f"expected 11 plotted points for Figure {figure}({panel}) {label}, found {len(sub)}"
    return sub.theta.to_numpy(), sub.value.to_numpy()


# ----------------------------------------------------------------------------- Figure B.1
@pytest.mark.claims("FB1")
def test_figure_b1_matches_the_authors_matlab_values(repo_root, figb1, record):
    """Figure B.1 against the authors' MATLAB output.
    Points: the 9 plotted series of Figure B.1 at the 11 values of theta 0, 0.1, ..., 1 and
    the parameters of its caption: 99 values.
    Computed: `c2c.figures.figureB1_data`, from `find_general_exo` of `c2c.closed_form`, and
    the table `numerics/matlab/Figure2_MATLAB/Figure2_reference.csv`. The number of values
    that agree digit for digit at 15 significant digits is recorded.
    Criterion: the two tables have the same columns, and the largest absolute difference is
    below 1e-10."""
    ref = pd.read_csv(repo_root / MATLAB_B1)
    assert list(ref.columns) == list(figb1.columns)
    diff = float((figb1 - ref).abs().to_numpy().max())
    lines = (repo_root / MATLAB_B1).read_text().strip().split("\n")[1:]
    same = sum(f"{figb1[col][i]:.15g}" == cell
               for i, line in enumerate(lines) for col, cell in zip(ref.columns[1:], line.split(",")[1:]))
    record("values_equal_digit_for_digit", same, stable=False)      # 99 of 99 on the build machine
    record("values_compared", int(ref.shape[0] * (ref.shape[1] - 1)))
    record("max_abs_difference", diff, stable=False)
    assert diff < 1e-10


@pytest.mark.claims("FB1")
@pytest.mark.parametrize("panel", list("abcd"))
def test_figure_b1_matches_the_published_figure(panel, published, figb1, record):
    """Figure B.1, one panel, against the published figure.
    Points: one panel of Figure B.1 (a, b, c or d) with its 2 plotted series (3 in panel b),
    11 values of theta each.
    Computed: the recomputed values of `figureB1_data`, and the values that
    `published_data.csv` reads back from the panel's EPS file.
    Criterion: each series has 11 plotted points whose theta agree with the recomputed grid
    within 1e-9, and the largest absolute difference is at most the panel's extraction error
    bound in `published_data_calibration.json` plus 1e-9."""
    table, calib = published
    bound = _bound(calib, FIGB1_FILES[panel])
    worst = 0.0
    for s in F.FIGB1_PANELS[panel][2]:
        theta, value = _series(table, "B.1", panel, f"Scenario {s}")
        assert np.allclose(theta, figb1.theta, atol=1e-9)
        worst = max(worst, float(np.abs(value - figb1[f"{panel}_{s}"]).max()))
    record("extraction_error_bound", bound)
    record("max_abs_difference", worst)
    assert worst <= bound + 1e-9


# ----------------------------------------------------------------------------- Figure 1
@pytest.mark.claims("F1")
@pytest.mark.parametrize("panel", list("abcd"))
def test_figure_1_matches_the_published_figure(panel, published, fig1, record):
    """Figure 1, one panel, against the published figure.
    Points: one panel of Figure 1 (a, b, c or d) with the series of Scenarios S and N, 11
    values of theta each (0.01, 0.1, ..., 0.9, 0.99).
    Computed: the equilibrium profits of `figure1_data`, from the two-price game that
    `c2c.pricing` solves, rounded to four decimals and unrounded, and the values that
    `published_data.csv` reads back from the panel's EPS file. The published panels were
    drawn from four-decimal data.
    Criterion: each series has 11 plotted points whose theta agree within 1e-9, the largest
    absolute difference to the four-decimal values is at most the panel's extraction error
    bound plus 1e-9, and to the unrounded values at most 5e-5 plus that bound plus 1e-9."""
    table, calib = published
    data = fig1[0]
    mine = data[data.panel == panel].sort_values("theta")
    bound = _bound(calib, FIG1_FILES[panel])
    worst_rounded = worst_raw = 0.0
    for label, col in (("Scenario S", "profit_S"), ("Scenario N", "profit_N")):
        theta, value = _series(table, "1", panel, label)
        assert np.allclose(theta, mine.theta, atol=1e-9)
        worst_rounded = max(worst_rounded, float(np.abs(value - mine[col].round(4)).max()))
        worst_raw = max(worst_raw, float(np.abs(value - mine[col]).max()))
    record("extraction_error_bound", bound)
    record("max_abs_difference_to_four_decimal_values", worst_rounded)
    record("max_abs_difference_to_unrounded_values", worst_raw)
    assert worst_rounded <= bound + 1e-9
    assert worst_raw <= 5e-5 + bound + 1e-9


@pytest.mark.claims("F1")
def test_figure_1_equilibria_are_unique_and_the_continuation_is_constant(fig1, record):
    """Figure 1: the two-price game that the figure plots has one equilibrium at every point.
    Points: the 44 parameter points of Figure 1 (4 panels, 11 values of theta), Scenarios S
    and N.
    Computed: `figure1_data`, which runs `pricing.pricing_equilibrium` at every point and
    scenario. The solver raises unless exactly one second-period price pair is an equilibrium
    at every feasible sales state, `figure1_point` raises unless there is exactly one
    first-period pure equilibrium, and the solver warns if another price pair is an
    equilibrium at some sales state.
    Criterion: the table has all 44 rows, and no warning was issued."""
    data, caught = fig1
    assert len(data) == 44                      # figure1_point raises if an equilibrium is not unique
    assert not caught, [str(w.message) for w in caught]
    record("parameter_points", 44)


# ----------------------------------------------------------------------------- statements in the text
@pytest.mark.claims("N1")
def test_split_ratios_are_constant_over_time_in_figure_1(fig1, record):
    """Section 5.3: equilibrium prices may differ across the two periods, but
    the market split is the same in both periods at every plotted point.
    Points: the 44 parameter points of Figure 1, Scenarios S and N.
    Computed: the shares alpha_{A,t} = 1/2 + beta (p_{B,t} - p_{A,t}) at the equilibrium
    prices of `figure1_data` in both periods, and the number of pairs of point and scenario
    at which a price changes between the periods.
    Criterion: the two shares are exactly equal at every point and scenario, and a price
    changes between the periods at one pair or more."""
    data, _ = fig1
    beta = F.FIG1_PARAMS["beta"]
    differs = 0
    for s in ("S", "N"):
        a1 = 0.5 + beta * (data[f"pb1_{s}"] - data[f"pa1_{s}"])
        a2 = 0.5 + beta * (data[f"pb2_{s}"] - data[f"pa2_{s}"])
        assert np.array_equal(a1.to_numpy(), a2.to_numpy())
        differs += int(((data[f"pa1_{s}"] != data[f"pa2_{s}"]) | (data[f"pb1_{s}"] != data[f"pb2_{s}"])).sum())
    record("points_where_prices_change_between_periods", differs)
    assert differs > 0                          # "the equilibrium prices across the two periods may not be the same"


def _gap(data, panel):
    d = data[data.panel == panel].sort_values("theta")
    return d.theta.to_numpy(), (d.profit_N - d.profit_S).to_numpy()


@pytest.mark.claims("N2")
def test_moderate_gamma_panels_show_one_profit_crossing(fig1, record):
    """Section 5.3, Figure 1(a) and (c), gamma = 0.7. Retailer A: Scenario N
    becomes more profitable than Scenario S as theta increases to 1. Retailer
    B: Scenario S yields the higher profit when theta is small.
    Points: panels (a) and (c) of Figure 1 (c_A = 0.10 and 0.95), 11 values of theta.
    Computed: the gap Pi^N - Pi^S of the plotted retailer from `figure1_data`, and the
    crossings of `figure1_crossings`, located by Brent's method between neighbouring
    values of theta at which the gap changes sign.
    Criterion: in each panel the gap is negative at theta = 0.01 and positive at 0.99, its
    sign changes between exactly one pair of neighbouring values, and `figure1_crossings`
    returns exactly one crossing."""
    data, _ = fig1
    crossings = F.figure1_crossings()
    for panel in ("a", "c"):
        theta, gap = _gap(data, panel)
        assert gap[0] < 0 and gap[-1] > 0                  # S above N at small theta, N above S near 1
        assert np.sum(np.diff(np.sign(gap)) != 0) == 1     # a single change of sign on the plotted grid
        assert len(crossings[panel]) == 1
        record(f"crossing_theta_panel_{panel}", round(crossings[panel][0], 9))


@pytest.mark.claims("N3", "N4")
def test_strong_gamma_panels_show_no_crossing(fig1, record):
    """Section 5.3, Figure 1(b) and (d), gamma = 2. Each retailer earns more in
    Scenario N at every theta, with equal market shares in the two periods.
    Points: panels (b) and (d) of Figure 1 (c_A = 0.10 and 0.95), 11 values of theta.
    Computed: the gap Pi^N - Pi^S of the plotted retailer from `figure1_data`, and the
    crossings of `figure1_crossings`. The equal shares are checked by the N1 check above.
    Criterion: the gap is positive at all 11 values in both panels, and `figure1_crossings`
    returns no crossing for either panel."""
    data, _ = fig1
    for panel in ("b", "d"):
        _, gap = _gap(data, panel)
        assert np.all(gap > 0)
        record(f"min_profit_advantage_of_N_panel_{panel}", float(gap.min()))
    assert F.figure1_crossings()["b"] == [] and F.figure1_crossings()["d"] == []


@pytest.mark.claims("N5")
def test_figure_b1_patterns_described_in_appendix_b(figb1, record):
    """Online Appendix B. Panel (b): retailer B's order quantity in Scenario GN
    decreases in theta. Panels (a), (c), (d): the comparisons of Propositions
    1, 5 and 6 carry over, each with a single crossing in theta.
    Points: the 11 values of theta 0, 0.1, ..., 1 of Figure B.1, all four panels.
    Computed: the series of `figureB1_data`: y_{B,1} in Scenarios GN, GS and 0 for panel
    (b), and the gaps GS - GN of panels (a), (c) and (d).
    Criterion: b_GN falls at every step, the range of b_GS is below 0.05 and that of b_0 is
    exactly 0, and each of the three gaps is positive at theta = 0, negative at theta = 1 and
    changes sign between exactly one pair of neighbouring values."""
    assert np.all(np.diff(figb1.b_GN) < 0)                           # free-riding of retailer B
    assert np.ptp(figb1.b_GS) < 0.05 and np.ptp(figb1.b_0) == 0      # GS almost flat, benchmark flat
    for panel, first in (("a", +1), ("c", +1), ("d", +1)):           # GS above GN first, then below
        gap = (figb1[f"{panel}_GS"] - figb1[f"{panel}_GN"]).to_numpy()
        assert np.sign(gap[0]) == first and np.sign(gap[-1]) == -first
        assert np.sum(np.diff(np.sign(gap)) != 0) == 1
        k = int(np.nonzero(np.diff(np.sign(gap)) != 0)[0][0])
        record(f"crossing_between_theta_panel_{panel}", f"{figb1.theta[k]:.1f} and {figb1.theta[k + 1]:.1f}")


@pytest.mark.supports("F1", "FB1")
def test_published_data_match_a_fresh_extraction_from_the_eps_files(repo_root, tmp_path, record):
    """Points: the 8 EPS panels of Figure 1 and Figure B.1 in `paper/`.
    Computed: `numerics/figures/extract_published_data.py` reads every plotted vertex
    back from the vector graphics into a temporary folder.
    Criterion: the fresh extraction equals the committed `published_data.csv` and
    `published_data_calibration.json` byte for byte, so that every comparison with a
    published figure in this file uses data that the EPS files reproduce."""
    import subprocess
    import sys
    run = subprocess.run([sys.executable, str(repo_root / "numerics/figures/extract_published_data.py"),
                          "--out-dir", str(tmp_path)], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout[-2000:] + run.stderr[-2000:]
    for name in ("published_data.csv", "published_data_calibration.json"):
        assert (tmp_path / name).read_bytes() == (repo_root / "numerics/figures" / name).read_bytes(), name
    rows = (tmp_path / "published_data.csv").read_text().count("\n") - 1
    record("panels", 8)
    record("plotted_points", rows)


@pytest.mark.supports("F1", "FB1", "N1", "N2", "N3", "N4", "N5", "N6")
def test_numerical_statements_are_quoted_from_the_paper(repo_root, record):
    """Points: the nine entries of `numerics/numerical_statements.yaml`, including N7,
    which the repository lists and does not check.
    Computed: each quote, against the LaTeX source of the paper with every \\ref
    printed as the number that `numerics/paper_labels.json` gives.
    Criterion: every quote occurs verbatim, up to whitespace, so that the checks of
    this file test the paper's own sentences, and exactly N7 carries a field `excluded`."""
    import json
    import re
    import yaml
    from c2c import paper
    tables = json.loads((repo_root / "numerics/paper_labels.json").read_text(encoding="utf-8")).values()
    printed = {label: entry["number"] for table in tables for label, entry in table.items()}
    text = re.sub(r"\\ref\{([^}]*)\}", lambda m: printed[m.group(1)], paper.text())
    entries = yaml.safe_load((repo_root / "numerics/numerical_statements.yaml").read_text(encoding="utf-8"))
    for entry in entries:
        assert " ".join(entry["quote"].split()) in text, f"{entry['id']}: not found in the paper: {entry['quote']}"
    assert [e["id"] for e in entries] == ["F1", "FB1", "N1", "N2", "N3", "N4", "N5", "N6", "N7"]
    assert [e["id"] for e in entries if e.get("excluded")] == ["N7"]
    record("statements_quoted", len(entries))
