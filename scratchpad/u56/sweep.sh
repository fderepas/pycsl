#!/bin/bash
# sweep.sh <tree> <outprefix> : corpus(root+pyref) + mirror emission sweeps, cwd = tree root
T=$1; O=$2; cd "$T" || exit 2
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
mkdir -p "$O"
echo "$(date -u) start corpus" ; bin/byte-diff-sweep.sh "$O/bd" > "$O/bd.log" 2>&1; echo "bd rc=$?"
echo "$(date -u) start mirror" ; bin/mirror-emit-sweep.sh "$O/mir" > "$O/mir.log" 2>&1; echo "mir rc=$?"
echo "$(date -u) done"
