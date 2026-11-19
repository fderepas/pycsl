#!/bin/bash
# probe.sh <rel> <Qualified.fn> <tag> [old=new ...]   -- run via HEAVY_QUICK=1 heavy.sh (--no-proof only)
L=/home/fabrice/git/pycsl-lvE/scratchpad/lvE; R=/home/fabrice/git/pycsl-lvE; T=$L/st
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
cd $T; rel=$1; fn=$2; tag=$3; shift 3; f=src/self-annotate/src/$rel
cp $R/$f $f
msg=$(python3 bin/port-one-mirror-body.py $T $rel "$fn" --convert 2>&1)
case "$msg" in *--replace*) python3 bin/port-one-mirror-body.py $T $rel "$fn" --convert --replace >/dev/null 2>&1;; esac
[ $# -gt 0 ] && python3 $L/rename.py $f "$fn" "$@" > $L/probe/$tag.patchlog 2>&1
[ -f $L/probe/$tag.extra.sh ] && bash $L/probe/$tag.extra.sh $f >> $L/probe/$tag.patchlog 2>&1
cp $f $L/probe/$tag.src.py
tc=$(timeout 1500 python3 src/pycsl/pycsl.py $f --import-path $T/src/pycsl --no-proof ${PROBE_ARGS} 2>&1)
printf '%s' "$tc" > $L/probe/$tag.log
if printf '%s' "$tc" | grep -q 'Verification SUCCESS'; then v=TC-OK; d=""; elif printf '%s' "$tc" | grep -q 'PIPELINE ERROR'; then v=REFUSED; d=$(printf '%s' "$tc" | grep -A3 'PIPELINE ERROR' | tail -3 | tr '\n\t' '  ' | cut -c1-400); else v=L3-TC; d=$(printf '%s' "$tc" | grep -B2 -A3 -E '^File "|line [0-9]+, characters' | head -6 | tr '\n\t' '  ' | cut -c1-400); fi
echo -e "$tag\t$rel\t$fn\t$v\t$d" >> $L/probe/results.tsv
cp $R/$f $f
