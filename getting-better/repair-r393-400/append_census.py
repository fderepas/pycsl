#!/usr/bin/env python3
"""append_census.py FILE... : append the coverage tool's own `_census_row` for each given expected-FAIL witness
that has no row yet (a targeted --append-new: the base tree already lacks rows for 327 older witnesses)."""
import importlib.util, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("rwc", os.path.join(ROOT, "bin", "check-refusal-witness-coverage.py"))
rwc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rwc)
have = {r[0] for r in (rwc.census() or [])}
py = os.path.join(ROOT, ".venv", "bin", "python3")
done = []
with open(rwc.CENSUS, "a", encoding="utf-8") as fh:
    for f in sys.argv[1:]:
        if os.path.basename(f) in have:
            continue
        fh.write(rwc._census_row(py, f)); fh.flush(); done.append(os.path.basename(f))
print("appended %d row(s): %s" % (len(done), ", ".join(done)))
