#!/bin/bash
f="$1"; tag="$2"
ROOT="/home/fabrice.derepas@canonical.com/git/pycsl"; cd "$ROOT"
rm -f "scratchpad/nt/tc_${tag}.done" "scratchpad/nt/tc_${tag}.log"
timeout 1800 .venv/bin/python3 src/pycsl/pycsl.py --no-proof "$f" --import-path src/pycsl > "scratchpad/nt/tc_${tag}.log" 2>&1
if grep -q "L3-tc ✓" "scratchpad/nt/tc_${tag}.log"; then echo "TC_OK" > "scratchpad/nt/tc_${tag}.done"; else echo "TC_FAIL" > "scratchpad/nt/tc_${tag}.done"; fi
