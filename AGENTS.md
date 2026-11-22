# Instructions for AI agents

## The repository

| Path | Content | May a verifier edit it? |
|---|---|---|
| `paper/` | Reference manuscript and online appendix (TeX and PDF), bibliography, and eight EPS figure panels. The INFORMS class `informs1.cls` and style `ormsv080.bst` are present only in a local copy | no |
| `theory.md` | The model, the assumptions, and the 16 lemmas and propositions with their proofs | no |
| `numerics/` | Python model, the authors' MATLAB code and its Python port, numerical checks, the paper's numerical statements | no |
| `verification/` | One folder per verification run, written by the agent that ran it | only your own run folder |

`theory.md` follows the paper. Where it departs from the paper, the result lists the departure under **Differences from the paper**, and a paragraph added to a proof is marked **Added in this file**.

In the paper and in `theory.md`, unqualified *increasing* and *decreasing* mean nondecreasing and nonincreasing, respectively. Equality is allowed. An explicit *strictly* or a symbol such as `<` or `>` retains its strict meaning. Apply this convention to both statements and proofs.

## Finding things

- A result by ID: `grep -n '^### P5$' theory.md`. IDs: L1 to L4 (Lemmas 1 to 4), P1 to P9 (Propositions 1 to 9), LA1 and LA2 (Lemmas A.1 and A.2), LB1 (Lemma B.1). Parts are written `P5.c1`. The index at the top of `theory.md` lists all sixteen.
- The *In the paper* line of each result gives its LaTeX label, for example `prop:pfta`. Look it up in `paper/Manuscript.tex` or `paper/OnlineAppendix.tex`. The corresponding PDF gives its printed number. The numerical checks use `numerics/paper_labels.json`. Part 1 explains how to verify the map from the TeX sources.
- Figure 1 uses `paper/figure1.eps` through `paper/figure4.eps` in panel order. Figure B.1 uses `paper/yaG.eps`, `paper/ybG.eps`, `paper/piaG.eps` and `paper/pibG.eps`.
- The numerical statements of the paper (Figures 1 and B.1, and N1 to N7 in the text): `numerics/numerical_statements.yaml`. N7 is listed there with a field `excluded` that gives the reason the repository does not check it.
- The checks of a result: `python numerics/run.py -k P5`, or `pytest numerics -k P5`. Each check's docstring states its points, what it computes, and its pass criterion.
- The code: `numerics/README.md`.

## Using the model

Run from the repository root with `numerics` on the path. Example: is the order pair that Lemma 3 states an equilibrium of the model at one parameter point?

```python
import sys; sys.path.insert(0, "numerics")
from c2c import primitives as pm
from c2c.section4 import Params, Game, claimed_first_period, distributions

prm = Params(pa1=4.0, pb1=4.4, pa2=4.2, pb2=4.6, ca=1.0, cb=1.5, beta=0.2, theta=0.5, gamma=2.0)
mu, sigma = 10.0, 4.0
dist = distributions(mu, sigma)["uniform"]
ya, yb, *_ = claimed_first_period(prm, "N", dist.ppf)       # what Lemma 3 states
pay_a, pay_b = Game(prm, "N", dist).period1_payoffs()       # payoffs built from the model's definition
print(pm.nash_gap(pay_a, pay_b, ya, yb, 1.5 * (mu + sigma)))  # best responses and the largest gain from deviating
```

## Verifying the paper

The aim is to decide, for each of the 16 results, whether the statement in `theory.md` is true and proved, and whether the statement as printed in the paper holds, and to decide whether the numerical statements F1, FB1 and N1 to N6 hold. The text that the paper puts around a result (motivation, interpretation, discussion) is out of scope.

`theory.md` and `numerics/` were prepared from the paper by others, so both are themselves under test. A full run has four parts, in this order:

1. **Consistency with the paper**: `theory.md` against the paper, and the code in `numerics/` against the paper. The later parts rely on both, so do this first.
2. **The results**: the 16 lemmas and propositions.
3. **The numerical statements**: F1, FB1, N1 to N6, and the reason for excluding N7.
4. **Overall judgement and summary**: whether the theoretical results and the numerical results are verified, by fixed rules, and a short summary of the run. A run is not complete without it.

When the request is limited to theory, use `scope: theory_only`. Complete Part 1 for the theory and the numerical code, quotations and predicates used to check it. Verify all 16 results in Part 2 and give the theoretical judgement in Part 4. Skip the independent numerical statements in Part 3. State the scope of the code comparison and mark the numerical-results judgement `not_assessed`.

