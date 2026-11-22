# Notice on copyright and reuse

This repository contains material of two kinds, under different terms.

## Code

Everything under `numerics/`, and the configuration files at the top level, is released under the MIT License. See [LICENSE](LICENSE).

## Text and figures of the paper

The following are derived from the paper and are **not** covered by the MIT License:

- `paper/`: the manuscript and its online appendix, as PDF and LaTeX, and the figure panels,
- `theory.md`: the model, statements and proofs of the paper, converted to Markdown,
- `numerics/figures/published_data.csv` and its calibration file: the data read back from the published figure panels,
- quotations of the paper in `numerics/numerical_statements.yaml`, in the checks, and in `verification/`.

The paper is

> Zheyu Jiang, Xin Geng, Nan Yang, Renyu Zhang. Dynamic Competition in Online Retailing: Implications of Customer-to-Customer Interactions. *Manufacturing & Service Operations Management*, forthcoming.

Copyright in the paper has been transferred to INFORMS. The text here is the authors' own version of the manuscript, not the version typeset by INFORMS, and is posted by the authors for the purpose of verification, in reliance on the rights that the INFORMS copyright transfer leaves with authors. The version of record is the one published by INFORMS. Its DOI will be added here when it is assigned. No permission to redistribute or adapt the text or the figures of the paper is granted by this repository.

Compiling the PDF files in `paper/` with pdfLaTeX requires the INFORMS document class `informs1.cls` and the bibliography style `ormsv080.bst`. They are not included in this repository. To compile, put copies of both files in `paper/` alongside the LaTeX sources.
