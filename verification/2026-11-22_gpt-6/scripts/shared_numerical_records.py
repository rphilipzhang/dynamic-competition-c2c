"""Assemble the eight numerical records using this run's per-claim test counts and independent figure work."""
from pathlib import Path
import re
import yaml
r=Path(__file__).resolve().parents[1]
notes={
'F1':"All four panels agree with the eight extracted series (88 ordinates) within the calibrated plotting/rounding bounds. The two-price payoff tables were also checked over the entire theta interval with exact rational sign tests. Both firms choose 4 in period 2 at all feasible sales states. In S at gamma=2 both charge 2 in period 1, while the other first-period equilibria are (4,4). See logs/extraction.log and logs/figure_intervals.json.",
'FB1':"The 99 EPS ordinates of the four panels agree within the panel-specific calibration bounds. The maximum absolute difference from the authors' reference CSV is 4.974e-14. Costs, uniform support, fixed prices and GS/GN mixture weights agree with Appendix B. See logs/figure_intervals.json and logs/extraction.log.",
'N1':"At every plotted point in each scenario the two firms charge the same price within a period, so each receives share 1/2 in both periods. Given the (4,4) continuation, (2,2) in S when gamma=2 supplies the price-change examples. Comparing all unilateral deviations at the sales-triangle vertices, whose payoffs are affine in sales, and isolating their roots in theta confirms these equilibria over [0,1].",
'N2':"At gamma=.7 the N-minus-S profit gap is negative at zero and positive at one for A in panel (a) and B in panel (c). Exact rational root isolation gives one crossing per panel, at theta=0.7697356971 and 0.5799982575, respectively. The plotted grid brackets both.",
'N3':"At gamma=2, Figure 1(b)'s N-minus-S profit of A is strictly positive at both endpoints; neither the numerator nor the denominator of the rational difference has a root in [0,1]. Shares are equal across periods at the verified price equilibria.",
'N4':"At gamma=2, Figure 1(d)'s N-minus-S profit of B is strictly positive at both endpoints; neither the numerator nor the denominator of the rational difference has a root in [0,1]. The period shares are equal.",
'N5':"B's GN order in Figure B.1(b) has strictly negative derivative for the entire substitution interval; the benchmark is constant. In panels (a), (c) and (d) the GS-minus-GN differences change from positive to negative. Exact root isolation gives one crossing per panel at 0.5318370520, 0.8883411042 and 0.1565061670. This supports the stated patterns at these fixed mixtures and parameter values.",
'N6':"Three nonuniform laws (triangular, beta(2,5) and truncated normal) are probed in 16 sampled markets each, with 41 theta nodes and finite gamma levels. Equilibrium checks also exercise these laws. The tests cover selected, sometimes weaker, patterns in P1–P6: a no-more-than-one-crossing predicate need not exhibit a crossing. The nonuniform P2(c) hump, the P5(c2)/P6(c2) cost cutoffs and Section 5 are untested. The authors' full nonuniform experiments are unavailable."}
class D(yaml.SafeDumper): pass
class Quote(str): pass
D.add_representer(Quote,lambda d,s:d.represent_scalar('tag:yaml.org,2002:str',s,style='"'))
rows=[]
for k,note in notes.items():
    report=(r/'logs'/('report_'+k+'.md')).read_text()
    direct,support=re.search(r'^\| \['+k+r'\]\(#[^)]*\) \| (.*?) \| (.*?) \|$',report,re.M).groups()
    assert 'pytest exit status: 0.' in report
    rows.append(dict(id=k,holds=Quote('partly' if k=='N6' else 'yes'),checks={'direct':direct+' passed','supporting':support+' passed' if support!='–' else '0/0'},assessment=note,findings=[]))
(r/'numerical_statements.yaml').write_text(yaml.dump(rows,Dumper=D,sort_keys=False,allow_unicode=True,width=110))
