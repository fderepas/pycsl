#!/bin/bash
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=/home/fabrice/git/pycsl-u77/scratchpad/u77/tmp
U=/home/fabrice/git/pycsl-u77/scratchpad/u77
for a in h:/home/fabrice/git/pycsl-u77 b:/home/fabrice/git/pycsl-u77b; do tag=${a%%:*}; T=${a#*:}; cd $T
  .venv/bin/python3 src/pycsl/pycsl.py $U/wit/$tag/src/10530_u77b1_float_field_pyval_self_eq_float_finite_assumed.py --import-path $U/wit/$tag/src --no-proof --soundness-report > $U/wit/$tag/10530.report.log 2>&1; echo "rc=$?" >> $U/wit/$tag/10530.report.log
done; echo QDONE
