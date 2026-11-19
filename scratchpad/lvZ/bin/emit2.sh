#!/bin/bash
# emit.sh <tag> <probes...> : --no-proof emissions, sequential, under ONE QUICK slot; cwd = tree root
tag=$1; shift
T=${EMIT_TREE:-/home/fabrice/git/pycsl-lvZ}; R=/home/fabrice/git/pycsl-lvZ/scratchpad/lvZ; L=$R/logs/emit-$tag; mkdir -p $L
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; cd $T || exit 2
: > $L/summary.tsv
for p in "$@"; do b=$(basename $p .py); [ "$b" = main ] && b=$(basename $(dirname $p)); ls "$p" >/dev/null || { echo "MISSING $p"; continue; }
  f=$L/$b.log; m="${p%.py}.mlw"; rm -f "$m"
  timeout 300 .venv/bin/python3 src/pycsl/pycsl.py "$p" --no-proof --keep-mlw > $f 2>&1; echo "rc=$?" >> $f
  [ -f "$m" ] && mv "$m" $L/$b.mlw
  echo -e "$b\t$(grep -oE 'Verification SUCCESS|PYCSL-[A-Z0-9-]+|PIPELINE ERROR|L3-tc ✗|rror.{0,100}' $f | head -1)" >> $L/summary.tsv
done
echo DONE >> $L/summary.tsv
