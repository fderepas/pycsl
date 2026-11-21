import importlib.util, sys, os
spec = importlib.util.spec_from_file_location("de", "bin/check-directive-enforcement.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
out = "scratchpad/u63/w"
for tbl in ("CASES", "ASSUMPTION_CASES"):
    for k, v in getattr(m, tbl).items():
        if k not in ("footprint", "fresh_globals", "mutex_invariant", "propagate_frame"): continue
        print(tbl, k, type(v), len(v) if isinstance(v, tuple) else "")
        for i, x in enumerate(v if isinstance(v, tuple) else [v]):
            if isinstance(x, str):
                open(f"{out}/{k}_{i}.py", "w").write(x)
            else:
                print("  item", i, repr(x)[:200])
v = m.ASSUMPTION_CASES["propagate_frame"]
for i in (0, 1):
    d = f"{out}/pf{i}"; os.makedirs(d, exist_ok=True)
    for rel, body in v[i].items(): open(os.path.join(d, rel), "w").write(body)
print(m._MAIN)
