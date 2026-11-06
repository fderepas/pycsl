#!/bin/bash
# nd.sh <tree> <file> : --no-proof --keep-mlw of a scratch program (QUICK)
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
cd $1; f=$2; rm -f ${f%.py}.mlw
timeout 600 python3 src/pycsl/pycsl.py $f --no-proof --keep-mlw > ${f%.py}.log 2>&1; echo "rc=$?" >> ${f%.py}.log
