#!/bin/bash
# candidate sweeps + honesty planes + fast planes on the lvK tree, sequential (NORMAL)
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
R=/home/fabrice/git/pycsl-lvK; O=$R/scratchpad/lvK/sw; T=${1:-c}; cd $R
rm -rf "$O/mir_$T"
bin/mirror-emit-sweep.sh $O/mir_$T > $O/mir_$T.log 2>&1
python3 bin/byte-diff-compare.py $O/mir_base $O/mir_$T --min-files 45 > $O/cmp-mirror-$T.txt 2>&1; echo "rc=$?" >> $O/cmp-mirror-$T.txt
python3 bin/check-yield-erasure.py --emit-dir $O/mir_$T > $O/plane-yield-$T.txt 2>&1; echo "rc=$?" >> $O/plane-yield-$T.txt
python3 bin/check-computed-rhs-erasure.py --emit-dir $O/mir_$T > $O/plane-rhs-$T.txt 2>&1; echo "rc=$?" >> $O/plane-rhs-$T.txt
python3 bin/check-emitted-vacuity.py --emit > $O/plane-vacuity-$T.txt 2>&1; echo "rc=$?" >> $O/plane-vacuity-$T.txt
bin/run-soundness-planes.sh > $O/planes-$T.txt 2>&1; echo "rc=$?" >> $O/planes-$T.txt
rm -rf "$O/corpus_$T"
bin/byte-diff-sweep.sh $O/corpus_$T > $O/corpus_$T.log 2>&1
python3 bin/byte-diff-compare.py $O/corpus_base $O/corpus_$T > $O/cmp-corpus-$T.txt 2>&1; echo "rc=$?" >> $O/cmp-corpus-$T.txt
python3 bin/byte-diff-compare.py $O/corpus_base/pyref $O/corpus_$T/pyref > $O/cmp-pyref-$T.txt 2>&1; echo "rc=$?" >> $O/cmp-pyref-$T.txt
echo done > $O/cand-$T.done
