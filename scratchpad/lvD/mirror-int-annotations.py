import ast, os
M="src/self-annotate/src"; L="src/pycsl"
def walk(tree, pre=""):
    for n in ast.iter_child_nodes(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            yield pre+n.name, n
            yield from walk(n, pre+n.name+".")
        elif isinstance(n,ast.ClassDef):
            yield from walk(n, pre+n.name+".")
def u(a): return ast.unparse(a) if a is not None else None
for root,_,fs in os.walk(M):
    for f in fs:
        if not f.endswith(".py"): continue
        mp=os.path.join(root,f); rel=os.path.relpath(mp,M); lp=os.path.join(L,rel)
        if not os.path.exists(lp): continue
        try: mt=dict(walk(ast.parse(open(mp).read()))); lt=dict(walk(ast.parse(open(lp).read())))
        except Exception as e: continue
        for q,mn in mt.items():
            ln=lt.get(q)
            if ln is None: continue
            mr,lr=u(mn.returns),u(ln.returns)
            if mr in ("int","List[int]") and lr not in (None,"int",mr):
                print(f"RET\t{rel}\t{q}\tmirror={mr}\tlive={lr}")
            for ma,la in zip(mn.args.args, ln.args.args):
                if u(ma.annotation) in ("int","List[int]") and u(la.annotation) not in (None,"int",u(ma.annotation)):
                    print(f"ARG\t{rel}\t{q}\t{ma.arg}\tmirror={u(ma.annotation)}\tlive={u(la.annotation)}")
