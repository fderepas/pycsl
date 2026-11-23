#!/bin/bash
# cpy.sh [listfile] : run every probe under /usr/bin/python3 and the venv python, script mode, -B, ulimit'd,
# cwd /tmp (or the probe's cwd field), PYTHONPATH = the --import-path root
PR=/home/fabrice/git/pycsl-u71/scratchpad/u71/probes; L=${1:-/home/fabrice/git/pycsl-u71/scratchpad/u71/tools/probes.lst}
while IFS='|' read -r n x f c; do
  [ -z "$n" ] && continue; case "$n" in \#*) continue;; esac
  ff=$PR/$f; pp=; [ -n "$x" ] && pp="$(dirname "$(dirname "$ff")")/$x"
  case "$n" in r2d-dep|r2r-dep|v2down|*-noX) pp=;; esac
  for py in /usr/bin/python3 /home/fabrice/git/pycsl/.venv/bin/python3; do
    out=$(cd "${c:+$PR/$c}" 2>/dev/null || cd /tmp; [ -z "$c" ] && cd /tmp; PYTHONPATH="$pp" timeout 60 bash -c "ulimit -v 2000000; $py -B $ff" 2>&1 | tail -3 | tr '\n' ' ')
    echo "$n | $py | ${pp:+PYTHONPATH=$pp} | $out"
  done
done < "$L"
