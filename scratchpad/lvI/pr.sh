#!/bin/bash
# pr.sh <tree> <file> <tag> : full proof of a scratch program (NORMAL)
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
cd $1; f=$2; O=$(dirname $f)/$3.log
timeout 900 python3 src/pycsl/pycsl.py $f > $O 2>&1; echo "rc=$?" >> $O
