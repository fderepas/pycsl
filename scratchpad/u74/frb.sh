#!/bin/bash
# frb.sh: the param-frame probe (fr1.py) proved in the BASE tree pycsl-u74b
cd /home/fabrice/git/pycsl-u74b; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=/home/fabrice/git/pycsl-u74/scratchpad/u74/tmp
cp /home/fabrice/git/pycsl-u74/scratchpad/u74/rt/fr1.py /home/fabrice/git/pycsl-u74/scratchpad/u74/rt/frb.py
timeout 900 .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl-u74/scratchpad/u74/rt/frb.py --import-path src/pycsl --keep-mlw > /home/fabrice/git/pycsl-u74/scratchpad/u74/rt/frb.log 2>&1; echo "rc=$?" >> /home/fabrice/git/pycsl-u74/scratchpad/u74/rt/frb.log
