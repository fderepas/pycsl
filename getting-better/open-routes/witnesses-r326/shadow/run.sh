#!/bin/bash
# NOTE pycsl runs from /home/fabrice/git/pycsl-r310; extra args via PYCSL_ARGS
# run.sh <probe.py...> : CPython check + pycsl proof via heavy.sh
T=/home/fabrice/git/pycsl
D=/home/fabrice/git/pycsl/scratchpad/rt19/shadow
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
for f in "$@"; do
  b=$(basename $f .py)
  cpy=$(cd $D && $T/.venv/bin/python3 $b.py >/dev/null 2>&1; echo $?)
  out=$D/$b.out
  (cd /home/fabrice/git/pycsl && /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py $D/$b.py --import-path src/pycsl $PYCSL_ARGS) > $out 2>&1
  rc=$?
  last=$(grep -E "proven|FAILED|Error|error|refus|REFUS|Unknown|Timeout" $out | tail -1 | cut -c1-140)
  flag=""; [ $rc = 0 ] && [ $cpy != 0 ] && flag="  <<<<< FALSE PROOF"
  echo "$b cpy=$cpy pycsl=$rc :: $last$flag"
  echo "$(date -u +%FT%TZ) $b cpy=$cpy pycsl=$rc$flag" >> $D/progress.txt
done
