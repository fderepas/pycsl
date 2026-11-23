#!/bin/bash
# FP.sh : full proofs (p.sh: cwd = tree root, PYTHON_CPU_COUNT=2, timeout 3600 per file) of rt75's
# c01 / c12 / c12b / c13 / c19 / c21 and the witnesses 10360-10363, at base (pycsl-u65b) and head (pycsl-u65).
W=/home/fabrice/git/pycsl-u65; P=$W/scratchpad/u65/probes; C=$W/test-suite/corpus/pycsl-reference; L=$W/scratchpad/u65/logs/FP
F="$P/c01_control.py $P/c12_mutrec_first_vacuous.py $P/c12b_norec_control.py $P/c13_lemma_vacuous.py $P/c19_exempt_mangle_clash.py $P/c21_mangle_clash_control.py $P/c22_rebind_noreturn_then_vacuous.py $(ls $C/1036[0-4]_*.py | tr '\n' ' ')"
for f in $F; do ls $f >/dev/null || exit 3; done
echo "FP start $(date -u) head=$(git -C $W log --oneline -1 | cut -c1-9)"
bash $W/scratchpad/u65/tools/p.sh $W $L/head -- $F | sed 's/^/[head] /'
bash $W/scratchpad/u65/tools/p.sh /home/fabrice/git/pycsl-u65b $L/base -- $F | sed 's/^/[base] /'
echo "FP end $(date -u)"