The section *Verification roadmap* at the top of `theory.md` gives the dependencies between the results, an order, and what kind of argument each proof makes.

### Rules

1. Choose a run ID `<YYYY-MM-DD>_<model>`, with the date on which the run starts, for example `2026-11-21_claude-opus-5-5`. If `verification/<run-id>/` exists, add a suffix (`-b`, `-c`). Write only inside `verification/<run-id>/`, temporary files included. Create `verification/<run-id>/tmp/` and run every command with `PYTHONDONTWRITEBYTECODE=1` and with `TMPDIR` and `MPLCONFIGDIR` set to the absolute path of that folder. Delete the folder when the run is complete.
2. Independence. Read nothing outside the repository root, and do not list it either. Do not open any other folder in `verification/` until your own run is complete. If you have seen one, or anything outside the repository, say so under `prior_exposure`.
3. Do not edit `paper/`, `theory.md` or `numerics/` during a verification run. If you believe that a check in `numerics/` is wrong or does not test what it names, report it as a finding with scope `numerics`.
4. Run one test process at a time. The full set of checks takes about three minutes on one core. If subagents share the work, run `python numerics/run.py -k <ID> --report verification/<run-id>/logs/report_<ID>.md` once for every in-scope ID yourself, one after another, before you hand out the work, and let the subagents read those logs. A subagent runs its own scripts, not the test suite.
5. A clean record is a valid outcome. Do not manufacture findings. Before you report an error, try to refute it: derive the step a second way, or compute it.
6. Record each finding once. A finding of Part 1 that concerns one result goes in that result's record, and the entry of `consistency.yaml` names it by ID (`see: P5/F3`). A finding of Part 1 that concerns several results, or none, goes in `consistency.yaml`. A finding of Part 2 that several results share goes in the record of the first of them in the order of `theory.md`, and the other records name it in a step note (`see: P5/F1`).
7. Record a false or missing proof step even when the conclusion holds. A claim that the text asserts without a derivation, or with an incomplete one, is not a missing step: if you derive it under the same hypotheses and quantifiers, its status is `verified` (see *Definitions*). To establish that the issue is immaterial, give a derivation under the same hypotheses and quantifiers, or identify an independent verified argument that bypasses the step. Trace its effect on results that cite it. A finite numerical probe alone cannot establish a general repair.

### Part 1. Consistency with the paper

Use `paper/Manuscript.tex` and `paper/OnlineAppendix.tex` for word-for-word comparisons of statements, assumptions and proofs. To recover the printed numbers, copy the contents of `paper/` to a build directory inside your run folder. From that copy, run `latexmk -pdf Manuscript.tex OnlineAppendix.tex`. If `paper/` lacks the class or the style, the build fails: say so in `consistency.yaml`, read the printed numbers from the PDFs in `paper/`, and name the comparisons you could not complete. Read the number in the first field of each `\newlabel` entry in the two generated `.aux` files, keeping each document's labels together. Normalise whitespace and resolve `\ref{...}` and `\eqref{...}` with those numbers, retaining the parentheses for `\eqref`. Compare the result with `numerics/paper_labels.json` and use the PDFs in `paper/` to check the printed references. The map leaves out labels inside unnumbered environments such as `equation*` and `eqnarray*`, because LaTeX prints no number for them.

**`theory.md` against the paper.** `theory.md` may depart from the paper only where it says so. Check every part of it:

1. *Model* against Section 3 of the paper: the text must be the paper's, word for word up to the conversion to Markdown.
2. *Assumptions*: every quoted sentence must occur in the paper. The titles and scopes are editorial. Check each scope against the paper. For A3, Section 3.2.1 introduces the i.i.d. seed demand and its density. The closing paragraph of Section 3 specifies interval support and strictly positive density in its interior for the general-distribution equilibrium. Use that class for L1–L3 and LB1 when checking general-demand uniqueness. The main analysis from Section 4 uses the uniform distribution in A10.
3. *Implicit conditions* I1 to I3 and the *Hypotheses* line of each result are editorial. Check that each is used where it is listed, and that no result needs a condition that its line omits.
4. *Setup* paragraphs at the start of each section of results: word for word.
5. Each result's *Statement* and *Proof*: every difference from the paper's text must be listed under *Differences from the paper*, or be a paragraph marked *Added in this file*. Everything else must be the paper's text. For each listed difference, decide whether it is needed (see *Definitions*).

