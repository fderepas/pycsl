import ast, os
from collections import Counter
ROOTS=["test-suite/corpus","src/self-annotate","src/pycsl","src/pycsl_lib"]
lit=[];unk=[]
for root in ROOTS:
    for dp,dn,fns in os.walk(root):
        dn[:]=[d for d in dn if d not in(".git","__pycache__",".venv")]
        for fn in fns:
            if not fn.endswith(".py"): continue
            p=os.path.join(dp,fn)
            try: t=ast.parse(open(p,encoding="utf-8",errors="replace").read())
            except Exception: continue
            for cls in ast.walk(t):
                if not isinstance(cls,ast.ClassDef): continue
                for ch in cls.body:
                    if not(isinstance(ch,ast.FunctionDef) and ch.name=="__init__"): continue
                    for st in ast.walk(ch):
                        a=r=None
                        if isinstance(st,ast.Assign) and len(st.targets)==1: a,r=st.targets[0],st.value
                        elif isinstance(st,ast.AnnAssign): a,r=st.target,st.value
                        if not(isinstance(a,ast.Attribute) and isinstance(a.value,ast.Name)
                               and a.value.id=="self" and r is not None): continue
                        if isinstance(r,ast.List) and r.elts:
                            allc=all(isinstance(e,ast.Constant) and isinstance(e.value,int)
                                     and not isinstance(e.value,bool) for e in r.elts)
                            (lit if allc else unk).append((root,p,cls.name+"."+a.attr))
print("ROUTE #87 — NON-EMPTY list literal stored to a field in __init__")
print("  all-int-constant (faithful arm):", len(lit), dict(Counter(x[0] for x in lit)))
print("  other (unconstrained arm)      :", len(unk), dict(Counter(x[0] for x in unk)))
print()
for lbl,rows in (("CONSTANT",lit),("NON-CONSTANT",unk)):
    print("---",lbl,"in corpus/mirror ---")
    for r in rows:
        if r[0] in ("test-suite/corpus","src/self-annotate"): print("   ",r[1],r[2])
