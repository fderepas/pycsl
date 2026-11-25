#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u75/scratchpad/u75/tmp; mkdir -p "$TMPDIR"
# PB.sh <tree> <tag> : --no-proof of every probe (D lists + u71all r-list) and witness, then a FULL proof of
# every probe / witness whose --no-proof reached SUCCESS (hoare, PYTHON_CPU_COUNT=2, timeout 3600).
U=/home/fabrice/git/pycsl-u75/scratchpad/u75; T=$1; L=$U/logs/PB-$2; mkdir -p $L
echo "## PB $2 $T $(git -C $T rev-parse --short HEAD) start $(date -u)"
for l in rt83 rt81 u73 u75; do bash $U/tools/D.sh q $T $L/qd $(cat $U/tools/$l.lst) | sed "s/^/[q:$l] /"; done > $L/q.txt
bash $U/tools/r.sh q $T $L/qp $U/tools/u71all.lst | sed 's/^/[q:p] /' >> $L/q.txt
bash $U/tools/wit.sh q $T $L/qw | sed 's/^/[q:w] /' >> $L/q.txt
cat $L/q.txt
S=$(grep "Verification SUCCESS" $L/q.txt | grep "^\[q:\(rt83\|rt81\|u73\|u75\)\]" | awk '{print $2}')
[ -n "$S" ] && bash $U/tools/D.sh p $T $L/pd $S | sed 's/^/[p:d] /'
grep "Verification SUCCESS" $L/q.txt | grep "^\[q:p\]" | awk '{print $2}' > $L/plist.txt
awk -F"|" "NR==FNR{s[\$1]=1; next} (\$1 in s)" $L/plist.txt $U/tools/u71all.lst > $L/plist.lst
bash $U/tools/r.sh p $T $L/pp $L/plist.lst | sed 's/^/[p:p] /'
bash $U/tools/wit.sh p $T $L/pw | sed 's/^/[p:w] /'
echo "## PB $2 end $(date -u)"
