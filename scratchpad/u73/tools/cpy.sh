#!/bin/bash
# cpy.sh <listfile> : run every probe of an r.sh list under /usr/bin/python3 and the venv python, script mode,
# -B, ulimit -v 2000000, cwd = the probe's cwd field (else /tmp), PYTHONPATH = the --import-path entries joined.
PR=/home/fabrice/git/pycsl-u73/scratchpad/u73/probes; L=$1
while IFS='|' read -r n x f c; do
  [ -z "$n" ] && continue; case "$n" in \#*) continue;; esac
  pp=$(echo "${x//@P@/$PR}" | grep -oE -- "--import-path [^ ]+" | cut -d' ' -f2 | paste -sd:)
  for py in /usr/bin/python3 /home/fabrice/git/pycsl/.venv/bin/python3; do
    out=$(if [ -n "$c" ]; then cd "$PR/$c"; else cd /tmp; fi; PYTHONPATH="$pp" timeout 60 bash -c "ulimit -v 2000000; $py -B $PR/$f" 2>&1 | tail -2 | tr '\n' ' ' | cut -c1-200)
    echo "$n | $(basename $(dirname $(dirname $py))) | ${pp:+PYTHONPATH=$pp} | $out"
  done
done < "$L"
