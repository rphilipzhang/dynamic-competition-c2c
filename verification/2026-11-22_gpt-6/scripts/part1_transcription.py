"""Compare the model, result statements, proofs, assumption quotes and setups against both freshly rebuilt sources."""
from pathlib import Path
import ast, difflib, json, re, subprocess
import yaml

r=Path(__file__).resolve().parents[1]
docs={n:Path('paper',n+'.tex').read_text() for n in ('Manuscript','OnlineAppendix')}
md=Path('theory.md').read_text()
labels={}
printed=[]
pagecounts={}
for n,source in docs.items():
    labels[n]={k:{'number':v,'page':p} for k,v,p in re.findall(r'^\\newlabel\{([^}]+)\}\{\{([^{}]*)\}\{([^{}]*)\}',(r/'build'/(n+'.aux')).read_text(),re.M)}
    def pages(folder):
        return subprocess.check_output(['pdftotext','-layout',folder/(n+'.pdf'),'-']).decode().split('\f')
    pages1,pages2=pages(Path('paper')),pages(r/'build')
    assert pages1==pages2,n
    pagecounts[n]=len(pages1)-1
    def visible(k,kind):
        v=labels[n][k]; num=v['number']
        needle=(kind+num+'.' if kind in ('lemma','proposition') else ('('+num+')' if kind=='eq' else 'figure'+num))
        assert needle.lower() in re.sub(r'\s+','',pages1[int(v['page'])-1]).lower(),(k,v)
        printed.append((n,k,num,v['page']))
    for k in labels[n]:
        if k.startswith('lem:'):visible(k,'lemma')
        if k.startswith('prop:'):visible(k,'proposition')
        if k in ('fig:general','fig:compare'):visible(k,'figure')
    for m in re.finditer(r'\\begin\{(eqnarray|equation)\}(.*?)\\end\{\1\}',source,re.S):
        for k in re.findall(r'\\label\{([^}]+)\}',m[2]):visible(k,'eq')
assert labels==json.loads(Path('numerics/paper_labels.json').read_text())
def unwrap(s,pattern,before='',after=''):
    while m:=re.search(pattern,s):
        i=m.end(); depth=1
        while depth:
            if s[i] in '{}' and s[i-1]!='\\':depth+=1 if s[i]=='{' else -1
            i+=1
        s=s[:m.start()]+before+s[m.end():i-1]+after+s[i:]
    return s
def tokens(s,n):
    s=re.sub(r'(?m)^\s*%.*$','',s).replace("’","'").replace('--','–')
    s=re.sub(r'\\(eqref|ref)\{([^}]+)\}',lambda m:('({})' if m[1]=='eqref' else '{}').format(labels[n][m[2]]['number']),s)
    s=re.sub(r'\\citep(?:\[([^\]]*)\]\[([^\]]*)\])?\{([^}]+)\}',lambda m:'['+(m[1] or '')+' '+'; '.join('@'+k.strip() for k in m[3].split(','))+(m[2] or '')+']',s)
    s=re.sub(r'\\cite\{([^}]+)\}',r'@\1',s)
    s=unwrap(s,r'\\footnote\{','[Footnote: ',']')
    s=unwrap(s,r'\\(?:textbf|textit|emph|subsection|subsubsection|paragraph)\{')
    s=unwrap(s,r'\{\\(?:noindent\\)?(?:bf|it)\s+')
    s=re.sub(r'\\(?:begin|end)\{(?:equation|eqnarray|align|aligned|itemize|enumerate)\*?\}', '',s)
    s=re.sub(r'\\(?:label|tag|vspace)\{[^{}]*\}', '',s)
    s=re.sub(r'\\item\s*\[([^\]]+)\]',r'\1',s)
    s=re.sub(r'(?m)^#{3,4} [\d.]+ |(?m:^- (?=\*?\*?\())','',s)
    s=s.replace('**','').replace(r'\noindent',' ')
    s=re.sub(r'(?m)^\*([^*\n]+)\*$',r'\1',s)
    s=re.sub(r'(?<!\w)\*([A-Za-z][^*\n]{0,40}?)\*(?!\w)',r'\1',s)
    s=re.sub(r'(?<=\d)&(?=\d)','TextAmp',s.replace(r'\&','TextAmp'))
    s=s.replace('&','').replace('TextAmp','&').replace('~',' ').replace(r'\S','§').replace(r'\qed','∎')
    s=re.sub(r'\\(?:nonumber|notag|quad|qquad)\b|\\\\|\\[][(),;! ]|[$]',' ',s)
    return re.findall(r'\\[A-Za-z]+|\\[^\s]|[A-Za-z]+|\d+|[^\s]',s)
pairs={}
def compare(k,a,b,n):
    l,h=tokens(a,n),tokens(b,n)
    delta=[] if l==h else [(op,' '.join(l[i:j]),' '.join(h[u:v])) for op,i,j,u,v in difflib.SequenceMatcher(None,l,h,autojunk=False).get_opcodes() if op!='equal']
    pairs[k]={'words_and_math_tokens':len(h),'changes':delta}
