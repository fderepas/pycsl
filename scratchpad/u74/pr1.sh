#!/bin/bash
# pr1.sh <file.py> [args]: a proof/probe run of a small user program (cwd = worktree root)
cd /home/fabrice/git/pycsl-u74; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
f=$1; shift
timeout 1200 .venv/bin/python3 src/pycsl/pycsl.py $f --import-path src/pycsl --keep-mlw "$@" > ${f%.py}.log 2>&1; echo "rc=$?" >> ${f%.py}.log
