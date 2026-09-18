import ast, glob, os, warnings
warnings.filterwarnings("ignore")
os.chdir("/home/fabrice/git/pycsl")
PURE={"len","abs","min","max","int","str","bool","float","isinstance","range","list","dict","set","frozenset","tuple","sorted","sum","any","all","hash","repr","ord","chr"}
files=[]
for pat in ["test-suite/corpus/pycsl-reference/**/*.py","test-suite/corpus/python-reference/**/*.py","src/self-annotate/src/**/*.py","src/pycsl_lib/**/*.py"]:
    files+=glob.glob(pat, recursive=True)
for f in sorted(files):
    try: t=ast.parse(open(f).read())
    except Exception: continue
    hit={}
    for c in ast.walk(t):
        if not isinstance(c, ast.ClassDef): continue
        for init in [s for s in c.body if isinstance(s, ast.FunctionDef) and s.name=="__init__"]:
            par={}
            for p in ast.walk(init):
                for ch in ast.iter_child_nodes(p): par[id(ch)]=p
            why=set()
            for n in ast.walk(init):
                if isinstance(n, ast.Subscript) and isinstance(n.ctx,(ast.Store,ast.Del)):
                    r=n.value
                    while isinstance(r, ast.Subscript): r=r.value
                    while isinstance(r, ast.Attribute) and not (isinstance(r.value, ast.Name) and r.value.id=="self"): r=r.value
                    if isinstance(r, ast.Attribute) and isinstance(r.value, ast.Name) and r.value.id=="self": why.add("store:"+r.attr)
                if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Load) and isinstance(n.value, ast.Name) and n.value.id=="self":
                    p=par.get(id(n))
                    if isinstance(p, ast.Subscript) and p.value is n: continue
                    if isinstance(p, ast.Attribute) and p.value is n: continue
                    if isinstance(p, ast.Call) and (p.func is n or (isinstance(p.func, ast.Name) and p.func.id in PURE)): continue
                    if isinstance(p,(ast.Compare,ast.BoolOp,ast.UnaryOp,ast.BinOp,ast.FormattedValue)): continue
                    if isinstance(p,(ast.If,ast.While,ast.IfExp,ast.Assert)) and getattr(p,"test",None) is n: continue
                    if isinstance(p,(ast.For,ast.comprehension)) and p.iter is n: continue
                    why.add("escape:"+n.attr)
            if why: hit[c.name]=sorted(why)
    if hit:
        cons=[n.func.id for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in hit]
        if cons: print(f, hit, len(cons))
