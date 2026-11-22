#!/bin/bash
# --no-proof each probe; cwd = tree root
cd /home/fabrice/git/pycsl-u68
for f in "$@"; do echo "=== $f"; PYTHON_CPU_COUNT=2 .venv/bin/python3 src/pycsl/pycsl.py --no-proof "$f" 2>&1 | grep -E "PIPELINE ERROR|PYCSL-|SUCCESS|FAIL|rror" -A1 | head -8; done
