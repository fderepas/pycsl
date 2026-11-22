#!/bin/bash
# run #9 input: whole-file proofs of small mirror files under u62's corrected probe tooling (int75), LOW, sequential
cd /home/fabrice/git/pycsl
PQ_ENV="HEAVY_LOW=1 PYTHON_CPU_COUNT=2" bash scratchpad/run9/bin/proveq.sh /home/fabrice/git/pycsl-int75 r9diag \
  errors.py frontend/__init__.py frontend/module_collect.py frontend/exec_splice.py frontend/import_classifier.py \
  module6_whyml/abstract_ops.py module6_whyml/scc.py module6_whyml/identifiers.py module6_whyml/struct_format.py \
  proof_axiom_allowlist.py frontend/ConcurrencyChecker.py proof2why3/ir.py module6_whyml/irx.py proof2why3/sertop.py
