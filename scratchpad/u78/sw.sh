#!/bin/bash
# sw.sh: corpus root + pyref + mirror emission sweeps, base pycsl-u78b (detached run9-u77) then head pycsl-u78, each with cwd = its tree root; then compares.
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
U=/home/fabrice/git/pycsl-u78/scratchpad/u78; export PYTHON_CPU_COUNT=2 TMPDIR=$U/tmp
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
# (time box) witnesses + census rows first
bash $U/wit.sh
cd /home/fabrice/git/pycsl-u78 && .venv/bin/python3 $U/cen_rows.py test-suite/corpus/pycsl-reference/1054[0-5]_*.py > $U/logs/CEN.out 2>&1; echo "cen rc=$?"
for a in base:/home/fabrice/git/pycsl-u78b head:/home/fabrice/git/pycsl-u78; do tag=${a%%:*}; T=${a#*:}; cd $T || exit 2
  echo "$tag start $(date -u) $(git log --oneline -1 | cut -c1-10) $(grep oom_kill $EV)"
  rm -rf "/home/fabrice/git/pycsl-u78/scratchpad/u78/sw/$tag"; mkdir -p $U/sw/$tag
  bash bin/byte-diff-sweep.sh $U/sw/$tag/bd > $U/sw/$tag/bd.log 2>&1; echo "$tag bd rc=$? $(grep -E '^emitted|emitted [0-9]+ of' $U/sw/$tag/bd.log | tr '\n' ' ')"
  bash bin/mirror-emit-sweep.sh $U/sw/$tag/mir > $U/sw/$tag/mir.log 2>&1; echo "$tag mir rc=$? $(tail -1 $U/sw/$tag/mir.log)"
  git status --short src | head -3
done
cd /home/fabrice/git/pycsl-u78
python3 bin/byte-diff-compare.py $U/sw/base/bd $U/sw/head/bd --min-files 3000 > $U/sw/C-root.txt 2>&1; echo "compare root rc=$? $(tail -2 $U/sw/C-root.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $U/sw/base/bd/pyref $U/sw/head/bd/pyref --min-files 2000 > $U/sw/C-pyref.txt 2>&1; echo "compare pyref rc=$? $(tail -2 $U/sw/C-pyref.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $U/sw/base/mir $U/sw/head/mir --min-files 45 > $U/sw/C-mir.txt 2>&1; echo "compare mir rc=$? $(tail -2 $U/sw/C-mir.txt | tr '\n' ' ')"
diff -rq $U/sw/base/mir $U/sw/head/mir > $U/sw/diffrq-mir.txt 2>&1; echo "diff -rq mir lines $(wc -l < $U/sw/diffrq-mir.txt)"
echo "sw end $(date -u) $(grep oom_kill $EV)"
echo SWEEPS-DONE
# (chained in the same heavy job to avoid re-queueing; time box) witnesses, census rows, gates
bash $U/G.sh
echo SWDONE
