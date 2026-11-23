#!/bin/bash
# probe.sh <variant.py> <rel-in-mirror> <tag> [extra pycsl args] -- --no-proof only (HEAVY_QUICK=1 heavy.sh)
L=/home/fabrice/git/pycsl-u67/scratchpad/u67; T=$L/st
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0 PYTHON_CPU_COUNT=2
v=$1; rel=$2; tag=$3; shift 3
cd $T; f=src/self-annotate/src/$rel
cp /home/fabrice/git/pycsl-u67/$f $L/orig.$tag.py
cp $v $f; rm -f ${f%.py}.mlw
timeout 1500 python3 src/pycsl/pycsl.py $f --import-path $T/src/pycsl --verification-image $T/src/self-annotate/src --no-proof --keep-mlw "$@" > $L/v/$tag.log 2>&1
echo "rc=$?" >> $L/v/$tag.log
m=${f%.py}.mlw; [ -f $m ] && cp $m $L/v/$tag.mlw
cp $L/orig.$tag.py $f
