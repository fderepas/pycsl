import ast, os, sys
roots = ["src/pycsl", "src/self-annotate/src", "src/pycsl_lib",
         "test-suite/corpus/pycsl-reference", "test-suite/corpus/python-reference",
         "test-suite/corpus/negative", "tests"]
kinds = {}
for r in roots:
    if not os.path.isdir(r): continue
    for root,_d,files in os.walk(r):
        for fn in files:
            if not fn.endswith('.py'): continue
            p=os.path.join(root,fn)
            try: tree=ast.parse(open(p,errors='replace').read())
            except Exception: continue
            for n in ast.walk(tree):
                if not isinstance(n, ast.AugAssign): continue
                t=n.target
                if isinstance(t, ast.Name): k="Name (handled)"
                elif isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id=='self': k="self.f (handled)"
                elif isinstance(t, ast.Subscript) and not isinstance(t.slice, ast.Slice): k="a[k] (handled)"
                elif isinstance(t, ast.Subscript): k="*** a[lo:hi] SLICE (DROPPED)"
                elif isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name): k="*** obj.f  non-self Name base (DROPPED)"
                elif isinstance(t, ast.Attribute) and isinstance(t.value, ast.Subscript): k="*** a[i].f  subscript base (DROPPED)"
                elif isinstance(t, ast.Attribute): k="*** x.y.f  nested attr base (DROPPED)"
                else: k="*** %s (DROPPED)" % type(t).__name__
                kinds.setdefault(k,[]).append(f"{p}:{n.lineno}")
for k in sorted(kinds):
    print(f"{len(kinds[k]):5d}  {k}")
    if k.startswith("***"):
        for s in kinds[k][:12]: print("          ",s)
