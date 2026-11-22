# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k LA1 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**7 of 7 checks passed.** pytest exit status: 0.

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
| [LA1](#la1) | 4/4 | 3/3 |
| [LA2](#la2) | – | 3/3 |
| [P7](#p7) | – | – |
| [P8](#p8) | – | 3/3 |
| [P9](#p9) | – | 3/3 |
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

### LA1

- direct (LA1.a): [test_lemma_a1a_best_response_iteration_returns_to_the_claimed_orders](#check-2): passed
- direct (LA1.a): [test_lemma_a1a_first_period_inventory_equilibrium_of_scenario_s](#check-3): passed
- direct (LA1.b): [test_lemma_a1b_upper_bound_is_the_unique_second_period_price_equilibrium](#check-5): passed
- direct (LA1.b): [test_second_period_inventory_equilibrium_at_any_price_pair[S]](#check-6): passed
- supporting: [test_first_period_machinery_reproduces_the_model](#check-1): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-4): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-7): passed

### LA2

- supporting: [test_first_period_machinery_reproduces_the_model](#check-1): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-4): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-7): passed

### P8

- supporting: [test_first_period_machinery_reproduces_the_model](#check-1): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-4): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-7): passed

### P9

- supporting: [test_first_period_machinery_reproduces_the_model](#check-1): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-4): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-7): passed

## Checks

<a id="check-1"></a>
### `tests/test_section_5_first_period.py::test_first_period_machinery_reproduces_the_model`

- **Outcome:** passed (0.8 s)
- **Supports:** LA1, LA2, P8, P9
- **What:** Three numerical tools of `section5` against direct computations (seed 5200).
- **Points:** (1) 300 markets of `draw_market`, a share uniform on [0.02, 0.98], orders uniform on [0, 1.5 (mu + sigma)]. (2) 24 markets, gamma log-uniform on [10, 1e4], total sales R_1 uniform on [0.2, 1] (mu + sigma). (3) In each of these, 5 order pairs per scenario at prices uniform on the box, orders 0.6 to 1.1 times the claimed ones, in Scenario S gamma at least 100 and only pairs at which both retailers charge p_hi at every sales state.
- **Computed:** (1) expected sales from `first_period_nodes` and from `primitives.Uniform`. (2) prices, profits and slope in R_1 of `SecondPeriodN` and of a direct solution of the price game from the primitives, the slope by a central difference of step 1e-3 R_1. (3) `marginal_profits` and central differences of `first_period_profits` of step 1e-6 (mu + sigma).
- **Criterion:** (1) errors at most 1e-13 (mu + sigma), weights summing to 1 within 1e-13. (2) no table problem, prices within 1e-10 p_hi, profits within 1e-10 and slopes within 1e-7 relative. (3) errors at most 1e-6 p_hi (1 + gamma), 120 pairs in Scenario N, 100 or more in S.
- **Recorded:** node points = 300; price game states = 24; order pairs scenario N = 120; order pairs scenario S = 120

<a id="check-2"></a>
### `tests/test_section_5_first_period.py::test_lemma_a1a_best_response_iteration_returns_to_the_claimed_orders`

- **Outcome:** passed (0.3 s)
- **Tests directly:** LA1.a
- **What:** Uniqueness probe for Lemma A.1(a): alternating best responses from several starts.
- **Points:** 10 markets of `draw_market` (seed 5202), one first-period price pair each, gamma = 1e3 and 1e5, 3 starting pairs per case: 60 runs. A starting order of retailer i is uniform on [L_i / gamma, 1.5 (mu + sigma)], with L_i the dominance number of `SecondPeriodS`. Below L_i / gamma the rival of a deviating retailer could sell so little that it would not charge the upper bound in period 2, and the continuation used here would not apply.
- **Computed:** alternating best replies over [0, 1.5 (mu + sigma)], found from payoff values with `argmax_on_interval`, for at most 30 sweeps or until a sweep moves less than 1e-9 (mu + sigma). The width of the excluded strip is recorded.
- **Criterion:** L_i / gamma < alpha_i (mu - sigma) for both retailers, every run ends within 1e-4 (mu + sigma) of the claimed pair in the sum of the two distances, and every rival order at which a best reply was evaluated lies above that rival's strip.
- **Recorded:** runs = 60; widest excluded strip over order interval = 0.0004

<a id="check-3"></a>
### `tests/test_section_5_first_period.py::test_lemma_a1a_first_period_inventory_equilibrium_of_scenario_s`

- **Outcome:** passed (3.6 s)
- **Tests directly:** LA1.a
- **What:** Lemma A.1(a): for gamma large the first-period inventory subgame of Scenario S has the equilibrium y_A = (alpha_A + theta alpha_B) zeta_A - theta alpha_B zeta_B, y_B = alpha_B zeta_B with zeta_i = F^-1(1 - c_i / (p_{i,1} + gamma (p_hi - c_i))), and the form is exact.
- **Points:** 30 markets of `draw_market` (seed 5201), one first-period price pair each, uniform on the price box, gamma = 1, 10, 100, 1e3, 1e4, 1e5 and 1e6.
- **Computed:** at the claimed orders, with the continuation of `SecondPeriodS`, whether gamma times each retailer's smallest first-period sales exceeds its dominance number, the best deviation found by `primitives.best_response` on 4001 points of [0, 1.5 (mu + sigma)], and both marginal profits of the model, whose vanishing detects an error of order 1 / gamma.
- **Criterion:** the claim holds at a market and gamma if that dominance condition holds, the gain is at most 1e-8 p_hi (mu + sigma)(1 + gamma), each best response lies within 2e-5 (mu + sigma) of the claim and each marginal profit is at most 1e-12 (10 + gamma) c_i. Once it holds at a market it must hold at every larger gamma, it must hold at all 30 markets from gamma = 1e5 on, and it must fail at gamma = 1 at one market or more.
- **Recorded:** markets = 30; gamma ladder = [1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0]; points where the claim holds by gamma = [3, 25, 30, 30, 30, 30, 30]; holds at all points from gamma = 100.0; tolerance on relative gain from deviation = 1e-08

<a id="check-4"></a>
### `tests/test_section_5_second_period.py::test_helpers_agree_with_the_primitives`

- **Outcome:** passed (0.2 s)
- **Supports:** LA1, LA2, P8, P9
- **What:** `section5.expected_sales` and `section5.benchmark_orders` against the primitives.
- **Points:** 2,000 markets of `draw_market` (seed 5100), each with C2C demands that are zero or uniform on [0, 3 (mu + sigma)], orders uniform on [0, 2 (mu + sigma)] above them, a share uniform on [0.02, 0.98] and a price pair uniform on the price box.
- **Computed:** expected sales from `section5.expected_sales` and from `primitives.Uniform`, and order quantities from `benchmark_orders` and from `section4.claimed_benchmark`.
- **Criterion:** every difference is at most 1e-13 (mu + sigma), and retailer B has the higher critical fractile at one price pair or more.
- **Recorded:** points = 2000; price pairs where retailer B has the higher fractile = 130

<a id="check-5"></a>
### `tests/test_section_5_second_period.py::test_lemma_a1b_upper_bound_is_the_unique_second_period_price_equilibrium`

- **Outcome:** passed (2.9 s)
- **Tests directly:** LA1.b
- **What:** Lemma A.1(b): in Scenario S, given positive first-period sales of both retailers and gamma large, the second-period price game has the unique pure equilibrium (p_hi, p_hi).
- **Points:** 30 markets of `draw_market` (seed 5102), one sales state each with R_{A,1} and R_{B,1} uniform on [0.02, 1] (mu + sigma) / 2, gamma = 1, 10, 100, 1e3, 1e4, 1e5 and 1e6.
- **Computed:** second-period profits from the primitives at the inventory equilibrium, on a 61 by 61 price grid and on each whole price interval, best-response iteration from the four corners of the box and from one random pair (at most 20 sweeps), and the advantage of p_hi: the smallest payoff loss from another grid price per unit of price difference.
- **Criterion:** the claim holds at a market and gamma if (p_hi, p_hi) is the only pure equilibrium of the grid game, the search finds no relative gain above 1e-8 and no best response farther than 1e-12 p_hi, and every iteration ends within 1e-12 p_hi. Once it holds it must keep holding, it must hold at all markets from 1e5 on and fail at gamma = 1 at one market or more, and the advantage must be positive at 1e5 and grow from 1e5 to 1e6 by R_{i,1} per unit of gamma within a relative error of 1e-6.
- **Recorded:** markets = 30; gamma ladder = [1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0]; points where the claim holds by gamma = [17, 30, 30, 30, 30, 30, 30]; holds at all points from gamma = 10.0; smallest advantage of upper bound over gamma times sales at gamma 1e5 = 0.9998

<a id="check-6"></a>
### `tests/test_section_5_second_period.py::test_second_period_inventory_equilibrium_at_any_price_pair[S]`

- **Outcome:** passed (0.5 s)
- **Tests directly:** LA1.b
- **What:** Lemmas A.1(b) and A.2(b), last sentence of each: at given second-period prices and first-period sales the orders y^0_{i,2} + Z_{i,2} are the equilibrium of the inventory subgame, and each profit is pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2}.
- **Points:** 100 markets of `draw_market` (seed 5101), gamma log-uniform on [0.1, 1000], one sales state each, uniform on the triangle R_A, R_B >= 0, R_A + R_B <= mu + sigma. At every second point the prices are uniform on the price box. At the others they are drawn, where the box allows, from the pairs with c_A / p_A > c_B / p_B.
- **Computed:** from the primitives, `primitives.nash_gap` on [0, U] with U = max(Z_A, Z_B) + 1.5 (mu + sigma), the profits at the claimed orders, and at the first 20 points best-response iteration (801-point grid, at most 60 sweeps) from two random starting pairs.
- **Criterion:** no deviation gains more than 1e-8 p_hi U, each best response lies within 2e-5 U of the claim, the profit identity holds within 1e-11 p_hi U, every iteration ends within 1e-4 U of the claim, and retailer B has the higher fractile at 10 points or more.
- **Recorded:** points = 100; points where retailer B has the higher fractile = 25; tolerance on relative gain from deviation = 1e-08

<a id="check-7"></a>
### `tests/test_section_5_transcription.py::test_claims_of_section_5_are_transcribed_from_the_paper`

- **Outcome:** passed (0.0 s)
- **Supports:** LA1, LA2, P8, P9
- **What:** `section5.claimed_*` against a second transcription of Lemmas A.1 and A.2 and Propositions 8 and 9.
- **Points:** 500 markets of `draw_market` (seed 5400), each with first-period prices uniform on the price box, gamma log-uniform on [1, 1e6], and two sorted prices uniform on the box for the price-path predicates.
- **Computed:** the 17 LaTeX strings of `QUOTES` against the LaTeX source in `paper/`, and both transcriptions of the limit prices, nu_i, the claimed first-period orders of Scenarios S and N, the ratio of the two sides of (A.22), the bound in (A.23) and the first-period limit prices of the proof of Proposition 9.
- **Criterion:** every string occurs verbatim, up to whitespace, every difference is at most 1e-12 max(1, |value|), the claimed Scenario S prices are (p_lo, p_lo) and (p_hi, p_hi), the predicates of Proposition 9 accept and reject the test pairs as its inequalities require, and `CLAIMED_SLOPE_SIGNS` equals the table written from Proposition 8.
- **Recorded:** latex strings found in the paper = 17; random points = 500
