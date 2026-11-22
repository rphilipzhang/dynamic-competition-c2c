# Verification run 2026-11-22_claude-opus-5-5

## Overall judgement

- **Theoretical results:** `verified`
- **Numerical results:** `verified_with_qualifications`
- **Consistency with the paper:** `theory.md` `consistent`; `numerics/` `consistent`

The theoretical results are verified and the numerical results are verified with qualifications. All 16 lemmas and propositions are sound and all 16 printed statements hold as printed; every proof step was re-derived by hand, symbolically or in exact arithmetic, and none needed a repair. F1, FB1 and N1 to N5 hold. N6, that all results stay qualitatively the same under other demand distributions, holds only partly: the repository tests weak forms of Propositions 1 to 6 under three distributions, and not Proposition 2(c), the cost thresholds of Propositions 5(c2) and 6(c2), or Section 5. The paper needs no correction of severity minor or above. Five editorial corrections: P5 and P6, include the (c2) thresholds in the final choice of the gamma threshold; P8, say that the neighbourhood in (b2) is around a pair satisfying (A.23); LA2, delete a stray "> 0"; P1, use one symbol for the theta threshold. theory.md and numerics/ are consistent with the paper, with editorial findings only. The run did not check N7, which the repository excludes for lack of a solver. One model did the work; the large-gamma thresholds rest on the proofs and are probed only numerically.

## The run

| | |
|---|---|
| Model | claude-opus-5-5 |
| Harness | Claude Code (Agent SDK), one orchestrating agent and four subagents of the same model |
| Date | 2026-11-22, 11:19 to 12:43 CST (about 1 h 25 min) |
| Repository version | none (the copy is not a git repository; git was not run). `CITATION.cff` gives version 1.0.0. |
| Scope | full |
| Prior exposure | The orchestrator's session context listed one-line memory notes saying that an earlier verification run of this repository exists and where the paper's LaTeX is kept elsewhere. No earlier audit, no other folder of `verification/` and no file outside the repository root was read. No earlier conversation about this paper. |
| Effort | The orchestrator ran the checks of every in-scope ID one after another (`logs/report_<ID>.md`), did Part 1 for the model, assumptions, setup paragraphs and label map, built the paper, re-derived by hand the proofs of L1-L3 and LB1 and key steps of P1, P3, P4, P5(a) and of the Section 5 limit prices and nu_A > nu_B as a check on the subagents, and wrote Parts 3 and 4. Temporary files were kept in the run folder and removed at the end; `logs/run_logs.sh` is the script that produced the per-ID logs. Subagents: L1-L3, LB1, L4; P1-P6; LA1, LA2, P7-P9; and the MATLAB port with the numerical statements. 26 scripts in `scripts/`. Final run of all checks: 93 of 93 passed in 218 s (`numerical_checks.md`). |

## Consistency of `theory.md` and `numerics/` with the paper

| Item | Method | Result | Findings |
|---|---|---|---|
| theory.md Model | script | consistent | none |
| theory.md Assumptions | script | consistent | none |
| theory.md Implicit conditions | reading | consistent | none |
| theory.md Setup of the Exogenous Price Model | script | consistent | none |
| theory.md Setup of the Endogenous Price Model | script | consistent | none |
| theory.md Notation used in the proofs for Section 5 | script | consistent | none |
| theory.md Definition of the mixed scenario | script | consistent | none |
| theory.md L1 | script | consistent | none |
| theory.md L2 | script | consistent | none |
| theory.md L3 | script | consistent | none |
| theory.md L4 | script | consistent | none |
| theory.md P1 | script | consistent | none |
| theory.md P2 | script | consistent | none |
| theory.md P3 | script | consistent | none |
| theory.md P4 | script | consistent | none |
| theory.md P5 | script | consistent | none |
| theory.md P6 | script | consistent | none |
| theory.md LA1 | script | consistent | see LA1/F1 (editorial) |
| theory.md LA2 | script | consistent | none |
| theory.md P7 | script | consistent | none |
| theory.md P8 | script | consistent | none |
| theory.md P9 | script | consistent | none |
| theory.md LB1 | script | consistent_with_listed_differences | none (difference 1 needed, case 2) |
| numerics paper_labels.json | script | consistent | none |
| numerics c2c/primitives.py | reading | consistent | none |
| numerics claimed_* of c2c/section4.py | reading | consistent | none |
| numerics claimed_* of c2c/section5.py | reading | consistent | none |
| numerics c2c/closed_form.py | script | consistent | none |
| numerics c2c/pricing.py | script | consistent | none |
| numerics c2c/figures.py | script | consistent | none |
| numerics quotations | script | consistent | C1 (editorial) |
| numerics predicates of the checks | reading | consistent | C2 (editorial) |

## Results

