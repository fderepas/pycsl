#!/bin/bash
# CR.sh <tree> : the real _census_row (cwd-relative paths) for the u72 FAIL witnesses 10450-10456 and the
# u70 rows 10420-10423 whose outcome u72 changes. cwd = tree root.
W=$1; cd $W || exit 2; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
.venv/bin/python3 - <<'PY'
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location("rwc", "bin/check-refusal-witness-coverage.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
C = os.path.join("test-suite", "corpus", "pycsl-reference")
for n in sorted(os.listdir(C)):
    if n[:6] in ("10420_", "10421_", "10422_", "10423_") or n[:6] in tuple(f"{i}_" for i in range(10450, 10457)):
        sys.stdout.write(m._census_row(os.path.join(m.ROOT, ".venv", "bin", "python3"), os.path.join(C, n)))
PY
