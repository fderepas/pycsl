#!/bin/bash
# CEN2.sh: real census rows for the u76 FAIL witnesses + 9063 (refusal changed), then the rt84 k-probes
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=/home/fabrice/git/pycsl-u76/scratchpad/u76/tmp
U=/home/fabrice/git/pycsl-u76/scratchpad/u76; cd /home/fabrice/git/pycsl-u76 || exit 2
C=test-suite/corpus/pycsl-reference
.venv/bin/python3 $U/cen_rows.py $(ls $C/1051[0-5]_*.py $C/1052[0124]_*.py | sed "s|^|$PWD/|") $PWD/$C/9063_u30_r568_w04_any_receiver_pure_caller.py; echo "cen rc=$?"
$U/p.sh h k1 k2
for n in k4 k6 k7 k9; do for t in h b; do $U/run.sh $t $n --no-proof; done; done
for n in k1 k2 k3 k4 k5 k6 k7 k8 k9; do echo "$n CPython: $(cd $U/c && timeout 60 bash -c "ulimit -v 2000000; python3 -E -s $n.py" 2>&1 | tail -1)"; done
echo CEN2 done
