# Numerical checks

Written by `numerics/run.py` on 2026-11-22. Command: `python numerics/run.py -k FB1 --report ...`. Python 3.12.7 on Darwin, with numpy 1.26.4, scipy 1.13.1, sympy 1.14.0, mpmath 1.3.0, pandas 2.2.2, matplotlib 3.9.2, PyYAML 6.0.1, pytest 7.4.4.

**9 of 9 checks passed.** pytest exit status: 0.

A *direct* check tests a part of the result itself. A *supporting* check confirms a tool that direct checks rely on, for example that a closed form equals the model at random points. Every check computes at finitely many points. For a result that holds for all parameters it is a search for counterexamples. For a result that holds for a parameter large enough it probes large values of that parameter.

The selection counts only FB1. Other IDs that the selected checks name appear only in the description of each check below.

## Numerical statements of the paper

| ID | Direct checks passed | Supporting checks passed |
|---|---|---|
| [FB1](#fb1) | 5/5 | 4/4 |

## Checks by ID

### FB1

- direct: [test_figure_b1_matches_the_authors_matlab_values](#check-1): passed
- direct: [test_figure_b1_matches_the_published_figure[a]](#check-2): passed
- direct: [test_figure_b1_matches_the_published_figure[b]](#check-3): passed
- direct: [test_figure_b1_matches_the_published_figure[c]](#check-4): passed
- direct: [test_figure_b1_matches_the_published_figure[d]](#check-5): passed
- supporting: [test_numerical_statements_are_quoted_from_the_paper](#check-6): passed
- supporting: [test_published_data_match_a_fresh_extraction_from_the_eps_files](#check-7): passed
- supporting: [test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]](#check-8): passed
- supporting: [test_closed_form_profits_of_the_mixed_scenario_equal_the_model](#check-9): passed

## Checks

<a id="check-1"></a>
### `tests/test_figures.py::test_figure_b1_matches_the_authors_matlab_values`

- **Outcome:** passed (0.0 s)
- **Tests directly:** FB1
- **What:** Figure B.1 against the authors' MATLAB output.
- **Points:** the 9 plotted series of Figure B.1 at the 11 values of theta 0, 0.1, ..., 1 and the parameters of its caption: 99 values.
- **Computed:** `c2c.figures.figureB1_data`, from `find_general_exo` of `c2c.closed_form`, and the table `numerics/matlab/Figure2_MATLAB/Figure2_reference.csv`. The number of values that agree digit for digit at 15 significant digits is recorded.
- **Criterion:** the two tables have the same columns, and the largest absolute difference is below 1e-10.
- **Recorded:** values compared = 99
- **At the level of rounding error (differs between machines):** values equal digit for digit = 99; max abs difference = 4.9738e-14

<a id="check-2"></a>
### `tests/test_figures.py::test_figure_b1_matches_the_published_figure[a]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** FB1
- **What:** Figure B.1, one panel, against the published figure.
- **Points:** one panel of Figure B.1 (a, b, c or d) with its 2 plotted series (3 in panel b), 11 values of theta each.
- **Computed:** the recomputed values of `figureB1_data`, and the values that `published_data.csv` reads back from the panel's EPS file.
- **Criterion:** each series has 11 plotted points whose theta agree with the recomputed grid within 1e-9, and the largest absolute difference is at most the panel's extraction error bound in `published_data_calibration.json` plus 1e-9.
- **Recorded:** extraction error bound = 1.29e-06; max abs difference = 1.00985e-06

<a id="check-3"></a>
### `tests/test_figures.py::test_figure_b1_matches_the_published_figure[b]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** FB1
- **What:** Figure B.1, one panel, against the published figure.
- **Points:** one panel of Figure B.1 (a, b, c or d) with its 2 plotted series (3 in panel b), 11 values of theta each.
- **Computed:** the recomputed values of `figureB1_data`, and the values that `published_data.csv` reads back from the panel's EPS file.
- **Criterion:** each series has 11 plotted points whose theta agree with the recomputed grid within 1e-9, and the largest absolute difference is at most the panel's extraction error bound in `published_data_calibration.json` plus 1e-9.
- **Recorded:** extraction error bound = 1.35e-06; max abs difference = 1.03725e-06

<a id="check-4"></a>
### `tests/test_figures.py::test_figure_b1_matches_the_published_figure[c]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** FB1
- **What:** Figure B.1, one panel, against the published figure.
- **Points:** one panel of Figure B.1 (a, b, c or d) with its 2 plotted series (3 in panel b), 11 values of theta each.
- **Computed:** the recomputed values of `figureB1_data`, and the values that `published_data.csv` reads back from the panel's EPS file.
- **Criterion:** each series has 11 plotted points whose theta agree with the recomputed grid within 1e-9, and the largest absolute difference is at most the panel's extraction error bound in `published_data_calibration.json` plus 1e-9.
- **Recorded:** extraction error bound = 3.68e-06; max abs difference = 3.52403e-06

<a id="check-5"></a>
### `tests/test_figures.py::test_figure_b1_matches_the_published_figure[d]`

- **Outcome:** passed (0.0 s)
- **Tests directly:** FB1
- **What:** Figure B.1, one panel, against the published figure.
- **Points:** one panel of Figure B.1 (a, b, c or d) with its 2 plotted series (3 in panel b), 11 values of theta each.
- **Computed:** the recomputed values of `figureB1_data`, and the values that `published_data.csv` reads back from the panel's EPS file.
- **Criterion:** each series has 11 plotted points whose theta agree with the recomputed grid within 1e-9, and the largest absolute difference is at most the panel's extraction error bound in `published_data_calibration.json` plus 1e-9.
- **Recorded:** extraction error bound = 9.99e-07; max abs difference = 9.15257e-07

<a id="check-6"></a>
### `tests/test_figures.py::test_numerical_statements_are_quoted_from_the_paper`

- **Outcome:** passed (0.0 s)
- **Supports:** F1, FB1, N1, N2, N3, N4, N5, N6
- **Points:** the nine entries of `numerics/numerical_statements.yaml`, including N7, which the repository lists and does not check.
- **Computed:** each quote, against the LaTeX source of the paper with every \ref printed as the number that `numerics/paper_labels.json` gives.
- **Criterion:** every quote occurs verbatim, up to whitespace, so that the checks of this file test the paper's own sentences, and exactly N7 carries a field `excluded`.
- **Recorded:** statements quoted = 9

<a id="check-7"></a>
### `tests/test_figures.py::test_published_data_match_a_fresh_extraction_from_the_eps_files`

- **Outcome:** passed (0.5 s)
- **Supports:** F1, FB1
- **Points:** the 8 EPS panels of Figure 1 and Figure B.1 in `paper/`.
- **Computed:** `numerics/figures/extract_published_data.py` reads every plotted vertex back from the vector graphics into a temporary folder.
- **Criterion:** the fresh extraction equals the committed `published_data.csv` and `published_data_calibration.json` byte for byte, so that every comparison with a published figure in this file uses data that the EPS files reproduce.
- **Recorded:** panels = 8; plotted points = 187

<a id="check-8"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_order_quantities_are_the_claimed_equilibrium_quantities[G]`

- **Outcome:** passed (0.0 s)
- **Supports:** LB1.first, FB1, N5
- **What:** Link (a): the order quantities of `c2c.closed_form` against those of `section4.claimed_first_period`. `test_port_matches_paper.py` ties the first to the LaTeX source of the paper and `test_equilibria_from_primitives.py` checks the second against the model. Case 0 is Lemma 1, cases S and N are Lemmas 2 and 3, case G is Lemma B.1.
- **Points:** seed 1111. Cases 0, S and N: 500 points, 200 of `draw_exogenous`, 200 of `draw_without_a11` and 100 of `draw_edge_exact`. Case G: the 300 regular and edge points only, because the code implements the mixed scenario only for the ordering of Lemma B.1.
- **Computed:** y_{A,1} and y_{B,1} from `first_period_s` (with gamma = 0 in case 0), `first_period_n` or `find_general_exo`, and from `claimed_first_period` with the uniform quantile function.
- **Criterion:** every difference is at most 1e-12 mu, and in cases 0, S and N retailer B has the higher critical fractile at one point or more.
- **Recorded:** points regular = 200; points edge = 100; points where retailer B has the higher fractile = 0
- **At the level of rounding error (differs between machines):** max relative difference = 7.44804e-16

<a id="check-9"></a>
### `tests/test_profits_and_price_game.py::test_closed_form_profits_of_the_mixed_scenario_equal_the_model`

- **Outcome:** passed (0.1 s)
- **Supports:** FB1, N5
- **What:** Link (b) for the mixed scenario of Online Appendix B (Lemma B.1).
- **Points:** 300 points (seed 506), 200 of `draw_exogenous` and 100 of `draw_edge_exact`, all of which satisfy A11, because the code implements only the ordering of Lemma B.1.
- **Computed:** total two-period profits of both retailers at the orders of `find_general_exo`, from that function and from the payoffs of `section4.Game` (scenario G) integrated exactly under the uniform distribution. The code returns no expected sales for this scenario, so sales are not compared.
- **Criterion:** every difference is at most 1e-9 mu (1 + gamma) max(p_{B,1}, p_{B,2}).
- **Recorded:** points regular = 200; points edge = 100; points where retailer B has the higher fractile = 0
- **At the level of rounding error (differs between machines):** max relative error profit = 8.04278e-15
