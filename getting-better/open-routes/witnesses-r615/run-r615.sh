#!/bin/bash
# route #615 witness driver.  Usage (through heavy.sh, cwd anywhere):
#   heavy.sh getting-better/open-routes/witnesses-r615/run-r615.sh <tree> <outdir>
# Runs two corpus PASS programs through the FULL pycsl proof (non-vacuity gate on, the default)
# with the why3 wrapper in ./bin prepended to PATH, once per failure mode, and prints one TSV row
# per run: mode, file, rc, final verdict line, count of 'could not be checked' lines.
#   2823 (route #267 control): has a call to a \trusted callee -> exercises BOTH the call-site
#        probe and the per-function probe;  0351: per-function probe only.
# Expected at the BASE (pre-#615): every mode -> rc 0 'Verification SUCCESS' (the dead probe is
# read as 'not vacuous': fail-open).  Expected at HEAD: off -> SUCCESS; kill-pf / exit137-pf /
# ulimit-pf / kill-cs -> rc 1 'Verification FAILED (vacuity could not be checked)'
# (0351 has no call-site probe, so kill-cs is SUCCESS for it at both).
T=${1:?tree}; O=${2:?outdir}; mkdir -p "$O"
W=$(cd "$(dirname "$0")" && pwd)
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
export PATH="$W/bin:$PATH"
cd "$T" || exit 2
C=test-suite/corpus/pycsl-reference
# R615_ONLY=main runs only the main-goal part below.
[ "$R615_ONLY" = main ] || for m in off kill-pf exit137-pf ulimit-pf kill-cs; do
  for f in $C/2823_gen36_r267_trusted_consistent_on_one_branch_control.py $C/0351.py; do
    b=$(basename "$f" .py | cut -c1-4); L="$O/$m-$b.log"
    R615_MODE=$m PYTHONHASHSEED=0 timeout 900 .venv/bin/python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl > "$L" 2>&1; rc=$?
    v=$(grep -oE 'Verification (SUCCESS|FAILED)[^.]*' "$L" | tail -1)
    n=$(grep -c 'could not be checked' "$L")
    echo -e "$m\t$b\trc=$rc\t$v\tcnbc=$n"
  done
done
# main-goal phase (route #615 part 2): off = the honest verdict (FAIL, a timeout), kill-main = the
# full-file why3 run killed after its first record.
for m in off kill-main; do
  f=$W/w615_main_kill_ctl.py; L="$O/$m-w615main.log"
  R615_MODE=$m PYTHONHASHSEED=0 timeout 900 .venv/bin/python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl > "$L" 2>&1; rc=$?
  v=$(grep -oE 'Verification (SUCCESS|FAILED)[^.]*' "$L" | tail -1)
  n=$(grep -c 'Prover result is' "$L")
  echo -e "$m\tw615main\trc=$rc\t$v\tgoals=$n"
done
