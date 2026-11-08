#!/bin/bash
# candidate sweeps + honesty planes + fast planes, all on the lvI tree, sequential (NORMAL)
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
R=/home/fabrice/git/pycsl-lvI; O=$R/scratchpad/lvI/sw; cd $R
bin/mirror-emit-sweep.sh $O/mir_cand > $O/mir_cand.log 2>&1
python3 bin/byte-diff-compare.py $O/mir_base $O/mir_cand --min-files 45 > $O/cmp-mirror.txt 2>&1; echo "rc=$?" >> $O/cmp-mirror.txt
python3 bin/check-yield-erasure.py --emit-dir $O/mir_cand > $O/plane-yield.txt 2>&1; echo "rc=$?" >> $O/plane-yield.txt
python3 bin/check-computed-rhs-erasure.py --emit-dir $O/mir_cand > $O/plane-rhs.txt 2>&1; echo "rc=$?" >> $O/plane-rhs.txt
python3 bin/check-emitted-vacuity.py --emit > $O/plane-vacuity.txt 2>&1; echo "rc=$?" >> $O/plane-vacuity.txt
bin/run-soundness-planes.sh > $O/planes.txt 2>&1; echo "rc=$?" >> $O/planes.txt
bin/byte-diff-sweep.sh $O/corpus_cand > $O/corpus_cand.log 2>&1
python3 bin/byte-diff-compare.py $O/corpus_base $O/corpus_cand > $O/cmp-corpus.txt 2>&1; echo "rc=$?" >> $O/cmp-corpus.txt
python3 bin/byte-diff-compare.py $O/corpus_base/pyref $O/corpus_cand/pyref > $O/cmp-pyref.txt 2>&1; echo "rc=$?" >> $O/cmp-pyref.txt
echo done > $O/cand.done
