#!/usr/bin/env python3
"""remeasure_census.py <pattern>... : re-run (through the coverage tool's own `_census_row`) every census row
whose message matches one of the given substrings, and every row of a witness listed with --files; rewrite them in place."""
import importlib.util, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("rwc", os.path.join(ROOT, "bin", "check-refusal-witness-coverage.py"))
rwc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rwc)
pats = sys.argv[1:]
py = os.path.join(ROOT, ".venv", "bin", "python3")
corpus = os.path.join(ROOT, "test-suite", "corpus")
paths = {}
for d, _, fs in os.walk(corpus):
    for f in fs:
        if f.endswith(".py"):
            paths.setdefault(f, os.path.join(d, f))
lines = open(rwc.CENSUS, encoding="utf-8").read().splitlines(True)
out, changed = [], []
for l in lines:
    cols = l.rstrip("\n").split("\t")
    if not l.startswith("#") and len(cols) >= 3 and any(p in cols[2] for p in pats) and cols[0] in paths:
        nl = rwc._census_row(py, paths[cols[0]])
        if nl != l:
            changed.append(cols[0])
        out.append(nl)
    else:
        out.append(l)
open(rwc.CENSUS, "w", encoding="utf-8").write("".join(out))
print("re-measured; changed rows:", len(changed), " ".join(changed))
