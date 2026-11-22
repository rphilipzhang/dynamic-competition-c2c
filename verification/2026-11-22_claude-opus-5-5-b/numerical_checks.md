# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**93 of 93 checks passed.** pytest exit status: 0.

A *direct* check tests a part of the result itself. A *supporting* check confirms a tool that direct checks rely on, for example that a closed form equals the model at random points. Every check computes at finitely many points. For a result that holds for all parameters it is a search for counterexamples. For a result that holds for a parameter large enough it probes large values of that parameter.

## Results of theory.md

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [L1](#l1) | 3/3 | 3/3 |
| [L2](#l2) | 8/8 | 3/3 |
| [L3](#l3) | 8/8 | 3/3 |
| [L4](#l4) | 2/2 | 4/4 |
| [P1](#p1) | 2/2 | 4/4 |
| [P2](#p2) | 3/3 | 4/4 |
| [P3](#p3) | 2/2 | 5/5 |
| [P4](#p4) | 1/1 | 3/3 |
| [P5](#p5) | 4/4 | 7/7 |
| [P6](#p6) | 4/4 | 6/6 |
| [LA1](#la1) | 4/4 | 3/3 |
| [LA2](#la2) | 5/5 | 3/3 |
| [P7](#p7) | 2/2 | 1/1 |
| [P8](#p8) | 3/3 | 3/3 |
| [P9](#p9) | 2/2 | 3/3 |
| [LB1](#lb1) | 6/6 | 2/2 |

## Numerical statements of the paper

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [F1](#f1) | 9/9 | 8/8 |
| [FB1](#fb1) | 5/5 | 4/4 |
| [N1](#n1) | 1/1 | 1/1 |
| [N2](#n2) | 1/1 | 1/1 |
| [N3](#n3) | 1/1 | 1/1 |
| [N4](#n4) | 1/1 | 1/1 |
| [N5](#n5) | 1/1 | 3/3 |
| [N6](#n6) | 2/2 | 1/1 |

## Checks by ID

### L1

- direct (L1.eq): [test_benchmark_equilibrium_of_lemma_1](#check-1): passed
- direct (L1.unique): [test_first_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[0]](#check-5): passed
- direct (L1.unique): [test_second_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[0]](#check-12): passed
- supporting: [test_benchmark_profit_polynomials_match_lemma_1](#check-34): passed
- supporting: [test_expected_leftovers_in_the_code_follow_from_the_model](#check-36): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-41): passed

### L2

- direct (L2.first): [test_first_period_equilibrium[S]](#check-4): passed
- direct (L2.unique): [test_first_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[S]](#check-8): passed
- direct (L2.second): [test_second_period_equilibrium_and_continuation_value[S]](#check-11): passed
- direct (L2.unique): [test_second_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[S]](#check-15): passed
- direct (L2.first): [test_branch_conditions_in_the_code_are_the_fractile_orderings](#check-35): passed
- direct (L2.first, L2.profits): [test_scenario_s_code_matches_lemma_2](#check-40): passed
- direct (L2.profits): [test_closed_form_sales_and_profits_equal_the_model[S]](#check-47): passed
- direct (L2.profits): [test_second_period_profit_function_equals_the_model[S]](#check-53): passed
- supporting: [test_expected_leftovers_in_the_code_follow_from_the_model](#check-36): passed
- supporting: [test_mixed_scenario_reduces_to_scenarios_s_and_n](#check-38): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-44): passed

### L3

- direct (L3.first): [test_first_period_equilibrium[N]](#check-3): passed
- direct (L3.unique): [test_first_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[N]](#check-7): passed
- direct (L3.second): [test_second_period_equilibrium_and_continuation_value[N]](#check-10): passed
- direct (L3.unique): [test_second_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[N]](#check-14): passed
- direct (L3.first): [test_branch_conditions_in_the_code_are_the_fractile_orderings](#check-35): passed
- direct (L3.first, L3.profits): [test_scenario_n_code_matches_lemma_3](#check-39): passed
- direct (L3.profits): [test_closed_form_sales_and_profits_equal_the_model[N]](#check-46): passed
- direct (L3.profits): [test_second_period_profit_function_equals_the_model[N]](#check-52): passed
- supporting: [test_expected_leftovers_in_the_code_follow_from_the_model](#check-36): passed
- supporting: [test_mixed_scenario_reduces_to_scenarios_s_and_n](#check-38): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-43): passed

### L4

- direct (L4.a): [test_lemma_4a_benchmark_order_per_unit_of_share](#check-57): passed
- direct (L4.b): [test_lemma_4b_order_per_unit_of_share_in_scenarios_s_and_n](#check-58): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-41): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-43): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-44): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-75): passed

### P1

- direct (P1.i): [test_proposition_1_i_order_quantities_of_retailer_a_increase_in_theta](#check-59): passed
- direct (P1.ii): [test_proposition_1_ii_threshold_in_theta_for_large_gamma](#check-60): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-41): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-43): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-44): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-75): passed

### P2

- direct (P2.a): [test_proposition_2a_order_quantity_of_retailer_b_and_theta](#check-61): passed
- direct (P2.b): [test_proposition_2b_ordering_of_the_order_quantities_of_retailer_b](#check-62): passed
- direct (P2.c): [test_proposition_2c_gap_of_retailer_b_rises_then_falls_in_gamma](#check-63): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-41): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-43): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-44): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-75): passed

### P3

- direct (P3.a): [test_proposition_3a_expected_sales_of_retailer_a_for_large_gamma](#check-64): passed
- direct (P3.b): [test_proposition_3b_expected_sales_of_retailer_b](#check-65): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-43): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-44): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-46): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[S]](#check-47): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-75): passed

### P4

- direct: [test_proposition_4_total_sales_fall_then_rise_in_theta](#check-66): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-43): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-46): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-75): passed

### P5

- direct (P5.a): [test_proposition_5a_profit_of_retailer_a_in_scenario_s_increases_in_theta](#check-67): passed
- direct (P5.b): [test_proposition_5b_profit_of_retailer_a_exceeds_the_benchmark](#check-68): passed
- direct (P5.c1): [test_proposition_5c1_shares_decide_the_comparison_for_retailer_a](#check-69): passed
- direct (P5.c2): [test_proposition_5c2_threshold_in_theta_above_the_cost_threshold](#check-70): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-41): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-43): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-44): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-46): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[S]](#check-47): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-75): passed
- supporting: [test_threshold_gamma_a4_of_proposition_5c2_depends_on_c_b](#check-76): passed

### P6

- direct (P6.a): [test_proposition_6a_profit_of_retailer_b_and_theta](#check-71): passed
- direct (P6.b): [test_proposition_6b_profit_of_retailer_b_exceeds_the_benchmark](#check-72): passed
- direct (P6.c1): [test_proposition_6c1_shares_decide_the_comparison_for_retailer_b](#check-73): passed
- direct (P6.c2): [test_proposition_6c2_threshold_in_theta_below_the_cost_threshold](#check-74): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]](#check-41): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-43): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-44): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-46): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[S]](#check-47): passed
- supporting: [test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas](#check-75): passed

### LA1

- direct (LA1.a): [test_lemma_a1a_best_response_iteration_returns_to_the_claimed_orders](#check-78): passed
- direct (LA1.a): [test_lemma_a1a_first_period_inventory_equilibrium_of_scenario_s](#check-79): passed
- direct (LA1.b): [test_lemma_a1b_upper_bound_is_the_unique_second_period_price_equilibrium](#check-89): passed
- direct (LA1.b): [test_second_period_inventory_equilibrium_at_any_price_pair[S]](#check-92): passed
- supporting: [test_first_period_machinery_reproduces_the_model](#check-77): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-88): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-93): passed

### LA2

- direct (LA2.a): [test_lemma_a2a_error_bound_is_uniform_in_theta_near_one](#check-80): passed
- direct (LA2.a): [test_lemma_a2a_first_period_inventory_equilibrium_of_scenario_n](#check-81): passed
- direct (LA2.a): [test_lemma_a2a_uniqueness_probes](#check-82): passed
- direct (LA2.b): [test_lemma_a2b_second_period_prices_approach_the_limit_prices_at_rate_one_over_gamma](#check-90): passed
- direct (LA2.b): [test_second_period_inventory_equilibrium_at_any_price_pair[N]](#check-91): passed
- supporting: [test_first_period_machinery_reproduces_the_model](#check-77): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-88): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-93): passed

### P7

- direct (P7.a): [test_proposition_7a_shape_in_the_own_price](#check-54): passed
- direct (P7.b): [test_proposition_7b_shape_in_the_rival_price](#check-55): passed
- supporting: [test_second_period_orders_of_this_file_are_the_equilibrium_of_the_model](#check-56): passed

### P8

- direct (P8.a): [test_proposition_8a_orders_of_scenario_s_fall_in_own_price_and_rise_in_rival_price](#check-83): passed
- direct (P8.b2): [test_proposition_8b2_reversal_when_gamma_times_one_minus_theta_is_bounded](#check-84): passed
- direct (P8.b1, P8.b2): [test_proposition_8b_orders_of_scenario_n_at_fixed_theta](#check-85): passed
- supporting: [test_first_period_machinery_reproduces_the_model](#check-77): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-88): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-93): passed

### P9

- direct (P9.a): [test_proposition_9a_price_path_of_scenario_s](#check-86): passed
- direct (P9.b): [test_proposition_9b_price_path_of_scenario_n](#check-87): passed
- supporting: [test_first_period_machinery_reproduces_the_model](#check-77): passed
- supporting: [test_helpers_agree_with_the_primitives](#check-88): passed
- supporting: [test_claims_of_section_5_are_transcribed_from_the_paper](#check-93): passed

### LB1

- direct (LB1.first): [test_first_period_equilibrium[G]](#check-2): passed
- direct (LB1.unique): [test_first_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[G]](#check-6): passed
- direct (LB1.second): [test_second_period_equilibrium_and_continuation_value[G]](#check-9): passed
- direct (LB1.unique): [test_second_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[G]](#check-13): passed
- direct (LB1.first): [test_mixed_scenario_code_matches_lemma_b1](#check-37): passed
- direct (LB1.first): [test_mixed_scenario_reduces_to_scenarios_s_and_n](#check-38): passed
- supporting: [test_expected_leftovers_in_the_code_follow_from_the_model](#check-36): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]](#check-42): passed

### F1

- direct: [test_figure_1_equilibria_are_unique_and_the_continuation_is_constant](#check-16): passed
- direct: [test_figure_1_matches_the_published_figure[a]](#check-17): passed
- direct: [test_figure_1_matches_the_published_figure[b]](#check-18): passed
- direct: [test_figure_1_matches_the_published_figure[c]](#check-19): passed
- direct: [test_figure_1_matches_the_published_figure[d]](#check-20): passed
- direct: [test_figure_1_inventory_equilibria_hold_in_the_model](#check-48): passed
- direct: [test_figure_1_payoff_matrices_equal_the_model](#check-49): passed
- direct: [test_figure_1_second_period_prices_are_an_equilibrium_at_every_sales_state](#check-50): passed
- direct: [test_second_period_inventory_equilibrium_for_all_price_pairs_of_figure_1](#check-51): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-28): passed
- supporting: [test_published_data_match_a_fresh_extraction_from_the_eps_files](#check-29): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]](#check-43): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]](#check-44): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[N]](#check-46): passed
- supporting: [test_closed_form_sales_and_profits_equal_the_model[S]](#check-47): passed
- supporting: [test_second_period_profit_function_equals_the_model[N]](#check-52): passed
- supporting: [test_second_period_profit_function_equals_the_model[S]](#check-53): passed

### FB1

- direct: [test_figure_b1_matches_the_authors_matlab_values](#check-21): passed
- direct: [test_figure_b1_matches_the_published_figure[a]](#check-22): passed
- direct: [test_figure_b1_matches_the_published_figure[b]](#check-23): passed
- direct: [test_figure_b1_matches_the_published_figure[c]](#check-24): passed
- direct: [test_figure_b1_matches_the_published_figure[d]](#check-25): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-28): passed
- supporting: [test_published_data_match_a_fresh_extraction_from_the_eps_files](#check-29): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]](#check-42): passed
- supporting: [test_closed_form_profits_of_the_mixed_scenario_equal_the_model](#check-45): passed

### N1

- direct: [test_split_ratios_are_constant_over_time_in_figure_1](#check-30): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-28): passed

### N2

- direct: [test_moderate_gamma_panels_show_one_profit_crossing](#check-27): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-28): passed

### N3

- direct: [test_strong_gamma_panels_show_no_crossing](#check-31): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-28): passed

### N4

- direct: [test_strong_gamma_panels_show_no_crossing](#check-31): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-28): passed

### N5

- direct: [test_figure_b1_patterns_described_in_appendix_b](#check-26): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-28): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]](#check-42): passed
- supporting: [test_closed_form_profits_of_the_mixed_scenario_equal_the_model](#check-45): passed

### N6

- direct: [test_large_gamma_patterns_under_other_distributions](#check-32): passed
- direct: [test_order_quantities_and_sales_patterns_under_other_distributions](#check-33): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-28): passed

## Checks

<a id="check-1"></a>
### `tests/test_equilibria_from_primitives.py::test_benchmark_equilibrium_of_lemma_1`

- **Outcome:** passed (8.5 s)
- **Tests directly:** L1.eq
- **What:** Lemma 1: the claimed order quantities of the single-period game without C2C interactions.
- **Points:** 109 points (seed 101). 78 regular points of `draw_exogenous`, 60 under the uniform distribution and 6 under each of the triangular, beta(2,5) and truncated normal ones, and 31 edge points of `draw_edge_exact`, 30 uniform and 1 truncated normal. One game at the first-period prices of every point and, under the uniform distribution, one more at its second-period prices: 199 games.
- **Computed:** the quantities of `section4.claimed_benchmark` through the quantile function, and `primitives.nash_gap` on [0, 1.5 (mu + sigma)] for the payoffs of `section4.Game` with scenario "0", built from the primitives.
- **Criterion:** both critical fractiles lie in [0, 1] with retailer A's the higher one (up to 1e-12 at edge points), no deviation gains more than 1e-8 mu, and each best response lies within 2e-5 max(1, mu) of the claimed quantity.
- **Recorded:** regular points = 78; edge points = 31; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; games checked = 199; tolerance on relative gain from deviation = 1e-08
- **At the level of rounding error (differs between machines):** max relative gain from deviation = 3.67413e-14; max distance best response to claim = 5.89548e-07

<a id="check-2"></a>
### `tests/test_equilibria_from_primitives.py::test_first_period_equilibrium[G]`

- **Outcome:** passed (8.2 s)
- **Tests directly:** LB1.first
- **What:** First period of Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 109 points (seed 303), 78 regular (60 uniform, 6 under each other distribution) and 31 edge (30 uniform, 1 triangular).
- **Computed:** the claimed orders and critical fractiles of `section4.claimed_first_period`, and `primitives.nash_gap` on [0, 1.5 (mu + sigma)] for the two-period payoffs of `section4.Game`, built from the primitives with the continuation pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2}.
- **Criterion:** both fractiles lie in [0, 1] with retailer A's the higher one (up to 1e-12 at edge points), and with scale mu (1 + gamma) no deviation gains more than 1e-8 times the scale and each best response lies within 2e-5 max(1, scale) of the claim.
- **Recorded:** regular points = 78; edge points = 31; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; tolerance on relative gain from deviation = 1e-08
- **At the level of rounding error (differs between machines):** max relative gain from deviation = 5.89037e-15; max distance best response to claim = 6.43718e-07

<a id="check-3"></a>
### `tests/test_equilibria_from_primitives.py::test_first_period_equilibrium[N]`

- **Outcome:** passed (8.3 s)
- **Tests directly:** L3.first
- **What:** First period of Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 109 points (seed 303), 78 regular (60 uniform, 6 under each other distribution) and 31 edge (30 uniform, 1 triangular).
- **Computed:** the claimed orders and critical fractiles of `section4.claimed_first_period`, and `primitives.nash_gap` on [0, 1.5 (mu + sigma)] for the two-period payoffs of `section4.Game`, built from the primitives with the continuation pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2}.
- **Criterion:** both fractiles lie in [0, 1] with retailer A's the higher one (up to 1e-12 at edge points), and with scale mu (1 + gamma) no deviation gains more than 1e-8 times the scale and each best response lies within 2e-5 max(1, scale) of the claim.
- **Recorded:** regular points = 78; edge points = 31; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; tolerance on relative gain from deviation = 1e-08
- **At the level of rounding error (differs between machines):** max relative gain from deviation = 1.48646e-14; max distance best response to claim = 1.18671e-06

<a id="check-4"></a>
### `tests/test_equilibria_from_primitives.py::test_first_period_equilibrium[S]`

- **Outcome:** passed (8.2 s)
- **Tests directly:** L2.first
- **What:** First period of Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 109 points (seed 303), 78 regular (60 uniform, 6 under each other distribution) and 31 edge (30 uniform, 1 triangular).
- **Computed:** the claimed orders and critical fractiles of `section4.claimed_first_period`, and `primitives.nash_gap` on [0, 1.5 (mu + sigma)] for the two-period payoffs of `section4.Game`, built from the primitives with the continuation pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2}.
- **Criterion:** both fractiles lie in [0, 1] with retailer A's the higher one (up to 1e-12 at edge points), and with scale mu (1 + gamma) no deviation gains more than 1e-8 times the scale and each best response lies within 2e-5 max(1, scale) of the claim.
- **Recorded:** regular points = 78; edge points = 31; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; tolerance on relative gain from deviation = 1e-08
- **At the level of rounding error (differs between machines):** max relative gain from deviation = 1.41846e-14; max distance best response to claim = 8.85512e-07

<a id="check-5"></a>
### `tests/test_equilibria_from_primitives.py::test_first_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[0]`

- **Outcome:** passed (3.3 s)
- **Tests directly:** L1.unique
- **What:** Uniqueness in the first period of Lemma 1 (case 0), Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 28 points (seed 404), 15 regular (12 uniform, 1 under each other distribution) and 13 edge (12 uniform, 1 truncated normal).
- **Computed:** `section4.scan_fixed_points` for T(y_B) = BR_B(BR_A(y_B)) of the two-period payoffs on [0, 1.5 (mu + sigma)], with 21 coarse and 41 fine nodes and a best-response grid of 801 under the uniform distribution, 9, 15 and 101 under the others.
- **Criterion:** T(y_B) - y_B is positive at the lowest node and negative at the highest, its sign changes between exactly one pair of neighbouring nodes, and that pair encloses the claimed y_B up to the noise allowance 1e-6 max(mu + sigma, max T). Two equilibria between the same two neighbouring nodes would not be seen.
- **Recorded:** regular points = 15; edge points = 13; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; evaluations of the composed best response = 1584
- **At the level of rounding error (differs between machines):** widest bracket of the fixed point relative to demand = 0.000285715

<a id="check-6"></a>
### `tests/test_equilibria_from_primitives.py::test_first_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[G]`

- **Outcome:** passed (3.4 s)
- **Tests directly:** LB1.unique
- **What:** Uniqueness in the first period of Lemma 1 (case 0), Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 28 points (seed 404), 15 regular (12 uniform, 1 under each other distribution) and 13 edge (12 uniform, 1 truncated normal).
- **Computed:** `section4.scan_fixed_points` for T(y_B) = BR_B(BR_A(y_B)) of the two-period payoffs on [0, 1.5 (mu + sigma)], with 21 coarse and 41 fine nodes and a best-response grid of 801 under the uniform distribution, 9, 15 and 101 under the others.
- **Criterion:** T(y_B) - y_B is positive at the lowest node and negative at the highest, its sign changes between exactly one pair of neighbouring nodes, and that pair encloses the claimed y_B up to the noise allowance 1e-6 max(mu + sigma, max T). Two equilibria between the same two neighbouring nodes would not be seen.
- **Recorded:** regular points = 15; edge points = 13; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; evaluations of the composed best response = 1584
- **At the level of rounding error (differs between machines):** widest bracket of the fixed point relative to demand = 0.00730044

<a id="check-7"></a>
### `tests/test_equilibria_from_primitives.py::test_first_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[N]`

- **Outcome:** passed (3.4 s)
- **Tests directly:** L3.unique
- **What:** Uniqueness in the first period of Lemma 1 (case 0), Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 28 points (seed 404), 15 regular (12 uniform, 1 under each other distribution) and 13 edge (12 uniform, 1 truncated normal).
- **Computed:** `section4.scan_fixed_points` for T(y_B) = BR_B(BR_A(y_B)) of the two-period payoffs on [0, 1.5 (mu + sigma)], with 21 coarse and 41 fine nodes and a best-response grid of 801 under the uniform distribution, 9, 15 and 101 under the others.
- **Criterion:** T(y_B) - y_B is positive at the lowest node and negative at the highest, its sign changes between exactly one pair of neighbouring nodes, and that pair encloses the claimed y_B up to the noise allowance 1e-6 max(mu + sigma, max T). Two equilibria between the same two neighbouring nodes would not be seen.
- **Recorded:** regular points = 15; edge points = 13; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; evaluations of the composed best response = 1584
- **At the level of rounding error (differs between machines):** widest bracket of the fixed point relative to demand = 0.00730044

<a id="check-8"></a>
### `tests/test_equilibria_from_primitives.py::test_first_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[S]`

- **Outcome:** passed (3.4 s)
- **Tests directly:** L2.unique
- **What:** Uniqueness in the first period of Lemma 1 (case 0), Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 28 points (seed 404), 15 regular (12 uniform, 1 under each other distribution) and 13 edge (12 uniform, 1 truncated normal).
- **Computed:** `section4.scan_fixed_points` for T(y_B) = BR_B(BR_A(y_B)) of the two-period payoffs on [0, 1.5 (mu + sigma)], with 21 coarse and 41 fine nodes and a best-response grid of 801 under the uniform distribution, 9, 15 and 101 under the others.
- **Criterion:** T(y_B) - y_B is positive at the lowest node and negative at the highest, its sign changes between exactly one pair of neighbouring nodes, and that pair encloses the claimed y_B up to the noise allowance 1e-6 max(mu + sigma, max T). Two equilibria between the same two neighbouring nodes would not be seen.
- **Recorded:** regular points = 15; edge points = 13; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; evaluations of the composed best response = 1584
- **At the level of rounding error (differs between machines):** widest bracket of the fixed point relative to demand = 0.000285715

<a id="check-9"></a>
### `tests/test_equilibria_from_primitives.py::test_second_period_equilibrium_and_continuation_value[G]`

- **Outcome:** passed (7.7 s)
- **Tests directly:** LB1.second
- **What:** Second period of Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 109 points (seed 202), 78 regular (60 uniform, 6 under each other distribution) and 31 edge (30 uniform, 1 beta(2,5)). One first-period sales state per point, R_A uniform on [0, mu + sigma] and R_B uniform on [0, mu + sigma - R_A].
- **Computed:** the claimed orders y^0_{i,2} + Z_{i,2}, `primitives.nash_gap` on [0, 1.5 (mu + sigma)(1 + gamma)] for the second-period payoffs of `section4.Game`, and each retailer's profit there, all from the primitives.
- **Criterion:** with scale mu (1 + gamma), no deviation gains more than 1e-8 times the scale, each best response lies within 2e-5 max(1, scale) of the claim, and each profit differs from pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2} by at most 1e-9 times the scale.
- **Recorded:** regular points = 78; edge points = 31; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']
- **At the level of rounding error (differs between machines):** max relative gain from deviation = 3.61154e-14; max relative error of continuation value = 1.80577e-14

<a id="check-10"></a>
### `tests/test_equilibria_from_primitives.py::test_second_period_equilibrium_and_continuation_value[N]`

- **Outcome:** passed (7.8 s)
- **Tests directly:** L3.second
- **What:** Second period of Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 109 points (seed 202), 78 regular (60 uniform, 6 under each other distribution) and 31 edge (30 uniform, 1 beta(2,5)). One first-period sales state per point, R_A uniform on [0, mu + sigma] and R_B uniform on [0, mu + sigma - R_A].
- **Computed:** the claimed orders y^0_{i,2} + Z_{i,2}, `primitives.nash_gap` on [0, 1.5 (mu + sigma)(1 + gamma)] for the second-period payoffs of `section4.Game`, and each retailer's profit there, all from the primitives.
- **Criterion:** with scale mu (1 + gamma), no deviation gains more than 1e-8 times the scale, each best response lies within 2e-5 max(1, scale) of the claim, and each profit differs from pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2} by at most 1e-9 times the scale.
- **Recorded:** regular points = 78; edge points = 31; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']
- **At the level of rounding error (differs between machines):** max relative gain from deviation = 8.48791e-15; max relative error of continuation value = 2.70865e-14

<a id="check-11"></a>
### `tests/test_equilibria_from_primitives.py::test_second_period_equilibrium_and_continuation_value[S]`

- **Outcome:** passed (7.8 s)
- **Tests directly:** L2.second
- **What:** Second period of Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 109 points (seed 202), 78 regular (60 uniform, 6 under each other distribution) and 31 edge (30 uniform, 1 beta(2,5)). One first-period sales state per point, R_A uniform on [0, mu + sigma] and R_B uniform on [0, mu + sigma - R_A].
- **Computed:** the claimed orders y^0_{i,2} + Z_{i,2}, `primitives.nash_gap` on [0, 1.5 (mu + sigma)(1 + gamma)] for the second-period payoffs of `section4.Game`, and each retailer's profit there, all from the primitives.
- **Criterion:** with scale mu (1 + gamma), no deviation gains more than 1e-8 times the scale, each best response lies within 2e-5 max(1, scale) of the claim, and each profit differs from pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2} by at most 1e-9 times the scale.
- **Recorded:** regular points = 78; edge points = 31; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']
- **At the level of rounding error (differs between machines):** max relative gain from deviation = 2.79616e-14; max relative error of continuation value = 1.44642e-14

<a id="check-12"></a>
### `tests/test_equilibria_from_primitives.py::test_second_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[0]`

- **Outcome:** passed (3.4 s)
- **Tests directly:** L1.unique
- **What:** Uniqueness in the second period of Lemma 1 (case 0, the benchmark game at the second-period prices), Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 28 points (seed 505), 15 regular (12 uniform, 1 under each other distribution) and 13 edge (12 uniform, 1 beta(2,5)), each with one random first-period sales state (seed 405) drawn as in the second-period equilibrium check.
- **Computed:** `section4.scan_fixed_points` for the composed best-response map of the second-period payoffs on [0, 1.5 (mu + sigma)(1 + gamma)], with the nodes and grids of the first-period scan.
- **Criterion:** as in the first-period scan, with the claimed y^0_{B,2} + Z_{B,2} in place of y_B: one change of sign, from positive to negative, between two neighbouring nodes that enclose the claim up to the noise allowance 1e-6 max(mu + sigma, max T).
- **Recorded:** regular points = 15; edge points = 13; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; evaluations of the composed best response = 1584
- **At the level of rounding error (differs between machines):** widest bracket of the fixed point relative to demand = 0.000285715

<a id="check-13"></a>
### `tests/test_equilibria_from_primitives.py::test_second_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[G]`

- **Outcome:** passed (3.4 s)
- **Tests directly:** LB1.unique
- **What:** Uniqueness in the second period of Lemma 1 (case 0, the benchmark game at the second-period prices), Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 28 points (seed 505), 15 regular (12 uniform, 1 under each other distribution) and 13 edge (12 uniform, 1 beta(2,5)), each with one random first-period sales state (seed 405) drawn as in the second-period equilibrium check.
- **Computed:** `section4.scan_fixed_points` for the composed best-response map of the second-period payoffs on [0, 1.5 (mu + sigma)(1 + gamma)], with the nodes and grids of the first-period scan.
- **Criterion:** as in the first-period scan, with the claimed y^0_{B,2} + Z_{B,2} in place of y_B: one change of sign, from positive to negative, between two neighbouring nodes that enclose the claim up to the noise allowance 1e-6 max(mu + sigma, max T).
- **Recorded:** regular points = 15; edge points = 13; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; evaluations of the composed best response = 1584
- **At the level of rounding error (differs between machines):** widest bracket of the fixed point relative to demand = 0.00191011

<a id="check-14"></a>
### `tests/test_equilibria_from_primitives.py::test_second_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[N]`

- **Outcome:** passed (3.4 s)
- **Tests directly:** L3.unique
- **What:** Uniqueness in the second period of Lemma 1 (case 0, the benchmark game at the second-period prices), Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 28 points (seed 505), 15 regular (12 uniform, 1 under each other distribution) and 13 edge (12 uniform, 1 beta(2,5)), each with one random first-period sales state (seed 405) drawn as in the second-period equilibrium check.
- **Computed:** `section4.scan_fixed_points` for the composed best-response map of the second-period payoffs on [0, 1.5 (mu + sigma)(1 + gamma)], with the nodes and grids of the first-period scan.
- **Criterion:** as in the first-period scan, with the claimed y^0_{B,2} + Z_{B,2} in place of y_B: one change of sign, from positive to negative, between two neighbouring nodes that enclose the claim up to the noise allowance 1e-6 max(mu + sigma, max T).
- **Recorded:** regular points = 15; edge points = 13; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; evaluations of the composed best response = 1584
- **At the level of rounding error (differs between machines):** widest bracket of the fixed point relative to demand = 0.00142599

<a id="check-15"></a>
### `tests/test_equilibria_from_primitives.py::test_second_period_equilibrium_is_the_only_fixed_point_found_by_a_scan[S]`

- **Outcome:** passed (3.4 s)
- **Tests directly:** L2.unique
- **What:** Uniqueness in the second period of Lemma 1 (case 0, the benchmark game at the second-period prices), Lemma 2 (case S), Lemma 3 (case N) or Lemma B.1 (case G).
- **Points:** 28 points (seed 505), 15 regular (12 uniform, 1 under each other distribution) and 13 edge (12 uniform, 1 beta(2,5)), each with one random first-period sales state (seed 405) drawn as in the second-period equilibrium check.
- **Computed:** `section4.scan_fixed_points` for the composed best-response map of the second-period payoffs on [0, 1.5 (mu + sigma)(1 + gamma)], with the nodes and grids of the first-period scan.
- **Criterion:** as in the first-period scan, with the claimed y^0_{B,2} + Z_{B,2} in place of y_B: one change of sign, from positive to negative, between two neighbouring nodes that enclose the claim up to the noise allowance 1e-6 max(mu + sigma, max T).
- **Recorded:** regular points = 15; edge points = 13; distributions = ['beta(2,5)', 'triangular', 'truncated normal', 'uniform']; evaluations of the composed best response = 1584
- **At the level of rounding error (differs between machines):** widest bracket of the fixed point relative to demand = 0.00191011

<a id="check-16"></a>
### `tests/test_figures.py::test_figure_1_equilibria_are_unique_and_the_continuation_is_constant`

- **Outcome:** passed (0.0 s)
- **Tests directly:** F1
- **What:** Figure 1: the two-price game that the figure plots has one equilibrium at every point.
- **Points:** the 44 parameter points of Figure 1 (4 panels, 11 values of theta), Scenarios S and N.
- **Computed:** `figure1_data`, which runs `pricing.pricing_equilibrium` at every point and scenario. The solver raises unless exactly one second-period price pair is an equilibrium at every feasible sales state, `figure1_point` raises unless there is exactly one first-period pure equilibrium, and the solver warns if another price pair is an equilibrium at some sales state.
- **Criterion:** the table has all 44 rows, and no warning was issued.
- **Recorded:** parameter points = 44

<a id="check-17"></a>
### `tests/test_figures.py::test_figure_1_matches_the_published_figure[a]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** F1
- **What:** Figure 1, one panel, against the published figure.
- **Points:** one panel of Figure 1 (a, b, c or d) with the series of Scenarios S and N, 11 values of theta each (0.01, 0.1, ..., 0.9, 0.99).
- **Computed:** the equilibrium profits of `figure1_data`, from the two-price game that `c2c.pricing` solves, rounded to four decimals and unrounded, and the values that `published_data.csv` reads back from the panel's EPS file. The published panels were drawn from four-decimal data.
- **Criterion:** each series has 11 plotted points whose theta agree within 1e-9, the largest absolute difference to the four-decimal values is at most the panel's extraction error bound plus 1e-9, and to the unrounded values at most 5e-5 plus that bound plus 1e-9.
- **Recorded:** extraction error bound = 2.72e-06; max abs difference to four decimal values = 2.2e-06; max abs difference to unrounded values = 4.67573e-05

<a id="check-18"></a>
### `tests/test_figures.py::test_figure_1_matches_the_published_figure[b]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** F1
- **What:** Figure 1, one panel, against the published figure.
- **Points:** one panel of Figure 1 (a, b, c or d) with the series of Scenarios S and N, 11 values of theta each (0.01, 0.1, ..., 0.9, 0.99).
- **Computed:** the equilibrium profits of `figure1_data`, from the two-price game that `c2c.pricing` solves, rounded to four decimals and unrounded, and the values that `published_data.csv` reads back from the panel's EPS file. The published panels were drawn from four-decimal data.
- **Criterion:** each series has 11 plotted points whose theta agree within 1e-9, the largest absolute difference to the four-decimal values is at most the panel's extraction error bound plus 1e-9, and to the unrounded values at most 5e-5 plus that bound plus 1e-9.
- **Recorded:** extraction error bound = 1.65e-05; max abs difference to four decimal values = 1.6e-05; max abs difference to unrounded values = 5.64286e-05

<a id="check-19"></a>
### `tests/test_figures.py::test_figure_1_matches_the_published_figure[c]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** F1
- **What:** Figure 1, one panel, against the published figure.
- **Points:** one panel of Figure 1 (a, b, c or d) with the series of Scenarios S and N, 11 values of theta each (0.01, 0.1, ..., 0.9, 0.99).
- **Computed:** the equilibrium profits of `figure1_data`, from the two-price game that `c2c.pricing` solves, rounded to four decimals and unrounded, and the values that `published_data.csv` reads back from the panel's EPS file. The published panels were drawn from four-decimal data.
- **Criterion:** each series has 11 plotted points whose theta agree within 1e-9, the largest absolute difference to the four-decimal values is at most the panel's extraction error bound plus 1e-9, and to the unrounded values at most 5e-5 plus that bound plus 1e-9.
- **Recorded:** extraction error bound = 1.92e-06; max abs difference to four decimal values = 1.796e-06; max abs difference to unrounded values = 4.86077e-05

<a id="check-20"></a>
### `tests/test_figures.py::test_figure_1_matches_the_published_figure[d]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** F1
- **What:** Figure 1, one panel, against the published figure.
- **Points:** one panel of Figure 1 (a, b, c or d) with the series of Scenarios S and N, 11 values of theta each (0.01, 0.1, ..., 0.9, 0.99).
- **Computed:** the equilibrium profits of `figure1_data`, from the two-price game that `c2c.pricing` solves, rounded to four decimals and unrounded, and the values that `published_data.csv` reads back from the panel's EPS file. The published panels were drawn from four-decimal data.
- **Criterion:** each series has 11 plotted points whose theta agree within 1e-9, the largest absolute difference to the four-decimal values is at most the panel's extraction error bound plus 1e-9, and to the unrounded values at most 5e-5 plus that bound plus 1e-9.
- **Recorded:** extraction error bound = 1.46e-05; max abs difference to four decimal values = 1e-05; max abs difference to unrounded values = 5.51625e-05

<a id="check-21"></a>
### `tests/test_figures.py::test_figure_b1_matches_the_authors_matlab_values`

- **Outcome:** passed (0.0 s)
- **Tests directly:** FB1
- **What:** Figure B.1 against the authors' MATLAB output.
- **Points:** the 9 plotted series of Figure B.1 at the 11 values of theta 0, 0.1, ..., 1 and the parameters of its caption: 99 values.
- **Computed:** `c2c.figures.figureB1_data`, from `find_general_exo` of `c2c.closed_form`, and the table `numerics/matlab/Figure2_MATLAB/Figure2_reference.csv`. The number of values that agree digit for digit at 15 significant digits is recorded.
- **Criterion:** the two tables have the same columns, and the largest absolute difference is below 1e-10.
- **Recorded:** values compared = 99
- **At the level of rounding error (differs between machines):** values equal digit for digit = 99; max abs difference = 4.9738e-14

<a id="check-22"></a>
### `tests/test_figures.py::test_figure_b1_matches_the_published_figure[a]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** FB1
- **What:** Figure B.1, one panel, against the published figure.
- **Points:** one panel of Figure B.1 (a, b, c or d) with its 2 plotted series (3 in panel b), 11 values of theta each.
- **Computed:** the recomputed values of `figureB1_data`, and the values that `published_data.csv` reads back from the panel's EPS file.
- **Criterion:** each series has 11 plotted points whose theta agree with the recomputed grid within 1e-9, and the largest absolute difference is at most the panel's extraction error bound in `published_data_calibration.json` plus 1e-9.
- **Recorded:** extraction error bound = 1.29e-06; max abs difference = 1.00985e-06

<a id="check-23"></a>
### `tests/test_figures.py::test_figure_b1_matches_the_published_figure[b]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** FB1
- **What:** Figure B.1, one panel, against the published figure.
- **Points:** one panel of Figure B.1 (a, b, c or d) with its 2 plotted series (3 in panel b), 11 values of theta each.
- **Computed:** the recomputed values of `figureB1_data`, and the values that `published_data.csv` reads back from the panel's EPS file.
- **Criterion:** each series has 11 plotted points whose theta agree with the recomputed grid within 1e-9, and the largest absolute difference is at most the panel's extraction error bound in `published_data_calibration.json` plus 1e-9.
- **Recorded:** extraction error bound = 1.35e-06; max abs difference = 1.03725e-06

<a id="check-24"></a>
### `tests/test_figures.py::test_figure_b1_matches_the_published_figure[c]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** FB1
- **What:** Figure B.1, one panel, against the published figure.
- **Points:** one panel of Figure B.1 (a, b, c or d) with its 2 plotted series (3 in panel b), 11 values of theta each.
- **Computed:** the recomputed values of `figureB1_data`, and the values that `published_data.csv` reads back from the panel's EPS file.
- **Criterion:** each series has 11 plotted points whose theta agree with the recomputed grid within 1e-9, and the largest absolute difference is at most the panel's extraction error bound in `published_data_calibration.json` plus 1e-9.
- **Recorded:** extraction error bound = 3.68e-06; max abs difference = 3.52403e-06

<a id="check-25"></a>
### `tests/test_figures.py::test_figure_b1_matches_the_published_figure[d]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** FB1
- **What:** Figure B.1, one panel, against the published figure.
- **Points:** one panel of Figure B.1 (a, b, c or d) with its 2 plotted series (3 in panel b), 11 values of theta each.
- **Computed:** the recomputed values of `figureB1_data`, and the values that `published_data.csv` reads back from the panel's EPS file.
- **Criterion:** each series has 11 plotted points whose theta agree with the recomputed grid within 1e-9, and the largest absolute difference is at most the panel's extraction error bound in `published_data_calibration.json` plus 1e-9.
- **Recorded:** extraction error bound = 9.99e-07; max abs difference = 9.15257e-07

<a id="check-26"></a>
### `tests/test_figures.py::test_figure_b1_patterns_described_in_appendix_b`

- **Outcome:** passed (0.0 s)
- **Tests directly:** N5
- **What:** Online Appendix B. Panel (b): retailer B's order quantity in Scenario GN decreases in theta. Panels (a), (c), (d): the comparisons of Propositions 1, 5 and 6 carry over, each with a single crossing in theta.
- **Points:** the 11 values of theta 0, 0.1, ..., 1 of Figure B.1, all four panels.
- **Computed:** the series of `figureB1_data`: y_{B,1} in Scenarios GN, GS and 0 for panel (b), and the gaps GS - GN of panels (a), (c) and (d).
- **Criterion:** b_GN falls at every step, the range of b_GS is below 0.05 and that of b_0 is exactly 0, and each of the three gaps is positive at theta = 0, negative at theta = 1 and changes sign between exactly one pair of neighbouring values.
- **Recorded:** crossing between theta panel a = 0.5 and 0.6; crossing between theta panel c = 0.8 and 0.9; crossing between theta panel d = 0.1 and 0.2

<a id="check-27"></a>
### `tests/test_figures.py::test_moderate_gamma_panels_show_one_profit_crossing`

- **Outcome:** passed (0.0 s)
- **Tests directly:** N2
- **What:** Section 5.3, Figure 1(a) and (c), gamma = 0.7. Retailer A: Scenario N becomes more profitable than Scenario S as theta increases to 1. Retailer B: Scenario S yields the higher profit when theta is small.
- **Points:** panels (a) and (c) of Figure 1 (c_A = 0.10 and 0.95), 11 values of theta.
- **Computed:** the gap Pi^N - Pi^S of the plotted retailer from `figure1_data`, and the crossings of `figure1_crossings`, located by Brent's method between neighbouring values of theta at which the gap changes sign.
- **Criterion:** in each panel the gap is negative at theta = 0.01 and positive at 0.99, its sign changes between exactly one pair of neighbouring values, and `figure1_crossings` returns exactly one crossing.
- **Recorded:** crossing theta panel a = 0.769736; crossing theta panel c = 0.579998

<a id="check-28"></a>
### `tests/test_figures.py::test_numerical_statements_are_quoted_from_the_paper`

- **Outcome:** passed (0.0 s)
- **Supports:** F1, FB1, N1, N2, N3, N4, N5, N6
- **Points:** the nine entries of `numerics/numerical_statements.yaml`, including N7, which the repository lists and does not check.
- **Computed:** each quote, against the LaTeX source of the paper with every \ref printed as the number that `numerics/paper_labels.json` gives.
- **Criterion:** every quote occurs verbatim, up to whitespace, so that the checks of this file test the paper's own sentences, and exactly N7 carries a field `excluded`.
- **Recorded:** statements quoted = 9

<a id="check-29"></a>
### `tests/test_figures.py::test_published_data_match_a_fresh_extraction_from_the_eps_files`

- **Outcome:** passed (0.5 s)
- **Supports:** F1, FB1
- **Points:** the 8 EPS panels of Figure 1 and Figure B.1 in `paper/`.
- **Computed:** `numerics/figures/extract_published_data.py` reads every plotted vertex back from the vector graphics into a temporary folder.
- **Criterion:** the fresh extraction equals the committed `published_data.csv` and `published_data_calibration.json` byte for byte, so that every comparison with a published figure in this file uses data that the EPS files reproduce.
- **Recorded:** panels = 8; plotted points = 187

<a id="check-30"></a>
### `tests/test_figures.py::test_split_ratios_are_constant_over_time_in_figure_1`

- **Outcome:** passed (0.0 s)
- **Tests directly:** N1
- **What:** Section 5.3: equilibrium prices may differ across the two periods, but the market split is the same in both periods at every plotted point.
- **Points:** the 44 parameter points of Figure 1, Scenarios S and N.
- **Computed:** the shares alpha_{A,t} = 1/2 + beta (p_{B,t} - p_{A,t}) at the equilibrium prices of `figure1_data` in both periods, and the number of pairs of point and scenario at which a price changes between the periods.
- **Criterion:** the two shares are exactly equal at every point and scenario, and a price changes between the periods at one pair or more.
- **Recorded:** points where prices change between periods = 22

<a id="check-31"></a>
### `tests/test_figures.py::test_strong_gamma_panels_show_no_crossing`

- **Outcome:** passed (0.1 s)
- **Tests directly:** N3, N4
- **What:** Section 5.3, Figure 1(b) and (d), gamma = 2. Each retailer earns more in Scenario N at every theta, with equal market shares in the two periods.
- **Points:** panels (b) and (d) of Figure 1 (c_A = 0.10 and 0.95), 11 values of theta.
- **Computed:** the gap Pi^N - Pi^S of the plotted retailer from `figure1_data`, and the crossings of `figure1_crossings`. The equal shares are checked by the N1 check above.
- **Criterion:** the gap is positive at all 11 values in both panels, and `figure1_crossings` returns no crossing for either panel.
- **Recorded:** min profit advantage of N panel b = 9.77993; min profit advantage of N panel d = 9.90863

<a id="check-32"></a>
### `tests/test_other_distributions.py::test_large_gamma_patterns_under_other_distributions`

- **Outcome:** passed (0.0 s)
- **Tests directly:** N6
- **What:** Weak forms of the parts of Propositions 1 and 3 to 6 that the paper states for gamma large.
- **Points:** the 48 points and 41 values of theta of the previous check, gamma = 1e3, 1e4, 1e8.
- **Computed:** orders and expected sales as there, and two-period profits from the payoffs of `section4.Game`. The number of points at which E[R^N_1] visibly falls and then rises is recorded.
- **Criterion:** at gamma = 1e3 and 1e4, y^S_A - y^N_A and E[R^S_A] - E[R^N_A] change sign at most once, from positive to negative, E[R^S_A] is non-decreasing and E[R^N_A] increasing overall, E[R^N_1] changes direction at most once, from falling to rising, Pi^S_A is non-decreasing, all four profits exceed the benchmark at every theta, Pi^S_B is nearly constant and Pi^N_B increasing overall, and where the shares agree within 1e-6 each Pi^S_i - Pi^N_i changes sign at most once, from positive to negative. At gamma = 1e8, alpha_{A,1} < alpha_{A,2} - 1e-6 gives Pi^S_A < Pi^N_A and Pi^S_B > Pi^N_B at every theta, and alpha_{A,1} > alpha_{A,2} + 1e-6 the reverse. Sign checks ignore entries below 1e-9 (1 + max |d|), and none of the "at most once" checks requires a change to exist.
- **Recorded:** P1 at most one crossing of y A: failures = 0; P3a sales of A: failures = 0; P3a at most one crossing of sales of A: failures = 0; P4 at most one change of direction: failures = 0; P5a: failures = 0; P5b: failures = 0; P5c2 weak: failures = 0; P6a: failures = 0; P6b: failures = 0; P6c2 weak: failures = 0; P5c1: failures = 0; P6c1: failures = 0; P4 visibly falls then rises at gamma = 1000: points = 48; P4 visibly falls then rises at gamma = 10000: points = 48

<a id="check-33"></a>
### `tests/test_other_distributions.py::test_order_quantities_and_sales_patterns_under_other_distributions`

- **Outcome:** passed (0.0 s)
- **Tests directly:** N6
- **What:** Patterns of the parts of Propositions 1 to 3 that the paper states for every gamma.
- **Points:** 48 points of `draw_exogenous` (seed 808), 16 for each of the triangular, beta(2,5) and truncated normal distributions on [mu - sigma, mu + sigma], every second one with equal shares in both periods, 41 values of theta on [0, 1], gamma = 2, 1e3, 1e4.
- **Computed:** for the benchmark and Scenarios S and N, the orders of `claimed_first_period` through the quantile function and expected first-period sales by quadrature.
- **Criterion:** retailer A has the higher fractile at every evaluation, y^0_A and y^N_A are increasing overall, y^S_A is increasing overall at gamma = 2 and non-decreasing at the larger values, y^N_B and E[R^N_B] are decreasing overall, y^0_B, y^S_B and E[R^S_B] are nearly constant, and y^0_B < y^N_B < y^S_B and E[R^N_B] < E[R^S_B] at every theta. With t = 1e-10 (1 + max |v|), "increasing overall" means no step below -t and a total rise above t, and "nearly constant" means a range of at most 10 t.
- **Recorded:** parameter points = 48; distributions = ['triangular', 'beta(2,5)', 'truncated normal']; gammas = [2.0, 1000.0, 10000.0]

<a id="check-34"></a>
### `tests/test_port_matches_paper.py::test_benchmark_profit_polynomials_match_lemma_1`

- **Outcome:** passed (0.2 s)
- **Supports:** L1.eq
- **What:** Benchmark profits pi^0 = (p - c) y^0 - p E[L^0] at the equilibrium of Lemma 1.
- **Points:** 25 random rational parameter points (seed 1), at their second-period prices. The points need not satisfy the assumptions of the paper.
- **Computed:** pi^0_A and pi^0_B from this file's transcription of Lemma 1 and of the end of its proof, and `pfta_t2_case1` and `pftb_t2_case1` of `c2c.closed_form`, all in exact rational arithmetic. Three LaTeX strings of Lemma 1 and its proof are quoted.
- **Criterion:** both profits are equal as rational numbers at every point, and every quoted string occurs verbatim, up to whitespace, in the LaTeX source in `paper/`.
- **Recorded:** exact rational points = 25

<a id="check-35"></a>
### `tests/test_port_matches_paper.py::test_branch_conditions_in_the_code_are_the_fractile_orderings`

- **Outcome:** passed (0.0 s)
- **Tests directly:** L2.first, L3.first
- **What:** Which retailer has the higher critical fractile, as the code decides it.
- **Points:** 25 random rational parameter points (seed 6).
- **Computed:** the branch flag that `first_period_s` and `first_period_n` derive from an inequality in prices, and the comparison of the fractiles of Lemmas 2 and 3, c_B (p_{A,1} + g_A (p_{A,2} - c_A)) >= c_A (p_{B,1} + g_B (p_{B,2} - c_B)), with g_i = gamma in Scenario S and g_i = alpha_{i,2} gamma in Scenario N, in exact rational arithmetic.
- **Criterion:** the flag equals the comparison at every point, in both scenarios.
- **Recorded:** exact rational points = 25

<a id="check-36"></a>
### `tests/test_port_matches_paper.py::test_expected_leftovers_in_the_code_follow_from_the_model`

- **Outcome:** passed (0.0 s)
- **Supports:** L1, L2, L3, LB1
- **What:** The two expected-leftover expressions used throughout `c2c.closed_form`.
- **Points:** none. The check is symbolic in the positive symbols a_A, a_B, zeta_A, zeta_B, theta, mu and sigma.
- **Computed:** E[(y_i - D_i)^+] at the order quantities of Lemmas 1, 2, 3 and B.1, by SymPy integration of the demand system of Section 3 over X ~ U[mu - sigma, mu + sigma] for mu - sigma <= zeta_B <= zeta_A <= mu + sigma, and `_leftover_high` and `_leftover_low` of `c2c.closed_form` in the same symbols.
- **Criterion:** each of the two differences expands to exactly 0.

<a id="check-37"></a>
### `tests/test_port_matches_paper.py::test_mixed_scenario_code_matches_lemma_b1`

- **Outcome:** passed (0.3 s)
- **Tests directly:** LB1.first
- **What:** Mixed scenario of Online Appendix B: Lemma B.1.
- **Points:** 25 random rational parameter points (seed 4), each with a weight lambda_S drawn from the multiples of 1/1000 in [0, 1] (seed 40) and lambda_N = 1 - lambda_S.
- **Computed:** first-period order quantities and total two-period profits of both retailers from this file's transcription of Lemma B.1, and from `find_general_exo` of `c2c.closed_form`, in exact rational arithmetic. Four LaTeX strings of Online Appendix B are quoted.
- **Criterion:** the four values are equal as rational numbers at every point, and every quoted string occurs verbatim, up to whitespace, in the LaTeX source in `paper/`.
- **Recorded:** exact rational points = 25

<a id="check-38"></a>
### `tests/test_port_matches_paper.py::test_mixed_scenario_reduces_to_scenarios_s_and_n`

- **Outcome:** passed (0.1 s)
- **Tests directly:** LB1.first
- **Supports:** L2, L3
- **What:** Online Appendix B: Scenario S is the mixed scenario with weights (1, 0) and Scenario N is the mixed scenario with weights (0, 1).
- **Points:** 25 random rational parameter points (seed 5).
- **Computed:** `find_general_exo` with weights (1, 0) and (0, 1), and the order quantities and total profits of `first_period_s`, `spfta_t1`, `spftb_t1` and of `first_period_n`, `npfta_t1`, `npftb_t1`, with the branch of the lemmas forced, in exact rational arithmetic. The sentence of Online Appendix B on the Scenario S case is quoted.
- **Criterion:** both pairs of four-value tuples are equal as rational numbers at every point, and the quoted sentence occurs verbatim, up to whitespace, in the LaTeX source in `paper/`.
- **Recorded:** exact rational points = 25

<a id="check-39"></a>
### `tests/test_port_matches_paper.py::test_scenario_n_code_matches_lemma_3`

- **Outcome:** passed (0.3 s)
- **Tests directly:** L3.first, L3.profits
- **What:** Scenario N: Lemma 3 and equations (A.12) and (A.14) with rho = 1.
- **Points:** 25 random rational parameter points (seed 3).
- **Computed:** critical values, order quantities and expected leftovers of the first period and total two-period profits of both retailers, from this file's transcription of Lemma 3, (A.12) and (A.14), and from `first_period_n`, `npfta_t1` and `npftb_t1` of `c2c.closed_form` with the branch of Lemma 3 forced, all in exact rational arithmetic. Three LaTeX strings of Lemma 3 and its proof are quoted.
- **Criterion:** the six first-period values and both profits are equal as rational numbers at every point, and every quoted string occurs verbatim, up to whitespace, in the LaTeX source in `paper/`.
- **Recorded:** exact rational points = 25

<a id="check-40"></a>
### `tests/test_port_matches_paper.py::test_scenario_s_code_matches_lemma_2`

- **Outcome:** passed (0.3 s)
- **Tests directly:** L2.first, L2.profits
- **What:** Scenario S: Lemma 2 and equations (A.8) and (A.10) with rho = 1.
- **Points:** 25 random rational parameter points (seed 2).
- **Computed:** critical values, order quantities and expected leftovers of the first period and total two-period profits of both retailers, from this file's transcription of Lemma 2, (A.8) and (A.10), and from `first_period_s`, `spfta_t1` and `spftb_t1` of `c2c.closed_form` with the branch of Lemma 2 forced, all in exact rational arithmetic. Three LaTeX strings of Lemma 2 and its proof are quoted.
- **Criterion:** the six first-period values and both profits are equal as rational numbers at every point, and every quoted string occurs verbatim, up to whitespace, in the LaTeX source in `paper/`.
- **Recorded:** exact rational points = 25

<a id="check-41"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[0]`

- **Outcome:** passed (0.0 s)
- **Supports:** L1.eq, L4.a, P1.i, P2.a, P2.b, P5.b, P6.b
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 34
- **At the level of rounding error (differs between machines):** max relative difference = 4.686e-16

<a id="check-42"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]`

- **Outcome:** passed (0.0 s)
- **Supports:** LB1.first, FB1, N5
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points edge = 100; points where retailer B has the higher fractile = 0
- **At the level of rounding error (differs between machines):** max relative difference = 7.44804e-16

<a id="check-43"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[N]`

- **Outcome:** passed (0.0 s)
- **Supports:** L3.first, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P4, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 26
- **At the level of rounding error (differs between machines):** max relative difference = 7.44804e-16

<a id="check-44"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[S]`

- **Outcome:** passed (0.0 s)
- **Supports:** L2.first, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P5.a, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2, F1
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points without A11 = 200; points edge = 100; points where retailer B has the higher fractile = 33
- **At the level of rounding error (differs between machines):** max relative difference = 7.44804e-16

<a id="check-45"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_profits_of_the_mixed_scenario_equal_the_model`

- **Outcome:** passed (0.1 s)
- **Supports:** FB1, N5
- **What:** Link (b) for the mixed scenario of Online Appendix B (Lemma B.1).
- **Points:** 300 points (seed 506), 200 of `draw_exogenous` and 100 of `draw_edge_exact`, all of which satisfy A11, because the code implements only the ordering of Lemma B.1.
- **Computed:** total two-period profits of both retailers at the orders of `find_general_exo`, from that function and from the payoffs of `section4.Game` (scenario G) integrated exactly under the uniform distribution. The code returns no expected sales for this scenario, so sales are not compared.
- **Criterion:** every difference is at most 1e-9 mu (1 + gamma) max(p_{B,1}, p_{B,2}).
- **Recorded:** points regular = 200; points edge = 100; points where retailer B has the higher fractile = 0
- **At the level of rounding error (differs between machines):** max relative error profit = 8.04278e-15

<a id="check-46"></a>
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

<a id="check-47"></a>
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

<a id="check-48"></a>
### `tests/test_profits_and_price_game.py::test_figure_1_inventory_equilibria_hold_in_the_model`

- **Outcome:** passed (0.2 s)
- **Tests directly:** F1
- **What:** Figure 1: the first-period inventory equilibria behind the payoff matrices, including the price pairs that violate assumption A11.
- **Points:** the 4 panels of Figure 1 at theta = 0.01, 0.5 and 0.99, Scenarios S and N, and the 4 first-period price pairs of {2, 4}: 96 inventory games.
- **Computed:** the orders of `section4.claimed_first_period` at the second-period prices of `pricing.pricing_equilibrium`, and `primitives.nash_gap` on [0, 1.5 (mu + sigma)] for the two-period payoffs of `section4.Game`, built from the primitives.
- **Criterion:** the solver issues no warning, and in every game no deviation gains more than 1e-7 and each best response lies within 2e-5 of the claimed order, both absolute.
- **Recorded:** inventory games checked = 96
- **At the level of rounding error (differs between machines):** max gain from deviation = 1.42109e-14; max distance best response to claim = 1.63615e-07

<a id="check-49"></a>
### `tests/test_profits_and_price_game.py::test_figure_1_payoff_matrices_equal_the_model`

- **Outcome:** passed (0.1 s)
- **Tests directly:** F1
- **What:** Figure 1: the payoff matrices of the first-period price game.
- **Points:** the 44 parameter points of Figure 1 (4 panels, 11 values of theta), Scenarios S and N, and the 4 first-period price pairs of {2, 4}: 352 cells.
- **Computed:** `pricing.pricing_equilibrium` with warnings turned into errors, and at its second-period prices the two-period profits from the primitives (`section4.Game`) at the orders of `section4.claimed_first_period`, for either ordering of the fractiles.
- **Criterion:** no warning, both fractiles in [0, 1] in every cell, every payoff of the solver within 1e-9 (absolute) of the model's, and retailer B has the higher fractile in one cell or more.
- **Recorded:** payoff cells compared = 352; cells where retailer B has the higher fractile = 44
- **At the level of rounding error (differs between machines):** max abs error = 5.68434e-14

<a id="check-50"></a>
### `tests/test_profits_and_price_game.py::test_figure_1_second_period_prices_are_an_equilibrium_at_every_sales_state`

- **Outcome:** passed (0.1 s)
- **Tests directly:** F1
- **What:** Figure 1: the solver's second-period price pair is the equilibrium whatever the first-period sales.
- **Points:** the 4 panels of Figure 1 at theta = 0.01, 0.3, 0.6 and 0.99, Scenarios S and N (32 cases), the 10 first-period sales states listed in the code, among them the corners (0, 0), (15, 0) and (0, 15) of the sales triangle, and the 4 price pairs of {2, 4}.
- **Computed:** second-period profits of both retailers from the primitives (`section4.Game`) at the orders y^0_{i,2} + Z_{i,2}, and at each state the price pairs from which no unilateral price change gains more than 1e-9.
- **Criterion:** in each case the solver runs without warning, its pair is such a pair at all 10 states, and it is the only price pair that is.
- **Recorded:** price games solved = 320

<a id="check-51"></a>
### `tests/test_profits_and_price_game.py::test_second_period_inventory_equilibrium_for_all_price_pairs_of_figure_1`

- **Outcome:** passed (0.1 s)
- **Tests directly:** F1
- **What:** Figure 1: the second-period inventory equilibrium y^0_{i,2} + Z_{i,2} that the profits above use, at every price pair, including pairs at which retailer B has the higher critical fractile.
- **Points:** (c_A, gamma) = (0.10, 0.7) and (0.95, 2.0), Scenarios S and N, theta = 0.01, 0.5 and 0.99, the 4 second-period price pairs of {2, 4}, and the sales state (R_A, R_B) = (5, 3.75): 48 games.
- **Computed:** `primitives.nash_gap` on [0, 1.5 (mu + sigma)(1 + gamma)] for the second-period payoffs of `section4.Game` at the claimed orders.
- **Criterion:** no unilateral deviation gains more than 1e-7 (absolute) in any game.
- **Recorded:** inventory games checked = 48
- **At the level of rounding error (differs between machines):** max gain from deviation = 1.42109e-14

<a id="check-52"></a>
### `tests/test_profits_and_price_game.py::test_second_period_profit_function_equals_the_model[N]`

- **Outcome:** passed (0.1 s)
- **Tests directly:** L3.profits
- **Supports:** F1
- **What:** Link (c) for Scenario S or Scenario N: the second-period profit that the appendix states and that the price game uses, as a function of prices and first-period sales.
- **Points:** 400 points of `draw_exogenous` (seed 909) with p_{A,2} and p_{B,2} redrawn independently on [1.05 c_B, 4 c_B], so that A11 is not imposed, and beta reduced to at most 0.45 / |p_{B,2} - p_{A,2}|. One sales state per point, R_A uniform on [0, mu + sigma] and R_B uniform on [0, mu + sigma - R_A].
- **Computed:** `closed_form.period2_profit`, and the profits that `section4.Game` computes from the primitives at the orders y^0_{i,2} + Z_{i,2}.
- **Criterion:** each difference is at most 1e-11 mu (1 + gamma) p_{i,2}, and c_A / p_{A,2} > c_B / p_{B,2} at one point or more.
- **Recorded:** parameter points = 400; points where retailer B has the higher fractile = 66
- **At the level of rounding error (differs between machines):** max relative error = 5.10395e-16

<a id="check-53"></a>
### `tests/test_profits_and_price_game.py::test_second_period_profit_function_equals_the_model[S]`

- **Outcome:** passed (0.1 s)
- **Tests directly:** L2.profits
- **Supports:** F1
- **What:** Link (c) for Scenario S or Scenario N: the second-period profit that the appendix states and that the price game uses, as a function of prices and first-period sales.
- **Points:** 400 points of `draw_exogenous` (seed 909) with p_{A,2} and p_{B,2} redrawn independently on [1.05 c_B, 4 c_B], so that A11 is not imposed, and beta reduced to at most 0.45 / |p_{B,2} - p_{A,2}|. One sales state per point, R_A uniform on [0, mu + sigma] and R_B uniform on [0, mu + sigma - R_A].
- **Computed:** `closed_form.period2_profit`, and the profits that `section4.Game` computes from the primitives at the orders y^0_{i,2} + Z_{i,2}.
- **Criterion:** each difference is at most 1e-11 mu (1 + gamma) p_{i,2}, and c_A / p_{A,2} > c_B / p_{B,2} at one point or more.
- **Recorded:** parameter points = 400; points where retailer B has the higher fractile = 66
- **At the level of rounding error (differs between machines):** max relative error = 5.34973e-16

<a id="check-54"></a>
### `tests/test_proposition_7_shapes.py::test_proposition_7a_shape_in_the_own_price`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P7.a
- **What:** Proposition 7(a), read literally: y_{i,2} as a function of the own second-period price.
- **Points:** 4,000 points of `draw_bounded_prices` (seed 1010), each with one sales state (R_A uniform on [0, mu + sigma], R_B on [0, mu + sigma - R_A]) and one rival price uniform on [p_lo, p_hi], Scenarios S and N, both retailers: 16,000 curves on a grid of 1,501 own prices between the price bounds.
- **Computed:** the orders of `second_period_orders` (Lemma 1 for either ordering of the fractiles plus Z_{i,2}) and the signs of their steps, ignoring steps of absolute value at most 1e-11 (1 + largest order on the grid). The number of accepted curves that end with a positive step is recorded. The proof implies that there are none.
- **Criterion:** every curve has no positive step, or its steps turn from positive to negative exactly once or exactly twice.
- **Recorded:** curves = 16000; points with theta equal to 0 = 490; points with theta equal to 1 = 495; sampled region = assumptions: A1, A10, A12, A13. c_B, c_A / c_B, mu, sigma / mu: as in draw_exogenous. beta: uniform on [0.02, 0.6]. p_hi: between 1/(2 beta) + 1.01 w and 1/(2 beta) + 2 w, with w = (mu + sigma)(c_A + 2 c_B)/(3 mu). p_lo: uniform on the interval that A12 and A13 leave, shrunk by one thousandth at both ends. theta: 0 with probability 1/8, 1 with probability 1/8, otherwise uniform on (0, 1). gamma: log-uniform on [0.05, 50]; 1 interior local maxima = 666; 2 interior local maxima = 2; decreasing = 15332; accepted curves that end with a positive slope = 0

<a id="check-55"></a>
### `tests/test_proposition_7_shapes.py::test_proposition_7b_shape_in_the_rival_price`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P7.b
- **What:** Proposition 7(b): y_{i,2} as a function of the rival's second-period price.
- **Points:** the 4,000 points, sales states and fixed prices of the 7(a) check, Scenarios S and N, both retailers: 16,000 curves on a grid of 1,501 rival prices.
- **Computed:** the orders of `second_period_orders` and the signs of their steps, ignoring steps of absolute value at most 1e-11 (1 + largest order on the grid).
- **Criterion:** every curve has no negative step, or its steps are negative first and positive afterwards, with exactly one change of sign.
- **Recorded:** curves = 16000; points with theta equal to 0 = 490; points with theta equal to 1 = 495; sampled region = assumptions: A1, A10, A12, A13. c_B, c_A / c_B, mu, sigma / mu: as in draw_exogenous. beta: uniform on [0.02, 0.6]. p_hi: between 1/(2 beta) + 1.01 w and 1/(2 beta) + 2 w, with w = (mu + sigma)(c_A + 2 c_B)/(3 mu). p_lo: uniform on the interval that A12 and A13 leave, shrunk by one thousandth at both ends. theta: 0 with probability 1/8, 1 with probability 1/8, otherwise uniform on (0, 1). gamma: log-uniform on [0.05, 50]; decreasing then increasing = 205; increasing = 15795

<a id="check-56"></a>
### `tests/test_proposition_7_shapes.py::test_second_period_orders_of_this_file_are_the_equilibrium_of_the_model`

- **Outcome:** passed (1.1 s)
- **Supports:** P7.a, P7.b
- **What:** Prerequisite of both parts: `second_period_orders` against the model.
- **Points:** 300 points of `draw_bounded_prices` (seed 1020), each with a pair of second-period prices uniform on [p_lo, p_hi] and one sales state drawn as above, Scenarios S and N: 600 second-period games.
- **Computed:** `second_period_orders`, the quantities of `section4.claimed_benchmark` plus the C2C-induced demand Z_{i,2}, and `primitives.nash_gap` on [0, 1.5 (mu + sigma)(1 + gamma)] for the second-period payoffs of `section4.Game`, built from the primitives.
- **Criterion:** the orders agree with the claimed ones within 1e-12 relative to the order, with scale mu (1 + gamma) no deviation gains more than 1e-8 times the scale and each best response lies within 2e-5 max(1, scale) of the order, and retailer B has the higher critical fractile at some but not all of the 300 points.
- **Recorded:** second period games = 600; points where retailer B has the higher fractile = 22
- **At the level of rounding error (differs between machines):** max relative difference to claimed benchmark = 7.53897e-16; max relative gain from deviation = 4.3215e-15

<a id="check-57"></a>
### `tests/test_propositions_exogenous.py::test_lemma_4a_benchmark_order_per_unit_of_share`

- **Outcome:** passed (0.0 s)
- **Tests directly:** L4.a
- **What:** Lemma 4(a): y^0_{A,t} / alpha_{A,t} >= y^0_{B,t} / alpha_{B,t}.
- **Points:** the 210 sample points (120 regular, 90 edge). Period 1 on the theta grid of gamma = 1/20, because the benchmark does not depend on gamma. Period 2 on the 21 values k / 20 of theta.
- **Computed:** e_t = y^0_{A,t} / alpha_{A,t} - y^0_{B,t} / alpha_{B,t} from `first_period_s` with gamma = 0, at the first-period prices for t = 1 and at the second-period prices for t = 2, in exact rational arithmetic.
- **Criterion:** e_t >= 0 at every node, and e_t = 0 at every node where A11 holds with equality in period t, e_t > 0 at every node otherwise.
- **Recorded:** regular points = 120; edge points = 90; points with equality in period 1 = 16; points with equality in period 2 = 12

<a id="check-58"></a>
### `tests/test_propositions_exogenous.py::test_lemma_4b_order_per_unit_of_share_in_scenarios_s_and_n`

- **Outcome:** passed (0.0 s)
- **Tests directly:** L4.b
- **What:** Lemma 4(b): y^k_{A,t} / alpha_{A,t} >= y^k_{B,t} / alpha_{B,t} for k = S and N.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid in period 1, the 21 values k / 20 of theta in period 2.
- **Computed:** e^k = y^k_{A,1} / alpha_{A,1} - y^k_{B,1} / alpha_{B,1} from `first_period_s` and `first_period_n` in exact rational arithmetic. By Lemmas 2 and 3 the second-period orders net of Z_{i,2} are the benchmark quantities at the second-period prices, so period 2 is the inequality of part (a) for t = 2. Second-period orders are not computed in any other way.
- **Criterion:** at every node and gamma e^S >= 0 and e^N > 0, e^S = 0 at every node where A11 holds with equality in both periods and e^S > 0 otherwise, and the period-2 condition of the Lemma 4(a) check holds.
- **Recorded:** regular points = 120; edge points = 90

<a id="check-59"></a>
### `tests/test_propositions_exogenous.py::test_proposition_1_i_order_quantities_of_retailer_a_increase_in_theta`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P1.i
- **What:** Proposition 1, first sentence: the orders of retailer A increase in theta.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** y^0_{A,1}, y^S_{A,1} and y^N_{A,1} on the grid from `first_period_s` and `first_period_n` in exact rational arithmetic.
- **Criterion:** at every point and gamma y^N_{A,1} is strictly increasing in theta, y^0_{A,1} is strictly increasing, or equal at every node where A11 holds with equality in period 1, and y^S_{A,1} is strictly increasing, or equal at every node where A11 holds with equality in both periods.
- **Recorded:** points where y0 A is constant = 16; points where yS A is constant = 4; regular points = 120; edge points = 90

<a id="check-60"></a>
### `tests/test_propositions_exogenous.py::test_proposition_1_ii_threshold_in_theta_for_large_gamma`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P1.ii
- **What:** Proposition 1, second sentence: a threshold in theta for y^S_{A,1} - y^N_{A,1}.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** d = y^S_{A,1} - y^N_{A,1} on the grid in exact rational arithmetic, and for each kind of point the lowest rung from which the large-gamma criterion holds at every point.
- **Criterion:** at gamma = 1e50 and 1e60, at every point, d > 0 at theta = 0, d < 0 at theta = 1 and the sign pattern of d along the grid, zeros skipped, is "+-". This is the interior threshold of the proof, while the statement also allows one at an end point. At every gamma of the ladder, d > 0 at theta = 0 and the pattern is "+" or "+-", which is what the proof shows for every gamma.
- **Recorded:** regular points = 120; holds at every regular point from gamma = 100.0; edge points = 90; holds at every edge point from gamma = 1000000000.0

<a id="check-61"></a>
### `tests/test_propositions_exogenous.py::test_proposition_2a_order_quantity_of_retailer_b_and_theta`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P2.a
- **What:** Proposition 2(a): the orders of retailer B and theta.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** y^0_{B,1}, y^S_{B,1} and y^N_{B,1} on the grid in exact rational arithmetic. The closed forms of y^0_{B,1} and y^S_{B,1} do not contain theta, so that half is a statement about the formulas of Lemmas 1 and 2.
- **Criterion:** at every point and gamma y^N_{B,1} is strictly decreasing in theta, and y^0_{B,1} and y^S_{B,1} are each equal at every node.
- **Recorded:** regular points = 120; edge points = 90

<a id="check-62"></a>
### `tests/test_propositions_exogenous.py::test_proposition_2b_ordering_of_the_order_quantities_of_retailer_b`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P2.b
- **What:** Proposition 2(b): the ordering of the orders of retailer B across the scenarios.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** y^0_{B,1}, y^N_{B,1} and y^S_{B,1} on the grid in exact rational arithmetic.
- **Criterion:** y^0_{B,1} < y^N_{B,1} < y^S_{B,1}, both strict, at every node, point and gamma.
- **Recorded:** regular points = 120; edge points = 90

<a id="check-63"></a>
### `tests/test_propositions_exogenous.py::test_proposition_2c_gap_of_retailer_b_rises_then_falls_in_gamma`

- **Outcome:** passed (6.5 s)
- **Tests directly:** P2.c
- **What:** Proposition 2(c): y^S_{B,1} - y^N_{B,1} first rises and then falls in gamma.
- **Points:** 70 points of `draw_exogenous_exact` (seed 707) and 50 of `draw_edge_exact` (seed 717), every second one with equal shares, at theta = 0, 1/2, 9/10 and 999/1000: 480 curves. The grid of gamma has one node per decade from 1e-6 to 1e60, and seven more nodes, at 1.3 to 7.5 times the decade, in the four decades around the largest coarse value.
- **Computed:** the gap from `first_period_s` and `first_period_n` with the branch of Lemmas 2 and 3 forced, in exact rational arithmetic, and its increments along the grid.
- **Criterion:** on every curve the sign pattern of the increments, zeros skipped, is "+-". A second rise that begins and ends between two neighbouring nodes would not be seen.
- **Recorded:** regular points = 70; edge points = 50; curves checked = 480; gamma range = [1e-06, 1e+60]; largest gamma at which a curve peaks = 3200000.0

<a id="check-64"></a>
### `tests/test_propositions_exogenous.py::test_proposition_3a_expected_sales_of_retailer_a_for_large_gamma`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P3.a
- **What:** Proposition 3(a): expected sales of retailer A for gamma large.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** E[R^S_{A,1}], E[R^N_{A,1}] and d = E[R^S_{A,1}] - E[R^N_{A,1}] on the grid in exact rational arithmetic. For each kind of point two rungs are recorded: the lowest from which the large-gamma criterion holds at every point, and the lowest from which the change of sign of d exists at every point.
- **Criterion:** at gamma = 1e50 and 1e60, at every point, E[R^N_{A,1}] is strictly increasing in theta, E[R^S_{A,1}] is strictly increasing, or equal at every node where A11 holds with equality in both periods, and d > 0 at theta = 0, d < 0 at theta = 1 with sign pattern "+-", zeros skipped. At every gamma of the ladder, d > 0 at theta = 0 and the pattern is "+" or "+-".
- **Recorded:** a change of sign exists at every regular point from gamma = 100.0; a change of sign exists at every edge point from gamma = 1000000000.0; regular points = 120; holds at every regular point from gamma = 100.0; edge points = 90; holds at every edge point from gamma = 1000000000.0

<a id="check-65"></a>
### `tests/test_propositions_exogenous.py::test_proposition_3b_expected_sales_of_retailer_b`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P3.b
- **What:** Proposition 3(b): expected sales of retailer B.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** E[R^S_{B,1}] and E[R^N_{B,1}] on the grid from the closed forms, in exact rational arithmetic. The closed form of E[R^S_{B,1}] from Lemma 2 does not contain theta.
- **Criterion:** at every point and gamma E[R^N_{B,1}] is strictly decreasing in theta, E[R^S_{B,1}] is equal at every node, and E[R^N_{B,1}] < E[R^S_{B,1}] at every node.
- **Recorded:** regular points = 120; edge points = 90

<a id="check-66"></a>
### `tests/test_propositions_exogenous.py::test_proposition_4_total_sales_fall_then_rise_in_theta`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P4
- **What:** Proposition 4: total expected sales E[R^N_1] of Scenario N fall and then rise in theta.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid, which contains delta and 1 - delta with delta = 1e-30 / (1 + gamma), and the values 1 - t / gamma because the lowest point of E[R^N_1] lies at a distance of order 1 / gamma from theta = 1.
- **Computed:** E[R^N_{A,1}] + E[R^N_{B,1}] and its increments along the grid in exact rational arithmetic, and the lowest rung from which the criterion holds at every point of each kind.
- **Criterion:** at gamma = 1e50 and 1e60, at every point, the increment from 0 to delta is negative, the increment from 1 - delta to 1 is positive, and the sign pattern of the increments, zeros skipped, is "-+".
- **Recorded:** regular points = 120; holds at every regular point from gamma = 1000.0; edge points = 90; holds at every edge point from gamma = 1000000000.0

<a id="check-67"></a>
### `tests/test_propositions_exogenous.py::test_proposition_5a_profit_of_retailer_a_in_scenario_s_increases_in_theta`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P5.a
- **What:** Proposition 5(a): the profit Pi^S_A of retailer A in Scenario S increases in theta.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** Pi^S_A on the grid from `spfta_t1` in exact rational arithmetic, and the lowest rung from which the criterion holds at every point of each kind.
- **Criterion:** at gamma = 1e50 and 1e60, at every point, Pi^S_A is strictly increasing in theta, or equal at every node where A11 holds with equality in both periods.
- **Recorded:** points where the profit is constant = 4; regular points = 120; holds at every regular point from gamma = 0.05; edge points = 90; holds at every edge point from gamma = 0.05

<a id="check-68"></a>
### `tests/test_propositions_exogenous.py::test_proposition_5b_profit_of_retailer_a_exceeds_the_benchmark`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P5.b
- **What:** Proposition 5(b): the profits of retailer A exceed the benchmark.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** Pi^0_A, Pi^S_A and Pi^N_A on the grid from `spfta_t1` (with gamma = 0 for the benchmark) and `npfta_t1` in exact rational arithmetic, and the lowest rung from which the criterion holds at every point of each kind.
- **Criterion:** at gamma = 1e50 and 1e60, at every point, Pi^S_A > Pi^0_A and Pi^N_A > Pi^0_A at every node.
- **Recorded:** regular points = 120; holds at every regular point from gamma = 0.05; edge points = 90; holds at every edge point from gamma = 1000.0

<a id="check-69"></a>
### `tests/test_propositions_exogenous.py::test_proposition_5c1_shares_decide_the_comparison_for_retailer_a`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P5.c1
- **What:** Proposition 5(c1): where the shares differ between the periods, they decide the comparison of Pi^S_A and Pi^N_A.
- **Points:** the sample points whose shares alpha_{A,1} and alpha_{A,2} differ, compared exactly, so that no point is left out because its shares are close. Every gamma of the 12-rung ladder and its theta grid.
- **Computed:** Pi^S_A - Pi^N_A on the grid in exact rational arithmetic, and the lowest rung from which the criterion holds at every such point of each kind.
- **Criterion:** at gamma = 1e50 and 1e60, alpha_{A,1} < alpha_{A,2} gives Pi^S_A < Pi^N_A and alpha_{A,1} > alpha_{A,2} gives Pi^S_A > Pi^N_A, at every node of every such point.
- **Recorded:** regular points = 40; holds at every regular point from gamma = 100.0; edge points = 26; holds at every edge point from gamma = 1000000.0

<a id="check-70"></a>
### `tests/test_propositions_exogenous.py::test_proposition_5c2_threshold_in_theta_above_the_cost_threshold`

- **Outcome:** passed (1.2 s)
- **Tests directly:** P5.c2
- **What:** Proposition 5(c2): with equal shares and c_B above the threshold c_B-bar of the proof, a threshold in theta for Pi^S_A - Pi^N_A.
- **Points:** the sample points with equal shares at which the expression P5_SIGN_AT_THETA_ONE of the proof is negative, which is the condition c_B > c_B-bar, and 90 further points with equal shares that satisfy it, 60 of `draw_exogenous_exact` (seed 626) and 30 of `draw_edge_exact` (seed 636). Theta grid of each rung of the ladder.
- **Computed:** Pi^S_A - Pi^N_A on the grid in exact rational arithmetic. The sign patterns at the sample points below the cost threshold are recorded and not tested, because the statement says nothing about them.
- **Criterion:** the two LaTeX strings of the proof occur verbatim in the LaTeX source, and at gamma = 1e50 and 1e60, at every such point, the difference is positive at theta = 0, negative at theta = 1, with sign pattern "+-", zeros skipped.
- **Recorded:** points below the cost threshold = 97; signs along theta below the cost threshold = ['+']; regular points = 21; holds at every regular point from gamma = 1000.0; edge points = 26; holds at every edge point from gamma = 1000000000.0; further points = 90

<a id="check-71"></a>
### `tests/test_propositions_exogenous.py::test_proposition_6a_profit_of_retailer_b_and_theta`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P6.a
- **What:** Proposition 6(a): the profits of retailer B and theta.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** Pi^S_B and Pi^N_B on the grid from `spftb_t1` and `npftb_t1` in exact rational arithmetic, and the lowest rung from which the criterion holds at every point of each kind. The closed form of Pi^S_B from Lemma 2 does not contain theta.
- **Criterion:** at gamma = 1e50 and 1e60, at every point, Pi^S_B is equal at every node and Pi^N_B is strictly increasing in theta.
- **Recorded:** regular points = 120; holds at every regular point from gamma = 0.05; edge points = 90; holds at every edge point from gamma = 0.05

<a id="check-72"></a>
### `tests/test_propositions_exogenous.py::test_proposition_6b_profit_of_retailer_b_exceeds_the_benchmark`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P6.b
- **What:** Proposition 6(b): the profits of retailer B exceed the benchmark.
- **Points:** the 210 sample points (120 regular, 90 edge), every gamma of the 12-rung ladder and its theta grid.
- **Computed:** Pi^0_B, Pi^S_B and Pi^N_B on the grid from `spftb_t1` (with gamma = 0 for the benchmark) and `npftb_t1` in exact rational arithmetic, and the lowest rung from which the criterion holds at every point of each kind.
- **Criterion:** at gamma = 1e50 and 1e60, at every point, Pi^S_B > Pi^0_B and Pi^N_B > Pi^0_B at every node.
- **Recorded:** regular points = 120; holds at every regular point from gamma = 0.05; edge points = 90; holds at every edge point from gamma = 0.05

<a id="check-73"></a>
### `tests/test_propositions_exogenous.py::test_proposition_6c1_shares_decide_the_comparison_for_retailer_b`

- **Outcome:** passed (0.0 s)
- **Tests directly:** P6.c1
- **What:** Proposition 6(c1): where the shares differ between the periods, they decide the comparison of Pi^S_B and Pi^N_B.
- **Points:** the sample points whose shares differ between the periods, compared exactly. Every gamma of the 12-rung ladder and its theta grid.
- **Computed:** Pi^S_B - Pi^N_B on the grid in exact rational arithmetic, and the lowest rung from which the criterion holds at every such point of each kind.
- **Criterion:** at gamma = 1e50 and 1e60, alpha_{B,1} > alpha_{B,2} gives Pi^S_B > Pi^N_B and alpha_{B,1} < alpha_{B,2} gives Pi^S_B < Pi^N_B, at every node of every such point.
- **Recorded:** regular points = 40; holds at every regular point from gamma = 100.0; edge points = 26; holds at every edge point from gamma = 1000000.0

<a id="check-74"></a>
### `tests/test_propositions_exogenous.py::test_proposition_6c2_threshold_in_theta_below_the_cost_threshold`

- **Outcome:** passed (1.1 s)
- **Tests directly:** P6.c2
- **What:** Proposition 6(c2): with equal shares and a cost difference below the threshold of the proof, a threshold in theta for Pi^S_B - Pi^N_B.
- **Points:** the sample points with equal shares at which the bracket in P6_SIGN_AT_THETA_ZERO of the proof is positive, which is the cost condition, and 90 further points with equal shares that satisfy it, 60 of `draw_exogenous_exact` (seed 636) and 30 of `draw_edge_exact` (seed 646). Theta grid of each rung of the ladder.
- **Computed:** Pi^S_B - Pi^N_B on the grid in exact rational arithmetic. The sign patterns at the sample points above the cost threshold are recorded and not tested, because the statement says nothing about them.
- **Criterion:** the LaTeX string of the proof occurs verbatim in the LaTeX source, and at gamma = 1e50 and 1e60, at every such point, the difference is positive at theta = 0, negative at theta = 1, with sign pattern "+-", zeros skipped.
- **Recorded:** points above the cost threshold = 126; signs along theta above the cost threshold = ['-']; regular points = 7; holds at every regular point from gamma = 10.0; edge points = 11; holds at every edge point from gamma = 1000000000.0; further points = 90

<a id="check-75"></a>
### `tests/test_propositions_exogenous.py::test_sampled_points_are_admissible_and_in_the_region_of_the_lemmas`

- **Outcome:** passed (0.0 s)
- **Supports:** L4.a, L4.b, P1.i, P1.ii, P2.a, P2.b, P2.c, P3.a, P3.b, P4, P5.a, P5.b, P5.c1, P5.c2, P6.a, P6.b, P6.c1, P6.c2
- **What:** The sample of this file lies in the region of Lemmas 1 to 3.
- **Points:** the 210 sample points, 120 of `draw_exogenous_exact` (seed 606) and 90 of `draw_edge_exact` (seed 616), two thirds of each with equal shares in both periods, at every gamma of the 12-rung ladder from 1/20 to 1e60, on the theta grid of `theta_grid`.
- **Computed:** `ExactPoint.admissible` (A1, A7, A10, A11, I1 and I2, decided exactly), and from the closed forms the code's branch flag and the critical values zeta_A and zeta_B of the benchmark and of Scenarios S and N, in exact rational arithmetic. The bounds of both samplers and the number of edge points on each edge are recorded.
- **Criterion:** every point is admissible, and at every point, gamma and theta the code places retailer A's fractile above retailer B's and mu - sigma <= zeta_B <= zeta_A <= mu + sigma.
- **Recorded:** regular points = 120; edge points = 90; points with the same shares in both periods = 144; gamma ladder = [0.05, 1.0, 10.0, 100.0, 1000.0, 10000.0, 1000000.0, 1000000000.0, 1000000000000.0, 1e+18, 1e+50, 1e+60]; theta nodes at the top rung = 32; region of the regular points = assumptions: A1, A11 with strict inequalities, I1, I2. c_B: [0.5, 3], multiples of 1/1000. c_A / c_B: [0.05, 0.98], multiples of 1/1000. mu: [5, 20], multiples of 1/1000. sigma / mu: [0.1, 0.95], multiples of 1/1000. p_B,t / c_B: [1.05, 4], multiples of 1/1000. p_A,t: (c_A / c_B) p_B,t plus 0.001 to 0.999 of the distance to p_B,t. beta: at most 0.45 / (largest price gap) and at most 0.5, so the share of B is at least 0.05. equal_shares option: the same price gap in both periods, a fraction of the smallest gap that A11 allows. theta: [0.001, 0.999]. gamma: log-uniform on [0.05, 50]. lambda_S: [0.001, 0.999]. never reached: equality in A11, p_A = p_B, theta at 0 or 1, a share of B below 0.05; region of the edge points = assumptions: A1, A11 with equality allowed, I1, I2. rule: each coordinate takes an extreme value with probability 1/2, otherwise a value of draw_exogenous_exact. c_A / c_B: 1/1000 or 999/1000. sigma / mu: 1/100 or 999/1000. p_B,t / c_B: 1001/1000 or 50. p_A,t: (c_A / c_B) p_B,t (equality in A11) or p_B,t (shares 1/2). beta x largest price gap: 1/1000000 or 499/1000, the latter gives a share of B of 1/1000. beta when both price gaps are zero: 1/1000000 or 5. theta: 0 or 1. gamma: 1/100 or 1000. lambda_S: 0 or 1. equal_shares option: a common price gap that is zero, binding in A11, or regular. p_B,2 = p_B,1 with probability 1/4; edge points with beta = 1/1000000 without a price gap = 5; edge points with beta = 5 without a price gap = 6; edge points with beta x largest price gap = 1/1000000 = 15; edge points with beta x largest price gap = 499/1000 = 16; edge points with c A / c B = 1/1000 = 28; edge points with c A / c B = 999/1000 = 17; edge points with equality in A11 in both periods = 4; edge points with equality in A11 in period 1 = 16; edge points with equality in A11 in period 2 = 12; edge points with gamma = 1/100 = 24; edge points with gamma = 1000 = 16; edge points with lambda S = 0 = 24; edge points with lambda S = 1 = 23; edge points with p A = p B in period 1 = 24; edge points with p A = p B in period 2 = 22; edge points with p B / c B = 1001/1000 in period 1 = 22; edge points with p B / c B = 1001/1000 in period 2 = 19; edge points with p B / c B = 50 in period 1 = 23; edge points with p B / c B = 50 in period 2 = 31; edge points with same shares in both periods = 64; edge points with sigma / mu = 1/100 = 27; edge points with sigma / mu = 999/1000 = 15; edge points with theta = 0 = 26; edge points with theta = 1 = 21

<a id="check-76"></a>
### `tests/test_propositions_exogenous.py::test_threshold_gamma_a4_of_proposition_5c2_depends_on_c_b`

- **Outcome:** passed (0.2 s)
- **Supports:** P5
- **What:** Under the fixed-market interpretation of Proposition 5(c2) in theory.md, the threshold gamma^A_4 in the proof can depend on c_B. It grows without bound as c_B increases to p_{B,2} when p_{B,2} < p_{B,1}, and it can stay bounded as c_B increases to the end of its range when that end is p_{B,1}.
- **Points:** equal shares (alpha_{A,1} = alpha_{A,2} = 13/25), c_A = 1, beta = 1/10, mu = 10, sigma = 4. Prices p_A = (7/2, 3), p_B = (37/10, 16/5), where the range of c_B ends at p_{B,2} = 16/5, and the mirrored prices p_A = (3, 7/2), p_B = (16/5, 37/10), where it ends at p_{B,1} = 16/5. In each case c_B = 16/5 - eps for eps in {1/10, 1/100, 1/1000}, every point admissible and above c_B-bar. Gamma on the ladder 2^0, 2^1, ..., 2^30.
- **Computed:** Pi^S_A - Pi^N_A at theta = 1 from the closed forms of Lemmas 2 and 3 in exact rational arithmetic, and the smallest rung from which on it is negative on every larger rung. Pi^S_A - Pi^N_A at theta = 0 is positive at every rung used.
- **Criterion:** with p_{B,2} < p_{B,1} that rung rises by a factor of at least 10 with each tenfold decrease of eps. With p_{B,1} < p_{B,2} it is the same at every eps and at most 2^8.
- **Recorded:** rungs p B2 < p B1 = [4096, 262144, 33554432]; rungs p B1 < p B2 = [128, 128, 128]

<a id="check-77"></a>
### `tests/test_section_5_first_period.py::test_first_period_machinery_reproduces_the_model`

- **Outcome:** passed (0.8 s)
- **Supports:** LA1, LA2, P8, P9
- **What:** Three numerical tools of `section5` against direct computations (seed 5200).
- **Points:** (1) 300 markets of `draw_market`, a share uniform on [0.02, 0.98], orders uniform on [0, 1.5 (mu + sigma)]. (2) 24 markets, gamma log-uniform on [10, 1e4], total sales R_1 uniform on [0.2, 1] (mu + sigma). (3) In each of these, 5 order pairs per scenario at prices uniform on the box, orders 0.6 to 1.1 times the claimed ones, in Scenario S gamma at least 100 and only pairs at which both retailers charge p_hi at every sales state.
- **Computed:** (1) expected sales from `first_period_nodes` and from `primitives.Uniform`. (2) prices, profits and slope in R_1 of `SecondPeriodN` and of a direct solution of the price game from the primitives, the slope by a central difference of step 1e-3 R_1. (3) `marginal_profits` and central differences of `first_period_profits` of step 1e-6 (mu + sigma).
- **Criterion:** (1) errors at most 1e-13 (mu + sigma), weights summing to 1 within 1e-13. (2) no table problem, prices within 1e-10 p_hi, profits within 1e-10 and slopes within 1e-7 relative. (3) errors at most 1e-6 p_hi (1 + gamma), 120 pairs in Scenario N, 100 or more in S.
- **Recorded:** node points = 300; price game states = 24; order pairs scenario N = 120; order pairs scenario S = 120
- **At the level of rounding error (differs between machines):** max error node quadrature = 2.67904e-16; max relative error tabulated price = 1.70669e-14; max relative error tabulated profit = 3.9577e-14; max relative error tabulated slope = 2.97788e-11; max relative error marginal profit = 8.89555e-11

<a id="check-78"></a>
### `tests/test_section_5_first_period.py::test_lemma_a1a_best_response_iteration_returns_to_the_claimed_orders`

- **Outcome:** passed (0.3 s)
- **Tests directly:** LA1.a
- **What:** Uniqueness probe for Lemma A.1(a): alternating best responses from several starts.
- **Points:** 10 markets of `draw_market` (seed 5202), one first-period price pair each, gamma = 1e3 and 1e5, 3 starting pairs per case: 60 runs. A starting order of retailer i is uniform on [L_i / gamma, 1.5 (mu + sigma)], with L_i the dominance number of `SecondPeriodS`. Below L_i / gamma the rival of a deviating retailer could sell so little that it would not charge the upper bound in period 2, and the continuation used here would not apply.
- **Computed:** alternating best replies over [0, 1.5 (mu + sigma)], found from payoff values with `argmax_on_interval`, for at most 30 sweeps or until a sweep moves less than 1e-9 (mu + sigma). The width of the excluded strip is recorded.
- **Criterion:** L_i / gamma < alpha_i (mu - sigma) for both retailers, every run ends within 1e-4 (mu + sigma) of the claimed pair in the sum of the two distances, and every rival order at which a best reply was evaluated lies above that rival's strip.
- **Recorded:** runs = 60; widest excluded strip over order interval = 0.0004
- **At the level of rounding error (differs between machines):** largest number of sweeps = 3; max relative distance to claimed orders = 2.0235e-07

<a id="check-79"></a>
### `tests/test_section_5_first_period.py::test_lemma_a1a_first_period_inventory_equilibrium_of_scenario_s`

- **Outcome:** passed (3.5 s)
- **Tests directly:** LA1.a
- **What:** Lemma A.1(a): for gamma large the first-period inventory subgame of Scenario S has the equilibrium y_A = (alpha_A + theta alpha_B) zeta_A - theta alpha_B zeta_B, y_B = alpha_B zeta_B with zeta_i = F^-1(1 - c_i / (p_{i,1} + gamma (p_hi - c_i))), and the form is exact.
- **Points:** 30 markets of `draw_market` (seed 5201), one first-period price pair each, uniform on the price box, gamma = 1, 10, 100, 1e3, 1e4, 1e5 and 1e6.
- **Computed:** at the claimed orders, with the continuation of `SecondPeriodS`, whether gamma times each retailer's smallest first-period sales exceeds its dominance number, the best deviation found by `primitives.best_response` on 4001 points of [0, 1.5 (mu + sigma)], and both marginal profits of the model, whose vanishing detects an error of order 1 / gamma.
- **Criterion:** the claim holds at a market and gamma if that dominance condition holds, the gain is at most 1e-8 p_hi (mu + sigma)(1 + gamma), each best response lies within 2e-5 (mu + sigma) of the claim and each marginal profit is at most 1e-12 (10 + gamma) c_i. Once it holds at a market it must hold at every larger gamma, it must hold at all 30 markets from gamma = 1e5 on, and it must fail at gamma = 1 at one market or more.
- **Recorded:** markets = 30; gamma ladder = [1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0]; points where the claim holds by gamma = [3, 25, 30, 30, 30, 30, 30]; holds at all points from gamma = 100.0; tolerance on relative gain from deviation = 1e-08
- **At the level of rounding error (differs between machines):** max relative gain from deviation at top two gammas = 1.66993e-16; max relative distance best response to claim at top two gammas = 1.03507e-08; max marginal profit over its rounding allowance at top two gammas = 0.0151599

<a id="check-80"></a>
### `tests/test_section_5_first_period.py::test_lemma_a2a_error_bound_is_uniform_in_theta_near_one`

- **Outcome:** passed (1.7 s)
- **Tests directly:** LA2.a
- **What:** Lemma A.2(a) with the uniformity that Online Appendix A.2 announces for its bounds: the error of the closed form is of order gamma^-2 uniformly in theta, including theta close to 1, where the error changes regime.
- **Points:** 8 markets of `draw_market` (seed 5205), one first-period price pair each, uniform on the price box, gamma = 300, 1e3 and 3e3, and theta = 1 - l / gamma for l = 0, 0.03, 0.1, 0.3, 1, 3, 10 and 30.
- **Computed:** the scaled error gamma^2 e(gamma), with e as in the previous check, and for each gamma its largest value over l. Also recorded: the growth of that maximum, its ratio to the value at theta = 1, and how closely the scaled errors at gamma = 1e3 and 3e3 agree at fixed l <= 3 where they are ten times above rounding level.
- **Criterion:** `SecondPeriodN` reports no problem, the first-order conditions hold at y* within 1e-12 (10 + gamma) c_i, and the maximum grows by at most 10% plus 3e-14 gamma^2 from one gamma to the next. An error of order 1 / gamma would multiply it by about 3 at each step.
- **Recorded:** markets = 8; gammas = [300.0, 1000.0, 3000.0]; values of gamma times one minus theta = [0.0, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0]; range of growth of largest scaled error per step of gamma to one decimal = [1.0, 1.0]
- **At the level of rounding error (differs between machines):** range of growth of largest scaled error per step of gamma = [0.970194, 1.01105]; largest ratio of maximal scaled error to its value at theta 1 = 3.9559; entries compared between gamma 1e3 and 3e3 = 30; max relative change from gamma 1e3 to 3e3 at fixed level up to 3 = 0.00550064

<a id="check-81"></a>
### `tests/test_section_5_first_period.py::test_lemma_a2a_first_period_inventory_equilibrium_of_scenario_n`

- **Outcome:** passed (3.4 s)
- **Tests directly:** LA2.a
- **What:** Lemma A.2(a): for gamma large the first-period inventory subgame of Scenario N has an equilibrium that equals the stated closed form up to a term of order gamma^-2.
- **Points:** 16 markets of `draw_market` (seed 5203), one price pair each on the price box, theta set to 1 in every fourth market, to 0 in every fourth and to 0.9 theta in the others (theta just below 1 is left to the next check), gamma = 10, 30, 100, 300, 1e3, 3e3 and 1e4.
- **Computed:** with the continuation of `SecondPeriodN`, the solution y* of the model's two first-order conditions, e(gamma) = max_i |y_i* - y_i| / (mu + sigma) for the closed form y, the order -d log e / d log gamma between neighbouring values, and at gamma = 10, 100, 1e3 and 1e4 a 1001-point search of [0, 1.5 (mu + sigma)] from y, at 1e4 also from y*.
- **Criterion:** the conditions hold at y* within 1e-12 (10 + gamma) c_i, e shrinks on every step with e > 3e-13 at both ends, the order is at least 1.75 on such steps from gamma = 100 on (an error of order 1 / gamma gives 1), with 16 or more such steps in all, and from 1e3 on every search passes at every market: table without problem, relative gain at most 1e-8, best responses within 2e-5 (mu + sigma).
- **Recorded:** markets = 16; gamma ladder = [10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0]; gammas with search of the whole order interval = [10.0, 100.0, 1000.0, 10000.0]; points without profitable deviation by gamma = [16, 16, 16, 16]; no profitable deviation at all points from gamma = 10.0; observed order on last usable step rounded to integer, theta = 1 = [2]; observed order on last usable step rounded to integer, theta < 1 = [3]
- **At the level of rounding error (differs between machines):** range of observed order on last usable step, theta = 1 = [1.99777, 2.00354]; range of observed order on last usable step, theta < 1 = [2.72707, 2.99176]; usable steps from gamma 100 = 28; lowest observed order from gamma 100 = 1.99241; largest gamma squared times relative error from gamma 100 = 0.000642805; max relative gain from deviation at gamma 1e4 = 1.25163e-16; max relative distance best response at gamma 1e4 = 1.51857e-08

<a id="check-82"></a>
### `tests/test_section_5_first_period.py::test_lemma_a2a_uniqueness_probes`

- **Outcome:** passed (6.9 s)
- **Tests directly:** LA2.a
- **What:** Uniqueness probes for Lemma A.2(a) at gamma = 1e3 (seed 5204).
- **Points:** probe 1, 6 markets of `draw_market` with theta scaled to 0.8 theta, 3 starting pairs uniform on [d, 1.5 (mu + sigma)]^2. Probe 2, 4 markets with theta = 0.5, 0.95, 1 and the theta of `draw_market`, 121 values of y_B on [d, 1.5 (mu + sigma)]. One price pair per market. d = min(alpha_A, alpha_B, [1/2 - beta (p_hi - p_lo)] / 2) (mu - sigma). Below d total sales can approach zero, where the second-period price game leaves its large-gamma regime.
- **Computed:** best replies A and B over [0, 1.5 (mu + sigma)] from payoff values, continuation `SecondPeriodN`. Probe 1 alternates them, at most 60 sweeps, until a sweep moves less than 1e-7 (mu + sigma), and records the predicted contraction per sweep, which tends to 1 as theta tends to 1. Probe 2 evaluates the residual B(A(y_B)) - y_B.
- **Criterion:** no table problem and every rival order evaluated at least d. Probe 1: fewer than 60 sweeps, end point within 1e-4 (mu + sigma) of the closed form. Probe 2: residual positive at d and negative at 1.5 (mu + sigma), with a change of sign (product of signs at most 0) between exactly one pair of neighbours, which encloses the claimed y_B.
- **Recorded:** gamma = 1000.0; iteration runs = 18; largest predicted contraction factor per sweep = 0.63; sign changes of the fixed point residual per scanned market = [1, 1, 1, 1]
- **At the level of rounding error (differs between machines):** largest number of sweeps = 21; max relative distance to claimed orders after iteration = 3.32761e-07

<a id="check-83"></a>
### `tests/test_section_5_propositions.py::test_proposition_8a_orders_of_scenario_s_fall_in_own_price_and_rise_in_rival_price`

- **Outcome:** passed (0.5 s)
- **Tests directly:** P8.a
- **What:** Proposition 8(a): in Scenario S, for gamma large, y_{i,1} decreases in p_{i,1} and increases in p_{j,1}, for both retailers.
- **Points:** 20 markets of `draw_market` (seed 5300), a 9 by 9 grid of first-period prices that covers the price box, borders included, gamma = 1, 10, 100, 1e3, 1e4, 1e5 and 1e6.
- **Computed:** the orders of Lemma A.1(a) at all 81 pairs with the flags of `_orders_s` (both marginal profits within 1e-12 (10 + gamma) c_i and the continuation of `SecondPeriodS` pinned down), the four difference quotients between neighbouring grid points, and at gamma = 1e5 and 1e6 a 1001-point search of each order interval at one random grid pair.
- **Criterion:** the claim holds at a market and gamma if all 81 flags are true, every quotient has the claimed sign, and at the two largest gammas the search finds no relative gain above 1e-8 and no best response farther than 2e-5 (mu + sigma). It must hold at all markets from gamma = 1e5 on, and in each market the largest relative distance of a quotient from -beta (mu + sigma) or +beta (mu + sigma), its value when no retailer stocks out, must shrink at least fivefold from gamma = 1e5 to 1e6.
- **Recorded:** markets = 20; price pairs per market = 81; gamma ladder = [1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0]; markets where the claim holds by gamma = [2, 11, 16, 20, 20, 20, 20]; holds in all markets from gamma = 1000.0; largest relative distance of a slope from its limit at gamma 1e6 = 5.7e-07; smallest factor by which that distance shrinks from gamma 1e5 to 1e6 = 10.0

<a id="check-84"></a>
### `tests/test_section_5_propositions.py::test_proposition_8b2_reversal_when_gamma_times_one_minus_theta_is_bounded`

- **Outcome:** passed (2.8 s)
- **Tests directly:** P8.b2
- **What:** Under condition (A.22) of the Online Appendix, Proposition 8(b2) gives an open set of first-period price pairs on which y_{A,1} decreases and y_{B,1} increases in p_{B,1}, provided gamma is large and 0 <= gamma (1 - theta) <= l^D for some l^D > 0.
- **Points:** 8 markets of `draw_market` that satisfy (A.22) (seed 5302), a 3 by 3 patch of prices inside the set (A.23) of the proof, theta = 1 and 1 - l / gamma with one positive l, gamma = 100, 1e3, 1e4 and 1e5, and theta = 0.5 at gamma = 1e4 and 1e5.
- **Computed:** d y_A / d p_B and d y_B / d p_B of the solutions of the first-order conditions (`_orders_n`) by central differences of step 1e-4 (p_hi - p_lo), and at gamma = 1e4 and 1e5 a search of each order interval at the centre pair. The gap to the expansion (A.26) is recorded.
- **Criterion:** the claim holds at a market and gamma if at both values of theta all equilibria are solved, the table reports no problem, the slopes are negative for y_A and positive for y_B at all 9 pairs, and at the two largest gammas the search finds no relative gain above 1e-8 and no best response farther than 2e-5 (mu + sigma). It must hold at all markets from gamma = 1e4 on. At theta = 0.5 and gamma = 1e4 and 1e5 both signs are reversed at all 9 pairs.
- **Recorded:** markets = 8; gamma ladder = [100.0, 1000.0, 10000.0, 100000.0]; markets where the claim holds by gamma = [8, 8, 8, 8]; holds in all markets from gamma = 100.0; smallest ratio of the two sides of A22 = 1.002; largest tested value of gamma times one minus theta = 0.0096; smallest slope over beta mu plus sigma at gamma 1e5 = 0.00036
- **At the level of rounding error (differs between machines):** max difference to expansion A26 over beta mu plus sigma at gamma 1e5 = 6.04806e-06

<a id="check-85"></a>
### `tests/test_section_5_propositions.py::test_proposition_8b_orders_of_scenario_n_at_fixed_theta`

- **Outcome:** passed (3.4 s)
- **Tests directly:** P8.b1, P8.b2
- **What:** Proposition 8(b1) and the last sentence of 8(b2), Scenario N, gamma large. (b1) y_{A,1} decreases and y_{B,1} increases in p_{A,1}. (b2, fixed theta < 1) y_{A,1} increases and y_{B,1} decreases in p_{B,1}.
- **Points:** 6 markets of `draw_market` (seed 5301), a 7 by 7 grid of first-period prices that covers the price box, theta = 0, 0.5, 0.9 and 1 for (b1), whose thresholds Online Appendix A.2 announces as uniform in theta, and 0, 0.5 and 0.9 for (b2), gamma = 10, 100, 1e3, 1e4, 1e5.
- **Computed:** the solutions of the model's first-order conditions at all 49 pairs (`_orders_n`, `SecondPeriodN`), the difference quotients between neighbouring grid points, and at gamma = 1e4 and 1e5 a 1001-point search of each order interval at one random grid pair.
- **Criterion:** a part holds at a market, theta and gamma if the conditions are solved within 1e-12 (10 + gamma) c_i at all 49 pairs, the table reports no problem, every quotient of the part has the claimed sign, and at the two largest gammas the search finds no relative gain above 1e-8 and no best response farther than 2e-5 (mu + sigma). Each part must hold in every case from gamma = 1e4 on.
- **Recorded:** markets = 6; price pairs per market = 49; gamma ladder = [10.0, 100.0, 1000.0, 10000.0, 100000.0]; (b1): values of theta = [0.0, 0.5, 0.9, 1.0]; (b1): cases where the claim holds by gamma = [24, 24, 24, 24, 24]; (b1): holds in all cases from gamma = 10.0; (b1): smallest slope over beta (mu + sigma) at gamma 1e5 = 0.627; (b2) fixed theta: values of theta = [0.0, 0.5, 0.9]; (b2) fixed theta: cases where the claim holds by gamma = [18, 18, 18, 18, 18]; (b2) fixed theta: holds in all cases from gamma = 10.0; (b2) fixed theta: smallest slope over beta (mu + sigma) at gamma 1e5 = 1.0

<a id="check-86"></a>
### `tests/test_section_5_propositions.py::test_proposition_9a_price_path_of_scenario_s`

- **Outcome:** passed (9.2 s)
- **Tests directly:** P9.a
- **What:** Proposition 9(a): in Scenario S, for gamma large, the equilibrium prices are the lower bound in period 1 and the upper bound in period 2, for both retailers.
- **Points:** 20 markets of `draw_market` (seed 5303), gamma = 1, 10, 100, 1e3, 1e4, 1e5 and 1e6.
- **Computed:** the reduced payoffs (two-period profits at the orders of Lemma A.1(a), continuation `SecondPeriodS`) on a grid of 101 own by 41 rival prices, a search of each price interval, best-response iteration from the four corners, the second-period price game from the primitives on a 41 by 41 grid at the sales for seed demand mu - sigma, mu and mu + sigma, and the advantage of p_lo, the smallest loss per unit of price change to another grid price.
- **Criterion:** the claim holds at a market and gamma if `_orders_s` confirms every grid pair, p_lo is each retailer's best reply to every rival grid price, the search finds no relative gain above 1e-8, the search and iterations end within 1e-12 p_hi of (p_lo, p_lo), each grid game of period 2 has (p_hi, p_hi) as its only pure equilibrium, and p_lo = p_{i,1} < p_{i,2} = p_hi. Once it holds it must keep holding, it must hold at all markets from 1e5 on and fail at gamma = 1 somewhere, and the advantage must be positive at 1e5 and grow by a factor in [9.9, 10.1] from 1e5 to 1e6.
- **Recorded:** markets = 20; gamma ladder = [1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0]; markets where the claim holds by gamma = [1, 9, 15, 20, 20, 20, 20]; holds in all markets from gamma = 1000.0; smallest advantage of lower bound over gamma p hi beta mu at gamma 1e5 = 0.414; max deviation from tenfold growth of the advantage = 0.0002

<a id="check-87"></a>
### `tests/test_section_5_propositions.py::test_proposition_9b_price_path_of_scenario_n`

- **Outcome:** passed (14.9 s)
- **Tests directly:** P9.b
- **What:** Proposition 9(b): in Scenario N, for a fixed theta < 1 and gamma large, p_lo < p_{i,2} < p_{i,1} < p_hi for both retailers.
- **Points:** 5 markets of `draw_market` (seed 5304) with theta scaled to 0.9 theta, gamma = 100, 1e3 and 1e4. Above 1e4 first-period prices are located less accurately.
- **Computed:** the first-period price equilibrium of the reduced payoffs (`_orders_n`, `SecondPeriodN`) by best-response iteration over the price interval from (p_lo, p_hi) and (p_hi, p_lo), and the second-period prices at the sales of 201 seed demands on the support.
- **Criterion:** the claim holds at a market and gamma if the two runs agree within 1e-4 p_hi, the tables report no problem, the first-order conditions are solved at 41 own prices of each retailer and at the equilibrium, searches of the order intervals there and of the second-period price intervals at the mean seed demand find no relative gain above 1e-8 and no best response farther than 2e-5 (mu + sigma) or 2e-5 p_hi, and p_lo < min p_{i,2} and max p_{i,2} < p_{i,1} < p_hi. It must hold at all markets from gamma = 1e3 on, and the gap p_{i,1} - max p_{i,2} must change from 1e3 to 1e4 by at most a quarter of its change from 100 to 1e3.
- **Recorded:** markets = 5; gamma ladder = [100.0, 1000.0, 10000.0]; markets where the claim holds by gamma = [5, 5, 5]; holds in all markets from gamma = 100.0
- **At the level of rounding error (differs between machines):** smallest gap between period prices over p hi at gamma 1e4 = 0.0298499; largest ratio of late to early change of the gap = 0.12365; max relative difference to limit gap of the proof at gamma 1e4 = 0.00464635; range of gamma times distance to limit prices of the proof over p hi at gamma 1e4 = [0.0588349, 4.48853]; max relative distance between the two runs = 8.11665e-06

<a id="check-88"></a>
### `tests/test_section_5_second_period.py::test_helpers_agree_with_the_primitives`

- **Outcome:** passed (0.2 s)
- **Supports:** LA1, LA2, P8, P9
- **What:** `section5.expected_sales` and `section5.benchmark_orders` against the primitives.
- **Points:** 2,000 markets of `draw_market` (seed 5100), each with C2C demands that are zero or uniform on [0, 3 (mu + sigma)], orders uniform on [0, 2 (mu + sigma)] above them, a share uniform on [0.02, 0.98] and a price pair uniform on the price box.
- **Computed:** expected sales from `section5.expected_sales` and from `primitives.Uniform`, and order quantities from `benchmark_orders` and from `section4.claimed_benchmark`.
- **Criterion:** every difference is at most 1e-13 (mu + sigma), and retailer B has the higher critical fractile at one price pair or more.
- **Recorded:** points = 2000; price pairs where retailer B has the higher fractile = 130
- **At the level of rounding error (differs between machines):** max relative error expected sales = 0.0; max relative error benchmark orders = 0.0

<a id="check-89"></a>
### `tests/test_section_5_second_period.py::test_lemma_a1b_upper_bound_is_the_unique_second_period_price_equilibrium`

- **Outcome:** passed (2.9 s)
- **Tests directly:** LA1.b
- **What:** Lemma A.1(b): in Scenario S, given positive first-period sales of both retailers and gamma large, the second-period price game has the unique pure equilibrium (p_hi, p_hi).
- **Points:** 30 markets of `draw_market` (seed 5102), one sales state each with R_{A,1} and R_{B,1} uniform on [0.02, 1] (mu + sigma) / 2, gamma = 1, 10, 100, 1e3, 1e4, 1e5 and 1e6.
- **Computed:** second-period profits from the primitives at the inventory equilibrium, on a 61 by 61 price grid and on each whole price interval, best-response iteration from the four corners of the box and from one random pair (at most 20 sweeps), and the advantage of p_hi: the smallest payoff loss from another grid price per unit of price difference.
- **Criterion:** the claim holds at a market and gamma if (p_hi, p_hi) is the only pure equilibrium of the grid game, the search finds no relative gain above 1e-8 and no best response farther than 1e-12 p_hi, and every iteration ends within 1e-12 p_hi. Once it holds it must keep holding, it must hold at all markets from 1e5 on and fail at gamma = 1 at one market or more, and the advantage must be positive at 1e5 and grow from 1e5 to 1e6 by R_{i,1} per unit of gamma within a relative error of 1e-6.
- **Recorded:** markets = 30; gamma ladder = [1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0]; points where the claim holds by gamma = [17, 30, 30, 30, 30, 30, 30]; holds at all points from gamma = 10.0; smallest advantage of upper bound over gamma times sales at gamma 1e5 = 0.9998
- **At the level of rounding error (differs between machines):** max error of growth rate of the advantage = 1.08469e-13

<a id="check-90"></a>
### `tests/test_section_5_second_period.py::test_lemma_a2b_second_period_prices_approach_the_limit_prices_at_rate_one_over_gamma`

- **Outcome:** passed (3.9 s)
- **Tests directly:** LA2.b
- **What:** Lemma A.2(b): in Scenario N, given R_1 > 0 and gamma large, the second-period price equilibrium is unique and equals 1 / (2 beta) + (2 c_i + c_j) / 3 plus O(1 / gamma).
- **Points:** 2,000 markets of `draw_market` (seed 5106) for the notation of Online Appendix A.2, and 12 markets (seed 5103), one state each with R_1 uniform on [0.1, 1] (mu + sigma), at gamma = 10, 100, 1e3, 1e4, 1e5 and 1e6.
- **Computed:** the solution of the first-order conditions of the price game, a search of each price interval and best-response iteration from the four corners (at most 40 sweeps), with profits from the primitives, and e(gamma), the larger distance to the limit prices.
- **Criterion:** at the 2,000 markets nu_A > nu_B > 0, c_A / nu_A < c_B / nu_B, p_lo < limit_A < limit_B < p_hi and c_A / limit_A < c_B / limit_B. At the 12 markets e shrinks along the ladder, log10(e(gamma) / e(10 gamma)) lies in [0.99, 1.01] over the last two decades, gamma e at 1e5 and 1e6 agrees within 0.5% and never exceeds twice its value at 1e6, and from 1e5 on every market passes: relative gain at most 1e-8, best responses and iterations within 2e-5 p_hi.
- **Recorded:** markets = 12; gamma ladder = [10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0]; points where equilibrium is confirmed and unique by gamma = [12, 12, 12, 12, 12, 12]; unique equilibrium at all points from gamma = 10.0; range of observed order over last two decades = [1.0, 1.0]; max scaled distance on ladder over its value at gamma 1e6 = 1.0; range of gamma times distance over upper price bound at gamma 1e6 = [0.013, 0.341]; markets where both prices approach the limit from above = 12
- **At the level of rounding error (differs between machines):** max deviation of observed order from 1 over last two decades = 0.000213645; max relative change of scaled distance between gamma 1e5 and 1e6 = 4.92082e-05

<a id="check-91"></a>
### `tests/test_section_5_second_period.py::test_second_period_inventory_equilibrium_at_any_price_pair[N]`

- **Outcome:** passed (0.6 s)
- **Tests directly:** LA2.b
- **What:** Lemmas A.1(b) and A.2(b), last sentence of each: at given second-period prices and first-period sales the orders y^0_{i,2} + Z_{i,2} are the equilibrium of the inventory subgame, and each profit is pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2}.
- **Points:** 100 markets of `draw_market` (seed 5101), gamma log-uniform on [0.1, 1000], one sales state each, uniform on the triangle R_A, R_B >= 0, R_A + R_B <= mu + sigma. At every second point the prices are uniform on the price box. At the others they are drawn, where the box allows, from the pairs with c_A / p_A > c_B / p_B.
- **Computed:** from the primitives, `primitives.nash_gap` on [0, U] with U = max(Z_A, Z_B) + 1.5 (mu + sigma), the profits at the claimed orders, and at the first 20 points best-response iteration (801-point grid, at most 60 sweeps) from two random starting pairs.
- **Criterion:** no deviation gains more than 1e-8 p_hi U, each best response lies within 2e-5 U of the claim, the profit identity holds within 1e-11 p_hi U, every iteration ends within 1e-4 U of the claim, and retailer B has the higher fractile at 10 points or more.
- **Recorded:** points = 100; points where retailer B has the higher fractile = 25; tolerance on relative gain from deviation = 1e-08
- **At the level of rounding error (differs between machines):** max relative gain from deviation = 3.42203e-16; max relative distance best response to claim = 8.81193e-09; max relative error of profit identity = 2.53729e-16; max relative distance after best response iteration = 1.0485e-09

<a id="check-92"></a>
### `tests/test_section_5_second_period.py::test_second_period_inventory_equilibrium_at_any_price_pair[S]`

- **Outcome:** passed (0.5 s)
- **Tests directly:** LA1.b
- **What:** Lemmas A.1(b) and A.2(b), last sentence of each: at given second-period prices and first-period sales the orders y^0_{i,2} + Z_{i,2} are the equilibrium of the inventory subgame, and each profit is pi^0_{i,2} + (p_{i,2} - c_i) Z_{i,2}.
- **Points:** 100 markets of `draw_market` (seed 5101), gamma log-uniform on [0.1, 1000], one sales state each, uniform on the triangle R_A, R_B >= 0, R_A + R_B <= mu + sigma. At every second point the prices are uniform on the price box. At the others they are drawn, where the box allows, from the pairs with c_A / p_A > c_B / p_B.
- **Computed:** from the primitives, `primitives.nash_gap` on [0, U] with U = max(Z_A, Z_B) + 1.5 (mu + sigma), the profits at the claimed orders, and at the first 20 points best-response iteration (801-point grid, at most 60 sweeps) from two random starting pairs.
- **Criterion:** no deviation gains more than 1e-8 p_hi U, each best response lies within 2e-5 U of the claim, the profit identity holds within 1e-11 p_hi U, every iteration ends within 1e-4 U of the claim, and retailer B has the higher fractile at 10 points or more.
- **Recorded:** points = 100; points where retailer B has the higher fractile = 25; tolerance on relative gain from deviation = 1e-08
- **At the level of rounding error (differs between machines):** max relative gain from deviation = 3.0018e-16; max relative distance best response to claim = 9.84379e-09; max relative error of profit identity = 3.0018e-16; max relative distance after best response iteration = 5.19783e-09

<a id="check-93"></a>
### `tests/test_section_5_transcription.py::test_claims_of_section_5_are_transcribed_from_the_paper`

- **Outcome:** passed (0.0 s)
- **Supports:** LA1, LA2, P8, P9
- **What:** `section5.claimed_*` against a second transcription of Lemmas A.1 and A.2 and Propositions 8 and 9.
- **Points:** 500 markets of `draw_market` (seed 5400), each with first-period prices uniform on the price box, gamma log-uniform on [1, 1e6], and two sorted prices uniform on the box for the price-path predicates.
- **Computed:** the 17 LaTeX strings of `QUOTES` against the LaTeX source in `paper/`, and both transcriptions of the limit prices, nu_i, the claimed first-period orders of Scenarios S and N, the ratio of the two sides of (A.22), the bound in (A.23) and the first-period limit prices of the proof of Proposition 9.
- **Criterion:** every string occurs verbatim, up to whitespace, every difference is at most 1e-12 max(1, |value|), the claimed Scenario S prices are (p_lo, p_lo) and (p_hi, p_hi), the predicates of Proposition 9 accept and reject the test pairs as its inequalities require, and `CLAIMED_SLOPE_SIGNS` equals the table written from Proposition 8.
- **Recorded:** latex strings found in the paper = 17; random points = 500
- **At the level of rounding error (differs between machines):** largest relative difference = 1.76606e-15
