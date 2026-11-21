#!/usr/bin/env bash
# Prove exactly the mirrors whose emission MOVED (lesson (r): emission-diff before proof sweep).
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
WT="$1"       # worktree root
cd "$WT"
FILES=(
  src/self-annotate/src/frontend/Module2_Parser.py
  src/self-annotate/src/frontend/Module3_Weaver.py
  src/self-annotate/src/frontend/Module5_IREmitter.py
  src/self-annotate/src/frontend/exec_splice.py
  src/self-annotate/src/frontend/module_collect.py
  src/self-annotate/src/frontend/monomorphize.py
  src/self-annotate/src/frontend/pure_ast.py
  src/self-annotate/src/module6_whyml/expressions.py
  src/self-annotate/src/module6_whyml/functions.py
  src/self-annotate/src/module6_whyml/statements.py
  src/self-annotate/src/proof2why3/parser.py
  src/self-annotate/src/proof2why3/sertop.py
  src/self-annotate/src/pycsl.py
)
pass=0; fail=0
for f in "${FILES[@]}"; do
  t0=$(date +%s)
  out=$(timeout 9000 python3 src/pycsl/pycsl.py "$f" --import-path "$WT/src/pycsl" 2>&1)
  t1=$(date +%s)
  if echo "$out" | grep -q "Verification SUCCESS"; then
    echo "[PASS] $f ($((t1-t0))s)"; pass=$((pass+1))
  else
    echo "[FAIL] $f ($((t1-t0))s)"; echo "$out" | tail -12; fail=$((fail+1))
  fi
done
echo "MIRROR-PROOF: $pass passed / $fail failed"
echo "MIRROR-PROOF-DONE $(date -u +%H:%M:%SZ)"
