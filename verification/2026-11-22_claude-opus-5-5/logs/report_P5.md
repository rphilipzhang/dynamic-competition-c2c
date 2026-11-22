# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k P5 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**11 of 11 checks passed.** pytest exit status: 0.

A *direct* check tests a part of the result itself. A *supporting* check confirms a tool that direct checks rely on, for example that a closed form equals the model at random points. Every check computes at finitely many points. For a result that holds for all parameters it is a search for counterexamples. For a result that holds for a parameter large enough it probes large values of that parameter.

## Results of theory.md

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [L1](#l1) | – | 1/1 |
| [L2](#l2) | 1/1 | 1/1 |
| [L3](#l3) | 1/1 | 1/1 |
| [L4](#l4) | – | 4/4 |
| [P1](#p1) | – | 4/4 |
| [P2](#p2) | – | 4/4 |
| [P3](#p3) | – | 5/5 |
| [P4](#p4) | – | 3/3 |
| [P5](#p5) | 4/4 | 7/7 |
| [P6](#p6) | – | 6/6 |
| [LA1](#la1) | – | – |
| [LA2](#la2) | – | – |
| [P7](#p7) | – | – |
| [P8](#p8) | – | – |
| [P9](#p9) | – | – |
| [LB1](#lb1) | – | – |

## Numerical statements of the paper

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [F1](#f1) | – | 4/4 |
| [FB1](#fb1) | – | – |
| [N1](#n1) | – | – |
| [N2](#n2) | – | – |
| [N3](#n3) | – | – |
| [N4](#n4) | – | – |
| [N5](#n5) | – | – |
| [N6](#n6) | – | – |

## Checks by ID

### L1

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-1): passed

### L2

- direct (L2.profits): [test_closed_form_sales_and_profits_equal_the_model[S]](#check-5): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-3): passed

### L3

- direct (L3.profits): [test_closed_form_sales_and_profits_equal_the_model[N]](#check-4): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-2): passed

### L4

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-1): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-2): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-3): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-10): passed

### P1

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-1): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-2): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-3): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-10): passed

### P2

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-1): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-2): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-3): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-10): passed

### P3

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-2): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-3): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-4): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[S]](#check-5): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-10): passed

### P4

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-2): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-4): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-10): passed

### P5

- direct (P5.a): [test_proposition_5a_profit_of_retailer_a_in_scenario_s_increases_in_theta](#check-6): passed
- direct (P5.b): [test_proposition_5b_profit_of_retailer_a_exceeds_the_benchmark](#check-7): passed
- direct (P5.c1): [test_proposition_5c1_shares_decide_the_comparison_for_retailer_a](#check-8): passed
- direct (P5.c2): [test_proposition_5c2_threshold_in_theta_above_the_cost_threshold](#check-9): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-1): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-2): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-3): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-4): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[S]](#check-5): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-10): passed
- supporting: [test_threshold_gamma_a4_of_proposition_5c2_depends_on_c_b](#check-11): passed

### P6

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-1): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-2): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-3): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-4): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[S]](#check-5): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-10): passed

### F1

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-2): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-3): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-4): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[S]](#check-5): passed

## Checks

<a id="check-1"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]`

- **Outcome:** passed (0.0 s)
- **Supports:** L1.eq, L4.a, P1.i, P2.a, P2.b, P5.b, P6.b
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 34

<a id="check-2"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]`

- **Outcome:** passed (0.0 s)
- **Supports:** L3.first, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P4, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 26

<a id="check-3"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]`

- **Outcome:** passed (0.0 s)
- **Supports:** L2.first, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P5.a, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 33

<a id="check-4"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_sales_and_profits_equal_the_model[N]`

- **Outcome:** passed (0.1 s)
- **Tests directly:** L3.profits
- **Supports:** P3.a, P3.b, P4, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (b) for Scenario S (Lemma 2) or Scenario N (Lemma 3).
- **Points:** 500 points (seed 505), 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`, under the uniform distribution.
- **Computed:** at the closed-form orders, expected first-period sales y_i - E[(y_i - D_i)^+] and total two-period profits of both retailers from `c2c.closed_form`, and the same quantities from the exact integration of `primitives.Uniform` and the payoffs of `section4.Game`.
- **Criterion:** sales differ by at most 1e-11 mu, profits by at most 1e-9 mu (1 + gamma) times the largest of the four prices, and retailer B has the higher critical fractile at one point or more. The closed-form profits cancel to a much smaller value, so their rounding error grows with the terms. Over 117 alternative seeds it reached 7e-11 of the scale, at edge points. A wrong term in one of the closed forms changes a profit by far more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 26

<a id="check-5"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_sales_and_profits_equal_the_model[S]`

- **Outcome:** passed (0.1 s)
- **Tests directly:** L2.profits
- **Supports:** P3.a, P3.b, P5.a, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (b) for Scenario S (Lemma 2) or Scenario N (Lemma 3).
- **Points:** 500 points (seed 505), 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`, under the uniform distribution.
- **Computed:** at the closed-form orders, expected first-period sales y_i - E[(y_i - D_i)^+] and total two-period profits of both retailers from `c2c.closed_form`, and the same quantities from the exact integration of `primitives.Uniform` and the payoffs of `section4.Game`.
- **Criterion:** sales differ by at most 1e-11 mu, profits by at most 1e-9 mu (1 + gamma) times the largest of the four prices, and retailer B has the higher critical fractile at one point or more. The closed-form profits cancel to a much smaller value, so their rounding error grows with the terms. Over 117 alternative seeds it reached 7e-11 of the scale, at edge points. A wrong term in one of the closed forms changes a profit by far more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 31

<a id="check-6"></a>
### `tests/test_propositions_exogenous.py::test_proposition_5a_profit_of_retailer_a_in_scenario_s_increases_in_theta`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P5.a
- **What:** Proposition 5(a): the profit Pi^S_A of retailer A in Scenario S increases in theta.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** Pi^S_A on the grid from `spfta_t1` in exact rational arithmetic, and the lowest rung from which the criterion holds at every point of each kind.
- **Criterion:** at gamma = 1e50 and 1e60, at every point, Pi^S_A is strictly increasing in theta, or equal at every node where A11 holds with equality in both periods.
- **Recorded:** points where the profit is constant = 4; regular points = 120; holds at every regular point from gamma = 0.05; edge points = 90; holds at every edge point from gamma = 0.05

<a id="check-7"></a>
### `tests/test_propositions_exogenous.py::test_proposition_5b_profit_of_retailer_a_exceeds_the_benchmark`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P5.b
- **What:** Proposition 5(b): the profits of retailer A exceed the benchmark.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** Pi^0_A, Pi^S_A and Pi^N_A on the grid from `spfta_t1` (with gamma = 0 for the benchmark) and `npfta_t1` in exact rational arithmetic, and the lowest rung from which the criterion holds at every point of each kind.
- **Criterion:** at gamma = 1e50 and 1e60, at every point, Pi^S_A > Pi^0_A and Pi^N_A > Pi^0_A at every node.
- **Recorded:** regular points = 120; holds at every regular point from gamma = 0.05; edge points = 90; holds at every edge point from gamma = 1000.0

<a id="check-8"></a>
### `tests/test_propositions_exogenous.py::test_proposition_5c1_shares_decide_the_comparison_for_retailer_a`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P5.c1
- **What:** Proposition 5(c1): where the shares differ between the periods, they decide the comparison of Pi^S_A and Pi^N_A.
- **Points:** the sample points whose shares alpha_{A,1} and alpha_{A,2} differ, compared exactly, so that no point is left out because its shares are close. Every gamma of the 12-rung ladder and its theta grid.
- **Computed:** Pi^S_A - Pi^N_A on the grid in exact rational arithmetic, and the lowest rung from which the criterion holds at every such point of each kind.
- **Criterion:** at gamma = 1e50 and 1e60, alpha_{A,1} < alpha_{A,2} gives Pi^S_A < Pi^N_A and alpha_{A,1} > alpha_{A,2} gives Pi^S_A > Pi^N_A, at every node of every such point.
- **Recorded:** regular points = 40; holds at every regular point from gamma = 100.0; edge points = 26; holds at every edge point from gamma = 1000000.0

<a id="check-9"></a>
### `tests/test_propositions_exogenous.py::test_proposition_5c2_threshold_in_theta_above_the_cost_threshold`

- **Outcome:** passed (1.2 s)
- **Tests directly:** P5.c2
- **What:** Proposition 5(c2): with equal shares and c_B above the threshold c_B-bar of the proof, a threshold in theta for Pi^S_A - Pi^N_A.
- **Points:** the sample points with equal shares at which the expression P5_SIGN_AT_THETA_ONE of the proof is negative, which is the condition c_B > c_B-bar, and 90 further points with equal shares that satisfy it, 60 of `draw_exogenous_exact` (seed 626) and 30 of `draw_edge_exact` (seed 636). Theta grid of each rung of the ladder.
- **Computed:** Pi^S_A - Pi^N_A on the grid in exact rational arithmetic. The sign patterns at the sample points below the cost threshold are recorded and not tested, because the statement says nothing about them.
- **Criterion:** the two LaTeX strings of the proof occur verbatim in the LaTeX source, and at gamma = 1e50 and 1e60, at every such point, the difference is positive at theta = 0, negative at theta = 1, with sign pattern "+-", zeros skipped.
- **Recorded:** points below the cost threshold = 97; signs along theta below the cost threshold = ['+']; regular points = 21; holds at every regular point from gamma = 1000.0; edge points = 26; holds at every edge point from gamma = 1000000000.0; further points = 90

<a id="check-10"></a>
### `tests/test_propositions_exogenous.py::test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas`

- **Outcome:** passed (0.0 s)
- **Supports:** L4.a, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P4, P5.a, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2
- **What:** The sample of this file lies in the region of Lemmas 1 to 3.
- **Points:** the 210 sample points, 120 of `draw_exogenous_exact` (seed 606) and 90 of `draw_edge_exact` (seed 616), two thirds of each with equal shares in both periods, at every gamma of the 12-rung ladder from 1/20 to 1e60, on the theta grid of `theta_grid`.
- **Computed:** `ExactPoint.admissible` (A1, A7, A10, A11, I1 and I2, decided exactly), and from the closed forms the code's branch flag and the critical values zeta_A and zeta_B of the benchmark and of Scenarios S and N, in exact rational arithmetic. The bounds of both samplers and the number of edge points on each edge are recorded.
- **Criterion:** every point is admissible, and at every point, gamma and theta the code places retailer A's fractile above retailer B's and mu - sigma <= zeta_B <= zeta_A <= mu + sigma.
- **Recorded:** regular points = 120; edge points = 90; points with the same shares in both periods = 144; gamma ladder = [0.05, 1.0, 10.0, 100.0, 1000.0, 10000.0, 1000000.0, 1000000000.0, 1000000000000.0, 1e+18, 1e+50, 1e+60]; theta nodes at the top rung = 32; region of the regular points = assumptions: A1, A11 with strict inequalities, I1, I2. c_B: [0.5, 3], multiples of 1/1000. c_A / c_B: [0.05, 0.98], multiples of 1/1000. mu: [5, 20], multiples of 1/1000. sigma / mu: [0.1, 0.95], multiples of 1/1000. p_B,t / c_B: [1.05, 4], multiples of 1/1000. p_A,t: (c_A / c_B) p_B,t plus 0.001 to 0.999 of the distance to p_B,t. beta: at most 0.45 / (largest price gap) and at most 0.5, so the share of B is at least 0.05. equal_shares option: the same price gap in both periods, a fraction of the smallest gap that A11 allows. theta: [0.001, 0.999]. gamma: log-uniform on [0.05, 50]. lambda_S: [0.001, 0.999]. never reached: equality in A11, p_A = p_B, theta at 0 or 1, a share of B below 0.05; region of the edge points = assumptions: A1, A11 with equality allowed, I1, I2. rule: each coordinate takes an extreme value with probability 1/2, otherwise a value of draw_exogenous_exact. c_A / c_B: 1/1000 or 999/1000. sigma / mu: 1/100 or 999/1000. p_B,t / c_B: 1001/1000 or 50. p_A,t: (c_A / c_B) p_B,t (equality in A11) or p_B,t (shares 1/2). beta x largest price gap: 1/1000000 or 499/1000, the latter gives a share of B of 1/1000. beta when both price gaps are zero: 1/1000000 or 5. theta: 0 or 1. gamma: 1/100 or 1000. lambda_S: 0 or 1. equal_shares option: a common price gap that is zero, binding in A11, or regular. p_B,2 = p_B,1 with probability 1/4; edge points with beta = 1/1000000 without a price gap = 5; edge points with beta = 5 without a price gap = 6; edge points with beta x largest price gap = 1/1000000 = 15; edge points with beta x largest price gap = 499/1000 = 16; edge points with c A / c B = 1/1000 = 28; edge points with c A / c B = 999/1000 = 17; edge points with equality in A11 in both periods = 4; edge points with equality in A11 in period 1 = 16; edge points with equality in A11 in period 2 = 12; edge points with gamma = 1/100 = 24; edge points with gamma = 1000 = 16; edge points with lambda S = 0 = 24; edge points with lambda S = 1 = 23; edge points with p A = p B in period 1 = 24; edge points with p A = p B in period 2 = 22; edge points with p B / c B = 1001/1000 in period 1 = 22; edge points with p B / c B = 1001/1000 in period 2 = 19; edge points with p B / c B = 50 in period 1 = 23; edge points with p B / c B = 50 in period 2 = 31; edge points with same shares in both periods = 64; edge points with sigma / mu = 1/100 = 27; edge points with sigma / mu = 999/1000 = 15; edge points with theta = 0 = 26; edge points with theta = 1 = 21

<a id="check-11"></a>
### `tests/test_propositions_exogenous.py::test_threshold_gamma_a4_of_proposition_5c2_depends_on_c_b`

- **Outcome:** passed (0.2 s)
- **Supports:** P5
- **What:** Under the fixed-market interpretation of Proposition 5(c2) in theory.md, the threshold gamma^A_4 in the proof can depend on c_B. It grows without bound as c_B increases to p_{B,2} when p_{B,2} < p_{B,1}, and it can stay bounded as c_B increases to the end of its range when that end is p_{B,1}.
- **Points:** equal shares (alpha_{A,1} = alpha_{A,2} = 13/25), c_A = 1, beta = 1/10, mu = 10, sigma = 4. Prices p_A = (7/2, 3), p_B = (37/10, 16/5), where the range of c_B ends at p_{B,2} = 16/5, and the mirrored prices p_A = (3, 7/2), p_B = (16/5, 37/10), where it ends at p_{B,1} = 16/5. In each case c_B = 16/5 - eps for eps in {1/10, 1/100, 1/1000}, every point admissible and above c_B-bar. Gamma on the ladder 2^0, 2^1, ..., 2^30.
- **Computed:** Pi^S_A - Pi^N_A at theta = 1 from the closed forms of Lemmas 2 and 3 in exact rational arithmetic, and the smallest rung from which on it is negative on every larger rung. Pi^S_A - Pi^N_A at theta = 0 is positive at every rung used.
- **Criterion:** with p_{B,2} < p_{B,1} that rung rises by a factor of at least 10 with each tenfold decrease of eps. With p_{B,1} < p_{B,2} it is the same at every eps and at most 2^8.
- **Recorded:** rungs p B2 < p B1 = [4096, 262144, 33554432]; rungs p B1 < p B2 = [128, 128, 128]
