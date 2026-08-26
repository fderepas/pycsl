import ast,os,sys
LROOT=os.path.join(sys.argv[1],"src/pycsl"); MROOT=os.path.join(sys.argv[1],"src/self-annotate/src")
def qn(path):
    try: t=ast.parse(open(path).read())
    except Exception: return {}
    out={}
    def w(n,p):
        for c in ast.iter_child_nodes(n):
            if isinstance(c,(ast.FunctionDef,ast.AsyncFunctionDef)): out[p+c.name]=c
            elif isinstance(c,ast.ClassDef): w(c,p+c.name+".")
    w(t,""); return out
miss=0; mirrored=0
for dp,_,fns in os.walk(MROOT):
    if "__pycache__" in dp: continue
    for fn in fns:
        if not fn.endswith(".py"): continue
        mp=os.path.join(dp,fn); rel=os.path.relpath(mp,MROOT); lp=os.path.join(LROOT,rel)
        if not os.path.exists(lp): continue
        L=qn(lp); M=qn(mp); mirrored+=len(M)
        miss+=sum(1 for q in L if q not in M)
print(f"unmirrored_live={miss} mirrored_fns={mirrored}")
