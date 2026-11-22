# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k LB1 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**8 of 8 checks passed.** pytest exit status: 0.

A *direct* check tests a part of the result itself. A *supporting* check confirms a tool that direct checks rely on, for example that a closed form equals the model at random points. Every check computes at finitely many points. For a result that holds for all parameters it is a search for counterexamples. For a result that holds for a parameter large enough it probes large values of that parameter.

## Results of theory.md

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [L1](#l1) | – | 1/1 |
| [L2](#l2) | – | 2/2 |
| [L3](#l3) | – | 2/2 |
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
| [LB1](#lb1) | 6/6 | 2/2 |

## Numerical statements of the paper

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [F1](#f1) | – | – |
| [FB1](#fb1) | – | 1/1 |
| [N1](#n1) | – | – |
| [N2](#n2) | – | – |
| [N3](#n3) | – | – |
| [N4](#n4) | – | – |
| [N5](#n5) | – | 1/1 |
| [N6](#n6) | – | – |

## Checks by ID

### L1

- supporting: [test_expected_leftovers_in_the_code_follow_from_the_model](#check-5): passed

### L2

- supporting: [test_expected_leftovers_in_the_code_follow_from_the_model](#check-5): passed
- supporting: [test_mixed_scenario_reduces_to_scenarios_s_and_n](#check-7): passed

### L3

- supporting: [test_expected_leftovers_in_the_code_follow_from_the_model](#check-5): passed
- supporting: [test_mixed_scenario_reduces_to_scenarios_s_and_n](#check-7): passed

### LB1

- direct (LB1.first): [test_first_period_equilibrium[G]](#check-1): passed
- direct (LB1.unique): [test_first_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[G]](#check-2): passed
- direct (LB1.second): [test_second_period_equilibrium_and_continuation_value[G]](#check-3): passed
- direct (LB1.unique): [test_second_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[G]](#check-4): passed
- direct (LB1.first): [test_mixed_scenario_code_matches_lemma_b1](#check-6): passed
- direct (LB1.first): [test_mixed_scenario_reduces_to_scenarios_s_and_n](#check-7): passed
- supporting: [test_expected_leftovers_in_the_code_follow_from_the_model](#check-5): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]](#check-8): passed

### FB1

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]](#check-8): passed

### N5

- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]](#check-8): passed

## Checks

<a id="check-1"></a>
### `tests/test_equilibria_from_primitives.py::test_first_period_equilibrium[G]`

- **Outcome:** passed (7.8 s)
- **Tests directly:** LB1.first
- **What:** First period of Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 109 points (seed 303), 78 regular (60 uniform, 6 under each other distribution) and 31 edge (30 uniform, 1 triangular).
- **Computed:** the claimed orders and critical fractiles of `section4.claimed_first_period`, and `primitives.nash_gap` on [0, 1.5 (mu + sigma)] for the two-period payoffs of `section4.Game`, built from the primitives with the continuation pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2}.
- **Criterion:** both fractiles lie in [0, 1] with retailer A's the higher one (up to 1e-12 at edge points), and with scale mu (1 + gamma) no deviation gains more than 1e-8 times the scale and each best response lies within 2e-5 max(1, scale) of the claim.
- **Recorded:** regular points = 78; edge points = 31; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; tolerance on relative gain from deviation = 1e-08

<a id="check-2"></a>
### `tests/test_equilibria_from_primitives.py::test_first_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[G]`

- **Outcome:** passed (3.4 s)
- **Tests directly:** LB1.unique
- **What:** Uniqueness in the first period of Lemma 1 (case 0), Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 28 points (seed 404), 15 regular (12 uniform, 1 under each other distribution) and 13 edge (12 uniform, 1 truncated normal).
- **Computed:** `section4.scan_fixed_points` for T(y_B) = BR_B(BR_A(y_B)) of the two-period payoffs on [0, 1.5 (mu + sigma)], with 21 coarse and 41 fine nodes and a best-response grid of 801 under the uniform distribution, 9, 15 and 101 under the others.
- **Criterion:** T(y_B) - y_B is positive at the lowest node and negative at the highest, its sign changes between exactly one pair of neighbouring nodes, and that pair encloses the claimed y_B up to the noise allowance 1e-6 max(mu + sigma, max T). Two equilibria between the same two neighbouring nodes would not be seen.
- **Recorded:** regular points = 15; edge points = 13; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; evaluations of the composed best response = 1584

<a id="check-3"></a>
### `tests/test_equilibria_from_primitives.py::test_second_period_equilibrium_and_continuation_value[G]`

- **Outcome:** passed (7.7 s)
- **Tests directly:** LB1.second
- **What:** Second period of Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 109 points (seed 202), 78 regular (60 uniform, 6 under each other distribution) and 31 edge (30 uniform, 1 beta(2,5)). One first-period sales state per point, R_A uniform on [0, mu + sigma] and R_B uniform on [0, mu + sigma - R_A].
- **Computed:** the claimed orders y^0_{i,2} + Z_{i,2}, `primitives.nash_gap` on [0, 1.5 (mu + sigma)(1 + gamma)] for the second-period payoffs of `section4.Game`, and each retailer's profit there, all from the primitives.
- **Criterion:** with scale mu (1 + gamma), no deviation gains more than 1e-8 times the scale, each best response lies within 2e-5 max(1, scale) of the claim, and each profit differs from pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2} by at most 1e-9 times the scale.
- **Recorded:** regular points = 78; edge points = 31; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']

<a id="check-4"></a>
### `tests/test_equilibria_from_primitives.py::test_second_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[G]`

- **Outcome:** passed (3.4 s)
- **Tests directly:** LB1.unique
- **What:** Uniqueness in the second period of Lemma 1 (case 0, the benchmark game at the second-period prices), Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 28 points (seed 505), 15 regular (12 uniform, 1 under each other distribution) and 13 edge (12 uniform, 1 beta(2,5)), each with one random first-period sales state (seed 405) drawn as in the second-period equilibrium check.
- **Computed:** `section4.scan_fixed_points` for the composed best-response map of the second-period payoffs on [0, 1.5 (mu + sigma)(1 + gamma)], with the nodes and grids of the first-period scan.
- **Criterion:** as in the first-period scan, with the claimed y^0_{B,2} + Z_{B,2} in place of y_B: one change of sign, from positive to negative, between two neighbouring nodes that enclose the claim up to the noise allowance 1e-6 max(mu + sigma, max T).
- **Recorded:** regular points = 15; edge points = 13; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; evaluations of the composed best response = 1584

<a id="check-5"></a>
### `tests/test_port_matches_paper.py::test_expected_leftovers_in_the_code_follow_from_the_model`

- **Outcome:** passed (0.0 s)
- **Supports:** L1, L2, L3, LB1
- **What:** The two expected-leftover expressions used throughout `c2c.closed_form`.
- **Points:** none. The check is symbolic in the positive symbols a_A, a_B, zeta_A, zeta_B, theta, mu and sigma.
- **Computed:** E[(y_i - D_i)^+] at the order quantities of Lemmas 1, 2, 3 and B.1, by SymPy integration of the demand system of Section 3 over X ~ U[mu - sigma, mu + sigma] for mu - sigma <= zeta_B <= zeta_A <= mu + sigma, and `_leftover_high` and `_leftover_low` of `c2c.closed_form` in the same symbols.
- **Criterion:** each of the two differences expands to exactly 0.

<a id="check-6"></a>
### `tests/test_port_matches_paper.py::test_mixed_scenario_code_matches_lemma_b1`

- **Outcome:** passed (0.3 s)
- **Tests directly:** LB1.first
- **What:** Mixed scenario of Online Appendix B: Lemma B.1.
- **Points:** 25 random rational parameter points (seed 4), each with a weight lambda_S drawn from the multiples of 1/1000 in [0, 1] (seed 40) and lambda_N = 1 - lambda_S.
- **Computed:** first-period order quantities and total two-period profits of both retailers from this file's transcription of Lemma B.1, and from `find_general_exo` of `c2c.closed_form`, in exact rational arithmetic. Four LaTeX strings of Online Appendix B are quoted.
- **Criterion:** the four values are equal as rational numbers at every point, and every quoted string occurs verbatim, up to whitespace, in the LaTeX source in `paper/`.
- **Recorded:** exact rational points = 25

<a id="check-7"></a>
### `tests/test_port_matches_paper.py::test_mixed_scenario_reduces_to_scenarios_s_and_n`

- **Outcome:** passed (0.1 s)
- **Tests directly:** LB1.first
- **Supports:** L2, L3
- **What:** Online Appendix B: Scenario S is the mixed scenario with weights (1, 0) and Scenario N is the mixed scenario with weights (0, 1).
- **Points:** 25 random rational parameter points (seed 5).
- **Computed:** `find_general_exo` with weights (1, 0) and (0, 1), and the order quantities and total profits of `first_period_s`, `spfta_t1`, `spftb_t1` and of `first_period_n`, `npfta_t1`, `npftb_t1`, with the branch of the lemmas forced, in exact rational arithmetic. The sentence of Online Appendix B on the Scenario S case is quoted.
- **Criterion:** both pairs of four-value tuples are equal as rational numbers at every point, and the quoted sentence occurs verbatim, up to whitespace, in the LaTeX source in `paper/`.
- **Recorded:** exact rational points = 25

<a id="check-8"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]`

- **Outcome:** passed (0.0 s)
- **Supports:** LB1.first, FB1, N5
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points edge = 100; points where retailer B has the higher fractile = 0
