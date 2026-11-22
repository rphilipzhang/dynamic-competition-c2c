# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k P9 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**5 of 5 checks passed.** pytest exit status: 0.

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
| [LA1](#la1) | – | 3/3 |
| [LA2](#la2) | – | 3/3 |
| [P7](#p7) | – | – |
| [P8](#p8) | – | 3/3 |
| [P9](#p9) | 2/2 | 3/3 |
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

- supporting: [test_first_period_machinery_reproduces_the_model](#check-1): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-4): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-5): passed

### LA2

- supporting: [test_first_period_machinery_reproduces_the_model](#check-1): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-4): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-5): passed

### P8

- supporting: [test_first_period_machinery_reproduces_the_model](#check-1): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-4): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-5): passed

### P9

- direct (P9.a): [test_proposition_9a_price_path_of_scenario_s](#check-2): passed
- direct (P9.b): [test_proposition_9b_price_path_of_scenario_n](#check-3): passed
- supporting: [test_first_period_machinery_reproduces_the_model](#check-1): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-4): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-5): passed

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
### `tests/test_section_5_propositions.py::test_proposition_9a_price_path_of_scenario_s`

- **Outcome:** passed (9.5 s)
- **Tests directly:** P9.a
- **What:** Proposition 9(a): in Scenario S, for gamma large, the equilibrium prices are the lower bound in period 1 and the upper bound in period 2, for both retailers.
- **Points:** 20 markets of `draw_market` (seed 5303), gamma = 1, 10, 100, 1e3, 1e4, 1e5 and 1e6.
- **Computed:** the reduced payoffs (two-period profits at the orders of Lemma A.1(a), continuation `SecondPeriodS`) on a grid of 101 own by 41 rival prices, a search of each price interval, best-response iteration from the four corners, the second-period price game from the primitives on a 41 by 41 grid at the sales for seed demand mu - sigma, mu and mu + sigma, and the advantage of p_lo, the smallest loss per unit of price change to another grid price.
- **Criterion:** the claim holds at a market and gamma if `_orders_s` confirms every grid pair, p_lo is each retailer's best reply to every rival grid price, the search finds no relative gain above 1e-8, the search and iterations end within 1e-12 p_hi of (p_lo, p_lo), each grid game of period 2 has (p_hi, p_hi) as its only pure equilibrium, and p_lo = p_{i,1} < p_{i,2} = p_hi. Once it holds it must keep holding, it must hold at all markets from 1e5 on and fail at gamma = 1 somewhere, and the advantage must be positive at 1e5 and grow by a factor in [9.9, 10.1] from 1e5 to 1e6.
- **Recorded:** markets = 20; gamma ladder = [1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0]; markets where the claim holds by gamma = [1, 9, 15, 20, 20, 20, 20]; holds in all markets from gamma = 1000.0; smallest advantage of lower bound over gamma p hi beta mu at gamma 1e5 = 0.414; max deviation from tenfold growth of the advantage = 0.0002

<a id="check-3"></a>
### `tests/test_section_5_propositions.py::test_proposition_9b_price_path_of_scenario_n`

- **Outcome:** passed (15.0 s)
- **Tests directly:** P9.b
- **What:** Proposition 9(b): in Scenario N, for a fixed theta < 1 and gamma large, p_lo < p_{i,2} < p_{i,1} < p_hi for both retailers.
- **Points:** 5 markets of `draw_market` (seed 5304) with theta scaled to 0.9 theta, gamma = 100, 1e3 and 1e4. Above 1e4 first-period prices are located less accurately.
- **Computed:** the first-period price equilibrium of the reduced payoffs (`_orders_n`, `SecondPeriodN`) by best-response iteration over the price interval from (p_lo, p_hi) and (p_hi, p_lo), and the second-period prices at the sales of 201 seed demands on the support.
- **Criterion:** the claim holds at a market and gamma if the two runs agree within 1e-4 p_hi, the tables report no problem, the first-order conditions are solved at 41 own prices of each retailer and at the equilibrium, searches of the order intervals there and of the second-period price intervals at the mean seed demand find no relative gain above 1e-8 and no best response farther than 2e-5 (mu + sigma) or 2e-5 p_hi, and p_lo < min p_{i,2} and max p_{i,2} < p_{i,1} < p_hi. It must hold at all markets from gamma = 1e3 on, and the gap p_{i,1} - max p_{i,2} must change from 1e3 to 1e4 by at most a quarter of its change from 100 to 1e3.
- **Recorded:** markets = 5; gamma ladder = [100.0, 1000.0, 10000.0]; markets where the claim holds by gamma = [5, 5, 5]; holds in all markets from gamma = 100.0

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
### `tests/test_section_5_transcription.py::test_claims_of_section_5_are_transcribed_from_the_paper`

- **Outcome:** passed (0.0 s)
- **Supports:** LA1, LA2, P8, P9
- **What:** `section5.claimed_*` against a second transcription of Lemmas A.1 and A.2 and Propositions 8 and 9.
- **Points:** 500 markets of `draw_market` (seed 5400), each with first-period prices uniform on the price box, gamma log-uniform on [1, 1e6], and two sorted prices uniform on the box for the price-path predicates.
- **Computed:** the 17 LaTeX strings of `QUOTES` against the LaTeX source in `paper/`, and both transcriptions of the limit prices, nu_i, the claimed first-period orders of Scenarios S and N, the ratio of the two sides of (A.22), the bound in (A.23) and the first-period limit prices of the proof of Proposition 9.
- **Criterion:** every string occurs verbatim, up to whitespace, every difference is at most 1e-12 max(1, |value|), the claimed Scenario S prices are (p_lo, p_lo) and (p_hi, p_hi), the predicates of Proposition 9 accept and reject the test pairs as its inequalities require, and `CLAIMED_SLOPE_SIGNS` equals the table written from Proposition 8.
- **Recorded:** latex strings found in the paper = 17; random points = 500
