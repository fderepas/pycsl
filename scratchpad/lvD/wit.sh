#!/bin/bash
# wit.sh <tree> <tag> <ids...> : run corpus witnesses (from the lvD tree) with <tree>'s emitter. via heavy.sh
T=$1; tag=$2; shift 2; W=/home/fabrice/git/pycsl-lvD/test-suite/corpus/pycsl-reference; O=/home/fabrice/git/pycsl-lvD/scratchpad/lvD/wit
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
D=$(mktemp -d /tmp/lvdwit.XXXX); cd $T
for id in "$@"; do f=$(ls $W/${id}_*.py); cp $f $D/; b=$(basename $f)
  out=$(timeout 600 python3 src/pycsl/pycsl.py $D/$b --import-path src/pycsl 2>&1); 
  if echo "$out" | grep -q "Verification SUCCESS"; then v=PASS; elif echo "$out" | grep -q "PIPELINE ERROR"; then v=REFUSED; else v=FAIL; fi
  echo "$out" > $O/$tag.$id.log; echo -e "$tag\t$id\t$v\t$(grep -m1 'pycsl-expected' $f)" >> $O/results.tsv
done
rm -rf "${D:?}"
