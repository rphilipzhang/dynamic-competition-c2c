"""Validate the individual evidence records and compute the overall judgements from their fields."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import os
import re
import yaml

r=Path(__file__).resolve().parents[1]
def read(name):return yaml.safe_load((r/name).read_text())
order="L1 L2 L3 LB1 L4 P1 P2 P3 P4 P5 P6 LA1 LA2 P7 P8 P9".split()
proofs={p:read('proofs/'+p+'.yaml') for p in order}
assert len(list((r/'proofs').glob('*.yaml')))==16
c=read('consistency.yaml')
n=read('numerical_statements.yaml')
vocab=['sound','sound_with_gaps','error_suspected','not_verifiable']
paper_vocab=['holds_as_printed','holds_with_listed_differences','fails','not_verifiable']
def counts(entries,col,keys):
    data=Counter(e[col] for e in entries)
    assert set(data)<=set(keys)
    return {key:data[key] for key in keys}
v=counts(proofs.values(),'verdict',vocab)
w=counts(proofs.values(),'paper_statement',paper_vocab)
ns=counts(n,'holds',['yes','partly','no'])
h=Counter()
findings=[]
corrections=[]
categories={'theory.md':[],'numerics':[]}
for owner,row in list(proofs.items())+[(q['item'],q) for q in c]+[(q['id'],q) for q in n]:
    for f in row['findings']:
        if 'see' in f: continue
        h[f['severity']]+=1
        findings.append((owner,f))
        if f['scope'] in categories:categories[f['scope']].append(f['severity'])
        if f['scope'] in ('statement','proof'):
            corrections.append({'id':owner,'severity':f['severity'],'correction':f['suggested_fix']})
for item,rec in proofs.items():
    assert rec['id']==item and rec['run_id']==r.name and rec['auditor']['date']=='2026-11-22'
    assert rec['steps'] or rec.get('steps_in')
    for step in rec['steps']:
        assert step['status'] in ('verified','plausible','gap','error') and step['note']
        if step['status'] in ('gap','error') and rec['verdict'] in ('sound_with_gaps','sound'):
            assert step.get('repair') or step.get('bypassed_by'),(item,step)
    assert rec['restatement'] and rec['hypotheses_used'] and rec['confidence'] in ('high','medium','low')
    assert 'findings' in rec and 'unstated_hypotheses' in rec and 'differences_checked' in rec
assert len(c)>=31
assert [e['id'] for e in n]==['F1','FB1','N1','N2','N3','N4','N5','N6']
assert set(categories)=={'theory.md','numerics'}
def consistent(k):
    return 'inconsistent' if set(categories[k])&{'critical','major'} else 'consistent_with_findings' if 'minor' in categories[k] else 'consistent'
cj={'theory_md':consistent('theory.md'),'numerics':consistent('numerics')}
tj='not_verified' if v['error_suspected']+v['not_verifiable']+w['fails']+w['not_verifiable'] else 'verified'
assert not any(p['unstated_hypotheses'] for p in proofs.values()) or tj=='not_verified'
report=(r/'numerical_checks.md').read_text()
pas,tot=map(int,re.search(r'\*\*(\d+) of (\d+) checks passed\.',report).groups())
assert pas==tot and 'pytest exit status: 0.' in report
nj='not_verified' if ns['no'] else ('verified_with_qualifications' if ns['partly'] else 'verified')
def nodes(s):return set(re.findall(r'^### \x60([^\x60\n]+::[^\x60\n]+)\x60',s,re.M))
assert len(nodes(report))==tot
ids=order+[q['id'] for q in n]
filters={k:(r/'logs'/('report_'+k+'.md')).read_text() for k in ids}
assert all('pytest exit status: 0.' in s for s in filters.values())
assert set.union(*(nodes(s) for s in filters.values()))==nodes(report)
for k in ids:
    ln=re.search(r'^\| \['+k+r'\]\(#[^)]*\) \| (.*?) \| (.*?) \|$',filters[k],re.M).groups()
    assert ln==re.search(r'^\| \['+k+r'\]\(#[^)]*\) \| (.*?) \| (.*?) \|$',report,re.M).groups()
    vals=proofs[k]['numerical'] if k in proofs else next(e['checks'] for e in n if e['id']==k)
    def frac(s):
        m=re.search(r'\d+/\d+',s)
        return m[0] if m else '0/0'
    assert [frac(vals[k2]) for k2 in ('direct','supporting')]==[frac(t) for t in ln],(k,vals,ln)
old=json.loads((r/'logs/input_hashes.json').read_text())
for key,digest in old.items():
    assert hashlib.sha256(Path(key).read_bytes()).hexdigest()==digest,key
paths=set()
for root,dirs,files in os.walk("."):
    dirs[:]=[d for d in dirs if d not in (".git","verification","__pycache__",".pytest_cache")]
    for file in files:
        if file in ('.DS_Store',) and (Path(root)/file).as_posix() not in old:continue
        paths.add((Path(root)/file).as_posix())
assert paths==set(old),(paths-set(old),set(old)-paths)
assert len(filters)==24
rank={'critical':0,'major':1,'minor':2,'editorial':3}
corrections.sort(key=lambda f:rank[f['severity']])
findings.sort(key=lambda q:rank[q[1]['severity']])
base=f"The theoretical results are {tj.replace('_',' ')}. The numerical results are {nj.replace('_',' ')} because both figures and N1–N5 reproduce and N6 has only partial evidence under nonuniform demand."
stat=f" Of 16 results, {v['sound']} are sound"+(f" and {v['sound_with_gaps']} are sound with checked repairs" if v['sound_with_gaps'] else "")+f"; {w['holds_as_printed']} printed statements hold in context."
if v["sound"]==w["holds_as_printed"]==16:
    stat=" All 16 results are sound, and all 16 printed statements hold under the assumptions in force."
changes=" No technical manuscript correction was identified." if not corrections else " Manuscript corrections: "+"; ".join(x['id']+" "+x['correction'] for x in corrections)+"."
cons=f" The theory transcription is {cj['theory_md'].replace('_',' ')} and the numerical implementation is {cj['numerics'].replace('_',' ')}."
summary=base+stat+changes+cons+f" All {tot} distinct checks passed. P2(c)'s positive stationary point follows for every fixed theta<1. LB1 inherits its price condition from Section 4. The P5(c2) and P6(c2) bounds cover all theta within each qualifying market. N6 leaves P2(c), the two cost cutoffs and endogenous pricing under other laws untested. N7 is excluded because the mixed endogenous-price solver and the authors' output are unavailable. This single-model audit covers technical claims only."
assert len(summary.split())<=200,summary
exposure="Earlier discussion in this chat and the session introduction disclosed earlier audit outcomes and history, including P2(c), N6 and N7. No previous verification directory or external research material was opened for this run. See each proof record for reviewer context."
rec=dict(run_id=r.name,model='gpt-6',date='2026-11-22',repo_version='none',scope='full',prior_exposure=exposure,
         judgement=dict(theoretical_results=tj,numerical_results=nj,consistency=cj),
         results=dict(verdict=v,paper_statement=w),numerical_statements=ns,findings={k:h[k] for k in rank},
         checks={'passed':pas,'total':tot},corrections=corrections,summary=summary)
class D(yaml.SafeDumper):pass
class Quoted(str):pass
D.add_representer(Quoted,lambda d,s:d.represent_scalar('tag:yaml.org,2002:str',s,style='"'))
rec['numerical_statements']={Quoted(k):value for k,value in ns.items()}
(r/'summary.yaml').write_text(yaml.dump(rec,Dumper=D,sort_keys=False,allow_unicode=True,width=115))
s=["# Overall judgement","",f"- Theoretical results — **{tj}**",f"- Numerical results — **{nj}**",f"- Paper consistency — theory.md: **{cj['theory_md']}**, numerics/: **{cj['numerics']}**","",summary,"","## Run","",f"GPT-6, Codex, 2026-11-22. Full audit of the current working tree. Repository version: none (no Git metadata).",
   "",exposure,"",f"The parent ran 24 filtered test processes serially before assigning proof reviews. All tests were rerun unfiltered after Parts 1–3. The run compares document-local AUX maps, PDF page text, EPS ordinates, MATLAB scalar operations, exact rational polynomial signs and analytical proofs. The protected-input hash check covered {len(old)} files.","","## Consistency with the paper","","| Item | Comparison | Outcome |","|---|---|---|"]
for e in c:s.append(f"| {e['item']} | {e['compared_with']} | {e['result']} |")
s+=["","[Source comparison details](consistency.yaml) · [TeX and PDF evidence](logs/transcription.json) · [MATLAB comparison](logs/matlab.log)","","## Theory","","| Result | Theory verdict | Printed statement | Confidence | Direct | Critical / major / minor / editorial |","|---|---|---|---|---:|---|"]
for k,e in proofs.items():
    h2=Counter(f['severity'] for f in e['findings'])
    s.append(f"| [{k}](proofs/{k}.yaml) | {e['verdict']} | {e['paper_statement']} | {e['confidence']} | {e['numerical']['direct']} | "+' / '.join(str(h2[sev]) for sev in rank)+" |")
s+=["","## Numerical statements","","| Statement | Holds | Direct | Supporting |","|---|---|---:|---:|"]
for e in n:s.append(f"| {e['id']} | {e['holds']} | {e['checks']['direct']} | {e['checks']['supporting']} |")
s+=["","[Assessment by numerical statement](numerical_statements.yaml) · [Full test report](numerical_checks.md) · [Continuous-interval figure checks](logs/figure_intervals.json)","","## Findings",""]
for owner,f in findings:s.append(f"- {owner} ({f['severity']}, {f['scope']}) — {f['description']} Suggested change: {f['suggested_fix']}")
if not findings:s.append("No technical finding or required manuscript correction.")
s+=["","## Coverage limits","","- N6 was probed under triangular, beta(2,5) and truncated normal demand in 48 markets. Unchecked nonuniform claims include P2(c), P5(c2)/P6(c2) cost cutoffs, and Section 5. The authors' full nonuniform experiments were unavailable.",
"- N7 was excluded. Appendix B gives the mixture weights and the Section 5.3 price menu, but the repository supplies neither the mixed endogenous-price solver nor the authors' numerical output.",
"- Algebra and analytical arguments establish general statements. Sampled equilibria and finite gamma ladders are corroborating evidence. A single model family performed this review. Interpretive prose was outside the requested scope.",""]
(r/'README.md').write_text('\n'.join(s))
assert read('summary.yaml')['summary'] in (r/'README.md').read_text()
print(json.dumps({'judgement':rec['judgement'],'results':rec['results'],'checks':rec['checks'],'findings':rec['findings'],'numerical_statements':ns,'corrections':corrections,'distinct_filtered_ids':len(filters),'protected_input_files':len(old),'summary_words':len(summary.split())},indent=2))
