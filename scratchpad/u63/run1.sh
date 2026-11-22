#!/bin/bash
# run each failing case with --keep-mlw on the u63 tree; logs in scratchpad/u63/w/*.log
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
cd /home/fabrice/git/pycsl-u63; W=scratchpad/u63/w
r(){ n=$1; shift; PYTHON_CPU_COUNT=4 .venv/bin/python3 src/pycsl/pycsl.py "$@" --keep-mlw > $W/$n.log 2>&1; echo "$n rc=$? $(grep -oE 'Verification (SUCCESS|FAILED)[^.]*' $W/$n.log | tail -1)"; }
r footprint_0 --memory-model hoare $W/footprint_0.py
r footprint_1 --memory-model hoare $W/footprint_1.py
r fresh_globals_0 $W/fresh_globals_0.py
r fresh_globals_1 $W/fresh_globals_1.py
r mutex_invariant_0 --memory-model concurrent --strict-concurrent-checks $W/mutex_invariant_0.py
r mutex_invariant_1 --memory-model concurrent --strict-concurrent-checks $W/mutex_invariant_1.py
r pf0 --import-path $W/pf0 $W/pf0/main.py
r pf1 --import-path $W/pf1 $W/pf1/main.py
r enm --import-path src --verification-image src src/pycsl_lib/enm/__init__.py
r fut --import-path src --verification-image src src/pycsl_lib/fut/__init__.py
