#!/bin/bash
# pyc.sh TREE OUTDIR [extra pycsl flags]: run pycsl (proof, default model) on every probe; cwd = tree root.
T=$1; shift
O=$1; shift
mkdir -p "$O"
cd "$T"
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHON_CPU_COUNT=4
for c in "$(dirname "$(realpath "$0")")"/cases/*/; do c=${c%/}; n=$(basename $c); p=$(ls $c/prog_*.py)
  timeout 900 .venv/bin/python src/pycsl/pycsl.py "$@" "$p" > "$O/$n.log" 2>&1; rc=$?
  v=$(grep -oE "PYCSL-[A-Z0-9-]+" "$O/$n.log" | sort -u | tr '\n' ' ')
  s=$(grep -E "^\s*(Summary|Result|All|[0-9]+ */ *[0-9]+)|Valid|FAILED|PROVED|proved" "$O/$n.log" | tail -1)
  printf '%-34s rc=%-3s codes=[%s] %s\n' "$n" "$rc" "$v" "$s"
done
