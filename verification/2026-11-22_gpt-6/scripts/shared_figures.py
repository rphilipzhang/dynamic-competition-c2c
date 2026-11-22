"""Check both numerical figures over the continuous substitution interval using rational arithmetic."""
from itertools import product
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
import sympy as sp
sys.path.insert(0, "numerics")
from c2c import closed_form as cf
from c2c import figures

r = Path(__file__).resolve().parents[1]
theta = sp.Symbol("theta")
Q = sp.Rational
prices = (Q(2), Q(4))
pairs = list(product(prices, repeat=2))
fixed = (Q(1), Q("0.1"), Q(10), Q(5))

def fraction(x):
    return [sp.Poly(p, theta, domain=sp.QQ) for p in sp.cancel(x).as_numer_denom()]

def positive(x):
    n, d = fraction(x)
    return n.eval(0)*d.eval(0) > 0 and n.count_roots(0, 1) == d.count_roots(0, 1) == 0

def root_summary(x):
    n, d = fraction(x)
    assert d.count_roots(0, 1) == 0
    roots = [float((a+b)/2) for (a,b),_ in n.intervals(eps=Q(1,10**12)) if a >= 0 and b <= 1]
    assert len(roots) == n.count_roots(0, 1)
    return [int(sp.sign(n.eval(z)*d.eval(z))) for z in (0,1)], roots

def eq(tables):
    winners=[]
    for a,b in pairs:
        gains=[(v[a,b][0]-v[6-a,b][0],v[a,b][1]-v[a,6-b][1]) for v in tables]
        if all(positive(x) and positive(y) for x,y in gains):
            winners.append((a,b))
        else:
            # A common strictly profitable deviation excludes the candidate from the entire triangle.
            assert any(all(positive(-p[i]) for p in gains) for i in range(2))
    p, = winners
    return p

results={}
for letter,ca,g,i in [('a',Q('.1'),Q('.7'),0),('b',Q('.1'),Q(2),0),('c',Q('.95'),Q('.7'),1),('d',Q('.95'),Q(2),1)]:
    money={}
    for s in 'SN':
        tables=[{(a,b):cf.period2_profit(a,b,theta,ca,*fixed,s,g,Q(ra),Q(rb)) for a,b in pairs} for ra,rb in [(0,0),(15,0),(0,15)]]
        stage2=eq(tables)
        fns=(cf.spfta_t1,cf.spftb_t1) if s=='S' else (cf.npfta_t1,cf.npftb_t1)
        first={(a,b):tuple(f(a,b,*stage2,theta,ca,*fixed,g) for f in fns) for a,b in pairs}
        stage1=eq([first])
        assert stage2==(4,4) and stage1==((2,2) if s=='S' and g==2 else (4,4))
        money[s]=first[stage1][i]
    signs, roots=root_summary(money['N']-money['S'])
    assert (signs,len(roots)) == (([-1,1],1) if letter in 'ac' else ([1,1],0))
    results['F1'+letter]={'gap_signs':signs,'roots':roots}
for i,(letter,ca) in enumerate(zip("abcd",map(Q,[".5",".5",".1",".92"]))):
    args=(Q(2),Q(2),Q(2),Q(2),theta,ca,*fixed)
    gs,gn=(cf.find_general_exo(*args,Q(2),w,1-w)[i] for w in (Q('.8'),Q('.2')))
    if letter=='b':
        assert positive(-sp.diff(gn,theta)) and sp.diff(cf.find_general_exo(*args,Q(0),Q('.8'),Q('.2'))[i],theta)==0
        results['FB1b']='GN strictly decreasing, benchmark constant'
    else:
        signs,roots=root_summary(gs-gn)
        assert signs==[1,-1] and len(roots)==1
        results['FB1'+letter]={'gap_signs':signs,'roots':roots}
author=pd.read_csv('numerics/matlab/Figure2_MATLAB/Figure2_reference.csv')
ours=figures.figureB1_data()
results['matlab_max_abs_diff']=float(np.max(np.abs(author.to_numpy()-ours.to_numpy())))
assert results['matlab_max_abs_diff']<1.e-11
eps=pd.read_csv(r/'scratch/figure-data/published_data.csv',dtype={'figure':str})
cal=json.loads((r/'scratch/figure-data/published_data_calibration.json').read_text())['files']
series1=figures.figure1_data()
for (fig,panel,file,series),group in eps.groupby(['figure','panel','file','series']):
    s=series.split()[-1]
    expected=series1[series1.panel==panel]['profit_'+s].round(4) if fig=='1' else ours[panel+'_'+s]
    assert len(expected)==len(group)==11
    deviation=np.max(np.abs(group.value.to_numpy()-expected.to_numpy()))
    assert deviation<=cal[file]['y_axis']['resolution']['abs_error_bound_vs_plotted_double']+1.e-9
results['ordinates_by_figure']=eps.groupby('figure').size().to_dict()
print(json.dumps(results,indent=2))
