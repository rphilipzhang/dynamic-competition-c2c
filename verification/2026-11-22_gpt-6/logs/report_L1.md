# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k L1 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**6 of 6 checks passed.** pytest exit status: 0.

A *direct* check tests a part of the result itself. A *supporting* check confirms a tool that direct checks rely on, for example that a closed form equals the model at random points. Every check computes at finitely many points. For a result that holds for all parameters it is a search for counterexamples. For a result that holds for a parameter large enough it probes large values of that parameter.

## Results of theory.md

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [L1](#l1) | 3/3 | 3/3 |
| [L2](#l2) | – | 1/1 |
| [L3](#l3) | – | 1/1 |
| [L4](#l4) | – | 1/1 |
| [P1](#p1) | – | 1/1 |
| [P2](#p2) | – | 1/1 |
| [P3](#p3) | – | – |
| [P4](#p4) | – | – |
| [P5](#p5) | – | 1/1 |
| [P6](#p6) | – | 1/1 |
| [LA1](#la1) | – | – |
| [LA2](#la2) | – | – |
| [P7](#p7) | – | – |
| [P8](#p8) | – | – |
| [P9](#p9) | – | – |
| [LB1](#lb1) | – | 1/1 |

## Numerical statements of the paper

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [F1](#f1) | – | – |
| [FB1](#fb1) | – | – |
| [N1](#n1) | – | – |
| [N2](#n2) | – | – |
| [N3](#n3) | – | – |
| [N4](#n4) | – | – |
| [N5](#n5) | – | – |
| [N6](#n6) | – | – |

## Checks by ID

### L1

- direct (L1.eq): [test_benchmark_equilibrium_of_lemma_1](#check-1): passed
- direct (L1.unique): [test_first_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[0]](#check-2): passed
- direct (L1.unique): [test_second_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[0]](#check-3): passed
- supporting: [test_benchmark_profit_polynomials_match_lemma_1](#check-4): passed
- supporting: [test_expected_leftovers_in_the_code_follow_from_the_model](#check-5): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-6): passed

### L2

- supporting: [test_expected_leftovers_in_the_code_follow_from_the_model](#check-5): passed

### L3

- supporting: [test_expected_leftovers_in_the_code_follow_from_the_model](#check-5): passed

### L4

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-6): passed

### P1

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-6): passed

### P2

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-6): passed

### P5

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-6): passed

### P6

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-6): passed

### LB1

- supporting: [test_expected_leftovers_in_the_code_follow_from_the_model](#check-5): passed

## Checks

<a id="check-1"></a>
### `tests/test_equilibria_from_primitives.py::test_benchmark_equilibrium_of_lemma_1`

- **Outcome:** passed (8.9 s)
- **Tests directly:** L1.eq
- **What:** Lemma 1: the claimed order quantities of the single-period game without C2C interactions.
- **Points:** 109 points (seed 101). 78 regular points of `draw_exogenous`, 60 under the uniform distribution and 6 under each of the triangular, beta(2,5) and truncated normal ones, and 31 edge points of `draw_edge_exact`, 30 uniform and 1 truncated normal. One game at the first-period prices of every point and, under the uniform distribution, one more at its second-period prices: 199 games.
- **Computed:** the quantities of `section4.claimed_benchmark` through the quantile function, and `primitives.nash_gap` on [0, 1.5 (mu + sigma)] for the payoffs of `section4.Game` with scenario "0", built from the primitives.
- **Criterion:** both critical fractiles lie in [0, 1] with retailer A's the higher one (up to 1e-12 at edge points), no deviation gains more than 1e-8 mu, and each best response lies within 2e-5 max(1, mu) of the claimed quantity.
- **Recorded:** regular points = 78; edge points = 31; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; games checked = 199; tolerance on relative gain from deviation = 1e-08

<a id="check-2"></a>
### `tests/test_equilibria_from_primitives.py::test_first_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[0]`

- **Outcome:** passed (3.3 s)
- **Tests directly:** L1.unique
- **What:** Uniqueness in the first period of Lemma 1 (case 0), Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 28 points (seed 404), 15 regular (12 uniform, 1 under each other distribution) and 13 edge (12 uniform, 1 truncated normal).
- **Computed:** `section4.scan_fixed_points` for T(y_B) = BR_B(BR_A(y_B)) of the two-period payoffs on [0, 1.5 (mu + sigma)], with 21 coarse and 41 fine nodes and a best-response grid of 801 under the uniform distribution, 9, 15 and 101 under the others.
- **Criterion:** T(y_B) - y_B is positive at the lowest node and negative at the highest, its sign changes between exactly one pair of neighbouring nodes, and that pair encloses the claimed y_B up to the noise allowance 1e-6 max(mu + sigma, max T). Two equilibria between the same two neighbouring nodes would not be seen.
- **Recorded:** regular points = 15; edge points = 13; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; evaluations of the composed best response = 1584

<a id="check-3"></a>
### `tests/test_equilibria_from_primitives.py::test_second_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[0]`

- **Outcome:** passed (3.4 s)
- **Tests directly:** L1.unique
- **What:** Uniqueness in the second period of Lemma 1 (case 0, the benchmark game at the second-period prices), Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 28 points (seed 505), 15 regular (12 uniform, 1 under each other distribution) and 13 edge (12 uniform, 1 beta(2,5)), each with one random first-period sales state (seed 405) drawn as in the second-period equilibrium check.
- **Computed:** `section4.scan_fixed_points` for the composed best-response map of the second-period payoffs on [0, 1.5 (mu + sigma)(1 + gamma)], with the nodes and grids of the first-period scan.
- **Criterion:** as in the first-period scan, with the claimed y^0_{B,2} + Z_{B,2} in place of y_B: one change of sign, from positive to negative, between two neighbouring nodes that enclose the claim up to the noise allowance 1e-6 max(mu + sigma, max T).
- **Recorded:** regular points = 15; edge points = 13; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; evaluations of the composed best response = 1584

<a id="check-4"></a>
### `tests/test_port_matches_paper.py::test_benchmark_profit_polynomials_match_lemma_1`

- **Outcome:** passed (0.2 s)
- **Supports:** L1.eq
- **What:** Benchmark profits pi^0 = (p - c) y^0 - p E[L^0] at the equilibrium of Lemma 1.
- **Points:** 25 random rational parameter points (seed 1), at their second-period prices. The points need not satisfy the assumptions of the paper.
- **Computed:** pi^0_A and pi^0_B from this file's transcription of Lemma 1 and of the end of its proof, and `pfta_t2_case1` and `pftb_t2_case1` of `c2c.closed_form`, all in exact rational arithmetic. Three LaTeX strings of Lemma 1 and its proof are quoted.
- **Criterion:** both profits are equal as rational numbers at every point, and every quoted string occurs verbatim, up to whitespace, in the LaTeX source in `paper/`.
- **Recorded:** exact rational points = 25

<a id="check-5"></a>
### `tests/test_port_matches_paper.py::test_expected_leftovers_in_the_code_follow_from_the_model`

- **Outcome:** passed (0.0 s)
- **Supports:** L1, L2, L3, LB1
- **What:** The two expected-leftover expressions used throughout `c2c.closed_form`.
- **Points:** none. The check is symbolic in the positive symbols a_A, a_B, zeta_A, zeta_B, theta, mu and sigma.
- **Computed:** E[(y_i - D_i)^+] at the order quantities of Lemmas 1, 2, 3 and B.1, by SymPy integration of the demand system of Section 3 over X ~ U[mu - sigma, mu + sigma] for mu - sigma <= zeta_B <= zeta_A <= mu + sigma, and `_leftover_high` and `_leftover_low` of `c2c.closed_form` in the same symbols.
- **Criterion:** each of the two differences expands to exactly 0.

<a id="check-6"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]`

- **Outcome:** passed (0.0 s)
- **Supports:** L1.eq, L4.a, P1.i, P2.a, P2.b, P5.b, P6.b
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 34
