#!/bin/bash
# run-r616.sh <tree> <outdir> : full pycsl proof (vacuity gate on, the default) of the #616 witness and
# of corpus 2823 (#267 control), under R616_MODE=off and reject-cs. Prints mode, file, rc, verdict,
# number of call-site "could not be checked" lines.
T=${1:?tree}; O=${2:?outdir}; mkdir -p "$O"
W=$(cd "$(dirname "$0")" && pwd)
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
export PATH="$W/bin:$PATH"
cd "$T" || exit 2
C=test-suite/corpus/pycsl-reference
for m in off reject-cs; do
  for f in $W/w616_paren_string.py $C/2823_gen36_r267_trusted_consistent_on_one_branch_control.py; do
    b=$(basename "$f" .py | cut -c1-4); L="$O/$m-$b.log"
    R616_MODE=$m PYTHONHASHSEED=0 timeout 900 .venv/bin/python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl > "$L" 2>&1; rc=$?
    v=$(grep -oE 'Verification (SUCCESS|FAILED)[^.]*' "$L" | tail -1)
    n=$(grep -c 'call-site probe .*could not be checked' "$L")
    echo -e "$m\t$b\trc=$rc\t$v\tcs-cnbc=$n"
  done
done
