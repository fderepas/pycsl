#!/bin/bash
# job1: run each of the 21 formerly-rejected call-site probes ALONE (head rewriter), then base sweeps
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
U=/home/fabrice/git/pycsl-u56; cd $U || exit 2
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
oom(){ grep oom_kill $EV | grep -v group | awk '{print $2}'; }
O=$U/scratchpad/u56/pr; mkdir -p $O
export PYTHON_CPU_COUNT=2
while read f fn; do
  [ -z "$f" ] && continue
  [ -n "$ONLY" ] && [[ " $ONLY " != *" $fn "* ]] && continue
  o1=$(oom); t0=$SECONDS
  echo "$(date -u) probe $fn" >> $U/progress.txt
  PYTHONHASHSEED=0 timeout 14400 .venv/bin/python3 -W ignore scratchpad/u56/probe_run.py $U scratchpad/u56/emit/$f.mlw $fn > $O/$fn.log 2>&1
  rc=$?; o2=$(oom)
  printf '%s\t%s\trc=%s\t%ss\toom %s->%s\t%s\n' "$f" "$fn" $rc $((SECONDS-t0)) $o1 $o2 "$(grep -E '^RESULT|could not be checked' $O/$fn.log | tr '\n' ' ' | cut -c1-300)" >> $O/summary.tsv
done < $U/scratchpad/u56/fnlist-b.txt
exit 0
echo "$(date -u) base sweeps" >> $U/progress.txt
$U/scratchpad/u56/sweep.sh /home/fabrice/git/pycsl-u56-base $U/scratchpad/u56/sw/base
echo "$(date -u) job1 done" >> $U/progress.txt
