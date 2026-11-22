# Overall judgement

- Theoretical results — **verified**
- Numerical results — **verified_with_qualifications**
- Paper consistency — theory.md: **consistent**, numerics/: **consistent**

The theoretical results are verified. The numerical results are verified with qualifications because both figures and N1–N5 reproduce and N6 has only partial evidence under nonuniform demand. All 16 results are sound, and all 16 printed statements hold under the assumptions in force. No technical manuscript correction was identified. The theory transcription is consistent and the numerical implementation is consistent. All 93 distinct checks passed. P2(c)'s positive stationary point follows for every fixed theta<1. LB1 inherits its price condition from Section 4. The P5(c2) and P6(c2) bounds cover all theta within each qualifying market. N6 leaves P2(c), the two cost cutoffs and endogenous pricing under other laws untested. N7 is excluded because the mixed endogenous-price solver and the authors' output are unavailable. This single-model audit covers technical claims only.

## Run

GPT-6, Codex, 2026-11-22. Full audit of the current working tree. Repository version: none (no Git metadata).

Earlier discussion in this chat and the session introduction disclosed earlier audit outcomes and history, including P2(c), N6 and N7. No previous verification directory or external research material was opened for this run. See each proof record for reviewer context.

The parent ran 24 filtered test processes serially before assigning proof reviews. All tests were rerun unfiltered after Parts 1–3. The run compares document-local AUX maps, PDF page text, EPS ordinates, MATLAB scalar operations, exact rational polynomial signs and analytical proofs. The protected-input hash check covered 74 files.

## Consistency with the paper

| Item | Comparison | Outcome |
|---|---|---|
| theory.md Model | Manuscript.tex, Section 3 including the closing distribution paragraph | consistent |
| theory.md Notation | Manuscript.tex Sections 3–5 and OnlineAppendix.tex A.1, A.2, B | consistent |
| theory.md Assumptions A1–A15 | Manuscript.tex Sections 3–5 and OnlineAppendix.tex A.1, A.2, B | consistent |
| theory.md Implicit conditions I1–I3 | Interior fractiles and shares in Sections 3–5, Appendix A.1 and B | consistent |
| theory.md Setup Section 4 | Manuscript.tex, opening of Section 4 | consistent |
| theory.md Setup Section 5 | Manuscript.tex, opening of Section 5 | consistent |
| theory.md Setup Appendix A.2 | OnlineAppendix.tex, notation and setup before the joint proof | consistent |
| theory.md Setup Appendix B | OnlineAppendix.tex, opening of B | consistent |
| theory.md L1 | Manuscript.tex label lem:model0; OnlineAppendix.tex proof | consistent |
| theory.md L2 | Manuscript.tex label lem:models; OnlineAppendix.tex proof | consistent |
| theory.md L3 | Manuscript.tex label lem:modeln; OnlineAppendix.tex proof | consistent |
| theory.md L4 | Manuscript.tex label lem:oneside; OnlineAppendix.tex proof | consistent |
| theory.md P1 | Manuscript.tex label prop:yacompare; OnlineAppendix.tex proof | consistent |
| theory.md P2 | Manuscript.tex label prop:ybcompare; OnlineAppendix.tex proof | consistent |
| theory.md P3 | Manuscript.tex label prop:indsales; OnlineAppendix.tex proof | consistent |
| theory.md P4 | Manuscript.tex label prop:tsales; OnlineAppendix.tex proof | consistent |
| theory.md P5 | Manuscript.tex label prop:pfta; OnlineAppendix.tex proof | consistent |
| theory.md P6 | Manuscript.tex label prop:pftb; OnlineAppendix.tex proof | consistent |
| theory.md LA1 | OnlineAppendix.tex label lem:modelS-g; OnlineAppendix.tex proof | consistent |
| theory.md LA2 | OnlineAppendix.tex label lem:modelN-g; OnlineAppendix.tex proof | consistent |
| theory.md P7 | Manuscript.tex label prop:orderprice2; OnlineAppendix.tex proof | consistent |
| theory.md P8 | Manuscript.tex label prop:orderprice1; OnlineAppendix.tex proof | consistent |
| theory.md P9 | Manuscript.tex label prop:price; OnlineAppendix.tex proof | consistent |
| theory.md LB1 | OnlineAppendix.tex label lem:modelg; OnlineAppendix.tex proof | consistent_with_listed_differences |
| numerics paper_labels.json | Fresh document-local AUX files and both reference PDFs | consistent |
| numerics c2c/primitives.py | Section 3, demand, sales, C2C and timing equations; section4.Game and Section 5 payoff assembly | consistent |
| numerics c2c/section4.py claimed_* | L1, L2, L3, LB1 and Appendix A.1/B | consistent |
| numerics c2c/section5.py claimed_* and signs | Appendix A.2; LA1, LA2, P8 and P9 | consistent |
| numerics c2c/closed_form.py | Eight scalar MATLAB files in numerics/matlab and A.1/B uniform-demand profit and stock formulas | consistent |
| numerics c2c/pricing.py | Figure1_MATLAB/pricing_equilibrium.m and Section 5.3 | consistent |
| numerics c2c/figures.py | Figure1_reproduce.m, Num_pricing1.m, Exoprice2_Figure2.m; Sections 5.3/B and captions | consistent |
| numerics quotations and numerical-statement inventory | Both TeX sources, in particular Section 3, Section 5.3 and Appendix B | consistent |
| numerics figure extraction and reference tables | Eight EPS panels, Figure2_reference.csv and the plots in the two published PDFs | consistent |
| numerics check predicates | Result statements in both TeX files, numerical_statements.yaml and tests | consistent |