An unreported departure, an unnecessary change to the printed statement, or an incorrect addition is a finding with scope `theory.md`. A correct, explicitly marked supplementary proof detail can be retained even when the paper already establishes the step.

**`numerics/` against the paper.** The checks are only as good as the code they run. Check:

1. `numerics/c2c/primitives.py` against the model of Section 3: the demand split, the C2C-induced demand of each scenario, stockout-based substitution, sales, period profits and their sum over the two periods, and the timing. It must use no result of the paper.
2. The functions `claimed_*` in `numerics/c2c/section4.py` and `numerics/c2c/section5.py`, and the claimed signs in `section5.py`, against the statements they transcribe: Lemmas 1 to 3 and B.1, and Lemmas A.1 and A.2 and Propositions 8 and 9, with the definitions of Online Appendix A.2 that they use.
3. `numerics/c2c/closed_form.py`, `pricing.py` and `figures.py` against the paper's closed forms, line by line against the authors' MATLAB code in `numerics/matlab/`, and the parameter values in `figures.py` against the captions of Figures 1 and B.1 and the text of Section 5.3.
4. The predicates of the checks, against the statements: strict or weak inequalities, the quantifiers, which retailer, which scenario and which period. Do this for each check as part of step 8 of Part 2.
5. Every quotation in `numerics/numerical_statements.yaml` and in the checks, against the paper, and the reason of every entry with a field `excluded`: is it true, and does the paper make no other numerical statement that the file omits?

The formula quotation checks read the same TeX sources in `paper/`. Check each quotation in context and compare its numerical predicate with the statement it tests. The numerical-statement quotation check resolves references with `numerics/paper_labels.json`. The figure extraction check reads the eight EPS panels directly from `paper/` and compares a fresh extraction with the stored data and calibration in `numerics/figures/`.

Record Part 1 in `verification/<run-id>/consistency.yaml` (format below).

### Part 2. The results

Work through the results one at a time, in the order of the roadmap. A result may be given to a subagent, which then follows this file.

1. **Read.** In `theory.md`: the sections *Model* and *Notation and assumptions*, the setup paragraphs at the start of the result's section, and the result. Read the paper's statement and proof in the LaTeX source.
2. **Compare with the paper.** Use what Part 1 found for this result, and record in `differences_checked` whether each listed difference is needed.
3. **Restate** the statement in your own words with every quantifier explicit. For P5.c2 and P6.c2, use the fixed-market interpretation given below.
4. **Hypotheses.** List the assumptions the proof uses, by ID, including those used through a cited result. List any hypothesis it needs that neither the statement nor the list of assumptions provides. Under `unstated_hypotheses` list only genuinely new hypotheses, which restrict the claim. A condition in force by context or by the meaning of the model is not one of them: mention it in a step note.
5. **Check the proof step by step.** A step is one inference: a displayed equation, a case split, an appeal to an earlier result, a limit, a sign claim. Identify it by a short quotation or an equation number. Re-derive it, by hand, symbolically (SymPy) or numerically, rather than re-reading it. Paragraphs marked *Added in this file* are steps like any other. When symbolic simplification over many symbols is slow, check the identity in exact rational arithmetic at many random points instead, and say so.
6. **Check every cited result**: its hypotheses must hold where it is applied. When the proof uses a claim proved inside another proof rather than a stated result, list it under `relies_on`.
7. **Probe the boundary**: theta at 0 and 1, equal market shares, the price condition A11 with equality, critical fractiles at the ends of the support, small gamma.
8. **Test the statement numerically.** Read `logs/report_<ID>.md`, or run `python numerics/run.py -k <ID>`. Read what each check computes and decide whether it tests the part it names, with the predicate the statement uses. Add computations of your own where they help, as scripts in `verification/<run-id>/scripts/` that run from the repository root as `python verification/<run-id>/scripts/<name>.py`, with no arguments, and print the numbers you quote. The replay check runs each script exactly so. Put the inputs in the script, or write one script per input. Name a script `<ID>_<short-description>.py`, or `shared_<short-description>.py` if several results use it, or `part1_<short-description>.py` for Part 1. A statement for all parameters must survive a search for counterexamples. A statement for gamma large enough can only be probed. For each threshold, identify the parameters it may depend on. Hold those fixed when testing uniformity over the remaining parameters, including their endpoints. State which parameters varied in each probe.

