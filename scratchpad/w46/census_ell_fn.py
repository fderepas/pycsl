import ast, os
roots = ["src/pycsl", "src/self-annotate/src", "src/pycsl_lib",
         "test-suite/corpus/pycsl-reference", "test-suite/corpus/python-reference"]
for root in roots:
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('.git','__pycache__')]
        for f in sorted(fn):
            if not f.endswith(".py"): continue
            p = os.path.join(dp, f)
            try:
                srctxt = open(p, encoding="utf-8", errors="replace").read()
                t = ast.parse(srctxt)
            except Exception: continue
            lines = srctxt.split("\n")
            for fu in ast.walk(t):
                if not isinstance(fu, (ast.FunctionDef, ast.AsyncFunctionDef)): continue
                stmt_ids = set(); ann_ids = set()
                for n in ast.walk(fu):
                    if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and n.value.value is Ellipsis:
                        stmt_ids.add(id(n.value))
                    for fld in ("annotation", "returns"):
                        a = getattr(n, fld, None)
                        if a is not None:
                            for m in ast.walk(a): ann_ids.add(id(m))
                hits = [n.lineno for n in ast.walk(fu)
                        if isinstance(n, ast.Constant) and n.value is Ellipsis
                        and id(n) not in stmt_ids and id(n) not in ann_ids]
                if hits:
                    # is it \trusted?  look at the decorator/comment lines just above the def
                    above = "\n".join(lines[max(0, fu.lineno - 12):fu.lineno])
                    tr = "TRUSTED" if "\\trusted" in above or "\\abstract" in above else "concrete"
                    print("%-9s %s:%d  %s  (lines %s)" % (tr, p, fu.lineno, fu.name, hits))
