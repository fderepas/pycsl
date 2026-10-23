#!/bin/bash
# Route-#35 re-proof queue: 16 mirror files, TWO concurrent, longest first.
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
Q=(
  "module6_whyml/expressions.py:r35_expressions"
  "frontend/Module5_IREmitter.py:r35_m5ir"
  "frontend/pure_ast.py:r35_pureast"
  "Module6_WhyMLTranspiler.py:r35_m6t"
  "module6_whyml/statements.py:r35_statements"
  "module6_whyml/functions.py:r35_functions"
  "module6_whyml/stmt_control_flow.py:r35_scf"
  "module6_whyml/types.py:r35_types"
  "frontend/Module2_Parser.py:r35_m2p"
  "frontend/Module3_Weaver.py:r35_m3w"
  "module6_whyml/preamble.py:r35_preamble"
  "module6_whyml/auto_trust.py:r35_autotrust"
  "module6_whyml/scc.py:r35_scc"
  "proof2why3/sertop.py:r35_sertop"
  "proof2why3/crosscheck.py:r35_crosscheck"
  "frontend/desugar.py:r35_desugar"
)
for item in "${Q[@]}"; do
  f="src/self-annotate/src/${item%%:*}"
  n="${item##*:}"
  while [ "$(jobs -rp | wc -l)" -ge 2 ]; do sleep 20; done
  bash scratchpad/w7/pr2.sh "$f" "$n" 28800 &
  echo "$(date -u +%H:%M) started $n" >> scratchpad/w7/proofs/queue45.progress
done
wait
echo "$(date -u +%H:%M) QUEUE DONE" >> scratchpad/w7/proofs/queue45.progress
touch scratchpad/w7/proofs/QUEUE45_DONE
