#!/bin/bash
W=/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/dx1/witness
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
cd /home/fabrice/git/pycsl-dx1
for w in "$@"; do [ "$w" = --no-proof ] && continue; echo "== $w"; python3 $W/frame_witness.py /home/fabrice/git/pycsl-dx1 $W/$w.py --no-proof 2>&1 | grep -E "WITNESS|pycsl exit|L3-tc|ERROR|rror" | cut -c1-300; done
