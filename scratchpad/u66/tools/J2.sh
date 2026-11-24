#!/bin/bash
# J2.sh : u64 head (b1) full proofs of the key probes + witnesses; then the real _census_row for 10380
U=/home/fabrice/git/pycsl-u66/scratchpad/u66; L=$U/logs/J-b1; mkdir -p $L; T=/home/fabrice/git/pycsl-u66-b1
echo "## b1 $(git -C $T rev-parse --short HEAD)"
bash $U/tools/run.sh p $T $L/p $U/tools/probes-p.lst
bash $U/tools/run.sh p $T $L/pu $U/tools/probes-u66.lst
bash $U/tools/wit.sh p $T $L/w
echo "## census row (head tree u66)"
bash $U/tools/CR.sh > $U/logs/CR-row.tsv 2>$U/logs/CR-row.err; echo "CR rc=$? $(cut -c1-200 $U/logs/CR-row.tsv)"
