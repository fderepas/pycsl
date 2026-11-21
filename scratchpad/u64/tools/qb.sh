#!/bin/bash
# qb.sh <tree> <outdir> : --no-proof run of every u64 probe (cwd = tree root)
T=$1; O=$2; Q=/home/fabrice/git/pycsl-u64/scratchpad/u64/tools/q.sh; PR=/home/fabrice/git/pycsl-u64/scratchpad/u64/probes
$Q $T $O/v2d --import-path $PR/v2d/X2 -- $PR/v2d/P/prog.py
$Q $T $O/w5 --import-path $PR/w5/X2 -- $PR/w5/P/prog.py
$Q $T $O/v2 --import-path $PR/v2/X -- $PR/v2/P/prog.py
$Q $T $O/x1 --import-path $PR/x1/X -- $PR/x1/P/prog.py
$Q $T $O/x2 --import-path $PR/x2/X -- $PR/x2/P/prog.py
$Q $T $O/x3 --import-path $PR/x3/X2 -- $PR/x3/P/prog.py
$Q $T $O/v2down -- $PR/v2d/X2/depv2.py
$Q $T $O/v1f -- $PR/v1f/P/prog.py
