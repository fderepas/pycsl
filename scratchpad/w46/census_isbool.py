import ast, os, collections
roots = ["src/pycsl", "src/self-annotate/src", "src/pycsl_lib",
         "test-suite/corpus/pycsl-reference", "test-suite/corpus/python-reference", "tests"]
c = collections.Counter(); ex = collections.defaultdict(list)
for root in roots:
    if not os.path.isdir(root): continue
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('.git','__pycache__')]
        for f in sorted(fn):
            if not f.endswith(".py"): continue
            p = os.path.join(dp, f)
            try: t = ast.parse(open(p, encoding="utf-8", errors="replace").read())
            except Exception: continue
            for n in ast.walk(t):
                if not isinstance(n, ast.Compare): continue
                for op, cmp in zip(n.ops, n.comparators):
                    if not isinstance(op, (ast.Is, ast.IsNot)): continue
                    if isinstance(cmp, ast.Constant) and cmp.value in (True, False) \
                            and isinstance(cmp.value, bool):
                        k = ("is not" if isinstance(op, ast.IsNot) else "is") + " " + repr(cmp.value)
                        c[k] += 1
                        if len(ex[k]) < 8: ex[k].append("%s:%d" % (p, n.lineno))
for k, v in c.most_common():
    print("%4d  %s" % (v, k))
    for e in ex[k]: print("        %s" % e)
if not c: print("ZERO occurrences of `is True` / `is False` / `is not True` / `is not False` in any tree")
