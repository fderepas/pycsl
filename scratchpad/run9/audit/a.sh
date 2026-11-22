#!/bin/bash
# open() audit of one whole-file mirror proof (main repo tree, L19 tooling): every file opened by pycsl.py and all children
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; cd /home/fabrice/git/pycsl; O=/home/fabrice/git/pycsl/scratchpad/run9/audit
PYTHON_CPU_COUNT=2 strace -f -qq -e trace=open,openat,execve,stat,newfstatat,access -o $O/trace.txt .venv/bin/python3 src/pycsl/pycsl.py src/self-annotate/src/frontend/module_collect.py --import-path src/pycsl --verification-image src/self-annotate/src > $O/proof.log 2>&1; echo "rc=$?"
