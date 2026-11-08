import ast, glob, os, warnings
warnings.filterwarnings("ignore")
os.chdir("/home/fabrice/git/pycsl")
files=[]
for pat in ["test-suite/corpus/pycsl-reference/**/*.py","test-suite/corpus/python-reference/**/*.py","src/self-annotate/src/**/*.py","src/pycsl_lib/**/*.py"]:
    files+=glob.glob(pat, recursive=True)
for f in sorted(files):
    try: t=ast.parse(open(f).read())
    except Exception: continue
    kinds={}
    for c in ast.walk(t):
        if not isinstance(c, ast.ClassDef): continue
        for s in c.body:
            if isinstance(s, ast.FunctionDef) and s.name=="__init__":
                nested=set()
                for n in ast.walk(s):
                    if n is not s and isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.Lambda)):
                        nested|={id(x) for x in ast.walk(n)}
                ret=any(isinstance(n,ast.Return) and id(n) not in nested for n in ast.walk(s))
                params={a.arg for a in s.args.posonlyargs+s.args.args+s.args.kwonlyargs}-{"self"}
                reb={n.id for n in ast.walk(s) if id(n) not in nested and isinstance(n,ast.Name) and isinstance(n.ctx,(ast.Store,ast.Del))} & params
                if ret or reb: kinds[c.name]=("return" if ret else "")+(" rebind:"+",".join(sorted(reb)) if reb else "")
    if kinds:
        cons=[n.func.id for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in kinds]
        print(f, kinds, "same-file constructions:", len(cons))
