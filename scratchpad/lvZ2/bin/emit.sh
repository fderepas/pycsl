#!/bin/bash
# emit.sh <tag> <tree> <probes...> : --no-proof --keep-mlw emissions, sequential, one QUICK slot; cwd = tree root
tag=$1; T=$2; shift 2
W=/home/fabrice/git/pycsl-lvZ2/scratchpad/lvZ2; L=$W/logs/emit-$tag; mkdir -p $L
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; cd $T || exit 2
for p in "$@"; do
  ls "$p" >/dev/null || { echo "MISSING $p"; continue; }
  b=$(basename $p .py); d=$(basename $(dirname $p)); [ "$b" = main ] && b=$d
  case "$p" in */rt65/*) b=rt65.$b;; */rt67/*) b=rt67.$b;; */rt70/*) b=rt70.$b;; esac
  f=$L/$b.log; m="${p%.py}.mlw"; rm -f "$m"
  timeout 300 .venv/bin/python3 src/pycsl/pycsl.py "$p" --no-proof --keep-mlw > $f 2>&1; echo "rc=$?" >> $f
  [ -f "$m" ] && mv "$m" $L/$b.mlw
  echo -e "$b\t$(grep -oE 'Verification SUCCESS|PYCSL-[A-Z0-9-]+|PIPELINE ERROR|L3-tc ✗|rror.{0,100}' $f | head -1)"
done
