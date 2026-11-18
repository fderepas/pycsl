#!/bin/bash
# Run every probe under real CPython (rule 3: ulimit'd, -B so no cache is written).
PY=/home/fabrice/git/pycsl/.venv/bin/python
cd "$(dirname "${BASH_SOURCE[0]}")/cases"
for c in */; do c=${c%/}; p=$(ls $c/prog_*.py); for fl in "" "-O" "-OO" "-OOO" "--check-hash-based-pycs never" "--check-hash-based-pycs always"; do
  out=$(cd $c && timeout 60 bash -c "ulimit -v 2000000; $PY -B -E -s $fl $(basename $p)" 2>&1 | tail -1)
  printf '%-34s %-32s %s\n' "$c" "[${fl:-default}]" "$out"; done; done
