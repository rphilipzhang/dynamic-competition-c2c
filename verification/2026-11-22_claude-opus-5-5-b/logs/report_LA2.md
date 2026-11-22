# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k LA2 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**8 of 8 checks passed.** pytest exit status: 0.

A *direct* check tests a part of the result itself. A *supporting* check confirms a tool that direct checks rely on, for example that a closed form equals the model at random points. Every check computes at finitely many points. For a result that holds for all parameters it is a search for counterexamples. For a result that holds for a parameter large enough it probes large values of that parameter.

The selection counts only LA2. Other IDs that the selected checks name appear only in the description of each check below.

## Results of theory.md

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [LA2](#la2) | 5/5 | 3/3 |

## Checks by ID

### LA2

- direct (LA2.a): [test_lemma_a2a_error_bound_is_uniform_in_theta_near_one](#check-2): passed
- direct (LA2.a): [test_lemma_a2a_first_period_inventory_equilibrium_of_scenario_n](#check-3): passed
- direct (LA2.a): [test_lemma_a2a_uniqueness_probes](#check-4): passed
- direct (LA2.b): [test_lemma_a2b_second_period_prices_approach_the_limit_prices_at_rate_one_over_gamma](#check-6): passed
- direct (LA2.b): [test_second_period_inventory_equilibrium_at_any_price_pair[N]](#check-7): passed
- supporting: [test_first_period_machinery_reproduces_the_model](#check-1): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-5): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-8): passed

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
### `tests/test_section_5_first_period.py::test_lemma_a2a_error_bound_is_uniform_in_theta_near_one`

- **Outcome:** passed (1.6 s)
- **Tests directly:** LA2.a
- **What:** Lemma A.2(a) with the uniformity that Online Appendix A.2 announces for its bounds: the error of the closed form is of order gamma^-2 uniformly in theta, including theta close to 1, where the error changes regime.
- **Points:** 8 markets of `draw_market` (seed 5205), one first-period price pair each, uniform on the price box, gamma = 300, 1e3 and 3e3, and theta = 1 - l / gamma for l = 0, 0.03, 0.1, 0.3, 1, 3, 10 and 30.
- **Computed:** the scaled error gamma^2 e(gamma), with e as in the previous check, and for each gamma its largest value over l. Also recorded: the growth of that maximum, its ratio to the value at theta = 1, and how closely the scaled errors at gamma = 1e3 and 3e3 agree at fixed l <= 3 where they are ten times above rounding level.
- **Criterion:** `SecondPeriodN` reports no problem, the first-order conditions hold at y* within 1e-12 (10 + gamma) c_i, and the maximum grows by at most 10% plus 3e-14 gamma^2 from one gamma to the next. An error of order 1 / gamma would multiply it by about 3 at each step.
- **Recorded:** markets = 8; gammas = [300.0, 1000.0, 3000.0]; values of gamma times one minus theta = [0.0, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0]; range of growth of largest scaled error per step of gamma to one decimal = [1.0, 1.0]
- **At the level of rounding error (differs between machines):** range of growth of largest scaled error per step of gamma = [0.970194, 1.01105]; largest ratio of maximal scaled error to its value at theta 1 = 3.9559; entries compared between gamma 1e3 and 3e3 = 30; max relative change from gamma 1e3 to 3e3 at fixed level up to 3 = 0.00550064

<a id="check-3"></a>
### `tests/test_section_5_first_period.py::test_lemma_a2a_first_period_inventory_equilibrium_of_scenario_n`

- **Outcome:** passed (3.3 s)
- **Tests directly:** LA2.a
- **What:** Lemma A.2(a): for gamma large the first-period inventory subgame of Scenario N has an equilibrium that equals the stated closed form up to a term of order gamma^-2.
- **Points:** 16 markets of `draw_market` (seed 5203), one price pair each on the price box, theta set to 1 in every fourth market, to 0 in every fourth and to 0.9 theta in the others (theta just below 1 is left to the next check), gamma = 10, 30, 100, 300, 1e3, 3e3 and 1e4.
- **Computed:** with the continuation of `SecondPeriodN`, the solution y* of the model's two first-order conditions, e(gamma) = max_i |y_i* - y_i| / (mu + sigma) for the closed form y, the order -d log e / d log gamma between neighbouring values, and at gamma = 10, 100, 1e3 and 1e4 a 1001-point search of [0, 1.5 (mu + sigma)] from y, at 1e4 also from y*.
- **Criterion:** the conditions hold at y* within 1e-12 (10 + gamma) c_i, e shrinks on every step with e > 3e-13 at both ends, the order is at least 1.75 on such steps from gamma = 100 on (an error of order 1 / gamma gives 1), with 16 or more such steps in all, and from 1e3 on every search passes at every market: table without problem, relative gain at most 1e-8, best responses within 2e-5 (mu + sigma).
- **Recorded:** markets = 16; gamma ladder = [10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0]; gammas with search of the whole order interval = [10.0, 100.0, 1000.0, 10000.0]; points without profitable deviation by gamma = [16, 16, 16, 16]; no profitable deviation at all points from gamma = 10.0; observed order on last usable step rounded to integer, theta = 1 = [2]; observed order on last usable step rounded to integer, theta < 1 = [3]
- **At the level of rounding error (differs between machines):** range of observed order on last usable step, theta = 1 = [1.99777, 2.00354]; range of observed order on last usable step, theta < 1 = [2.72707, 2.99176]; usable steps from gamma 100 = 28; lowest observed order from gamma 100 = 1.99241; largest gamma squared times relative error from gamma 100 = 0.000642805; max relative gain from deviation at gamma 1e4 = 1.25163e-16; max relative distance best response at gamma 1e4 = 1.51857e-08

<a id="check-4"></a>
### `tests/test_section_5_first_period.py::test_lemma_a2a_uniqueness_probes`

- **Outcome:** passed (6.1 s)
- **Tests directly:** LA2.a
- **What:** Uniqueness probes for Lemma A.2(a) at gamma = 1e3 (seed 5204).
- **Points:** probe 1, 6 markets of `draw_market` with theta scaled to 0.8 theta, 3 starting pairs uniform on [d, 1.5 (mu + sigma)]^2. Probe 2, 4 markets with theta = 0.5, 0.95, 1 and the theta of `draw_market`, 121 values of y_B on [d, 1.5 (mu + sigma)]. One price pair per market. d = min(alpha_A, alpha_B, [1/2 - beta (p_hi - p_lo)] / 2) (mu - sigma). Below d total sales can approach zero, where the second-period price game leaves its large-gamma regime.
- **Computed:** best replies A and B over [0, 1.5 (mu + sigma)] from payoff values, continuation `SecondPeriodN`. Probe 1 alternates them, at most 60 sweeps, until a sweep moves less than 1e-7 (mu + sigma), and records the predicted contraction per sweep, which tends to 1 as theta tends to 1. Probe 2 evaluates the residual B(A(y_B)) - y_B.
- **Criterion:** no table problem and every rival order evaluated at least d. Probe 1: fewer than 60 sweeps, end point within 1e-4 (mu + sigma) of the closed form. Probe 2: residual positive at d and negative at 1.5 (mu + sigma), with a change of sign (product of signs at most 0) between exactly one pair of neighbours, which encloses the claimed y_B.
- **Recorded:** gamma = 1000.0; iteration runs = 18; largest predicted contraction factor per sweep = 0.63; sign changes of the fixed point residual per scanned market = [1, 1, 1, 1]
- **At the level of rounding error (differs between machines):** largest number of sweeps = 21; max relative distance to claimed orders after iteration = 3.32761e-07

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
### `tests/test_section_5_second_period.py::test_lemma_a2b_second_period_prices_approach_the_limit_prices_at_rate_one_over_gamma`

- **Outcome:** passed (3.9 s)
- **Tests directly:** LA2.b
- **What:** Lemma A.2(b): in Scenario N, given R_1 > 0 and gamma large, the second-period price equilibrium is unique and equals 1 / (2 beta) + (2 c_i + c_j) / 3 plus O(1 / gamma).
- **Points:** 2,000 markets of `draw_market` (seed 5106) for the notation of Online Appendix A.2, and 12 markets (seed 5103), one state each with R_1 uniform on [0.1, 1] (mu + sigma), at gamma = 10, 100, 1e3, 1e4, 1e5 and 1e6.
- **Computed:** the solution of the first-order conditions of the price game, a search of each price interval and best-response iteration from the four corners (at most 40 sweeps), with profits from the primitives, and e(gamma), the larger distance to the limit prices.
- **Criterion:** at the 2,000 markets nu_A > nu_B > 0, c_A / nu_A < c_B / nu_B, p_lo < limit_A < limit_B < p_hi and c_A / limit_A < c_B / limit_B. At the 12 markets e shrinks along the ladder, log10(e(gamma) / e(10 gamma)) lies in [0.99, 1.01] over the last two decades, gamma e at 1e5 and 1e6 agrees within 0.5% and never exceeds twice its value at 1e6, and from 1e5 on every market passes: relative gain at most 1e-8, best responses and iterations within 2e-5 p_hi.
- **Recorded:** markets = 12; gamma ladder = [10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0]; points where equilibrium is confirmed and unique by gamma = [12, 12, 12, 12, 12, 12]; unique equilibrium at all points from gamma = 10.0; range of observed order over last two decades = [1.0, 1.0]; max scaled distance on ladder over its value at gamma 1e6 = 1.0; range of gamma times distance over upper price bound at gamma 1e6 = [0.013, 0.341]; markets where both prices approach the limit from above = 12
- **At the level of rounding error (differs between machines):** max deviation of observed order from 1 over last two decades = 0.000213645; max relative change of scaled distance between gamma 1e5 and 1e6 = 4.92082e-05

<a id="check-7"></a>
### `tests/test_section_5_second_period.py::test_second_period_inventory_equilibrium_at_any_price_pair[N]`

- **Outcome:** passed (0.6 s)
- **Tests directly:** LA2.b
- **What:** Lemmas A.1(b) and A.2(b), last sentence of each: at given second-period prices and first-period sales the orders y^0_{i,2} + Z_{i,2} are the equilibrium of the inventory subgame, and each profit is pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2}.
- **Points:** 100 markets of `draw_market` (seed 5101), gamma log-uniform on [0.1, 1000], one sales state each, uniform on the triangle R_A, R_B >= 0, R_A + R_B <= mu + sigma. At every second point the prices are uniform on the price box. At the others they are drawn, where the box allows, from the pairs with c_A / p_A > c_B / p_B.
- **Computed:** from the primitives, `primitives.nash_gap` on [0, U] with U = max(Z_A, Z_B) + 1.5 (mu + sigma), the profits at the claimed orders, and at the first 20 points best-response iteration (801-point grid, at most 60 sweeps) from two random starting pairs.
- **Criterion:** no deviation gains more than 1e-8 p_hi U, each best response lies within 2e-5 U of the claim, the profit identity holds within 1e-11 p_hi U, every iteration ends within 1e-4 U of the claim, and retailer B has the higher fractile at 10 points or more.
- **Recorded:** points = 100; points where retailer B has the higher fractile = 25; tolerance on relative gain from deviation = 1e-08
- **At the level of rounding error (differs between machines):** max relative gain from deviation = 3.42203e-16; max relative distance best response to claim = 8.81193e-09; max relative error of profit identity = 2.53729e-16; max relative distance after best response iteration = 1.0485e-09

<a id="check-8"></a>
### `tests/test_section_5_transcription.py::test_claims_of_section_5_are_transcribed_from_the_paper`

- **Outcome:** passed (0.0 s)
- **Supports:** LA1, LA2, P8, P9
- **What:** `section5.claimed_*` against a second transcription of Lemmas A.1 and A.2 and Propositions 8 and 9.
- **Points:** 500 markets of `draw_market` (seed 5400), each with first-period prices uniform on the price box, gamma log-uniform on [1, 1e6], and two sorted prices uniform on the box for the price-path predicates.
- **Computed:** the 17 LaTeX strings of `QUOTES` against the LaTeX source in `paper/`, and both transcriptions of the limit prices, nu_i, the claimed first-period orders of Scenarios S and N, the ratio of the two sides of (A.22), the bound in (A.23) and the first-period limit prices of the proof of Proposition 9.
- **Criterion:** every string occurs verbatim, up to whitespace, every difference is at most 1e-12 max(1, |value|), the claimed Scenario S prices are (p_lo, p_lo) and (p_hi, p_hi), the predicates of Proposition 9 accept and reject the test pairs as its inequalities require, and `CLAIMED_SLOPE_SIGNS` equals the table written from Proposition 8.
- **Recorded:** latex strings found in the paper = 17; random points = 500
- **At the level of rounding error (differs between machines):** largest relative difference = 1.76606e-15
