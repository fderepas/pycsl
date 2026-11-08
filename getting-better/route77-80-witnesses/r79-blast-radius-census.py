import ast, os, sys, collections
ROOTS = ["test-suite/corpus", "src/self-annotate", "src/pycsl", "src/pycsl_lib"]
BASE = "/home/fabrice/git/pycsl"
tot_init = 0; tot_assign = 0
outside = []   # (file, cls, field, rhs, names_outside)
per_root = collections.Counter()
for R in ROOTS:
    for dp, dn, fn in os.walk(os.path.join(BASE, R)):
        if "__pycache__" in dp: continue
        for f in fn:
            if not f.endswith(".py"): continue
            p = os.path.join(dp, f)
            try: t = ast.parse(open(p, encoding="utf-8", errors="replace").read())
            except Exception: continue
            for cls in [n for n in ast.walk(t) if isinstance(n, ast.ClassDef)]:
                for m in cls.body:
                    if not (isinstance(m, ast.FunctionDef) and m.name == "__init__"): continue
                    tot_init += 1
                    pset = {a.arg for a in m.args.args} | {a.arg for a in m.args.kwonlyargs}
                    pset.discard("self")
                    for st in ast.walk(m):
                        tgt = None
                        if isinstance(st, ast.Assign) and len(st.targets) == 1: tgt = st.targets[0]
                        elif isinstance(st, ast.AnnAssign): tgt = st.target
                        else: continue
                        if not (isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name)
                                and tgt.value.id == "self"): continue
                        if st.value is None: continue
                        tot_assign += 1
                        names = {n.id for n in ast.walk(st.value) if isinstance(n, ast.Name)}
                        # the live capture rule: names non-empty, intersects pset, and subset of pset
                        captured = bool(names) and bool(names & pset) and names <= pset
                        if not captured:
                            out = names - pset
                            outside.append((os.path.relpath(p, BASE), cls.name, tgt.attr,
                                            ast.dump(st.value)[:0] or "", sorted(out)[:4]))
                            per_root[R] += 1
print("__init__ methods scanned      :", tot_init)
print("self.<field> = ... assignments:", tot_assign)
print("NOT captured (route #79 shape):", len(outside))
print("by root:", dict(per_root))
print()
print("--- sample of NOT-captured, by file ---")
c = collections.Counter(o[0] for o in outside)
for f, n in c.most_common(12): print("  %4d  %s" % (n, f))
