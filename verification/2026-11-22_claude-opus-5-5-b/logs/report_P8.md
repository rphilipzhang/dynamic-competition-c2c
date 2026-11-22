# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k P8 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**6 of 6 checks passed.** pytest exit status: 0.

A *direct* check tests a part of the result itself. A *supporting* check confirms a tool that direct checks rely on, for example that a closed form equals the model at random points. Every check computes at finitely many points. For a result that holds for all parameters it is a search for counterexamples. For a result that holds for a parameter large enough it probes large values of that parameter.

The selection counts only P8. Other IDs that the selected checks name appear only in the description of each check below.

## Results of theory.md

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [P8](#p8) | 3/3 | 3/3 |

## Checks by ID

### P8

- direct (P8.a): [test_proposition_8a_orders_of_scenario_s_fall_in_own_price_and_rise_in_rival_price](#check-2): passed
- direct (P8.b2): [test_proposition_8b2_reversal_when_gamma_times_one_minus_theta_is_bounded](#check-3): passed
- direct (P8.b1, P8.b2): [test_proposition_8b_orders_of_scenario_n_at_fixed_theta](#check-4): passed
- supporting: [test_first_period_machinery_reproduces_the_model](#check-1): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-5): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-6): passed

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
- **At the level of rounding error (differs between machines):** max error node quadrature = 2.67904e-16; max relative error tabulated price = 1.70669e-14; max relative error tabulated profit = 3.9577e-14; max relative error tabulated slope = 2.97788e-11; max relative error marginal profit = 8.89555e-11

<a id="check-2"></a>
### `tests/test_section_5_propositions.py::test_proposition_8a_orders_of_scenario_s_fall_in_own_price_and_rise_in_rival_price`

- **Outcome:** passed (0.4 s)
- **Tests directly:** P8.a
- **What:** Proposition 8(a): in Scenario S, for gamma large, y_{i,1} decreases in p_{i,1} and increases in p_{j,1}, for both retailers.
- **Points:** 20 markets of `draw_market` (seed 5300), a 9 by 9 grid of first-period prices that covers the price box, borders included, gamma = 1, 10, 100, 1e3, 1e4, 1e5 and 1e6.
- **Computed:** the orders of Lemma A.1(a) at all 81 pairs with the flags of `_orders_s` (both marginal profits within 1e-12 (10 + gamma) c_i and the continuation of `SecondPeriodS` pinned down), the four difference quotients between neighbouring grid points, and at gamma = 1e5 and 1e6 a 1001-point search of each order interval at one random grid pair.
- **Criterion:** the claim holds at a market and gamma if all 81 flags are true, every quotient has the claimed sign, and at the two largest gammas the search finds no relative gain above 1e-8 and no best response farther than 2e-5 (mu + sigma). It must hold at all markets from gamma = 1e5 on, and in each market the largest relative distance of a quotient from -beta (mu + sigma) or +beta (mu + sigma), its value when no retailer stocks out, must shrink at least fivefold from gamma = 1e5 to 1e6.
- **Recorded:** markets = 20; price pairs per market = 81; gamma ladder = [1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0]; markets where the claim holds by gamma = [2, 11, 16, 20, 20, 20, 20]; holds in all markets from gamma = 1000.0; largest relative distance of a slope from its limit at gamma 1e6 = 5.7e-07; smallest factor by which that distance shrinks from gamma 1e5 to 1e6 = 10.0

<a id="check-3"></a>
### `tests/test_section_5_propositions.py::test_proposition_8b2_reversal_when_gamma_times_one_minus_theta_is_bounded`

- **Outcome:** passed (2.8 s)
- **Tests directly:** P8.b2
- **What:** Under condition (A.22) of the Online Appendix, Proposition 8(b2) gives an open set of first-period price pairs on which y_{A,1} decreases and y_{B,1} increases in p_{B,1}, provided gamma is large and 0 <= gamma (1 - theta) <= l^D for some l^D > 0.
- **Points:** 8 markets of `draw_market` that satisfy (A.22) (seed 5302), a 3 by 3 patch of prices inside the set (A.23) of the proof, theta = 1 and 1 - l / gamma with one positive l, gamma = 100, 1e3, 1e4 and 1e5, and theta = 0.5 at gamma = 1e4 and 1e5.
- **Computed:** d y_A / d p_B and d y_B / d p_B of the solutions of the first-order conditions (`_orders_n`) by central differences of step 1e-4 (p_hi - p_lo), and at gamma = 1e4 and 1e5 a search of each order interval at the centre pair. The gap to the expansion (A.26) is recorded.
- **Criterion:** the claim holds at a market and gamma if at both values of theta all equilibria are solved, the table reports no problem, the slopes are negative for y_A and positive for y_B at all 9 pairs, and at the two largest gammas the search finds no relative gain above 1e-8 and no best response farther than 2e-5 (mu + sigma). It must hold at all markets from gamma = 1e4 on. At theta = 0.5 and gamma = 1e4 and 1e5 both signs are reversed at all 9 pairs.
- **Recorded:** markets = 8; gamma ladder = [100.0, 1000.0, 10000.0, 100000.0]; markets where the claim holds by gamma = [8, 8, 8, 8]; holds in all markets from gamma = 100.0; smallest ratio of the two sides of A22 = 1.002; largest tested value of gamma times one minus theta = 0.0096; smallest slope over beta mu plus sigma at gamma 1e5 = 0.00036
- **At the level of rounding error (differs between machines):** max difference to expansion A26 over beta mu plus sigma at gamma 1e5 = 6.04806e-06

<a id="check-4"></a>
### `tests/test_section_5_propositions.py::test_proposition_8b_orders_of_scenario_n_at_fixed_theta`

- **Outcome:** passed (3.3 s)
- **Tests directly:** P8.b1, P8.b2
- **What:** Proposition 8(b1) and the last sentence of 8(b2), Scenario N, gamma large. (b1) y_{A,1} decreases and y_{B,1} increases in p_{A,1}. (b2, fixed theta < 1) y_{A,1} increases and y_{B,1} decreases in p_{B,1}.
- **Points:** 6 markets of `draw_market` (seed 5301), a 7 by 7 grid of first-period prices that covers the price box, theta = 0, 0.5, 0.9 and 1 for (b1), whose thresholds Online Appendix A.2 announces as uniform in theta, and 0, 0.5 and 0.9 for (b2), gamma = 10, 100, 1e3, 1e4, 1e5.
- **Computed:** the solutions of the model's first-order conditions at all 49 pairs (`_orders_n`, `SecondPeriodN`), the difference quotients between neighbouring grid points, and at gamma = 1e4 and 1e5 a 1001-point search of each order interval at one random grid pair.
- **Criterion:** a part holds at a market, theta and gamma if the conditions are solved within 1e-12 (10 + gamma) c_i at all 49 pairs, the table reports no problem, every quotient of the part has the claimed sign, and at the two largest gammas the search finds no relative gain above 1e-8 and no best response farther than 2e-5 (mu + sigma). Each part must hold in every case from gamma = 1e4 on.
- **Recorded:** markets = 6; price pairs per market = 49; gamma ladder = [10.0, 100.0, 1000.0, 10000.0, 100000.0]; (b1): values of theta = [0.0, 0.5, 0.9, 1.0]; (b1): cases where the claim holds by gamma = [24, 24, 24, 24, 24]; (b1): holds in all cases from gamma = 10.0; (b1): smallest slope over beta (mu + sigma) at gamma 1e5 = 0.627; (b2) fixed theta: values of theta = [0.0, 0.5, 0.9]; (b2) fixed theta: cases where the claim holds by gamma = [18, 18, 18, 18, 18]; (b2) fixed theta: holds in all cases from gamma = 10.0; (b2) fixed theta: smallest slope over beta (mu + sigma) at gamma 1e5 = 1.0

<a id="check-5"></a>
### `tests/test_section_5_second_period.py::test_helpers_agree_with_the_primitives`

- **Outcome:** passed (0.2 s)
- **Supports:** LA1, LA2, P8, P9
- **What:** `section5.expected_sales` and `section5.benchmark_orders` against the primitives.
- **Points:** 2,000 markets of `draw_market` (seed 5100), each with C2C demands that are zero or uniform on [0, 3 (mu + sigma)], orders uniform on [0, 2 (mu + sigma)] above them, a share uniform on [0.02, 0.98] and a price pair uniform on the price box.
- **Computed:** expected sales from `section5.expected_sales` and from `primitives.Uniform`, and order quantities from `benchmark_orders` and from `section4.claimed_benchmark`.
- **Criterion:** every difference is at most 1e-13 (mu + sigma), and retailer B has the higher critical fractile at one price pair or more.
- **Recorded:** points = 2000; price pairs where retailer B has the higher fractile = 130
- **At the level of rounding error (differs between machines):** max relative error expected sales = 0.0; max relative error benchmark orders = 0.0

<a id="check-6"></a>
### `tests/test_section_5_transcription.py::test_claims_of_section_5_are_transcribed_from_the_paper`

- **Outcome:** passed (0.0 s)
- **Supports:** LA1, LA2, P8, P9
- **What:** `section5.claimed_*` against a second transcription of Lemmas A.1 and A.2 and Propositions 8 and 9.
- **Points:** 500 markets of `draw_market` (seed 5400), each with first-period prices uniform on the price box, gamma log-uniform on [1, 1e6], and two sorted prices uniform on the box for the price-path predicates.
- **Computed:** the 17 LaTeX strings of `QUOTES` against the LaTeX source in `paper/`, and both transcriptions of the limit prices, nu_i, the claimed first-period orders of Scenarios S and N, the ratio of the two sides of (A.22), the bound in (A.23) and the first-period limit prices of the proof of Proposition 9.
- **Criterion:** every string occurs verbatim, up to whitespace, every difference is at most 1e-12 max(1, |value|), the claimed Scenario S prices are (p_lo, p_lo) and (p_hi, p_hi), the predicates of Proposition 9 accept and reject the test pairs as its inequalities require, and `CLAIMED_SLOPE_SIGNS` equals the table written from Proposition 8.
- **Recorded:** latex strings found in the paper = 17; random points = 500
- **At the level of rounding error (differs between machines):** largest relative difference = 1.76606e-15
