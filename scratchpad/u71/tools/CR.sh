#!/bin/bash
# CR.sh : real _census_row for witnesses 10435-10438 (cwd-relative path, as the committed rows), printed to stdout
W=/home/fabrice/git/pycsl-u71; cd $W; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
.venv/bin/python3 - <<'PY'
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location("rwc", "bin/check-refusal-witness-coverage.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
C = os.path.join("test-suite", "corpus", "pycsl-reference")
for n in sorted(os.listdir(C)):
    if n[:6] in ("10435_", "10436_", "10437_", "10438_"):
        sys.stdout.write(m._census_row(os.path.join(m.ROOT, ".venv", "bin", "python3"), os.path.join(C, n)))
PY
