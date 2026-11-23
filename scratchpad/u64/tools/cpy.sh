#!/bin/bash
# cpy.sh <prog.py> [PYTHONPATH] : run prog under both interpreters, script mode, -B, ulimit'd, cwd /tmp
p=$1; pp=$2
for py in /usr/bin/python3 /home/fabrice/git/pycsl/.venv/bin/python3; do
  echo "== $py $p ${pp:+PYTHONPATH=$pp}"
  (cd /tmp && PYTHONPATH="$pp" timeout 60 bash -c "ulimit -v 2000000; $py -B $p" 2>&1 | tail -8)
done
