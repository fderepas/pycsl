#!/bin/bash
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
R=/home/fabrice/git/pycsl-lvI; L=$R/scratchpad/lvI; O=$L/sw; cd $R
bin/mirror-emit-sweep.sh $O/mir_cand2 > $O/mir_cand2.log 2>&1
python3 bin/byte-diff-compare.py $O/mir_base $O/mir_cand2 --min-files 45 > $O/cmp-mirror2.txt 2>&1; echo "rc=$?" >> $O/cmp-mirror2.txt
python3 bin/check-shadowed-selfcalls.py --emit-dir $O/mir_cand2 > $O/shad_cand2.txt 2>&1; echo "rc=$?" >> $O/shad_cand2.txt
python3 bin/check-yield-erasure.py --emit-dir $O/mir_cand2 > $O/plane-yield2.txt 2>&1; echo "rc=$?" >> $O/plane-yield2.txt
python3 bin/check-computed-rhs-erasure.py --emit-dir $O/mir_cand2 > $O/plane-rhs2.txt 2>&1; echo "rc=$?" >> $O/plane-rhs2.txt
python3 bin/check-emitted-vacuity.py --emit > $O/plane-vacuity2.txt 2>&1; echo "rc=$?" >> $O/plane-vacuity2.txt
bin/run-soundness-planes.sh > $O/planes4.txt 2>&1; echo "rc=$?" >> $O/planes4.txt
echo done > $L/b10b.done
