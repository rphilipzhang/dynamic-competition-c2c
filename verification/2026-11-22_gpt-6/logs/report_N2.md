# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k N2 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

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
| [N1](#n1) | – | 1/1 |
| [N2](#n2) | 1/1 | 1/1 |
| [N3](#n3) | – | 1/1 |
| [N4](#n4) | – | 1/1 |
| [N5](#n5) | – | 1/1 |
| [N6](#n6) | – | 1/1 |

## Checks by ID

### F1

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

### FB1

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

### N1

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

### N2

- direct: [test_moderate_gamma_panels_show_one_profit_crossing](#check-1): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

### N3

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

### N4

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

### N5

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

### N6

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

## Checks

<a id="check-1"></a>
### `tests/test_figures.py::test_moderate_gamma_panels_show_one_profit_crossing`

- **Outcome:** passed (0.0 s)
- **Tests directly:** N2
- **What:** Section 5.3, Figure 1(a) and (c), gamma = 0.7. Retailer A: Scenario N becomes more profitable than Scenario S as theta increases to 1. Retailer B: Scenario S yields the higher profit when theta is small.
- **Points:** panels (a) and (c) of Figure 1 (c_A = 0.10 and 0.95), 11 values of theta.
- **Computed:** the gap Pi^N - Pi^S of the plotted retailer from `figure1_data`, and the crossings of `figure1_crossings`, located by Brent's method between neighbouring values of theta at which the gap changes sign.
- **Criterion:** in each panel the gap is negative at theta = 0.01 and positive at 0.99, its sign changes between exactly one pair of neighbouring values, and `figure1_crossings` returns exactly one crossing.
- **Recorded:** crossing theta panel a = 0.769736; crossing theta panel c = 0.579998

<a id="check-2"></a>
### `tests/test_figures.py::test_numerical_statements_are_quoted_from_the_paper`

- **Outcome:** passed (0.0 s)
- **Supports:** F1, FB1, N1, N2, N3, N4, N5, N6
- **Points:** the nine entries of `numerics/numerical_statements.yaml`, including N7, which the repository lists and does not check.
- **Computed:** each quote, against the LaTeX source of the paper with every \ref printed as the number that `numerics/paper_labels.json` gives.
- **Criterion:** every quote occurs verbatim, up to whitespace, so that the checks of this file test the paper's own sentences, and exactly N7 carries a field `excluded`.
- **Recorded:** statements quoted = 9