| ID | Verdict (theory.md) | Paper statement | Confidence | Direct checks passed | Findings (critical / major / minor / editorial) |
|---|---|---|---|---|---|
| L1 | sound | holds_as_printed | high | 3/3 | 0 / 0 / 0 / 0 |
| L2 | sound | holds_as_printed | high | 8/8 | 0 / 0 / 0 / 0 |
| L3 | sound | holds_as_printed | high | 8/8 | 0 / 0 / 0 / 0 |
| LB1 | sound | holds_as_printed | high | 6/6 | 0 / 0 / 0 / 0 |
| L4 | sound | holds_as_printed | high | 2/2 | 0 / 0 / 0 / 0 |
| P1 | sound | holds_as_printed | high | 2/2 | 0 / 0 / 0 / 1 |
| P2 | sound | holds_as_printed | high | 3/3 | 0 / 0 / 0 / 0 |
| P3 | sound | holds_as_printed | high | 2/2 | 0 / 0 / 0 / 0 |
| P4 | sound | holds_as_printed | high | 1/1 | 0 / 0 / 0 / 0 |
| P5 | sound | holds_as_printed | high | 4/4 | 0 / 0 / 0 / 1 |
| P6 | sound | holds_as_printed | high | 4/4 | 0 / 0 / 0 / 1 |
| LA1 | sound | holds_as_printed | high | 4/4 | 0 / 0 / 0 / 1 |
| LA2 | sound | holds_as_printed | high | 5/5 | 0 / 0 / 0 / 1 |
| P7 | sound | holds_as_printed | high | 2/2 | 0 / 0 / 0 / 0 |
| P8 | sound | holds_as_printed | high | 3/3 | 0 / 0 / 0 / 1 |
| P9 | sound | holds_as_printed | high | 2/2 | 0 / 0 / 0 / 0 |

The direct counts of L2, L3 and LB1 each include two transcription checks that are tagged as direct (finding C2); the checks of the equilibrium property itself pass.

## Numerical statements

| ID | Holds | Direct | Supporting | Note |
|---|---|---|---|---|
| F1 | yes | 9/9 | 8/8 | recomputed panels match the published EPS points within the extraction bounds; equilibria unique and strict |
| FB1 | yes | 5/5 | 4/4 | port equals the authors' MATLAB values (99 of 99) and the published panels |
| N1 | yes | 1/1 | 1/1 | equal shares in both periods at all 44 points; prices change at 22 point-scenario pairs |
| N2 | yes | 1/1 | 1/1 | one crossing in panels (a) and (c), at theta = 0.770 and 0.580 |
| N3 | yes | 1/1 | 1/1 | N above S at every theta in panel (b), by at least 9.78 |
| N4 | yes | 1/1 | 1/1 | N above S at every theta in panel (d), by at least 9.91 |
| N5 | yes | 1/1 | 3/3 | GN order of B falls in theta; panels (c), (d) cross once |
| N6 | partly | 2/2 | 1/1 | only weak forms of P1-P6 under three distributions are tested |

## Findings of severity minor or above

None. The run recorded eight editorial findings, listed here for completeness with their fixes:

- P5/F1 (proof): the closing choice of gamma^A covers (a), (b), (c1) only. Fix: also require gamma^A >= gamma^A_4 for (c2).
- P6/F1 (proof): the same for gamma^B. Fix: also require gamma^B >= max{gamma^B_2, gamma^B_3} for (c2).
- P8/F1 (statement): (b2) does not say which price pair the open neighbourhood surrounds. Fix: a neighbourhood of a pair satisfying (A.23).
- LA2/F1 (proof): stray "> 0" after the bound C_{r_0}/gamma on |d^2 V_i|. Fix: delete it.
- P1/F1 (proof): the threshold is \underline{\theta}^{SN} in the statement and \theta^{SN} in the proof. Fix: one symbol.
- LA1/F1 (theory.md): the Hypotheses line of LA1 lists A13, which the Scenario S argument does not use. Fix: drop it or mark it as maintained but unused.
- C1 (numerics): `numerics/numerical_statements.yaml` omits the discussion sentence after Proposition 5 that Pi^N_A may decrease in theta at intermediate theta under strong cross-brand C2C; the sentence holds (286 of 1800 probed points). Fix: add an entry or mark it excluded as discussion.
- C2 (numerics): five transcription checks in `numerics/tests/test_port_matches_paper.py` are tagged `claims` for L2.first, L3.first and LB1.first. Fix: tag them `supports`.

## What the run did not check

- N7 (equilibrium prices with both C2C types under endogenous pricing): excluded by the repository, correctly, because no solver for that game exists in `numerics/`.
- The large-gamma thresholds (P1(ii), P3(a), P4, P5, P6, LA1, LA2, P8, P9) are established by the proofs; the checks and the run's own probes evaluate them only at finitely many, mostly very large, gamma.
- N6 beyond what the repository tests: Proposition 2(c), the cost thresholds of P5(c2) and P6(c2), the existence of the crossings, and all of Section 5 under other distributions.
- Equilibrium selection at second-period states of Section 5 that no unilateral first-period deviation reaches (recorded under LA1 and P9); the proofs' bounds do not depend on it.
- The provenance of the MATLAB files: several carry revision comments, and MATLAB is not installed, so the port was compared with the files as given. The published panels are reproduced, so this does not affect F1 or FB1.
- All work was done by one model; there is no second independent model.
