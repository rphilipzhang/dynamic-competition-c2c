# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k P3 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**7 of 7 checks passed.** pytest exit status: 0.

A *direct* check tests a part of the result itself. A *supporting* check confirms a tool that direct checks rely on, for example that a closed form equals the model at random points. Every check computes at finitely many points. For a result that holds for all parameters it is a search for counterexamples. For a result that holds for a parameter large enough it probes large values of that parameter.

The selection counts only P3. Other IDs that the selected checks name appear only in the description of each check below.

## Results of theory.md

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [P3](#p3) | 2/2 | 5/5 |

## Checks by ID

### P3

- direct (P3.a): [test_proposition_3a_expected_sales_of_retailer_a_for_large_gamma](#check-5): passed
- direct (P3.b): [test_proposition_3b_expected_sales_of_retailer_b](#check-6): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-1): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-2): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-3): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[S]](#check-4): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-7): passed

## Checks

<a id="check-1"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]`

- **Outcome:** passed (0.0 s)
- **Supports:** L3.first, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P4, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 26
- **At the level of rounding error (differs between machines):** max relative difference = 7.44804e-16

<a id="check-2"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]`

- **Outcome:** passed (0.0 s)
- **Supports:** L2.first, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P5.a, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 33
- **At the level of rounding error (differs between machines):** max relative difference = 7.44804e-16

<a id="check-3"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_sales_and_profits_equal_the_model[N]`

- **Outcome:** passed (0.1 s)
- **Tests directly:** L3.profits
- **Supports:** P3.a, P3.b, P4, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (b) for Scenario S (Lemma 2) or Scenario N (Lemma 3).
- **Points:** 500 points (seed 505), 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`, under the uniform distribution.
- **Computed:** at the closed-form orders, expected first-period sales y_i - E[(y_i - D_i)^+] and total two-period profits of both retailers from `c2c.closed_form`, and the same quantities from the exact integration of `primitives.Uniform` and the payoffs of `section4.Game`.
- **Criterion:** sales differ by at most 1e-11 mu, profits by at most 1e-9 mu (1 + gamma) times the largest of the four prices, and retailer B has the higher critical fractile at one point or more. The closed-form profits cancel to a much smaller value, so their rounding error grows with the terms. Over 117 alternative seeds it reached 7e-11 of the scale, at edge points. A wrong term in one of the closed forms changes a profit by far more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 26
- **At the level of rounding error (differs between machines):** max relative error expected sales = 3.83142e-15; max relative error profit = 2.23266e-13

<a id="check-4"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_sales_and_profits_equal_the_model[S]`

- **Outcome:** passed (0.1 s)
- **Tests directly:** L2.profits
- **Supports:** P3.a, P3.b, P5.a, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (b) for Scenario S (Lemma 2) or Scenario N (Lemma 3).
- **Points:** 500 points (seed 505), 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`, under the uniform distribution.
- **Computed:** at the closed-form orders, expected first-period sales y_i - E[(y_i - D_i)^+] and total two-period profits of both retailers from `c2c.closed_form`, and the same quantities from the exact integration of `primitives.Uniform` and the payoffs of `section4.Game`.
- **Criterion:** sales differ by at most 1e-11 mu, profits by at most 1e-9 mu (1 + gamma) times the largest of the four prices, and retailer B has the higher critical fractile at one point or more. The closed-form profits cancel to a much smaller value, so their rounding error grows with the terms. Over 117 alternative seeds it reached 7e-11 of the scale, at edge points. A wrong term in one of the closed forms changes a profit by far more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 31
- **At the level of rounding error (differs between machines):** max relative error expected sales = 4.59771e-15; max relative error profit = 2.23266e-13

<a id="check-5"></a>
### `tests/test_propositions_exogenous.py::test_proposition_3a_expected_sales_of_retailer_a_for_large_gamma`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P3.a
- **What:** Proposition 3(a): expected sales of retailer A for gamma large.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** E[R^S_{A,1}], E[R^N_{A,1}] and d = E[R^S_{A,1}] - E[R^N_{A,1}] on the grid in exact rational arithmetic. For each kind of point two rungs are recorded: the lowest from which the large-gamma criterion holds at every point, and the lowest from which the change of sign of d exists at every point.
- **Criterion:** at gamma = 1e50 and 1e60, at every point, E[R^N_{A,1}] is strictly increasing in theta, E[R^S_{A,1}] is strictly increasing, or equal at every node where A11 holds with equality in both periods, and d > 0 at theta = 0, d < 0 at theta = 1 with sign pattern "+-", zeros skipped. At every gamma of the ladder, d > 0 at theta = 0 and the pattern is "+" or "+-".
- **Recorded:** a change of sign exists at every regular point from gamma = 100.0; a change of sign exists at every edge point from gamma = 1000000000.0; regular points = 120; holds at every regular point from gamma = 100.0; edge points = 90; holds at every edge point from gamma = 1000000000.0

<a id="check-6"></a>
### `tests/test_propositions_exogenous.py::test_proposition_3b_expected_sales_of_retailer_b`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P3.b
- **What:** Proposition 3(b): expected sales of retailer B.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** E[R^S_{B,1}] and E[R^N_{B,1}] on the grid from the closed forms, in exact rational arithmetic. The closed form of E[R^S_{B,1}] from Lemma 2 does not contain theta.
- **Criterion:** at every point and gamma E[R^N_{B,1}] is strictly decreasing in theta, E[R^S_{B,1}] is equal at every node, and E[R^N_{B,1}] < E[R^S_{B,1}] at every node.
- **Recorded:** regular points = 120; edge points = 90

<a id="check-7"></a>
### `tests/test_propositions_exogenous.py::test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas`

- **Outcome:** passed (0.0 s)
- **Supports:** L4.a, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P4, P5.a, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2
- **What:** The sample of this file lies in the region of Lemmas 1 to 3.
- **Points:** the 210 sample points, 120 of `draw_exogenous_exact` (seed 606) and 90 of `draw_edge_exact` (seed 616), two thirds of each with equal shares in both periods, at every gamma of the 12-rung ladder from 1/20 to 1e60, on the theta grid of `theta_grid`.
- **Computed:** `ExactPoint.admissible` (A1, A7, A10, A11, I1 and I2, decided exactly), and from the closed forms the code's branch flag and the critical values zeta_A and zeta_B of the benchmark and of Scenarios S and N, in exact rational arithmetic. The bounds of both samplers and the number of edge points on each edge are recorded.
- **Criterion:** every point is admissible, and at every point, gamma and theta the code places retailer A's fractile above retailer B's and mu - sigma <= zeta_B <= zeta_A <= mu + sigma.
- **Recorded:** regular points = 120; edge points = 90; points with the same shares in both periods = 144; gamma ladder = [0.05, 1.0, 10.0, 100.0, 1000.0, 10000.0, 1000000.0, 1000000000.0, 1000000000000.0, 1e+18, 1e+50, 1e+60]; theta nodes at the top rung = 32; region of the regular points = assumptions: A1, A11 with strict inequalities, I1, I2. c_B: [0.5, 3], multiples of 1/1000. c_A / c_B: [0.05, 0.98], multiples of 1/1000. mu: [5, 20], multiples of 1/1000. sigma / mu: [0.1, 0.95], multiples of 1/1000. p_B,t / c_B: [1.05, 4], multiples of 1/1000. p_A,t: (c_A / c_B) p_B,t plus 0.001 to 0.999 of the distance to p_B,t. beta: at most 0.45 / (largest price gap) and at most 0.5, so the share of B is at least 0.05. equal_shares option: the same price gap in both periods, a fraction of the smallest gap that A11 allows. theta: [0.001, 0.999]. gamma: log-uniform on [0.05, 50]. lambda_S: [0.001, 0.999]. never reached: equality in A11, p_A = p_B, theta at 0 or 1, a share of B below 0.05; region of the edge points = assumptions: A1, A11 with equality allowed, I1, I2. rule: each coordinate takes an extreme value with probability 1/2, otherwise a value of draw_exogenous_exact. c_A / c_B: 1/1000 or 999/1000. sigma / mu: 1/100 or 999/1000. p_B,t / c_B: 1001/1000 or 50. p_A,t: (c_A / c_B) p_B,t (equality in A11) or p_B,t (shares 1/2). beta x largest price gap: 1/1000000 or 499/1000, the latter gives a share of B of 1/1000. beta when both price gaps are zero: 1/1000000 or 5. theta: 0 or 1. gamma: 1/100 or 1000. lambda_S: 0 or 1. equal_shares option: a common price gap that is zero, binding in A11, or regular. p_B,2 = p_B,1 with probability 1/4; edge points with beta = 1/1000000 without a price gap = 5; edge points with beta = 5 without a price gap = 6; edge points with beta x largest price gap = 1/1000000 = 15; edge points with beta x largest price gap = 499/1000 = 16; edge points with c A / c B = 1/1000 = 28; edge points with c A / c B = 999/1000 = 17; edge points with equality in A11 in both periods = 4; edge points with equality in A11 in period 1 = 16; edge points with equality in A11 in period 2 = 12; edge points with gamma = 1/100 = 24; edge points with gamma = 1000 = 16; edge points with lambda S = 0 = 24; edge points with lambda S = 1 = 23; edge points with p A = p B in period 1 = 24; edge points with p A = p B in period 2 = 22; edge points with p B / c B = 1001/1000 in period 1 = 22; edge points with p B / c B = 1001/1000 in period 2 = 19; edge points with p B / c B = 50 in period 1 = 23; edge points with p B / c B = 50 in period 2 = 31; edge points with same shares in both periods = 64; edge points with sigma / mu = 1/100 = 27; edge points with sigma / mu = 999/1000 = 15; edge points with theta = 0 = 26; edge points with theta = 1 = 21
