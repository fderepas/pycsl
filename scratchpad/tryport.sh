#!/bin/bash
cd /home/fabrice/git/pycsl
M=src/self-annotate/src/frontend/pure_ast.py
for m in "$@"; do
  cp $M /tmp/claude-1000/-home-fabrice-git-pycsl/8f7f6044-5a3d-4979-a728-07c3eb57e115/scratchpad/_pa_bak.py
  out=$(python3 scratchpad/port.py $m)
  case "$out" in *"ported"*) ;; *) echo "SKIP $m ($out)"; continue;; esac
  r=$(./scratchpad/tc.sh 2>&1 | tail -3)
  if echo "$r" | grep -q "L3-tc GREEN"; then echo "OK   $m"
  else echo "FAIL $m :: $(echo "$r" | tail -2 | head -1)"; cp /tmp/claude-1000/-home-fabrice-git-pycsl/8f7f6044-5a3d-4979-a728-07c3eb57e115/scratchpad/_pa_bak.py $M; fi
done
python3 bin/count-trusted-directives.py | head -1
