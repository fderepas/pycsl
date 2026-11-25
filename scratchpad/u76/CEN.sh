#!/bin/bash
# CEN.sh: append real census rows (bin/check-refusal-witness-coverage.py --append-new) in the worktree (cwd = worktree root)
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=/home/fabrice/git/pycsl-u76/scratchpad/u76/tmp
cd /home/fabrice/git/pycsl-u76 || exit 2
.venv/bin/python3 bin/check-refusal-witness-coverage.py --append-new; echo "append rc=$?"
U=/home/fabrice/git/pycsl-u76/scratchpad/u76
$U/p.sh h k1 k2
for n in k4 k6 k7 k9; do for t in h b; do $U/run.sh $t $n --no-proof; done; done
for n in k1 k2 k3 k4 k5 k6 k7 k8 k9; do echo "$n CPython: $(cd $U/c && timeout 60 bash -c "ulimit -v 2000000; python3 -E -s $n.py" 2>&1 | tail -1)"; done
