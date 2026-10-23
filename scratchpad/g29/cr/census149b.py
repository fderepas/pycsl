import ast, glob, os, warnings
warnings.filterwarnings("ignore")
os.chdir("/home/fabrice/git/pycsl")
files=[]
for pat in ["test-suite/corpus/pycsl-reference/**/*.py","test-suite/corpus/python-reference/**/*.py","src/self-annotate/src/**/*.py","src/pycsl_lib/**/*.py"]:
    files+=glob.glob(pat, recursive=True)
for f in sorted(files):
    try: t=ast.parse(open(f).read())
    except Exception: continue
    cls={}
    for n in ast.walk(t):
        if isinstance(n, ast.ClassDef):
            for s in n.body:
                if isinstance(s, ast.FunctionDef) and s.name=="__init__":
                    a=s.args
                    kd=[(x.arg, ast.unparse(d)) for x,d in zip(a.kwonlyargs,a.kw_defaults) if d is not None]
                    pd=list(zip([x.arg for x in (a.posonlyargs+a.args)][-len(a.defaults):], [ast.unparse(d) for d in a.defaults])) if a.defaults else []
                    if kd or pd: cls[n.name]=(kd,pd)
    for name,(kd,pd) in cls.items():
        calls=[c for c in ast.walk(t) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id==name]
        print(f, name, "kw:",kd, "pos:",pd, "calls:", [ (len(c.args), sorted(k.arg for k in c.keywords if k.arg)) for c in calls][:6])
