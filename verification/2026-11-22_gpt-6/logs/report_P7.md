# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k P7 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

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
| [P7](#p7) | 2/2 | 1/1 |
| [P8](#p8) | – | – |
| [P9](#p9) | – | – |
| [LB1](#lb1) | – | – |

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

### P7

- direct (P7.a): [test_proposition_7a_shape_in_the_own_price](#check-1): passed
- direct (P7.b): [test_proposition_7b_shape_in_the_rival_price](#check-2): passed
- supporting: [test_second_period_orders_of_this_file_are_the_equilibrium_of_the_model](#check-3): passed

## Checks

<a id="check-1"></a>
### `tests/test_proposition_7_shapes.py::test_proposition_7a_shape_in_the_own_price`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P7.a
- **What:** Proposition 7(a), read literally: y_{i,2} as a function of the own second-period price.
- **Points:** 4,000 points of `draw_bounded_prices` (seed 1010), each with one sales state (R_A uniform on [0, mu + sigma], R_B on [0, mu + sigma - R_A]) and one rival price uniform on [p_lo, p_hi], Scenarios S and N, both retailers: 16,000 curves on a grid of 1,501 own prices between the price bounds.
- **Computed:** the orders of `second_period_orders` (Lemma 1 for either ordering of the fractiles plus Z_{i,2}) and the signs of their steps, ignoring steps of absolute value at most 1e-11 (1 + largest order on the grid). The number of accepted curves that end with a positive step is recorded. The proof implies that there are none.
- **Criterion:** every curve has no positive step, or its steps turn from positive to negative exactly once or exactly twice.
- **Recorded:** curves = 16000; points with theta equal to 0 = 490; points with theta equal to 1 = 495; sampled region = assumptions: A1, A10, A12, A13. c_B, c_A / c_B, mu, sigma / mu: as in draw_exogenous. beta: uniform on [0.02, 0.6]. p_hi: between 1/(2 beta) + 1.01 w and 1/(2 beta) + 2 w, with w = (mu + sigma)(c_A + 2 c_B)/(3 mu). p_lo: uniform on the interval that A12 and A13 leave, shrunk by one thousandth at both ends. theta: 0 with probability 1/8, 1 with probability 1/8, otherwise uniform on (0, 1). gamma: log-uniform on [0.05, 50]; 1 interior local maxima = 666; 2 interior local maxima = 2; decreasing = 15332; accepted curves that end with a positive slope = 0

<a id="check-2"></a>
### `tests/test_proposition_7_shapes.py::test_proposition_7b_shape_in_the_rival_price`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P7.b
- **What:** Proposition 7(b): y_{i,2} as a function of the rival's second-period price.
- **Points:** the 4,000 points, sales states and fixed prices of the 7(a) check, Scenarios S and N, both retailers: 16,000 curves on a grid of 1,501 rival prices.
- **Computed:** the orders of `second_period_orders` and the signs of their steps, ignoring steps of absolute value at most 1e-11 (1 + largest order on the grid).
- **Criterion:** every curve has no negative step, or its steps are negative first and positive afterwards, with exactly one change of sign.
- **Recorded:** curves = 16000; points with theta equal to 0 = 490; points with theta equal to 1 = 495; sampled region = assumptions: A1, A10, A12, A13. c_B, c_A / c_B, mu, sigma / mu: as in draw_exogenous. beta: uniform on [0.02, 0.6]. p_hi: between 1/(2 beta) + 1.01 w and 1/(2 beta) + 2 w, with w = (mu + sigma)(c_A + 2 c_B)/(3 mu). p_lo: uniform on the interval that A12 and A13 leave, shrunk by one thousandth at both ends. theta: 0 with probability 1/8, 1 with probability 1/8, otherwise uniform on (0, 1). gamma: log-uniform on [0.05, 50]; decreasing then increasing = 205; increasing = 15795

<a id="check-3"></a>
### `tests/test_proposition_7_shapes.py::test_second_period_orders_of_this_file_are_the_equilibrium_of_the_model`

- **Outcome:** passed (1.1 s)
- **Supports:** P7.a, P7.b
- **What:** Prerequisite of both parts: `second_period_orders` against the model.
- **Points:** 300 points of `draw_bounded_prices` (seed 1020), each with a pair of second-period prices uniform on [p_lo, p_hi] and one sales state drawn as above, Scenarios S and N: 600 second-period games.
- **Computed:** `second_period_orders`, the quantities of `section4.claimed_benchmark` plus the C2C-induced demand Z_{i,2}, and `primitives.nash_gap` on [0, 1.5 (mu + sigma)(1 + gamma)] for the second-period payoffs of `section4.Game`, built from the primitives.
- **Criterion:** the orders agree with the claimed ones within 1e-12 relative to the order, with scale mu (1 + gamma) no deviation gains more than 1e-8 times the scale and each best response lies within 2e-5 max(1, scale) of the order, and retailer B has the higher critical fractile at some but not all of the 300 points.
- **Recorded:** second period games = 600; points where retailer B has the higher fractile = 22
