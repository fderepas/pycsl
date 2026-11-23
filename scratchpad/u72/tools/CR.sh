#!/bin/bash
# CR.sh <tree> <out.tsv> <witness-basename>... : the real _census_row (cwd-relative paths, as the committed rows)
# for each named FAIL witness. cwd = tree root.
W=$1; OUT=$(realpath -m $2); shift 2; cd $W || exit 2; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
.venv/bin/python3 - "$@" > $OUT <<'PY'
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location("rwc", "bin/check-refusal-witness-coverage.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
C = os.path.join("test-suite", "corpus", "pycsl-reference")
for n in sys.argv[1:]:
    sys.stdout.write(m._census_row(os.path.join(m.ROOT, ".venv", "bin", "python3"), os.path.join(C, n)))
PY
echo "CR rc=$? rows=$(wc -l < $OUT)"
