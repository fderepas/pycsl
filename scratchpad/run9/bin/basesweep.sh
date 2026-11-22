#!/bin/bash
# basesweep.sh <tree> <outdir> : corpus byte-diff sweep + mirror emission sweep (sequential) of a tree
T=$1; O=$2; H=/home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh; mkdir -p $O
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
(cd $T && $H bin/byte-diff-sweep.sh $O/bd > $O/bd.log 2>&1); echo "bd rc=$?" > $O/done.txt
(cd $T && $H bin/mirror-emit-sweep.sh $O/mir > $O/mir.log 2>&1); echo "mir rc=$?" >> $O/done.txt
ls $O/bd | grep -c mlw >> $O/done.txt; ls $O/bd/pyref | grep -c mlw >> $O/done.txt; ls $O/mir | grep -c mlw >> $O/done.txt
