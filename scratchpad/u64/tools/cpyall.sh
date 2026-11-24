#!/bin/bash
C=/home/fabrice/git/pycsl-u64/scratchpad/u64/tools/cpy.sh; PR=/home/fabrice/git/pycsl-u64/scratchpad/u64/probes
for x in "v2d X2" "w5 X2" "v2 X" "x1 X" "x2 X" "x3 X2" "v1f -"; do set -- $x; echo "#### $1"; pp=$PR/$1/$2; [ "$2" = - ] && pp=; $C $PR/$1/P/prog.py $pp; done
echo "#### v2down"; $C $PR/v2d/X2/depv2.py
