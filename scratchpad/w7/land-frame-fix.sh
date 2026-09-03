#!/bin/bash
# (#34 -> #35) Turnkey driver for landing the frame-preservation fix.
#   1. apply the patch,
#   2. re-emit + L3-tc the mirror (must stay 53/53),
#   3. re-verify the 50 changed corpus files (must be 50/50 after the two repairs
#      the patch already carries),
#   4. re-prove the ~10 mirror files whose emission changes — TWO AT A TIME, no more.
# A preservation clause that will not prove is a LIVE VICTIM: a converted, proved mirror
# method whose declared frame is a lie. Repair it with an honest `#@ assigns`, exactly as
# `frontend/ConcurrencyChecker._walk_body`, corpus 0721 and corpus 0723 were repaired.
set -u
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/w7/tmp
MIRRORS="frontend/pure_ast.py frontend/Module5_IREmitter.py frontend/Module2_Parser.py \
frontend/Module3_Weaver.py module6_whyml/statements.py module6_whyml/expressions.py \
frontend/ConcurrencyChecker.py frontend/ir_inline.py audit_proof_reverify.py \
Module6_WhyMLTranspiler.py"
echo "step 1: git apply scratchpad/w7/frame-preservation.patch"
echo "step 2: bash scratchpad/w5/l3sweep.sh <out>        # expect 53/53"
echo "step 3: bash scratchpad/w7/verify_changed.sh       # expect PROVE OK: 50"
echo "step 4: for each of these, scratchpad/w7/pr.sh src/self-annotate/src/<f> <tag>:"
for m in $MIRRORS; do echo "    $m"; done
