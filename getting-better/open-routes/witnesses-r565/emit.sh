#!/bin/bash
T=$1; O=$2; mkdir -p $O; cd /home/fabrice/git/pycsl/scratchpad/u28/${PROBES:-p}
for f in ${FILES:-*.py}; do cp $f $O/; (cd $O; timeout 120 $T/.venv/bin/python $T/src/pycsl/pycsl.py --no-proof --no-typecheck --keep-mlw $f > ${f%.py}.emit 2>&1; echo "$f rc=$? $(grep -E 'SUCCESS|PYCSL-|Error' ${f%.py}.emit | head -1 | cut -c1-150)"); done
