#!/bin/bash
# m1pre.sh : corpus sweep of int61 now, MOVED set vs the L9 sweep, full proofs of the moved files (expected verdicts checked later)
O=/home/fabrice/git/pycsl/scratchpad/run9/m1pre; mkdir -p $O; H=/home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh
T=/home/fabrice/git/pycsl-int61; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
(cd $T && HEAVY_PRIO=1 $H bin/byte-diff-sweep.sh $O/bd > $O/bd.log 2>&1)
python3 /home/fabrice/git/pycsl/bin/byte-diff-compare.py /home/fabrice/git/pycsl/scratchpad/run9/v57/bd-int $O/bd > $O/cmp-root.txt 2>&1
python3 /home/fabrice/git/pycsl/bin/byte-diff-compare.py /home/fabrice/git/pycsl/scratchpad/run9/v57/bd-int/pyref $O/bd/pyref > $O/cmp-pyref.txt 2>&1
for f in $O/bd/*.mlw; do b=$(basename $f); [ -f /home/fabrice/git/pycsl/scratchpad/run9/v57/bd-int/$b ] && ! cmp -s $f /home/fabrice/git/pycsl/scratchpad/run9/v57/bd-int/$b && echo ${b%.mlw}; done > $O/moved.txt
for b in $(cat $O/moved.txt); do ls $T/test-suite/corpus/pycsl-reference/$b.py; done > $O/moved-src.txt 2>/dev/null
HEAVY_PRIO=1 $H /home/fabrice/git/pycsl/scratchpad/run9/bin/full.sh $T $(cat $O/moved-src.txt) > $O/full.tsv 2>&1
echo DONE > $O/done.txt