**Thresholds in P5.c2 and P6.c2.** The cost cutoffs are sufficient. In the equal-share case, take each admissible market satisfying $\Delta c\geq\Delta^A$ or $0<\Delta c\leq\Delta^B$, respectively. For that market, the lower bound on $\gamma$ may depend on costs and applies to every $\theta\in[0,1]$. For each $\gamma$ at or above the bound, the substitution cutoff may depend on both the market and $\gamma$. Check the profit inequalities on both sides and at the cutoff as printed. A probe that holds $\gamma$ fixed while varying costs tests the stronger claim of a common bound across markets. Record the fixed-market interpretation as consistent with the printed (c2) statements. It adds no entry to `differences_checked` or `corrections`. Verify the arguments for those statements and grade any separate findings under the usual rules.

Two results with one joint proof, such as LA1 and LA2: put the steps in the record of the first, and in the record of the second list only the steps specific to it, with `steps_in: <first ID>`. Each record still gives its own verdict.

### Part 3. The numerical statements

For F1, FB1 and N1 to N6: run `python numerics/run.py -k <ID>`, read the checks, and compare what they compute with the quoted statement and with the published figure. For N7, which has a field `excluded`, check the reason and name N7 in the summary under what the run did not check.

Set `holds` to `"yes"` when the evidence supports every part of the statement, to `"partly"` when every part you could test holds but some part is untested or supported only in a weaker form, and to `"no"` when some part fails.

### Part 4. Overall judgement and summary

For a full run, finish Parts 1 to 3 and run all checks once more with `python numerics/run.py --report verification/<run-id>/numerical_checks.md`. For a theory-only run, use the same command with `-k 'L1 or L2 or L3 or L4 or P1 or P2 or P3 or P4 or P5 or P6 or P7 or P8 or P9 or LA1 or LA2 or LB1'` for a single report of the selected checks. Count each check in that report once. Apply the following rules to the requested scope. In each table take the first row that applies.

**Consistency with the paper**, separately for `theory.md` and for `numerics/`:

| Judgement | Applies when |
|---|---|
| `inconsistent` | A finding of scope `theory.md` [resp. `numerics`] has severity `critical` or `major`. |
| `consistent_with_findings` | A finding of that scope has severity `minor`. |
| `consistent` | Otherwise. |

**Theoretical results**, the 16 lemmas and propositions:

| Judgement | Applies when |
|---|---|
| `not_verified` | A result is `error_suspected` or `not_verifiable`, a paper statement `fails` or is `not_verifiable`, or establishing the conclusion requires a new restriction, a change to a substantive claim, or an unresolved essential step. |
| `verified` | All 16 substantive conclusions are established under the paper's assumptions and quantifiers. This includes `sound_with_gaps` when the record demonstrates the repair. A corrected cross-reference or an explicit restatement of an assumption already in force can preserve the conclusion. Record the evidence in each affected result. |

**Numerical results**, the numerical statements F1, FB1 and N1 to N6:

| Judgement | Applies when |
|---|---|
| `not_verified` | An entry has `holds: "no"`, or a check that an entry relies on fails, or `numerics/` is `inconsistent` with the paper in code that an entry relies on. |
| `verified_with_qualifications` | Every entry has `holds: "yes"` or `holds: "partly"`, and at least one has `"partly"`. |
| `verified` | Every entry has `holds: "yes"`. |

The theoretical judgement concerns the conclusions. Preserve the separate verdict on each printed statement, the status of each original proof step, and the finding's severity. A transcription discrepancy requires checking the primary source before judging the paper. List every correction the paper needs in `summary.yaml`, including demonstrated repairs to incorrect steps and necessary changes disclosed in `theory.md`. Grade a disclosed change as you would grade the finding it repairs. Name each correction of severity `minor` or above in the summary by result ID. Optional proof details, derivations that you supply for asserted claims, and standalone restatements of assumptions in force, including those in force only by context, need no manuscript edit.

**Summary.** One paragraph of at most 200 words, written for the authors and for a reader who will not open the records. It states:

1. the requested overall judgements and the main reason for each, in the opening sentences,
2. how many results received each verdict, and how many paper statements hold as printed,
3. every correction that the paper needs, as a short phrase with the result ID, most severe first,
4. whether the in-scope portions of `theory.md` and `numerics/` are consistent with the paper,
5. what the run did not check, and anything that limits its confidence, such as a single model or a part probed only numerically.

State the judgements directly. Give a reason or a limit only where it changes what a reader should conclude. The summary goes at the top of `README.md` and, with the judgements and the counts, into `summary.yaml` (formats below).

### Definitions

