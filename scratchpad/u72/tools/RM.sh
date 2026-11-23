#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u72/scratchpad/u72/tmp; mkdir -p $TMPDIR
# RM.sh <outdir> : --no-proof refusal message (the line after PIPELINE ERROR, as _census_row records it) of
# every census REFUSAL witness that imports a local module (tools/ref-local.lst), on b0 (L20) and h1.
# Files are read from the h1 tree (corpus identical to b0 for these), cwd = the tree whose pycsl runs.
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
U=/home/fabrice/git/pycsl-u72/scratchpad/u72; O=$(realpath -m $1); mkdir -p $O
for t in b0 h1; do T=/home/fabrice/git/pycsl-u72-$t; cd $T
  : > $O/$t.tsv
  while read f; do
    rel=${f#/home/fabrice/git/pycsl-u72-h1/}
    FL=($(grep -m1 '^# pycsl-flags:' $rel | cut -d: -f2-))
    out=$(timeout 300 $T/.venv/bin/python3 $T/src/pycsl/pycsl.py --no-proof "${FL[@]}" $rel 2>&1)
    msg=$(printf '%s\n' "$out" | grep -A1 'PIPELINE ERROR' | sed -n 2p | sed 's/^\s*//' | cut -c1-4000)
    printf '%s\t%s\n' "$(basename $rel)" "${msg:-<no refusal>}" >> $O/$t.tsv
    rm -f "${rel%.py}.mlw"
  done < $U/tools/ref-local.lst
done
echo "RM done $(date -u)"
