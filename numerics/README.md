# Numerics

Code that computes the model of the paper, and checks that test the paper's statements against it.

```
numerics/
├── run.py                       runs the checks and summarises them by result
├── numerical_statements.yaml    the paper's statements about Figures 1 and B.1 and its other numerical findings (F1, FB1, N1 to N7, of which N7 is listed and not checked)
├── paper_labels.json            printed LaTeX reference numbers from the manuscript and appendix
├── c2c/                         Python package
│   ├── primitives.py            the model of Section 3 from its definition, with no result of the paper
│   ├── section4.py              Section 4 and Online Appendix B: the order quantities that Lemmas 1 to 3 and B.1 state,
│   │                            payoffs built from primitives.py, and samplers of the parameter region
│   ├── section5.py              Section 5: what Lemmas A.1 and A.2 and Propositions 8 and 9 state, and solvers of the
│   │                            price and inventory game built from primitives.py
│   ├── predicates.py            exact and tolerance-based shape tests (increasing, single crossing, ...)
│   ├── paper.py                 reads the LaTeX source, for checks that quote the paper
│   ├── closed_form.py           line-by-line port of the authors' MATLAB closed forms
│   ├── pricing.py               line-by-line port of the authors' MATLAB price game (Figure 1)
│   └── figures.py               the numbers behind Figure 1 and Figure B.1, from the port
├── tests/                       the checks (pytest)
├── figures/
│   ├── make_figures.py          recomputes and redraws both figures into reproduced/
│   ├── reproduced/              the recomputed figures and their data
│   ├── extract_published_data.py  reads the plotted points back from the EPS panels in paper/ at the repository root
│   ├── published_data.csv       those points
│   └── published_data_calibration.json   how each panel was calibrated, with error bounds
└── matlab/                      the MATLAB code that the authors provided for Figure 1 and Figure B.1
```

## The checks

Every check names the results it bears on with a marker: `claims` for a part it tests directly, `supports` for a result whose direct checks rely on what it confirms. Each ID is also a pytest keyword:

```bash
python -m pytest numerics -k P5            # every check that names Proposition 5
python numerics/run.py -k "P8 or P9"       # the same through run.py, with a summary by result
python numerics/run.py --report FILE       # all checks, and a Markdown report of what each computed
```

| File | What it checks |
|---|---|
| `test_equilibria_from_primitives.py` | Lemmas 1 to 3 and B.1: the stated order quantities are an equilibrium of the model, under four demand distributions, and a scan of best responses finds no other |
| `test_propositions_exogenous.py` | Lemma 4 and Propositions 1 to 6, part by part, in exact rational arithmetic on random and boundary points |
| `test_profits_and_price_game.py` | the closed forms of sales and profits against the model, and the payoffs of the price game behind Figure 1 |
| `test_proposition_7_shapes.py` | Proposition 7: the shapes of the second-period orders as functions of prices |
| `test_section_5_second_period.py` | Lemmas A.1(b) and A.2(b) |
| `test_section_5_first_period.py` | Lemmas A.1(a) and A.2(a) |
| `test_section_5_propositions.py` | Propositions 8 and 9 |
| `test_section_5_transcription.py` | the claimed objects of Section 5 in `c2c/section5.py` are those of the paper |
| `test_port_matches_paper.py` | the formulas of the MATLAB port are the paper's formulas |
| `test_figures.py` | Figures 1 and B.1 against the published panels and the authors' MATLAB values, and statements N1 to N5 |
| `test_other_distributions.py` | statement N6: the comparisons of Section 4 under other demand distributions |

Every check computes at finitely many points. For a statement that holds for all parameters it is a search for counterexamples. For a statement that holds for gamma large enough it probes large values of gamma. A proof of a statement is checked by reading it, as [`AGENTS.md`](../AGENTS.md) describes.

## Two implementations

`c2c/primitives.py` computes demand, sales and expected profits from the definitions of Section 3 and uses no result of the paper. `c2c/closed_form.py`, `pricing.py` and `figures.py` port the authors' MATLAB code and use the paper's closed forms. The checks compare the closed forms with the model, so an error in either one shows up as a failed check.

The MATLAB code needs MATLAB. Everything else runs with the packages in [`requirements.txt`](../requirements.txt).