def section(s,start,end):return '\n'.join(s.splitlines()[start-1:end])
for name,n,a,b,c,d in [('model','Manuscript',84,172,120,219),('section4','Manuscript',174,176,307,309),('section5','Manuscript',350,358,879,887),('appendixA2','OnlineAppendix',327,334,889,899),('appendixB','OnlineAppendix',480,481,1162,1164)]:
    compare(name,section(docs[n],a,b),section(md,c,d),n)
headers=list(re.finditer(r'^### ((?:L[AB]?|P)\d+)$',md,re.M))
oa=docs['OnlineAppendix']
starts=list(re.finditer(r'^(?:\{\\(?:noindent\\)?bf Proof of (?:Lemma|Proposition)|\\noindent\\textbf\{Proof of Lemmas)',oa,re.M))
proofs={rid:oa[m.start():oa.index(r'\qed',m.end())+5] for rid,m in zip('L1 L2 L3 L4 P1 P2 P3 P4 P5 P6 LA1 P7 P8 P9 LB1'.split(),starts,strict=True)}
for i,m in enumerate(headers):
    k=m[1]
    body=re.split(r'^## ',md[m.end():headers[i+1].start() if i+1<len(headers) else len(md)],1,flags=re.M)[0]
    label=re.search(r'In the paper:.*?[(]\x60([^\x60]+)\x60[)]',body)[1]
    n='OnlineAppendix' if k in ('LA1','LA2','LB1') else 'Manuscript'
    stmt,pr=body.split('#### Statement\n',1)[1].split('#### Proof\n',1)
    tx,=[z[2] for z in re.finditer(r'\\begin\{(lemma|proposition)\}(.*?)\\end\{\1\}',docs[n],re.S) if r'\label{'+label+'}' in z[2]]
    compare(k+' statement',tx,'\n'.join(stmt.strip().splitlines()[1:]),n)
    if k=='LA2':assert 'joint with Lemma A.1' in pr
    else:
        compare(k+' proof',proofs[k],pr,'OnlineAppendix')
        nums=[labels['OnlineAppendix'][key]['number'] for key in re.findall(r'\\label\{([^}]+)\}',proofs[k])]
        assert all(t in nums for t in re.findall(r'\\tag\{([^}]+)\}',pr)),k
book={n:' '.join(tokens(s,n)) for n,s in docs.items()}
assumptions={m[1]:[any(' '.join(tokens(q,n)) in book[n] for n in docs) for q in re.findall(r'"(.*?)"',m[2].split('*Scope:*')[0])] for m in re.finditer(r'^- \*\*(A\d+)\.(.*)$',md,re.M)}
quotes={}
for v in yaml.safe_load(Path('numerics/numerical_statements.yaml').read_text()):
    k=v['id'];n='OnlineAppendix' if k in ('FB1','N5','N7') else 'Manuscript'
    quotes[k]=' '.join(tokens(v['quote'],n)) in book[n]
sites=[]
for name in ('test_port_matches_paper','test_propositions_exogenous','test_section_5_transcription'):
    tree=ast.parse(Path('numerics/tests',name+'.py').read_text())
    vals={i.targets[0].id:i.value for i in tree.body if isinstance(i,ast.Assign) and isinstance(i.targets[0],ast.Name)}
    if name=='test_section_5_transcription': strings=[v.value for a in vals['QUOTES'].values for v in a.elts]
    else:
        calls=[z.args[1] for z in ast.walk(tree) if isinstance(z,ast.Call) and isinstance(z.func,ast.Name) and z.func.id=='quoted' and len(z.args)==2]
        strings=[ast.literal_eval(vals[z.id] if isinstance(z,ast.Name) else z) for z in calls]
    for s in strings:
        which=[n for n in docs if ' '.join(s.split()) in ' '.join(docs[n].split())]
        assert which,(name,s)
        sites.append([name,which,s])
report=dict(labels={n:len(z) for n,z in labels.items()},pdf_pages=pagecounts,published_labels=printed,assumption_matches=assumptions,formula_quotes=sites,numerical_quotes=quotes,comparisons=pairs)
(r/'logs/transcription.json').write_text(json.dumps(report,indent=2))
print(len(pairs),'text sections;',len(printed),'printed labels;',len(sites),'formula quotations;',sum(map(len,assumptions.values())),'assumption quotations;',sum(quotes.values()),'numerical quotations')
for k,v in pairs.items():
    if v['changes']:print(k,str(v['changes'])[:450])
assert len(headers)==16 and len(assumptions)==15 and all(all(t) for t in assumptions.values()) and all(quotes.values())
assert [k for k,v in pairs.items() if v['changes']]==['LB1 statement']
assert len(pairs['LB1 statement']['changes'])==1 and 'price condition of Section 4' in pairs['LB1 statement']['changes'][0][2]
