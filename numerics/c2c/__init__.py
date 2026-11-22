"""Numerical companion to "Dynamic Competition in Online Retailing:
Implications of Customer-to-Customer Interactions" (Jiang, Geng, Yang and Zhang).

Modules
    closed_form   the paper's closed forms, ported line by line from the authors' MATLAB code
    pricing       finite-menu price equilibria (Section 5.3), ported from MATLAB
    figures       the numbers behind Figure 1 and Figure B.1
    primitives    the model of Section 3 computed from its definition, used for independent checks
    section4      the claims of Section 4, payoffs built from the primitives, and the parameter samplers
    section5      the same for Section 5, with solvers for its price and inventory games
    predicates    shape predicates for the tests
    paper         the LaTeX source of the paper, for checks that quote it
"""

__version__ = "1.0.0"
