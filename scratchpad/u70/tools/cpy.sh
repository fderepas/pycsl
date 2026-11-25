#!/bin/bash
# cpy.sh [listfile] : every probe under the system and the venv CPython, script mode, -B, ulimit'd, cwd /tmp
PR=/home/fabrice/git/pycsl-u70/scratchpad/u70/probes; L=${1:-/home/fabrice/git/pycsl-u70/scratchpad/u70/tools/p.lst}
while IFS='|' read -r n f; do
  [ -z "$n" ] && continue; case "$n" in \#*) continue;; esac
  for py in /usr/bin/python3 /home/fabrice/git/pycsl/.venv/bin/python3; do
    out=$(cd /tmp && timeout 60 bash -c "ulimit -v 2000000; $py -B $PR/$f" 2>&1 | tail -2 | tr '\n' ' ')
    echo "$n | $py | $out"
  done
done < "$L"
