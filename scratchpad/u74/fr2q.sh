#!/bin/bash
# fr2q.sh: the param-frame probe (fr2.py) proved in the BASE tree pycsl-u74b
cd /home/fabrice/git/pycsl-u74b; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=/home/fabrice/git/pycsl-u74/scratchpad/u74/tmp
cp /home/fabrice/git/pycsl-u74/scratchpad/u74/rt/fr2.py /home/fabrice/git/pycsl-u74/scratchpad/u74/rt/fr2q.py
timeout 900 .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl-u74/scratchpad/u74/rt/fr2q.py --import-path src/pycsl --keep-mlw --no-proof > /home/fabrice/git/pycsl-u74/scratchpad/u74/rt/fr2q.log 2>&1; echo "rc=$?" >> /home/fabrice/git/pycsl-u74/scratchpad/u74/rt/fr2q.log
