# cen_rows.py <file...>: append the REAL census row (bin/check-refusal-witness-coverage.py::_census_row) of each named witness
import importlib.util, os, sys
ROOT = "/home/fabrice/git/pycsl-u77h"
spec = importlib.util.spec_from_file_location("rwc", os.path.join(ROOT, "bin", "check-refusal-witness-coverage.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
have = {r[0] for r in (m.census() or [])}
rows = []
for f in sys.argv[1:]:
    if os.path.basename(f) in have:
        print("skip (has row)", f); continue
    r = m._census_row(sys.executable, f); rows.append(r); print(r, end="")
with open(m.CENSUS, "a", encoding="utf-8") as fh:
    fh.writelines(rows)
