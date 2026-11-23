#!/bin/bash
# u65 type-only census (retargeted u63 census.sh): this tree's _run_vacuity_gate probes over v75 emissions
# (emission == base; mirror 53 + corpus root + pyref), plus per-file probe counts at base and head.
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
export PYTHON_CPU_COUNT=2
U=/home/fabrice/git/pycsl-u65; B=/home/fabrice/git/pycsl-u65b; O=$U/scratchpad/u65/census; V=/home/fabrice/git/pycsl/scratchpad/run9/v75
mkdir -p $O; cd $U
{ ls $V/mir-int/*.mlw; ls $V/bd-int/*.mlw; ls $V/bd-int/pyref/*.mlw; } > $O/all.txt
.venv/bin/python scratchpad/u65/tools/count.py $B $O/count-base.tsv $O/all.txt > $O/count-base.log 2>&1
.venv/bin/python scratchpad/u65/tools/count.py $U $O/count-head.tsv $O/all.txt > $O/count-head.log 2>&1
split -n l/3 -d $O/all.txt $O/chunk.
for c in $O/chunk.0?; do .venv/bin/python scratchpad/u65/tools/pfcensus.py $U $c.tsv $(cat $c) > $c.log 2>&1 & done
wait; echo "census done $(date -u)" >> $O/done.txt
