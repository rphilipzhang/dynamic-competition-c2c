# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k N1 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**2 of 2 checks passed.** pytest exit status: 0.

A *direct* check tests a part of the result itself. A *supporting* check confirms a tool that direct checks rely on, for example that a closed form equals the model at random points. Every check computes at finitely many points. For a result that holds for all parameters it is a search for counterexamples. For a result that holds for a parameter large enough it probes large values of that parameter.

## Results of theory.md

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [L1](#l1) | – | – |
| [L2](#l2) | – | – |
| [L3](#l3) | – | – |
| [L4](#l4) | – | – |
| [P1](#p1) | – | – |
| [P2](#p2) | – | – |
| [P3](#p3) | – | – |
| [P4](#p4) | – | – |
| [P5](#p5) | – | – |
| [P6](#p6) | – | – |
| [LA1](#la1) | – | – |
| [LA2](#la2) | – | – |
| [P7](#p7) | – | – |
| [P8](#p8) | – | – |
| [P9](#p9) | – | – |
| [LB1](#lb1) | – | – |

## Numerical statements of the paper

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [F1](#f1) | – | 1/1 |
| [FB1](#fb1) | – | 1/1 |
| [N1](#n1) | 1/1 | 1/1 |
| [N2](#n2) | – | 1/1 |
| [N3](#n3) | – | 1/1 |
| [N4](#n4) | – | 1/1 |
| [N5](#n5) | – | 1/1 |
| [N6](#n6) | – | 1/1 |

## Checks by ID

### F1

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### FB1

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### N1

- direct: [test_split_ratios_are_constant_over_time_in_figure_1](#check-2): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### N2

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### N3

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### N4

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### N5

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### N6

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
