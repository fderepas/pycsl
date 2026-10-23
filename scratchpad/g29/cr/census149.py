import ast, glob, sys, os, json
ROOT="/home/fabrice/git/pycsl"; os.chdir(ROOT)
files=[]
for pat in ["test-suite/corpus/pycsl-reference/**/*.py","test-suite/corpus/python-reference/**/*.py","src/self-annotate/src/**/*.py","src/pycsl_lib/**/*.py"]:
    files+=glob.glob(pat, recursive=True)
tot_cls=0; hits=[]
for f in sorted(files):
    try: t=ast.parse(open(f).read())
    except Exception: continue
    classes={}
    for n in ast.walk(t):
        if isinstance(n, ast.ClassDef):
            for s in n.body:
                if isinstance(s, ast.FunctionDef) and s.name=="__init__":
                    a=s.args; pos=[x.arg for x in a.posonlyargs+a.args][1:]
                    nd=len(a.defaults)
                    if nd:
                        classes[n.name]=(len(pos), len(pos)-nd, [ast.unparse(d) for d in a.defaults])
    if not classes: continue
    tot_cls+=len(classes)
    for n in ast.walk(t):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in classes:
            npos, nreq, defs = classes[n.func.id]
            kws={k.arg for k in n.keywords}
            if len(n.args) < npos and not any(isinstance(x, ast.Starred) for x in n.args):
                hits.append((f, n.lineno, n.func.id, len(n.args), npos, defs))
print("classes with positional defaults:", tot_cls, "omitting call sites:", len(hits))
from collections import Counter
c=Counter(h[0] for h in hits)
for k,v in c.most_common(40): print(v, k)
