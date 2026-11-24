#!/bin/bash
# p.sh <h|b> <names>: FULL proofs of candidates c/<name>.py in head or base
t=$1; shift
for n in "$@"; do /home/fabrice/git/pycsl-u76/scratchpad/u76/run.sh $t $n; done
