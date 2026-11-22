#!/bin/bash
# CR.sh : real _census_row for the 3 witnesses vs the committed rows; witness full proofs at the final head.
W=/home/fabrice/git/pycsl-u64; L=$W/scratchpad/u64/logs/CR; mkdir -p $L; cd $W
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
.venv/bin/python3 - > $L/rows.tsv <<'PY'
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location("rwc", "bin/check-refusal-witness-coverage.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
C = os.path.join(m.ROOT, "test-suite", "corpus", "pycsl-reference")
for n in sorted(os.listdir(C)):
    if n.startswith(("10340_", "10341_", "10343_")):
        sys.stdout.write(m._census_row(os.path.join(m.ROOT, ".venv", "bin", "python3"), os.path.join(C, n)))
PY
grep -E "^1034[013]_" bin/refusal-witness-census.tsv > $L/committed.tsv
cmp $L/rows.tsv $L/committed.tsv && echo "census rows IDENTICAL to a real _census_row run" || { echo "census rows DIFFER"; diff $L/rows.tsv $L/committed.tsv | cut -c1-300; }
echo "## head $(git rev-parse --short HEAD)"; $W/scratchpad/u64/tools/wit.sh $W $L/pr-head p
