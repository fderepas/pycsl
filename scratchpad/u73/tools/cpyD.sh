#!/bin/bash
# cpyD.sh <probe-dir-rel>... : CPython (/usr/bin/python3 and venv), script mode, -B, ulimit -v 2000000;
# PYTHONPATH from `pp` (@P = probe dir), cwd from `cwd` else /tmp
PR=/home/fabrice/git/pycsl-u73/scratchpad/u73/probes
for k in "$@"; do P=$PR/$k
  pp=""; [ -f $P/pp ] && pp=$(sed "s#@P#$P#g" $P/pp)
  C=/tmp; [ -f $P/cwd ] && C="$P/$(cat $P/cwd)"
  for py in /usr/bin/python3 /home/fabrice/git/pycsl/.venv/bin/python3; do
    out=$(cd "$C" && PYTHONPATH="$pp" timeout 60 bash -c "ulimit -v 2000000; $py -B $P/P/prog.py" 2>&1 | tail -2 | tr '\n' ' ' | cut -c1-200)
    echo "$k | $(basename $(dirname $(dirname $py))) | ${pp:+PYTHONPATH=$pp} | $out"
  done
done
