#!/bin/bash
# emitw.sh <rel-mirror> <tag>: --no-proof emission of a worktree mirror file (cwd = worktree root), copy .mlw to v/<tag>.mlw
cd /home/fabrice/git/pycsl-u74; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=/home/fabrice/git/pycsl-u74/scratchpad/u74/tmp
f=src/self-annotate/src/$1
timeout 1500 .venv/bin/python3 src/pycsl/pycsl.py $f --import-path src/pycsl --verification-image src/self-annotate/src --no-proof --keep-mlw > scratchpad/u74/v/$2.log 2>&1; echo "rc=$?" >> scratchpad/u74/v/$2.log
cp ${f%.py}.mlw scratchpad/u74/v/$2.mlw
