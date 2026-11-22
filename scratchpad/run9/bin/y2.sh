#!/bin/bash
# wait for rt58's queued PRIO batch (pid given) to start, then run the rest of stream y
while kill -0 $1 2>/dev/null && [ -e /home/fabrice/git/pycsl/scratchpad/heavy/prio.d/$1 ]; do sleep 30; done
cd /home/fabrice/git/pycsl
PQ_ENV="HEAVY_PRIO=1 PYTHON_CPU_COUNT=6" scratchpad/run9/bin/proveq.sh /home/fabrice/git/pycsl-int61 int61y frontend/Module5_IREmitter.py core_ir_semantic.py module6_whyml/functions.py Module6_WhyMLTranspiler.py frontend/Module2_Parser.py pycsl.py frontend/ir_resolve.py frontend/Module1_Ingestor.py frontend/monomorphize.py module6_whyml/types.py errors.py frontend/ConcurrencyChecker.py frontend/Module3_Weaver.py frontend/__init__.py frontend/exec_splice.py frontend/import_classifier.py frontend/ir_inline.py ir_schema.py module6_whyml/expr_ghost_collections.py module6_whyml/expr_ghost_spec_ops.py
