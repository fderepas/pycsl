#!/bin/bash
# job4: corrected w616 witness (base + head), then the extra probes (types/functions) while before 10:30Z
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
U=/home/fabrice/git/pycsl-u56; cd $U || exit 2
G=$U/scratchpad/u56/gates; W=$U/getting-better/open-routes/witnesses-r616
$W/run-r616.sh /home/fabrice/git/pycsl-u56-base $G/wit2-base > $G/wit2-base.tsv 2>&1; echo "wit2-base rc=$?" >> $G/status.txt
$W/run-r616.sh $U $G/wit2-head > $G/wit2-head.tsv 2>&1; echo "wit2-head rc=$?" >> $G/status.txt
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
oom(){ grep oom_kill $EV | grep -v group | awk '{print $2}'; }
O=$U/scratchpad/u56/pr; export PYTHON_CPU_COUNT=2
while read f fn; do
  [ "$(date -u +%H%M)" \> "1030" ] && { echo "$(date -u) job4 skip $fn (time box)" >> $U/progress.txt; continue; }
  o1=$(oom); t0=$SECONDS; echo "$(date -u) job4 probe $fn" >> $U/progress.txt
  PYTHONHASHSEED=0 timeout 2400 .venv/bin/python3 -W ignore scratchpad/u56/probe_run.py $U scratchpad/u56/emit/$f.mlw $fn > $O/$fn.log 2>&1
  rc=$?; o2=$(oom)
  printf '%s\t%s\trc=%s\t%ss\toom %s->%s\t%s\n' "$f" "$fn" $rc $((SECONDS-t0)) $o1 $o2 "$(grep -E '^RESULT|could not be checked' $O/$fn.log | tr '\n' ' ' | cut -c1-300)" >> $O/summary.tsv
done < <(grep -E "split_tuple_type|types__? ?typeinferencemixin___first|refine_tuple|parse_mixin" $U/scratchpad/u56/fnlist-c.txt)
echo "$(date -u) job4 done" >> $U/progress.txt
