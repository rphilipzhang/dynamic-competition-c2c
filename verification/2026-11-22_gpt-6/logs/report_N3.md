# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k N3 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

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
| [N2](#n2) | – | 1/1 |
| [N3](#n3) | 1/1 | 1/1 |
| [N4](#n4) | 1/1 | 1/1 |
| [N5](#n5) | – | 1/1 |
| [N6](#n6) | – | 1/1 |

## Checks by ID

### F1

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### FB1

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### N1

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### N2

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### N3

- direct: [test_strong_gamma_panels_show_no_crossing](#check-2): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### N4

- direct: [test_strong_gamma_panels_show_no_crossing](#check-2): passed
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
### `tests/test_figures.py::test_strong_gamma_panels_show_no_crossing`

- **Outcome:** passed (0.1 s)
- **Tests directly:** N3, N4
- **What:** Section 5.3, Figure 1(b) and (d), gamma = 2. Each retailer earns more in Scenario N at every theta, with equal market shares in the two periods.
- **Points:** panels (b) and (d) of Figure 1 (c_A = 0.10 and 0.95), 11 values of theta.
- **Computed:** the gap Pi^N - Pi^S of the plotted retailer from `figure1_data`, and the crossings of `figure1_crossings`. The equal shares are checked by the N1 check above.
- **Criterion:** the gap is positive at all 11 values in both panels, and `figure1_crossings` returns no crossing for either panel.
- **Recorded:** min profit advantage of N panel b = 9.77993; min profit advantage of N panel d = 9.90863
