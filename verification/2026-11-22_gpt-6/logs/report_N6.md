# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k N6 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**3 of 3 checks passed.** pytest exit status: 0.

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
| [N3](#n3) | – | 1/1 |
| [N4](#n4) | – | 1/1 |
| [N5](#n5) | – | 1/1 |
| [N6](#n6) | 2/2 | 1/1 |

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

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### N4

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### N5

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-1): passed

### N6

- direct: [test_large_gamma_patterns_under_other_distributions](#check-2): passed
- direct: [test_order_quantities_and_sales_patterns_under_other_distributions](#check-3): passed
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
### `tests/test_other_distributions.py::test_large_gamma_patterns_under_other_distributions`

- **Outcome:** passed (0.0 s)
- **Tests directly:** N6
- **What:** Weak forms of the parts of Propositions 1 and 3 to 6 that the paper states for gamma large.
- **Points:** the 48 points and 41 values of theta of the previous check, gamma = 1e3, 1e4, 1e8.
- **Computed:** orders and expected sales as there, and two-period profits from the payoffs of `section4.Game`. The number of points at which E[R^N_1] visibly falls and then rises is recorded.
- **Criterion:** at gamma = 1e3 and 1e4, y^S_A - y^N_A and E[R^S_A] - E[R^N_A] change sign at most once, from positive to negative, E[R^S_A] is non-decreasing and E[R^N_A] increasing overall, E[R^N_1] changes direction at most once, from falling to rising, Pi^S_A is non-decreasing, all four profits exceed the benchmark at every theta, Pi^S_B is nearly constant and Pi^N_B increasing overall, and where the shares agree within 1e-6 each Pi^S_i - Pi^N_i changes sign at most once, from positive to negative. At gamma = 1e8, alpha_{A,1} < alpha_{A,2} - 1e-6 gives Pi^S_A < Pi^N_A and Pi^S_B > Pi^N_B at every theta, and alpha_{A,1} > alpha_{A,2} + 1e-6 the reverse. Sign checks ignore entries below 1e-9 (1 + max |d|), and none of the "at most once" checks requires a change to exist.
- **Recorded:** P1 at most one crossing of y A: failures = 0; P3a sales of A: failures = 0; P3a at most one crossing of sales of A: failures = 0; P4 at most one change of direction: failures = 0; P5a: failures = 0; P5b: failures = 0; P5c2 weak: failures = 0; P6a: failures = 0; P6b: failures = 0; P6c2 weak: failures = 0; P5c1: failures = 0; P6c1: failures = 0; P4 visibly falls then rises at gamma = 1000: points = 48; P4 visibly falls then rises at gamma = 10000: points = 48

<a id="check-3"></a>
### `tests/test_other_distributions.py::test_order_quantities_and_sales_patterns_under_other_distributions`

- **Outcome:** passed (0.0 s)
- **Tests directly:** N6
- **What:** Patterns of the parts of Propositions 1 to 3 that the paper states for every gamma.
- **Points:** 48 points of `draw_exogenous` (seed 808), 16 for each of the triangular, beta(2,5) and truncated normal distributions on [mu - sigma, mu + sigma], every second one with equal shares in both periods, 41 values of theta on [0, 1], gamma = 2, 1e3, 1e4.
- **Computed:** for the benchmark and Scenarios S and N, the orders of `claimed_first_period` through the quantile function and expected first-period sales by quadrature.
- **Criterion:** retailer A has the higher fractile at every evaluation, y^0_A and y^N_A are increasing overall, y^S_A is increasing overall at gamma = 2 and non-decreasing at the larger values, y^N_B and E[R^N_B] are decreasing overall, y^0_B, y^S_B and E[R^S_B] are nearly constant, and y^0_B < y^N_B < y^S_B and E[R^N_B] < E[R^S_B] at every theta. With t = 1e-10 (1 + max |v|), "increasing overall" means no step below -t and a total rise above t, and "nearly constant" means a range of at most 10 t.
- **Recorded:** parameter points = 48; distributions = ['triangular', 'beta(2,5)', 'truncated normal']; gammas = [2.0, 1000.0, 10000.0]
