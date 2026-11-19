import ast, glob, os
# Find functions across the live emitter + mirror that have `for x in <local>`
# where <local> is assigned an all-string tuple/list literal in the same function.
def all_str_literal(node):
    if isinstance(node, (ast.Tuple, ast.List)):
        if not node.elts: return False
        return all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.elts)
    return False

hits = []
roots = ["src/pycsl/module6_whyml", "src/self-annotate/src/module6_whyml",
         "src/pycsl", "src/self-annotate/src"]
seen=set()
for root in roots:
    for f in glob.glob(os.path.join(root, "**", "*.py"), recursive=True):
        if f in seen: continue
        seen.add(f)
        try:
            tree = ast.parse(open(f).read())
        except Exception:
            continue
        for fn in ast.walk(tree):
            if not isinstance(fn, ast.FunctionDef): continue
            litvars = set()
            for st in ast.walk(fn):
                if isinstance(st, ast.Assign) and all_str_literal(st.value):
                    for t in st.targets:
                        if isinstance(t, ast.Name): litvars.add(t.id)
            for st in ast.walk(fn):
                if isinstance(st, ast.For) and isinstance(st.iter, ast.Name) and st.iter.id in litvars:
                    hits.append((f, fn.name))
                    break
for f,n in hits:
    print(f"{n}\t{f}")
print("TOTAL functions:", len(hits))
print("UNIQUE func names:", len(set(n for _,n in hits)))