| Step status | Meaning |
|---|---|
| `verified` | You re-derived or computed the step and it is correct. This includes a claim that the text asserts without a derivation, or with an incomplete one, when you derive it yourself under the same hypotheses and quantifiers. Say in `note` that the derivation is yours. A finite numerical probe is not a derivation of a general claim. |
| `plausible` | The step reads as correct and is standard, but you did not re-derive it. |
| `gap` | The proof relies on a claim that the text does not state, or you could not derive a claim that the text asserts. Describe the missing step and record any verified repair. |
| `error` | The step is false as written. Attach evidence and record any verified repair separately. |

| Severity | Meaning |
|---|---|
| `critical` | The statement appears to be false, or the proof fails and no repair is apparent. |
| `major` | A step does not follow. Repair needs a new argument or an added hypothesis. |
| `minor` | A gap that a careful reader can fill with a routine argument, or an uncovered boundary case that does not affect the main claim. |
| `editorial` | A typo, a notational slip, or an ambiguity that does not affect correctness. |

Scope of a finding: `statement` (of the result), `proof`, `theory.md` (a departure of `theory.md` from the paper that is wrong, missing or not needed), or `numerics` (code that does not match the paper, or a check that is wrong or does not test what it names).

A listed difference is **needed** when at least one of these holds:

- the paper's version fails at an admissible point, or is not what the proof establishes,
- it states a hypothesis that the paper imposes only by context (for example in the opening paragraph of a section), so that the statement read alone would be false without it,
- it corrects an explicit inequality, formula or reference that fails to express the result established in the paper.

A difference that only rewords the paper, or adds what the statement already implies, is not needed. In particular, a point of equality is compatible with *increasing* and *decreasing*. A correct, marked proof addition explaining equality or providing another derivation may be recorded as supporting detail.

Verdict on the statement in `theory.md`. Take the first row that applies. Findings of scope `numerics` do not enter.

| Verdict | Applies when |
|---|---|
| `error_suspected` | An admissible counterexample survives rechecking, or an essential inference is demonstrably false and the conclusion lacks a verified alternative argument. |
| `not_verifiable` | An essential step remains unestablished or you could not follow the argument well enough to judge the conclusion. |
| `sound_with_gaps` | A proof step has a demonstrable error or omission and the record supplies or cites a checked argument establishing the same conclusion throughout the stated domain. |
| `sound` | The conclusion follows from verified or standard steps. Any remaining slips are editorial or occur in steps shown to be unnecessary. |

Judge each printed statement under the assumptions in force where it appears. Use `holds_as_printed` when it holds there, even if its proof needs repair. This includes a statement that needs a hypothesis the paper imposes only by context (the second case of *needed*): the difference in `theory.md` makes the hypothesis explicit and does not correct the printed statement. Use `holds_with_listed_differences` when a needed difference listed in `theory.md` corrects the printed statement (the first or third case). Explain whether it preserves the substantive conclusion. Use `fails` for a false claim in its stated setting and `not_verifiable` when the claim cannot be judged. A genuinely new hypothesis restricts the claim.

Confidence: `high` if you re-derived or computed every step and tested the statement numerically where possible, `medium` if you re-derived the main line and only read some steps, `low` otherwise.

### Output

```
verification/<run-id>/
  README.md                    the report: overall judgement and summary first, format below
  summary.yaml                 Part 4: the judgements, the counts and the summary, for machines
  consistency.yaml             Part 1: theory.md and numerics/ against the paper
  numerical_checks.md          the final full or theory-only check report (Part 4)
  proofs/<ID>.yaml             one record per result, 16 files
  numerical_statements.yaml    full run only, one entry for each of F1, FB1, N1 to N6
  scripts/                     your own scripts, if any
  logs/                        the per-ID reports of rule 4, if any
```

In every YAML file, quote the values `"yes"`, `"no"` and `"partly"`: unquoted, YAML reads `yes` and `no` as booleans.

A record in `proofs/<ID>.yaml`:

