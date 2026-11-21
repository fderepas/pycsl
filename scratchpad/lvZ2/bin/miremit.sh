#!/bin/bash
# miremit.sh <tree> <out> <files...> : single-file --no-proof mirror emissions (diagnostic probes), sequential
T=$1; O=$2; shift 2; mkdir -p $O; cd $T || exit 2
for f in "$@"; do n=$(printf '%s' "${f#src/self-annotate/src/}" | sed 's/\.py$//; s#/#__#g')
  rm -f "${f%.py}.mlw"
  PYTHONHASHSEED=0 timeout 900 .venv/bin/python3 src/pycsl/pycsl.py --no-proof --no-typecheck --keep-mlw --import-path $T/src/pycsl "$f" > $O/$n.log 2>&1
  if [ -f "${f%.py}.mlw" ]; then mv "${f%.py}.mlw" $O/$n.mlw; echo "$n EMIT"; else echo "$n NONE $(grep -m1 -oE 'PYCSL-[A-Z0-9-]+: line [0-9]+: `[^`]{0,80}' $O/$n.log)"; fi
done
