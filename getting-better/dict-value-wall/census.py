import ast, sys, json, re, collections
R='/home/fabrice/git/pycsl-g37ch26'
# trusted at HEAD (tsv rows)
tsv=[l.rstrip('\n').split('\t') for l in open(R+'/getting-better/trusted-reasons.tsv') if l.strip() and not l.startswith('#')]
tsv=[r for r in tsv if r[0]!='file']
trusted={(r[0],r[1]) for r in tsv}
# chain appendix
lines=open(R+'/getting-better/chain-plan-g36/chain-plan-g36.md').read().split('\n')[525:963]
chains={}
for l in lines:
    p=[x.strip() for x in l.split('|')]
    if len(p)<6 or '::' not in p[1]: continue
    f,q=p[1].split('::',1)
    fams=[x.strip() for x in p[3].split('>') if x.strip()]
    chains[(f,q)]=dict(cat=p[0],status=p[2],fams=fams,last=p[5])
def find(path,q):
    try: src=open(path).read()
    except FileNotFoundError: return None
    t=ast.parse(src); hit=[]
    def walk(n,pre):
        for c in ast.iter_child_nodes(n):
            if isinstance(c,(ast.FunctionDef,ast.AsyncFunctionDef)):
                qq=pre+c.name
                if qq==q: hit.append(c)
                walk(c,qq+'.')
            elif isinstance(c,ast.ClassDef): walk(c,pre+c.name+'.')
            else: walk(c,pre)
    walk(t,''); return hit[0] if hit else None
def shape_of_use(parent, node, default):
    """heuristic value shape of a dict read `node` from its parent context and default"""
    if default is not None:
        if isinstance(default,ast.Constant):
            v=default.value
            if isinstance(v,str): return 'str'
            if isinstance(v,bool): return 'bool'
            if isinstance(v,int): return 'int'
            if v is None: return 'Optional'
        if isinstance(default,(ast.List,ast.Tuple)): return 'list'
        if isinstance(default,ast.Dict): return 'dict'
        if isinstance(default,(ast.Set,)) : return 'set'
    if isinstance(parent,ast.Compare):
        for c in parent.comparators+[parent.left]:
            if c is node: continue
            if isinstance(c,ast.Constant):
                if isinstance(c.value,str): return 'str'
                if isinstance(c.value,bool): return 'bool'
                if isinstance(c.value,int): return 'int'
                if c.value is None: return 'Optional'
            if isinstance(c,(ast.Tuple,ast.List,ast.Set)) and c.elts and all(isinstance(e,ast.Constant) and isinstance(e.value,str) for e in c.elts): return 'str'
        if any(isinstance(o,(ast.In,ast.NotIn)) for o in parent.ops) and parent.left is not node: return 'collection'
    if isinstance(parent,(ast.For,ast.comprehension)) and parent.iter is node: return 'list'
    if isinstance(parent,ast.Attribute):
        a=parent.attr
        if a in ('get','items','keys','values','setdefault','update','pop'): return 'dict'
        if a in ('append','extend','insert'): return 'list'
        if a in ('startswith','endswith','split','strip','lower','upper','replace','join','format','rstrip','lstrip','find','isidentifier'): return 'str'
    if isinstance(parent,ast.Subscript) and parent.value is node:
        s=parent.slice
        if isinstance(s,ast.Constant) and isinstance(s.value,str): return 'dict'
        if isinstance(s,ast.Constant) and isinstance(s.value,int): return 'list'
        if isinstance(s,ast.Slice): return 'list/str'
        return 'dict/list'
    if isinstance(parent,ast.FormattedValue): return 'str'
    if isinstance(parent,ast.Call) and isinstance(parent.func,ast.Name):
        fn=parent.func.id
        if fn in ('len','sorted','list','set','tuple','enumerate','any','all','zip'): return 'list'
        if fn in ('whyml_ident','str'): return 'str'
        if fn=='isinstance': return 'any(isinstance)'
        if fn=='int': return 'int'
    if isinstance(parent,ast.BinOp): return 'int/str(arith)'
    if isinstance(parent,(ast.If,ast.While,ast.IfExp,ast.BoolOp,ast.UnaryOp)) : return 'truthy'
    return 'any'
