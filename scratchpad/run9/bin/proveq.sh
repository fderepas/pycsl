#!/bin/bash
# proveq.sh <tree> <tag> <mirror-rel>... : sequential driver whole-file mirror proofs, one log per file (oom before/after, tooling fingerprint)
T=$1; TAG=$2; shift 2; O=/home/fabrice/git/pycsl/scratchpad/run9; OP=$(cat $O/oompath)
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; cd $T
for f in "$@"; do b=$(echo $f | tr / _); L=$O/$TAG-$b.log; s=$(date +%s); o1=$(grep oom_kill $OP 2>/dev/null | awk '{print $2}')
  echo "$(date -u +%FT%H:%MZ) START $f" >> $O/$TAG-queue.txt
  env ${PQ_ENV:-HEAVY_PRIO=1 PYTHON_CPU_COUNT=4} /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py src/self-annotate/src/$f --import-path src/pycsl --verification-image src/self-annotate/src > $L 2>&1; rc=$?
  o2=$(grep oom_kill $OP 2>/dev/null | awk '{print $2}')
  echo "$f rc=$rc valid=$(grep -c 'Prover result is: Valid' $L) total=$(grep -c 'Prover result is:' $L) $(grep -oE 'Verification (SUCCESS|FAILED)[^.!]*' $L | tail -1 | tr ' ' _) $(( $(date +%s)-s ))s oom $o1->$o2 tree=$(git rev-parse --short HEAD) $(/home/fabrice/git/pycsl/scratchpad/run9/bin/fp.sh $T)" >> $O/$TAG-proofs.txt
done
echo "$(date -u +%FT%H:%MZ) QUEUE-DONE" >> $O/$TAG-queue.txt
