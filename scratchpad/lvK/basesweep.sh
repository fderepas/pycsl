#!/bin/bash
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
B=/home/fabrice/git/pycsl-lvKbase; O=/home/fabrice/git/pycsl-lvK/scratchpad/lvK/sw
cd $B && bin/mirror-emit-sweep.sh $O/mir_base > $O/mir_base.log 2>&1
cd $B && bin/byte-diff-sweep.sh $O/corpus_base > $O/corpus_base.log 2>&1
echo done > $O/base.done