OPS=collections.Counter
def census_body(fn):
    parents={}
    for n in ast.walk(fn):
        for c in ast.iter_child_nodes(n): parents[c]=n
    reads=[]; ops=collections.Counter()
    for n in ast.walk(fn):
        p=parents.get(n)
        # x["k"]
        if isinstance(n,ast.Subscript) and isinstance(n.slice,ast.Constant) and isinstance(n.slice.value,str):
            if isinstance(p,(ast.Assign,)) and n in p.targets: ops['store d["k"]=v']+=1; continue
            if isinstance(n.ctx,ast.Store): ops['store d["k"]=v']+=1; continue
            ops['subscript d["k"]']+=1
            reads.append((n.slice.value, shape_of_use(p,n,None),'sub'))
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute):
            a=n.func.attr
            if a=='get' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str):
                d=n.args[1] if len(n.args)>1 else None
                ops['.get(k, default)' if d is not None else '.get(k)']+=1
                sh=shape_of_use(p,n,d)
                if d is None and sh=='any': sh='Optional'
                reads.append((n.args[0].value, sh, 'get'))
                # chained .get(...) or {} / chained
                if isinstance(p,ast.BoolOp): ops['.get(..) or <default>']+=1
                if isinstance(p,ast.Attribute) and p.attr=='get': ops['chained .get(..).get']+=1
            elif a=='get': ops['.get(<non-literal key>)']+=1
            elif a in ('items','keys','values'):
                ops['.%s() iteration'%a]+=1
            elif a in ('update','setdefault','pop','popitem','clear'):
                ops['.%s()'%a]+=1
        if isinstance(n,ast.Compare) and any(isinstance(o,(ast.In,ast.NotIn)) for o in n.ops) and isinstance(n.left,ast.Constant) and isinstance(n.left.value,str):
            ops['"k" in d']+=1
        if isinstance(n,ast.Dict):
            if n.keys and all(isinstance(k,ast.Constant) and isinstance(k.value,str) for k in n.keys if k is not None):
                if isinstance(p,ast.Return): ops['dict literal returned']+=1
                else: ops['dict literal built']+=1
                if any(isinstance(k,ast.Constant) and k.value=='type' for k in n.keys): ops['IR-node literal {"type":..}']+=1
        if isinstance(n,ast.DictComp): ops['dict comprehension']+=1
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='isinstance' and len(n.args)==2 and isinstance(n.args[1],ast.Name) and n.args[1].id in ('dict','list'):
            ops['isinstance(x, dict|list) (generic walk)']+=1
    return reads, ops
def ann_dicts(fn):
    s=[]
    for a in fn.args.args+fn.args.kwonlyargs:
        if a.annotation is not None: s.append(ast.unparse(a.annotation))
    if fn.returns is not None: s.append('->'+ast.unparse(fn.returns))
    return s
out=[]
for (f,q) in sorted(trusted):
    live=find(R+'/src/pycsl/'+f,q)
    ch=chains.get((f,q))
    rec=dict(file=f,qual=q,live=live is not None, chain=ch)
    if live is not None:
        reads,ops=census_body(live)
        rec['reads']=reads; rec['ops']=dict(ops); rec['ann']=ann_dicts(live)
        src=ast.unparse(live)
        rec['dict_any']=bool(re.search(r'Dict\[str,\s*Any\]|\bdict\b|Dict\[', src))
        rec['nlines']=live.end_lineno-live.lineno+1
    out.append(rec)
json.dump(out,open('census.json','w'),indent=0)
print(len(out), sum(1 for r in out if r['live']), sum(1 for r in out if r['chain']))