[Source comparison details](consistency.yaml) · [TeX and PDF evidence](logs/transcription.json) · [MATLAB comparison](logs/matlab.log)

## Theory

| Result | Theory verdict | Printed statement | Confidence | Direct | Critical / major / minor / editorial |
|---|---|---|---|---:|---|
| [L1](proofs/L1.yaml) | sound | holds_as_printed | high | 3/3 passed | 0 / 0 / 0 / 0 |
| [L2](proofs/L2.yaml) | sound | holds_as_printed | high | 8/8 passed | 0 / 0 / 0 / 0 |
| [L3](proofs/L3.yaml) | sound | holds_as_printed | high | 8/8 passed | 0 / 0 / 0 / 0 |
| [LB1](proofs/LB1.yaml) | sound | holds_as_printed | high | 6/6 passed | 0 / 0 / 0 / 0 |
| [L4](proofs/L4.yaml) | sound | holds_as_printed | high | 2/2 passed | 0 / 0 / 0 / 0 |
| [P1](proofs/P1.yaml) | sound | holds_as_printed | high | 2/2 passed | 0 / 0 / 0 / 0 |
| [P2](proofs/P2.yaml) | sound | holds_as_printed | high | 3/3 passed | 0 / 0 / 0 / 0 |
| [P3](proofs/P3.yaml) | sound | holds_as_printed | high | 2/2 passed | 0 / 0 / 0 / 0 |
| [P4](proofs/P4.yaml) | sound | holds_as_printed | high | 1/1 passed | 0 / 0 / 0 / 0 |
| [P5](proofs/P5.yaml) | sound | holds_as_printed | high | 4/4 passed | 0 / 0 / 0 / 0 |
| [P6](proofs/P6.yaml) | sound | holds_as_printed | high | 4/4 passed | 0 / 0 / 0 / 0 |
| [LA1](proofs/LA1.yaml) | sound | holds_as_printed | high | 4/4 passed | 0 / 0 / 0 / 0 |
| [LA2](proofs/LA2.yaml) | sound | holds_as_printed | high | 5/5 passed | 0 / 0 / 0 / 0 |
| [P7](proofs/P7.yaml) | sound | holds_as_printed | high | 2/2 passed | 0 / 0 / 0 / 0 |
| [P8](proofs/P8.yaml) | sound | holds_as_printed | high | 3/3 passed | 0 / 0 / 0 / 0 |
| [P9](proofs/P9.yaml) | sound | holds_as_printed | high | 2/2 passed | 0 / 0 / 0 / 0 |

## Numerical statements

| Statement | Holds | Direct | Supporting |
|---|---|---:|---:|
| F1 | yes | 9/9 passed | 8/8 passed |
| FB1 | yes | 5/5 passed | 4/4 passed |
| N1 | yes | 1/1 passed | 1/1 passed |
| N2 | yes | 1/1 passed | 1/1 passed |
| N3 | yes | 1/1 passed | 1/1 passed |
| N4 | yes | 1/1 passed | 1/1 passed |
| N5 | yes | 1/1 passed | 3/3 passed |
| N6 | partly | 2/2 passed | 1/1 passed |

[Assessment by numerical statement](numerical_statements.yaml) · [Full test report](numerical_checks.md) · [Continuous-interval figure checks](logs/figure_intervals.json)

## Findings

No technical finding or required manuscript correction.

## Coverage limits

- N6 was probed under triangular, beta(2,5) and truncated normal demand in 48 markets. Unchecked nonuniform claims include P2(c), P5(c2)/P6(c2) cost cutoffs, and Section 5. The authors' full nonuniform experiments were unavailable.
- N7 was excluded. Appendix B gives the mixture weights and the Section 5.3 price menu, but the repository supplies neither the mixed endogenous-price solver nor the authors' numerical output.
- Algebra and analytical arguments establish general statements. Sampled equilibria and finite gamma ladders are corroborating evidence. A single model family performed this review. Interpretive prose was outside the requested scope.
