#!/bin/bash
# slowplanes.sh: single-underscore mirror emission + six planes run individually, full output kept.
T=/home/fabrice/git/pycsl-lvW; O=$T/scratchpad/lvW/planes; mkdir -p $O; E=$T/scratchpad/lvW/planes/emit_dir; mkdir -p $E
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; cd $T
OOM=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
echo "$(date -u +%FT%TZ) emit start oom=$(grep oom_kill $OOM)" >> $O/summary.txt
while IFS= read -r _src; do
  _rel="${_src#"$T/src/self-annotate/src/"}"; _name="${_rel%.py}"; _name="${_name//\//_}"
  rm -f "${_src%.py}.mlw"
  PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py "$_src" --import-path "$T/src/pycsl" --no-proof --keep-mlw >/dev/null 2>&1
  [ -f "${_src%.py}.mlw" ] && mv "${_src%.py}.mlw" "$E/$_name.mlw"
done < <(find "$T/src/self-annotate/src" -name '*.py' | sort)
echo "$(date -u +%FT%TZ) emitted $(ls $E/*.mlw | wc -l)" >> $O/summary.txt
for p in check-assigns-writes-survival.py check-trusted-frame-honesty.py check-getattr-erasure.py check-mirror-coverage.py check-vacuous-drivers.py check-claim-vacuity.py; do
  s=$(date +%s)
  case $p in check-assigns-writes-survival.py|check-trusted-frame-honesty.py) python3 bin/$p --emit-dir $E > $O/${p%.py}.log 2>&1 ;;
             *) python3 bin/$p > $O/${p%.py}.log 2>&1 ;; esac
  rc=$?; echo "$(date -u +%FT%TZ) $p rc=$rc wall=$(( $(date +%s)-s ))s oom=$(grep oom_kill $OOM)" >> $O/summary.txt
done
