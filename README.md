# Dynamic Competition in Online Retailing: Implications of Customer-to-Customer Interactions

Zheyu Jiang, Xin Geng, Nan Yang, Renyu Zhang

Paper on SSRN: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4074212>

Two retailers compete in price and inventory over two periods. Customer-to-customer (C2C) interactions turn each period's sales into extra demand in the next period, either for the retailer that made the sale (within-brand) or for the market as a whole (cross-brand). This repository holds the paper, its technical statements with their proofs, and code that checks them numerically. It is organised so that an AI agent, or a reader, can verify every lemma and proposition.

| Path | Content |
|---|---|
| [`paper/`](paper/) | The paper and its online appendix, as PDF and LaTeX, with the figure panels and bibliography. The INFORMS class and bibliography style are not included (see [`NOTICE.md`](NOTICE.md)) |
| [`theory.md`](theory.md) | The model, the assumptions, and the 16 lemmas and propositions with their proofs, each with the IDs that the checks use |
| [`numerics/`](numerics/) | The model in Python, the authors' MATLAB code and its Python port, 93 numerical checks, the paper's numerical statements, and the [LaTeX label map](numerics/paper_labels.json) |
| `verification/` | Reports of verification runs, one folder per run, each written by the AI agent that ran it |
| [`AGENTS.md`](AGENTS.md) | How an AI agent finds things here, uses the model, and runs a verification |

## Run the checks

Python 3.10 or later.

```bash
pip install -r requirements.txt
```

```bash
python numerics/run.py
```

That runs every check, in about three minutes, and prints the number of checks passed for each result. To run only the checks of one result, give its ID:

```bash
python numerics/run.py -k P5
```

To recompute and redraw Figure 1 and Figure B.1 into `numerics/figures/reproduced/`:

```bash
python numerics/figures/make_figures.py
```

## Verify the paper with an AI agent

Start an agent in the repository root and ask it to follow `AGENTS.md`. It first checks `theory.md` and the code in `numerics/` against the paper. It then checks each result, step by step through the proof and numerically, in the order of the *Verification roadmap* in `theory.md`, and the paper's numerical statements. It writes its records to `verification/<date>_<model>/`, and ends with an overall judgement on whether the theoretical and the numerical results are verified, with a summary, at the top of that folder's `README.md` and in its `summary.yaml`. Runs by different models sit side by side in `verification/`.

## How `theory.md` relates to the paper

`theory.md` reproduces the statements and proofs of the paper. Where a statement needed a hypothesis made explicit, a quantifier reordered, or a correction, and where a proof needed a step completed, the result lists the change under *Differences from the paper*, and an added paragraph is marked *Added in this file*. The index at the top of `theory.md` shows which results have such changes.

## Citation

Jiang Z, Geng X, Yang N, Zhang R. Dynamic competition in online retailing: Implications of customer-to-customer interactions. *Manufacturing & Service Operations Management*, forthcoming. Available on [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4074212). See [`CITATION.cff`](CITATION.cff).

## License

The code is under the MIT License ([`LICENSE`](LICENSE)). The text and figures of the paper are not: see [`NOTICE.md`](NOTICE.md).
