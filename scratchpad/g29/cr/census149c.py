import ast, glob, os, warnings
warnings.filterwarnings("ignore")
os.chdir("/home/fabrice/git/pycsl")
files=[]
for pat in ["test-suite/corpus/pycsl-reference/**/*.py","test-suite/corpus/python-reference/**/*.py","src/self-annotate/src/**/*.py","src/pycsl_lib/**/*.py"]:
    files+=glob.glob(pat, recursive=True)
trees={}
for f in files:
    try: trees[f]=ast.parse(open(f).read())
    except Exception: pass
# class -> (positional names (no self), pos defaults count, kwonly with defaults)
cls={}
bases={}
for f,t in trees.items():
    for n in ast.walk(t):
        if isinstance(n, ast.ClassDef):
            bases[n.name]=[ast.unparse(b).split('.')[-1] for b in n.bases]
            for s in n.body:
                if isinstance(s, ast.FunctionDef) and s.name=="__init__":
                    a=s.args
                    pos=[x.arg for x in a.posonlyargs+a.args][1:]
                    kwd=[x.arg for x,d in zip(a.kwonlyargs,a.kw_defaults) if d is not None]
                    if a.defaults or kwd:
                        cls[n.name]=(pos, len(a.defaults), kwd, f)
# inheritance: class without own init inherits
def ctor(c, seen=()):
    if c in cls: return cls[c]
    for b in bases.get(c, []):
        if b not in seen:
            r=ctor(b, seen+(c,))
            if r: return r
    return None
hits=[]
for f,t in trees.items():
    for n in ast.walk(t):
        if isinstance(n, ast.Call):
            nm = n.func.id if isinstance(n.func, ast.Name) else (n.func.attr if isinstance(n.func, ast.Attribute) else None)
            if not nm: continue
            c=ctor(nm)
            if not c: continue
            pos,nd,kwd,src=c
            kws={k.arg for k in n.keywords}
            omitted=[p for p in pos[len(n.args):] if p not in kws] + [k for k in kwd if k not in kws]
            if omitted:
                hits.append((f, n.lineno, nm, omitted))
print(len(hits))
from collections import Counter
for (k,v) in Counter((h[0],h[2]) for h in hits).most_common(50): print(v,k)