```yaml
id: P5
run_id: 2026-11-21_claude-opus-5-5
auditor: {model: claude-opus-5-5, harness: Claude Code, date: "2026-11-21", prior_exposure: none}
verdict: sound_with_gaps                  # on the statement in theory.md
paper_statement: holds_with_listed_differences
confidence: medium
restatement: >-
  One paragraph with every quantifier explicit.
differences_checked:                      # one entry per difference listed in theory.md
  - difference: 1
    needed: true
    note: How you checked it, and which case of the definition of needed applies.
hypotheses_used: [A1, A10, A11, I1]
unstated_hypotheses: []                   # genuinely new hypotheses the result needs
relies_on: []                             # claims proved inside other proofs, for example "LA1 joint proof, the bounds with derivatives"
steps:
  - id: 1
    locator: 'By Lemma 2&3, we have the closed forms'   # single quotes for text with backslashes
    claim: What the step asserts.
    status: verified                      # verified | plausible | gap | error
    method: symbolic                      # reading | re-derivation | symbolic | numerical
    note: What you did.
    # repair: for a gap or error step, the checked derivation under the original hypotheses and quantifiers, or the verified step that repairs it
    # bypassed_by: a verified independent argument, if the original step is unnecessary
findings:
  - id: F1
    severity: minor                       # critical | major | minor | editorial
    scope: proof                          # statement | proof | theory.md | numerics
    locator: "(A.19)"
    description: What is wrong or missing.
    suggested_fix: What would repair it.
    evidence: Evidence of the original problem and the checked derivation or cited step that repairs it, if applicable.
numerical:
  command: python numerics/run.py -k P5
  direct: "4/4 passed"
  supporting: "6/6 passed"
  assessment: Whether the checks test the parts they name, and what they leave out.
  own_checks: []
not_checked:
  - Anything the record does not cover, and why.
```

An entry of `numerical_statements.yaml` has the fields `id`, `holds` (`"yes"`, `"no"` or `"partly"`), `checks` (direct and supporting, passed of total), `assessment`, and `findings` as above.

`consistency.yaml` has one entry for each item of Part 1, that is, for each part of `theory.md` (the model, the assumptions, the implicit conditions, each setup paragraph, and each of the 16 results) and for each piece of code (`primitives.py`, the `claimed_*` functions of `section4.py` and of `section5.py`, the port in `closed_form.py`, `pricing.py` and `figures.py`, the quotations, and the label map `numerics/paper_labels.json`):

```yaml
- item: theory.md P5            # or: theory.md Model, numerics c2c/primitives.py, ...
  compared_with: Proposition 5 and its proof in paper/Manuscript.tex and paper/OnlineAppendix.tex
  method: script                # script | reading
  result: consistent_with_listed_differences   # consistent | consistent_with_listed_differences | consistent_with_findings | inconsistent
  note: What was compared and how. For a result, whether each listed difference is the only change at its place.
  findings: []                  # as in a proof record, with scope theory.md or numerics, or see: <ID>/<finding>
```

The result of an item: `inconsistent` if a finding on it is `critical` or `major`, `consistent_with_findings` if one is `minor`, and otherwise `consistent_with_listed_differences` or `consistent`.

`summary.yaml`:

```yaml
run_id: 2026-11-21_claude-opus-5-5
model: claude-opus-5-5
date: "2026-11-21"
repo_version: <git commit of the repository, or "none">
scope: full                                         # full | theory_only
judgement:
  theoretical_results: verified                     # verified | not_verified
  numerical_results: verified                       # verified | verified_with_qualifications | not_verified | not_assessed
  consistency: {theory_md: consistent, numerics: consistent}   # consistent | consistent_with_findings | inconsistent
results:                                            # counts over the 16 results
  verdict: {sound: 0, sound_with_gaps: 0, error_suspected: 0, not_verifiable: 0}
  paper_statement: {holds_as_printed: 0, holds_with_listed_differences: 0, fails: 0, not_verifiable: 0}
numerical_statements: {"yes": 0, "partly": 0, "no": 0}   # null for a theory-only run
findings: {critical: 0, major: 0, minor: 0, editorial: 0}   # each finding counted once
checks: {passed: 0, total: 0}
corrections:                                        # every correction the paper needs, most severe first
  - {id: P5, severity: minor, correction: One phrase.}
summary: >-
  The summary paragraph, as in README.md.
```

`README.md` holds, in this order:

1. **Overall judgement**: the Part 4 judgements within scope as a short list, then the summary paragraph,
2. the run: model, harness, date, repository version, prior exposure, effort,
3. the consistency of `theory.md` and of `numerics/` with the paper: one table with one row per item of `consistency.yaml`,
4. a table with one row per result: the verdict on the statement in `theory.md`, the verdict on the paper's statement, the confidence, the direct checks passed, and the number of findings by severity,
5. for a full run, a table with one row per numerical statement,
6. every finding of severity `minor` or above, most severe first, each with its suggested fix,
7. what the run did not check.

State the results directly.
