#!/bin/bash
# bat2.sh : 10251 (frame claim dropped) full proofs x3 models at HEAD of the lvZ tree; cwd = tree root
O=/home/fabrice/git/pycsl-lvZ/scratchpad/lvZ/bat2; mkdir -p $O
OOM=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
oom(){ grep oom_kill $OOM | awk '{print $2}'; }
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
cd /home/fabrice/git/pycsl-lvZ || exit 2
echo "head=$(git rev-parse --short HEAD)" > $O/wit.tsv
f=test-suite/corpus/pycsl-reference/10251_r617_imported_name_of_str_ctl.py
for mm in hoare typed store; do lg=$O/wit.10251.$mm.log; o0=$(oom)
  timeout 1200 .venv/bin/python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl --memory-model $mm > $lg 2>&1; rc=$?
  echo -e "10251\t$mm\trc=$rc\toom=$o0->$(oom)\t$(grep -oE 'Verification SUCCESS|Verification FAILED|PYCSL-R[0-9]+[A-Z0-9-]*|L3-tc ✗' $lg | head -1)\tvalid=$(grep -c 'Prover result is: Valid' $lg)/$(grep -c 'Prover result is:' $lg)" >> $O/wit.tsv
done
echo DONE >> $O/wit.tsv
