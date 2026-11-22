# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k N1 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**2 of 2 checks passed.** pytest exit status: 0.

A *direct* check tests a part of the result itself. A *supporting* check confirms a tool that direct checks rely on, for example that a closed form equals the model at random points. Every check computes at finitely many points. For a result that holds for all parameters it is a search for counterexamples. For a result that holds for a parameter large enough it probes large values of that parameter.

The selection counts only N1. Other IDs that the selected checks name appear only in the description of each check below.

## Numerical statements of the paper

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [N1](#n1) | 1/1 | 1/1 |

## Checks by ID

### N1

- direct: [test_split_ratios_are_constant_over_time_in_figure_1](#check-2): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

## Checks

<a id="check-1"></a>
### `tests/test_figures.py::test_numerical_statements_are_quoted_from_the_paper`

- **Outcome:** passed (0.0 s)
- **Supports:** F1, FB1, N1, N2, N3, N4, N5, N6
- **Points:** the nine entries of `numerics/numerical_statements.yaml`, including N7, which the repository lists and does not check.
- **Computed:** each quote, against the LaTeX source of the paper with every \ref printed as the number that `numerics/paper_labels.json` gives.
- **Criterion:** every quote occurs verbatim, up to whitespace, so that the checks of this file test the paper's own sentences, and exactly N7 carries a field `excluded`.
- **Recorded:** statements quoted = 9

<a id="check-2"></a>
### `tests/test_figures.py::test_split_ratios_are_constant_over_time_in_figure_1`

- **Outcome:** passed (0.0 s)
- **Tests directly:** N1
- **What:** Section 5.3: equilibrium prices may differ across the two periods, but the market split is the same in both periods at every plotted point.
- **Points:** the 44 parameter points of Figure 1, Scenarios S and N.
- **Computed:** the shares alpha_{A,t} = 1/2 + beta (p_{B,t} - p_{A,t}) at the equilibrium prices of `figure1_data` in both periods, and the number of pairs of point and scenario at which a price changes between the periods.
- **Criterion:** the two shares are exactly equal at every point and scenario, and a price changes between the periods at one pair or more.
- **Recorded:** points where prices change between periods = 22
