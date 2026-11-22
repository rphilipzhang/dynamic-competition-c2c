# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k N5 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**4 of 4 checks passed.** pytest exit status: 0.

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
| [LB1](#lb1) | – | 1/1 |

## Numerical statements of the paper

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [F1](#f1) | – | 1/1 |
| [FB1](#fb1) | – | 3/3 |
| [N1](#n1) | – | 1/1 |
| [N2](#n2) | – | 1/1 |
| [N3](#n3) | – | 1/1 |
| [N4](#n4) | – | 1/1 |
| [N5](#n5) | 1/1 | 3/3 |
| [N6](#n6) | – | 1/1 |

## Checks by ID

### LB1

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]](#check-3): passed

### F1

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

### FB1

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]](#check-3): passed
- supporting: [test_closed_form_profits_of_the_mixed_scenario_equal_the_model](#check-4): passed

### N1

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

### N2

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

### N3

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

### N4

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

### N5

- direct: [test_figure_b1_patterns_described_in_appendix_b](#check-1): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]](#check-3): passed
- supporting: [test_closed_form_profits_of_the_mixed_scenario_equal_the_model](#check-4): passed

### N6

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-2): passed

## Checks

<a id="check-1"></a>
### `tests/test_figures.py::test_figure_b1_patterns_described_in_appendix_b`

- **Outcome:** passed (0.0 s)
- **Tests directly:** N5
- **What:** Online Appendix B. Panel (b): retailer B's order quantity in Scenario GN decreases in theta. Panels (a), (c), (d): the comparisons of Propositions 1, 5 and 6 carry over, each with a single crossing in theta.
- **Points:** the 11 values of theta 0, 0.1, ..., 1 of Figure B.1, all four panels.
- **Computed:** the series of `figureB1_data`: y_{B,1} in Scenarios GN, GS and 0 for panel (b), and the gaps GS - GN of panels (a), (c) and (d).
- **Criterion:** b_GN falls at every step, the range of b_GS is below 0.05 and that of b_0 is exactly 0, and each of the three gaps is positive at theta = 0, negative at theta = 1 and changes sign between exactly one pair of neighbouring values.
- **Recorded:** crossing between theta panel a = 0.5 and 0.6; crossing between theta panel c = 0.8 and 0.9; crossing between theta panel d = 0.1 and 0.2

<a id="check-2"></a>
### `tests/test_figures.py::test_numerical_statements_are_quoted_from_the_paper`

- **Outcome:** passed (0.0 s)
- **Supports:** F1, FB1, N1, N2, N3, N4, N5, N6
- **Points:** the nine entries of `numerics/numerical_statements.yaml`, including N7, which the repository lists and does not check.
- **Computed:** each quote, against the LaTeX source of the paper with every \ref printed as the number that `numerics/paper_labels.json` gives.
- **Criterion:** every quote occurs verbatim, up to whitespace, so that the checks of this file test the paper's own sentences, and exactly N7 carries a field `excluded`.
- **Recorded:** statements quoted = 9

<a id="check-3"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]`

- **Outcome:** passed (0.0 s)
- **Supports:** LB1.first, FB1, N5
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points edge = 100; points where retailer B has the higher fractile = 0

<a id="check-4"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_profits_of_the_mixed_scenario_equal_the_model`

- **Outcome:** passed (0.1 s)
- **Supports:** FB1, N5
- **What:** Link (b) for the mixed scenario of Online Appendix B (Lemma B.1).
- **Points:** 300 points (seed 506), 200 of `draw_exogenous` and 100 of `draw_edge_exact`, all of which satisfy A11, because the code implements only the ordering of Lemma B.1.
- **Computed:** total two-period profits of both retailers at the orders of `find_general_exo`, from that function and from the payoffs of `section4.Game` (scenario G) integrated exactly under the uniform distribution. The code returns no expected sales for this scenario, so sales are not compared.
- **Criterion:** every difference is at most 1e-9 mu (1 + gamma) max(p_{B,1}, p_{B,2}).
- **Recorded:** points regular = 200; points edge = 100; points where retailer B has the higher fractile = 0
