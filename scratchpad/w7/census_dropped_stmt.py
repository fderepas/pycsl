import ast, os, sys, collections
HANDLED = {"Assign","AugAssign","Return","While","For","If","Continue","Assert",
           "Raise","AnnAssign","Expr","Try","With","Pass","Break","Delete","Match"}
BLOCK_FIELDS = ("body","orelse","finalbody")

def scan(root):
    hits = collections.Counter()
    detail = collections.defaultdict(list)
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ("__pycache__",".git","attic")]
        for fn in files:
            if not fn.endswith(".py"): continue
            p = os.path.join(dirpath, fn)
            try:
                t = ast.parse(open(p, encoding="utf-8", errors="replace").read())
            except Exception:
                continue
            # any AsyncFunctionDef anywhere
            for n in ast.walk(t):
                if isinstance(n, ast.AsyncFunctionDef):
                    hits["AsyncFunctionDef"] += 1
                    detail["AsyncFunctionDef"].append("%s:%d" % (p, n.lineno))
            # statements inside function bodies (blocks reached by _py_stmts_to_ir)
            for fnode in ast.walk(t):
                if not isinstance(fnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                stack = list(fnode.body)
                while stack:
                    st = stack.pop()
                    name = type(st).__name__
                    if name not in HANDLED:
                        hits[name] += 1
                        detail[name].append("%s:%d" % (p, st.lineno))
                    for f in BLOCK_FIELDS:
                        v = getattr(st, f, None)
                        if isinstance(v, list):
                            stack.extend(x for x in v if isinstance(x, ast.stmt))
                    for h in getattr(st, "handlers", []) or []:
                        stack.extend(h.body)
                    for c in getattr(st, "cases", []) or []:
                        stack.extend(c.body)
    return hits, detail

for root in sys.argv[1:]:
    h, d = scan(root)
    print("== %s ==" % root)
    for k, v in sorted(h.items(), key=lambda kv: -kv[1]):
        print("   %5d  %s   e.g. %s" % (v, k, d[k][0] if d[k] else ""))
    if not h: print("   (none)")
