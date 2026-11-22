# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k L4 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**6 of 6 checks passed.** pytest exit status: 0.

A *direct* check tests a part of the result itself. A *supporting* check confirms a tool that direct checks rely on, for example that a closed form equals the model at random points. Every check computes at finitely many points. For a result that holds for all parameters it is a search for counterexamples. For a result that holds for a parameter large enough it probes large values of that parameter.

The selection counts only L4. Other IDs that the selected checks name appear only in the description of each check below.

## Results of theory.md

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [L4](#l4) | 2/2 | 4/4 |

## Checks by ID

### L4

- direct (L4.a): [test_lemma_4a_benchmark_order_per_unit_of_share](#check-4): passed
- direct (L4.b): [test_lemma_4b_order_per_unit_of_share_in_scenarios_s_and_n](#check-5): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-1): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-2): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-3): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-6): passed

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
- **At the level of rounding error (differs between machines):** max relative difference = 4.686e-16

<a id="check-2"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]`

- **Outcome:** passed (0.0 s)
- **Supports:** L3.first, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P4, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 26
- **At the level of rounding error (differs between machines):** max relative difference = 7.44804e-16

<a id="check-3"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]`

- **Outcome:** passed (0.0 s)
- **Supports:** L2.first, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P5.a, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 33
- **At the level of rounding error (differs between machines):** max relative difference = 7.44804e-16

<a id="check-4"></a>
### `tests/test_propositions_exogenous.py::test_lemma_4a_benchmark_order_per_unit_of_share`

- **Outcome:** passed (0.0 s)
- **Tests directly:** L4.a
- **What:** Lemma 4(a): y^0_{A,t} / alpha_{A,t} >= y^0_{B,t} / alpha_{B,t}.
- **Points:** the 210 sample points (120 regular, 90 edge). Period 1 on the theta grid of gamma = 1/20, because the benchmark does not depend on gamma. Period 2 on the 21 values k / 20 of theta.
- **Computed:** e_t = y^0_{A,t} / alpha_{A,t} - y^0_{B,t} / alpha_{B,t} from `first_period_s` with gamma = 0, at the first-period prices for t = 1 and at the second-period prices for t = 2, in exact rational arithmetic.
- **Criterion:** e_t >= 0 at every node, and e_t = 0 at every node where A11 holds with equality in period t, e_t > 0 at every node otherwise.
- **Recorded:** regular points = 120; edge points = 90; points with equality in period 1 = 16; points with equality in period 2 = 12

<a id="check-5"></a>
### `tests/test_propositions_exogenous.py::test_lemma_4b_order_per_unit_of_share_in_scenarios_s_and_n`

- **Outcome:** passed (0.0 s)
- **Tests directly:** L4.b
- **What:** Lemma 4(b): y^k_{A,t} / alpha_{A,t} >= y^k_{B,t} / alpha_{B,t} for k = S and N.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid in period 1, the 21 values k / 20 of theta in period 2.
- **Computed:** e^k = y^k_{A,1} / alpha_{A,1} - y^k_{B,1} / alpha_{B,1} from `first_period_s` and `first_period_n` in exact rational arithmetic. By Lemmas 2 and 3 the second-period orders net of Z_{i,2} are the benchmark quantities at the second-period prices, so period 2 is the inequality of part (a) for t = 2. Second-period orders are not computed in any other way.
- **Criterion:** at every node and gamma e^S >= 0 and e^N > 0, e^S = 0 at every node where A11 holds with equality in both periods and e^S > 0 otherwise, and the period-2 condition of the Lemma 4(a) check holds.
- **Recorded:** regular points = 120; edge points = 90

<a id="check-6"></a>
### `tests/test_propositions_exogenous.py::test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas`

- **Outcome:** passed (0.0 s)
- **Supports:** L4.a, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P4, P5.a, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2
- **What:** The sample of this file lies in the region of Lemmas 1 to 3.
- **Points:** the 210 sample points, 120 of `draw_exogenous_exact` (seed 606) and 90 of `draw_edge_exact` (seed 616), two thirds of each with equal shares in both periods, at every gamma of the 12-rung ladder from 1/20 to 1e60, on the theta grid of `theta_grid`.
- **Computed:** `ExactPoint.admissible` (A1, A7, A10, A11, I1 and I2, decided exactly), and from the closed forms the code's branch flag and the critical values zeta_A and zeta_B of the benchmark and of Scenarios S and N, in exact rational arithmetic. The bounds of both samplers and the number of edge points on each edge are recorded.
- **Criterion:** every point is admissible, and at every point, gamma and theta the code places retailer A's fractile above retailer B's and mu - sigma <= zeta_B <= zeta_A <= mu + sigma.
- **Recorded:** regular points = 120; edge points = 90; points with the same shares in both periods = 144; gamma ladder = [0.05, 1.0, 10.0, 100.0, 1000.0, 10000.0, 1000000.0, 1000000000.0, 1000000000000.0, 1e+18, 1e+50, 1e+60]; theta nodes at the top rung = 32; region of the regular points = assumptions: A1, A11 with strict inequalities, I1, I2. c_B: [0.5, 3], multiples of 1/1000. c_A / c_B: [0.05, 0.98], multiples of 1/1000. mu: [5, 20], multiples of 1/1000. sigma / mu: [0.1, 0.95], multiples of 1/1000. p_B,t / c_B: [1.05, 4], multiples of 1/1000. p_A,t: (c_A / c_B) p_B,t plus 0.001 to 0.999 of the distance to p_B,t. beta: at most 0.45 / (largest price gap) and at most 0.5, so the share of B is at least 0.05. equal_shares option: the same price gap in both periods, a fraction of the smallest gap that A11 allows. theta: [0.001, 0.999]. gamma: log-uniform on [0.05, 50]. lambda_S: [0.001, 0.999]. never reached: equality in A11, p_A = p_B, theta at 0 or 1, a share of B below 0.05; region of the edge points = assumptions: A1, A11 with equality allowed, I1, I2. rule: each coordinate takes an extreme value with probability 1/2, otherwise a value of draw_exogenous_exact. c_A / c_B: 1/1000 or 999/1000. sigma / mu: 1/100 or 999/1000. p_B,t / c_B: 1001/1000 or 50. p_A,t: (c_A / c_B) p_B,t (equality in A11) or p_B,t (shares 1/2). beta x largest price gap: 1/1000000 or 499/1000, the latter gives a share of B of 1/1000. beta when both price gaps are zero: 1/1000000 or 5. theta: 0 or 1. gamma: 1/100 or 1000. lambda_S: 0 or 1. equal_shares option: a common price gap that is zero, binding in A11, or regular. p_B,2 = p_B,1 with probability 1/4; edge points with beta = 1/1000000 without a price gap = 5; edge points with beta = 5 without a price gap = 6; edge points with beta x largest price gap = 1/1000000 = 15; edge points with beta x largest price gap = 499/1000 = 16; edge points with c A / c B = 1/1000 = 28; edge points with c A / c B = 999/1000 = 17; edge points with equality in A11 in both periods = 4; edge points with equality in A11 in period 1 = 16; edge points with equality in A11 in period 2 = 12; edge points with gamma = 1/100 = 24; edge points with gamma = 1000 = 16; edge points with lambda S = 0 = 24; edge points with lambda S = 1 = 23; edge points with p A = p B in period 1 = 24; edge points with p A = p B in period 2 = 22; edge points with p B / c B = 1001/1000 in period 1 = 22; edge points with p B / c B = 1001/1000 in period 2 = 19; edge points with p B / c B = 50 in period 1 = 23; edge points with p B / c B = 50 in period 2 = 31; edge points with same shares in both periods = 64; edge points with sigma / mu = 1/100 = 27; edge points with sigma / mu = 999/1000 = 15; edge points with theta = 0 = 26; edge points with theta = 1 = 21
