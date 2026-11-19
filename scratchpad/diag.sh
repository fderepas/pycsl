#!/bin/bash
cd /home/fabrice/git/pycsl
M=src/self-annotate/src/frontend/pure_ast.py
S=/tmp/claude-1000/-home-fabrice-git-pycsl/8f7f6044-5a3d-4979-a728-07c3eb57e115/scratchpad
for m in "$@"; do
  cp $M $S/_pa_bak2.py
  out=$(python3 scratchpad/port.py $m)
  case "$out" in *"ported"*) ;; *) echo "SKIP $m ($out)"; continue;; esac
  r=$(./scratchpad/tc.sh 2>&1)
  if echo "$r" | grep -q "L3-tc GREEN"; then echo "OK   $m";
  else echo "FAIL $m"; echo "$r" | grep -v "^\[\*\]" | tail -3 | sed 's/^/       /'; fi
  cp $S/_pa_bak2.py $M
done
