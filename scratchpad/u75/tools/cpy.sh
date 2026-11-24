#!/bin/bash
# cpy.sh <probe-dir>... : run P/prog.py under both interpreters, script mode, -B, ulimit'd; cwd scratchpad/u75/tmp (or `cwd` file)
SP=/home/fabrice/git/pycsl-u75/scratchpad
for k in "$@"; do
  case "$k" in /*) P=$k;; *) P=$SP/$k;; esac
  C=$SP/u75/tmp; [ -f $P/cwd ] && C="$P/$(cat $P/cwd)"
  for py in /usr/bin/python3 /home/fabrice/git/pycsl/.venv/bin/python3; do
    out=$(cd "$C" && timeout 60 bash -c "ulimit -v 2000000; $py -B $P/P/prog.py" 2>&1 | tail -2 | tr '\n' ' ' | cut -c1-160)
    echo "$k [$py] $out"
  done
done
