# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k F1 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**17 of 17 checks passed.** pytest exit status: 0.

A *direct* check tests a part of the result itself. A *supporting* check confirms a tool that direct checks rely on, for example that a closed form equals the model at random points. Every check computes at finitely many points. For a result that holds for all parameters it is a search for counterexamples. For a result that holds for a parameter large enough it probes large values of that parameter.

## Results of theory.md

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [L1](#l1) | – | – |
| [L2](#l2) | 2/2 | 1/1 |
| [L3](#l3) | 2/2 | 1/1 |
| [L4](#l4) | – | 2/2 |
| [P1](#p1) | – | 2/2 |
| [P2](#p2) | – | 2/2 |
| [P3](#p3) | – | 4/4 |
| [P4](#p4) | – | 2/2 |
| [P5](#p5) | – | 4/4 |
| [P6](#p6) | – | 4/4 |
| [LA1](#la1) | – | – |
| [LA2](#la2) | – | – |
| [P7](#p7) | – | – |
| [P8](#p8) | – | – |
| [P9](#p9) | – | – |
| [LB1](#lb1) | – | – |

## Numerical statements of the paper

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [F1](#f1) | 9/9 | 8/8 |
| [FB1](#fb1) | – | 2/2 |
| [N1](#n1) | – | 1/1 |
| [N2](#n2) | – | 1/1 |
| [N3](#n3) | – | 1/1 |
| [N4](#n4) | – | 1/1 |
| [N5](#n5) | – | 1/1 |
| [N6](#n6) | – | 1/1 |

## Checks by ID

### L2

- direct (L2.profits): [test_closed_form_sales_and_profits_equal_the_model[S]](#check-11): passed
- direct (L2.profits): [test_second_period_profit_function_equals_the_model[S]](#check-17): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-9): passed

### L3

- direct (L3.profits): [test_closed_form_sales_and_profits_equal_the_model[N]](#check-10): passed
- direct (L3.profits): [test_second_period_profit_function_equals_the_model[N]](#check-16): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-8): passed

### L4

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-8): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-9): passed

### P1

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-8): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-9): passed

### P2

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-8): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-9): passed

### P3

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-8): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-9): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-10): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[S]](#check-11): passed

### P4

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-8): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-10): passed

### P5

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-8): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-9): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-10): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[S]](#check-11): passed

### P6

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-8): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-9): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-10): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[S]](#check-11): passed

### F1

- direct: [test_figure_1_equilibria_are_unique_and_the_continuation_is_constant](#check-1): passed
- direct: [test_figure_1_matches_the_published_figure[a]](#check-2): passed
- direct: [test_figure_1_matches_the_published_figure[b]](#check-3): passed
- direct: [test_figure_1_matches_the_published_figure[c]](#check-4): passed
- direct: [test_figure_1_matches_the_published_figure[d]](#check-5): passed
- direct: [test_figure_1_inventory_equilibria_hold_in_the_model](#check-12): passed
- direct: [test_figure_1_payoff_matrices_equal_the_model](#check-13): passed
- direct: [test_figure_1_second_period_prices_are_an_equilibrium_at_every_sales_state](#check-14): passed
- direct: [test_second_period_inventory_equilibrium_for_all_price_pairs_of_figure_1](#check-15): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-6): passed
- supporting: [test_published_data_match_a_fresh_extraction_from_the_eps_files](#check-7): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-8): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-9): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-10): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[S]](#check-11): passed
- supporting: [test_second_period_profit_function_equals_the_model[N]](#check-16): passed
- supporting: [test_second_period_profit_function_equals_the_model[S]](#check-17): passed

### FB1

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-6): passed
- supporting: [test_published_data_match_a_fresh_extraction_from_the_eps_files](#check-7): passed

### N1

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-6): passed

### N2

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-6): passed

### N3

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-6): passed

### N4

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-6): passed

### N5

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-6): passed

### N6

- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-6): passed

## Checks

<a id="check-1"></a>
### `tests/test_figures.py::test_figure_1_equilibria_are_unique_and_the_continuation_is_constant`

- **Outcome:** passed (0.0 s)
- **Tests directly:** F1
- **What:** Figure 1: the two-price game that the figure plots has one equilibrium at every point.
- **Points:** the 44 parameter points of Figure 1 (4 panels, 11 values of theta), Scenarios S and N.
- **Computed:** `figure1_data`, which runs `pricing.pricing_equilibrium` at every point and scenario. The solver raises unless exactly one second-period price pair is an equilibrium at every feasible sales state, `figure1_point` raises unless there is exactly one first-period pure equilibrium, and the solver warns if another price pair is an equilibrium at some sales state.
- **Criterion:** the table has all 44 rows, and no warning was issued.
- **Recorded:** parameter points = 44

<a id="check-2"></a>
### `tests/test_figures.py::test_figure_1_matches_the_published_figure[a]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** F1
- **What:** Figure 1, one panel, against the published figure.
- **Points:** one panel of Figure 1 (a, b, c or d) with the series of Scenarios S and N, 11 values of theta each (0.01, 0.1, ..., 0.9, 0.99).
- **Computed:** the equilibrium profits of `figure1_data`, from the two-price game that `c2c.pricing` solves, rounded to four decimals and unrounded, and the values that `published_data.csv` reads back from the panel's EPS file. The published panels were drawn from four-decimal data.
- **Criterion:** each series has 11 plotted points whose theta agree within 1e-9, the largest absolute difference to the four-decimal values is at most the panel's extraction error bound plus 1e-9, and to the unrounded values at most 5e-5 plus that bound plus 1e-9.
- **Recorded:** extraction error bound = 2.72e-06; max abs difference to four decimal values = 2.2e-06; max abs difference to unrounded values = 4.67573e-05

<a id="check-3"></a>
### `tests/test_figures.py::test_figure_1_matches_the_published_figure[b]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** F1
- **What:** Figure 1, one panel, against the published figure.
- **Points:** one panel of Figure 1 (a, b, c or d) with the series of Scenarios S and N, 11 values of theta each (0.01, 0.1, ..., 0.9, 0.99).
- **Computed:** the equilibrium profits of `figure1_data`, from the two-price game that `c2c.pricing` solves, rounded to four decimals and unrounded, and the values that `published_data.csv` reads back from the panel's EPS file. The published panels were drawn from four-decimal data.
- **Criterion:** each series has 11 plotted points whose theta agree within 1e-9, the largest absolute difference to the four-decimal values is at most the panel's extraction error bound plus 1e-9, and to the unrounded values at most 5e-5 plus that bound plus 1e-9.
- **Recorded:** extraction error bound = 1.65e-05; max abs difference to four decimal values = 1.6e-05; max abs difference to unrounded values = 5.64286e-05

<a id="check-4"></a>
### `tests/test_figures.py::test_figure_1_matches_the_published_figure[c]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** F1
- **What:** Figure 1, one panel, against the published figure.
- **Points:** one panel of Figure 1 (a, b, c or d) with the series of Scenarios S and N, 11 values of theta each (0.01, 0.1, ..., 0.9, 0.99).
- **Computed:** the equilibrium profits of `figure1_data`, from the two-price game that `c2c.pricing` solves, rounded to four decimals and unrounded, and the values that `published_data.csv` reads back from the panel's EPS file. The published panels were drawn from four-decimal data.
- **Criterion:** each series has 11 plotted points whose theta agree within 1e-9, the largest absolute difference to the four-decimal values is at most the panel's extraction error bound plus 1e-9, and to the unrounded values at most 5e-5 plus that bound plus 1e-9.
- **Recorded:** extraction error bound = 1.92e-06; max abs difference to four decimal values = 1.796e-06; max abs difference to unrounded values = 4.86077e-05

<a id="check-5"></a>
### `tests/test_figures.py::test_figure_1_matches_the_published_figure[d]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** F1
- **What:** Figure 1, one panel, against the published figure.
- **Points:** one panel of Figure 1 (a, b, c or d) with the series of Scenarios S and N, 11 values of theta each (0.01, 0.1, ..., 0.9, 0.99).
- **Computed:** the equilibrium profits of `figure1_data`, from the two-price game that `c2c.pricing` solves, rounded to four decimals and unrounded, and the values that `published_data.csv` reads back from the panel's EPS file. The published panels were drawn from four-decimal data.
- **Criterion:** each series has 11 plotted points whose theta agree within 1e-9, the largest absolute difference to the four-decimal values is at most the panel's extraction error bound plus 1e-9, and to the unrounded values at most 5e-5 plus that bound plus 1e-9.
- **Recorded:** extraction error bound = 1.46e-05; max abs difference to four decimal values = 1e-05; max abs difference to unrounded values = 5.51625e-05

<a id="check-6"></a>
### `tests/test_figures.py::test_numerical_statements_are_quoted_from_the_paper`

- **Outcome:** passed (0.0 s)
- **Supports:** F1, FB1, N1, N2, N3, N4, N5, N6
- **Points:** the nine entries of `numerics/numerical_statements.yaml`, including N7, which the repository lists and does not check.
- **Computed:** each quote, against the LaTeX source of the paper with every \ref printed as the number that `numerics/paper_labels.json` gives.
- **Criterion:** every quote occurs verbatim, up to whitespace, so that the checks of this file test the paper's own sentences, and exactly N7 carries a field `excluded`.
- **Recorded:** statements quoted = 9

<a id="check-7"></a>
### `tests/test_figures.py::test_published_data_match_a_fresh_extraction_from_the_eps_files`

- **Outcome:** passed (0.5 s)
- **Supports:** F1, FB1
- **Points:** the 8 EPS panels of Figure 1 and Figure B.1 in `paper/`.
- **Computed:** `numerics/figures/extract_published_data.py` reads every plotted vertex back from the vector graphics into a temporary folder.
- **Criterion:** the fresh extraction equals the committed `published_data.csv` and `published_data_calibration.json` byte for byte, so that every comparison with a published figure in this file uses data that the EPS files reproduce.
- **Recorded:** panels = 8; plotted points = 187

<a id="check-8"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]`

- **Outcome:** passed (0.0 s)
- **Supports:** L3.first, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P4, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 26

<a id="check-9"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]`

- **Outcome:** passed (0.0 s)
- **Supports:** L2.first, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P5.a, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 33

<a id="check-10"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_sales_and_profits_equal_the_model[N]`

- **Outcome:** passed (0.1 s)
- **Tests directly:** L3.profits
- **Supports:** P3.a, P3.b, P4, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (b) for Scenario S (Lemma 2) or Scenario N (Lemma 3).
- **Points:** 500 points (seed 505), 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`, under the uniform distribution.
- **Computed:** at the closed-form orders, expected first-period sales y_i - E[(y_i - D_i)^+] and total two-period profits of both retailers from `c2c.closed_form`, and the same quantities from the exact integration of `primitives.Uniform` and the payoffs of `section4.Game`.
- **Criterion:** sales differ by at most 1e-11 mu, profits by at most 1e-9 mu (1 + gamma) times the largest of the four prices, and retailer B has the higher critical fractile at one point or more. The closed-form profits cancel to a much smaller value, so their rounding error grows with the terms. Over 117 alternative seeds it reached 7e-11 of the scale, at edge points. A wrong term in one of the closed forms changes a profit by far more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 26

<a id="check-11"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_sales_and_profits_equal_the_model[S]`

- **Outcome:** passed (0.1 s)
- **Tests directly:** L2.profits
- **Supports:** P3.a, P3.b, P5.a, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (b) for Scenario S (Lemma 2) or Scenario N (Lemma 3).
- **Points:** 500 points (seed 505), 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`, under the uniform distribution.
- **Computed:** at the closed-form orders, expected first-period sales y_i - E[(y_i - D_i)^+] and total two-period profits of both retailers from `c2c.closed_form`, and the same quantities from the exact integration of `primitives.Uniform` and the payoffs of `section4.Game`.
- **Criterion:** sales differ by at most 1e-11 mu, profits by at most 1e-9 mu (1 + gamma) times the largest of the four prices, and retailer B has the higher critical fractile at one point or more. The closed-form profits cancel to a much smaller value, so their rounding error grows with the terms. Over 117 alternative seeds it reached 7e-11 of the scale, at edge points. A wrong term in one of the closed forms changes a profit by far more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 31

<a id="check-12"></a>
### `tests/test_profits_and_price_game.py::test_figure_1_inventory_equilibria_hold_in_the_model`

- **Outcome:** passed (0.2 s)
- **Tests directly:** F1
- **What:** Figure 1: the first-period inventory equilibria behind the payoff matrices, including the price pairs that violate assumption A11.
- **Points:** the 4 panels of Figure 1 at theta = 0.01, 0.5 and 0.99, Scenarios S and N, and the 4 first-period price pairs of {2, 4}: 96 inventory games.
- **Computed:** the orders of `section4.claimed_first_period` at the second-period prices of `pricing.pricing_equilibrium`, and `primitives.nash_gap` on [0, 1.5 (mu + sigma)] for the two-period payoffs of `section4.Game`, built from the primitives.
- **Criterion:** the solver issues no warning, and in every game no deviation gains more than 1e-7 and each best response lies within 2e-5 of the claimed order, both absolute.
- **Recorded:** inventory games checked = 96

<a id="check-13"></a>
### `tests/test_profits_and_price_game.py::test_figure_1_payoff_matrices_equal_the_model`

- **Outcome:** passed (0.1 s)
- **Tests directly:** F1
- **What:** Figure 1: the payoff matrices of the first-period price game.
- **Points:** the 44 parameter points of Figure 1 (4 panels, 11 values of theta), Scenarios S and N, and the 4 first-period price pairs of {2, 4}: 352 cells.
- **Computed:** `pricing.pricing_equilibrium` with warnings turned into errors, and at its second-period prices the two-period profits from the primitives (`section4.Game`) at the orders of `section4.claimed_first_period`, for either ordering of the fractiles.
- **Criterion:** no warning, both fractiles in [0, 1] in every cell, every payoff of the solver within 1e-9 (absolute) of the model's, and retailer B has the higher fractile in one cell or more.
- **Recorded:** payoff cells compared = 352; cells where retailer B has the higher fractile = 44

<a id="check-14"></a>
### `tests/test_profits_and_price_game.py::test_figure_1_second_period_prices_are_an_equilibrium_at_every_sales_state`

- **Outcome:** passed (0.1 s)
- **Tests directly:** F1
- **What:** Figure 1: the solver's second-period price pair is the equilibrium whatever the first-period sales.
- **Points:** the 4 panels of Figure 1 at theta = 0.01, 0.3, 0.6 and 0.99, Scenarios S and N (32 cases), the 10 first-period sales states listed in the code, among them the corners (0, 0), (15, 0) and (0, 15) of the sales triangle, and the 4 price pairs of {2, 4}.
- **Computed:** second-period profits of both retailers from the primitives (`section4.Game`) at the orders y^0_{i,2} + Z_{i,2}, and at each state the price pairs from which no unilateral price change gains more than 1e-9.
- **Criterion:** in each case the solver runs without warning, its pair is such a pair at all 10 states, and it is the only price pair that is.
- **Recorded:** price games solved = 320

<a id="check-15"></a>
### `tests/test_profits_and_price_game.py::test_second_period_inventory_equilibrium_for_all_price_pairs_of_figure_1`

- **Outcome:** passed (0.1 s)
- **Tests directly:** F1
- **What:** Figure 1: the second-period inventory equilibrium y^0_{i,2} + Z_{i,2} that the profits above use, at every price pair, including pairs at which retailer B has the higher critical fractile.
- **Points:** (c_A, gamma) = (0.10, 0.7) and (0.95, 2.0), Scenarios S and N, theta = 0.01, 0.5 and 0.99, the 4 second-period price pairs of {2, 4}, and the sales state (R_A, R_B) = (5, 3.75): 48 games.
- **Computed:** `primitives.nash_gap` on [0, 1.5 (mu + sigma)(1 + gamma)] for the second-period payoffs of `section4.Game` at the claimed orders.
- **Criterion:** no unilateral deviation gains more than 1e-7 (absolute) in any game.
- **Recorded:** inventory games checked = 48

<a id="check-16"></a>
### `tests/test_profits_and_price_game.py::test_second_period_profit_function_equals_the_model[N]`

- **Outcome:** passed (0.1 s)
- **Tests directly:** L3.profits
- **Supports:** F1
- **What:** Link (c) for Scenario S or Scenario N: the second-period profit that the appendix states and that the price game uses, as a function of prices and first-period sales.
- **Points:** 400 points of `draw_exogenous` (seed 909) with p_{A,2} and p_{B,2} redrawn independently on [1.05 c_B, 4 c_B], so that A11 is not imposed, and beta reduced to at most 0.45 / |p_{B,2} - p_{A,2}|. One sales state per point, R_A uniform on [0, mu + sigma] and R_B uniform on [0, mu + sigma - R_A].
- **Computed:** `closed_form.period2_profit`, and the profits that `section4.Game` computes from the primitives at the orders y^0_{i,2} + Z_{i,2}.
- **Criterion:** each difference is at most 1e-11 mu (1 + gamma) p_{i,2}, and c_A / p_{A,2} > c_B / p_{B,2} at one point or more.
- **Recorded:** parameter points = 400; points where retailer B has the higher fractile = 66

<a id="check-17"></a>
### `tests/test_profits_and_price_game.py::test_second_period_profit_function_equals_the_model[S]`

- **Outcome:** passed (0.1 s)
- **Tests directly:** L2.profits
- **Supports:** F1
- **What:** Link (c) for Scenario S or Scenario N: the second-period profit that the appendix states and that the price game uses, as a function of prices and first-period sales.
- **Points:** 400 points of `draw_exogenous` (seed 909) with p_{A,2} and p_{B,2} redrawn independently on [1.05 c_B, 4 c_B], so that A11 is not imposed, and beta reduced to at most 0.45 / |p_{B,2} - p_{A,2}|. One sales state per point, R_A uniform on [0, mu + sigma] and R_B uniform on [0, mu + sigma - R_A].
- **Computed:** `closed_form.period2_profit`, and the profits that `section4.Game` computes from the primitives at the orders y^0_{i,2} + Z_{i,2}.
- **Criterion:** each difference is at most 1e-11 mu (1 + gamma) p_{i,2}, and c_A / p_{A,2} > c_B / p_{B,2} at one point or more.
- **Recorded:** parameter points = 400; points where retailer B has the higher fractile = 66
