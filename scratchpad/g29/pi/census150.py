import ast, glob, os, warnings
warnings.filterwarnings("ignore")
os.chdir("/home/fabrice/git/pycsl")
PURE={"len","abs","min","max","int","str","bool","float","isinstance","range","list","dict","set","frozenset","tuple","sorted","sum","any","all","hash","repr","ord","chr"}
files=[]
for pat in ["test-suite/corpus/pycsl-reference/**/*.py","test-suite/corpus/python-reference/**/*.py","src/self-annotate/src/**/*.py","src/pycsl_lib/**/*.py"]:
    files+=glob.glob(pat, recursive=True)
def opaque(init):
    body=[s for s in init.body if not (isinstance(s,ast.Expr) and isinstance(s.value,ast.Constant) and isinstance(s.value.value,str))]
    skip=set(); sup=False
    if body and isinstance(body[0],ast.Expr):
        c=body[0].value
        if isinstance(c,ast.Call) and isinstance(c.func,ast.Attribute) and c.func.attr=="__init__" and isinstance(c.func.value,ast.Call) and isinstance(c.func.value.func,ast.Name) and c.func.value.func.id=="super" and not c.func.value.args and not c.keywords:
            skip={id(x) for x in ast.walk(c)}-{id(y) for a in c.args for y in ast.walk(a)}; sup=True
    roots={id(n.value) for n in ast.walk(init) if isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name)}
    for n in ast.walk(init):
        if id(n) in skip: continue
        if isinstance(n,ast.Call):
            r=n.func
            while isinstance(r,(ast.Attribute,ast.Subscript)): r=r.value
            if isinstance(r,ast.Call) and isinstance(r.func,ast.Name) and r.func.id=="super": return "opaque"
            if isinstance(r,ast.Name) and r.id=="self": return "opaque"
            if any(isinstance(m,ast.Name) and m.id=="self" for a in list(n.args)+[k.value for k in n.keywords] for m in ast.walk(a)) and not (isinstance(n.func,ast.Name) and n.func.id in PURE): return "opaque"
        elif isinstance(n,ast.Name) and n.id=="self" and isinstance(n.ctx,ast.Load) and id(n) not in roots: return "opaque"
    return "super" if sup else None
tot={}
for f in sorted(files):
    try: t=ast.parse(open(f).read())
    except Exception: continue
    kinds={}
    for c in ast.walk(t):
        if isinstance(c,ast.ClassDef):
            init=[s for s in c.body if isinstance(s,ast.FunctionDef) and s.name=="__init__"]
            pi=any(isinstance(s,ast.FunctionDef) and s.name=="__post_init__" for s in c.body)
            k=opaque(init[0]) if init else None
            if pi: k="post_init"
            if k: kinds[c.name]=k
    if not kinds: continue
    cons=[n.func.id for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in kinds]
    if cons:
        print(f, {k:(kinds[k], cons.count(k)) for k in set(cons)})
print("---- cross-file (by class name, collisions possible) ----")
allk={}
trees={}
for f in sorted(files):
    try: trees[f]=ast.parse(open(f).read())
    except Exception: continue
    for c in ast.walk(trees[f]):
        if isinstance(c,ast.ClassDef):
            init=[s for s in c.body if isinstance(s,ast.FunctionDef) and s.name=="__init__"]
            pi=any(isinstance(s,ast.FunctionDef) and s.name=="__post_init__" for s in c.body)
            k=opaque(init[0]) if init else None
            if pi: k="post_init"
            if k: allk.setdefault(c.name,set()).add((k,f))
from collections import Counter
cnt=Counter()
for f,t in trees.items():
    for n in ast.walk(t):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in allk:
            if not isinstance(getattr(n,'parent',None),ast.Raise):
                cnt[(f,n.func.id)]+=1
# exclude raise sites
rs=Counter()
for f,t in trees.items():
    for r in ast.walk(t):
        if isinstance(r,ast.Raise) and isinstance(r.exc,ast.Call) and isinstance(r.exc.func,ast.Name) and r.exc.func.id in allk:
            rs[(f,r.exc.func.id)]+=1
for k,v in sorted(cnt.items()):
    nr=v-rs.get(k,0)
    if nr>0: print(nr, k, sorted(x[0] for x in allk[k[1]]))
