import ast, os, sys, collections
roots = ["src/pycsl", "src/self-annotate/src", "src/pycsl_lib",
         "test-suite/corpus/pycsl-reference", "test-suite/corpus/python-reference"]
cnt = collections.Counter(); ex = collections.defaultdict(list)
class V(ast.NodeVisitor):
    def __init__(s, p): s.p = p; s.stmt_exprs = set(); s.ann = set()
def classify(tree, path):
    # positions where `...` is NOT a value expression
    stmt_expr_ids = set()
    ann_ids = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and n.value.value is Ellipsis:
            stmt_expr_ids.add(id(n.value))
        for fld in ("annotation", "returns"):
            a = getattr(n, fld, None)
            if a is not None:
                for m in ast.walk(a):
                    ann_ids.add(id(m))
        if isinstance(n, ast.AnnAssign) and n.annotation is not None:
            for m in ast.walk(n.annotation):
                ann_ids.add(id(m))
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and n.value is Ellipsis:
            if id(n) in stmt_expr_ids: k = "STUB-BODY (bare stmt)"
            elif id(n) in ann_ids:     k = "ANNOTATION"
            else:                      k = "*** VALUE POSITION ***"
            cnt[k] += 1
            if len(ex[k]) < 6: ex[k].append("%s:%d" % (path, n.lineno))
for root in roots:
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('.git','__pycache__')]
        for f in fn:
            if not f.endswith(".py"): continue
            p = os.path.join(dp, f)
            try: t = ast.parse(open(p, encoding="utf-8", errors="replace").read())
            except Exception: continue
            classify(t, p)
for k, c in cnt.most_common():
    print("%5d  %s" % (c, k))
    for e in ex[k]: print("         %s" % e)
