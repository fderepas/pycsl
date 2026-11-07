#!/bin/bash
# lvD survey: verbatim port + --no-proof --keep-mlw, ONE stub per call. Run ONLY as heavy.sh <this> <rel> <fn> <outdir> [--no-proof|...]
L=/home/fabrice/git/pycsl-lvD/scratchpad/lvD; T=${ST:-$L/st}
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
cd $T; rel=$1; fn=$2; out=$3; shift 3
f=src/self-annotate/src/$rel; cp $f /tmp/lvd.$$.bak
msg=$(python3 bin/port-one-mirror-body.py $T $rel "$fn" --convert 2>&1); mode=facade
case "$msg" in *--replace*) msg=$(python3 bin/port-one-mirror-body.py $T $rel "$fn" --convert --replace 2>&1); mode=replace;; esac
tag=$(echo $rel | tr / _)__$fn
case "$msg" in ABORT*) echo -e "$rel\t$fn\tPORT-ABORT\t$msg" >> $out/results.tsv; cp /tmp/lvd.$$.bak $f; exit 0;; esac
[ -n "$PATCH" ] && python3 $PATCH $f >> $out/$tag.patchlog 2>&1
cp $f $out/$tag.src.py
tc=$(timeout 900 python3 src/pycsl/pycsl.py $f --import-path $T/src/pycsl --keep-mlw "$@" 2>&1)
printf '%s' "$tc" > $out/$tag.log
if printf '%s' "$tc" | grep -q 'Verification SUCCESS'; then v=TC-OK; d=""; elif printf '%s' "$tc" | grep -q 'PIPELINE ERROR'; then v=REFUSED; d=$(printf '%s' "$tc" | grep -A3 'PIPELINE ERROR' | tail -3 | tr '\n\t' '  ' | cut -c1-260); else v=L3-TC; d=$(printf '%s' "$tc" | grep -A3 -E '^File "' | grep -v '^--' | head -4 | tr '\n\t' '  ' | cut -c1-300); fi
echo -e "$rel\t$fn\t$v\t$mode\t$d" >> $out/results.tsv
m=${f%.py}.mlw; [ -f "$m" ] && mv "$m" "$out/$tag.mlw"
cp /tmp/lvd.$$.bak $f; rm -f /tmp/lvd.$$.bak
