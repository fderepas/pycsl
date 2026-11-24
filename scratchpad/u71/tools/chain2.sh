#!/bin/bash
# chain2.sh : sweep snapshot h2 (final src) + compare vs base b1; probe/witness battery on h2, b1 (u69), b0 (L19);
# census rows (real _census_row) appended; GATES on the u71 tree. One NORMAL job, sequential.
U=/home/fabrice/git/pycsl-u71/scratchpad/u71; W=/home/fabrice/git/pycsl-u71
bash $U/tools/S.sh /home/fabrice/git/pycsl-u71-h2 $U/logs/G/h2
bash $U/tools/CMP.sh h2
for t in h2:/home/fabrice/git/pycsl-u71-h2 b1:/home/fabrice/git/pycsl-u71-b1 b0:/home/fabrice/git/pycsl-u71-b0; do
  bash $U/tools/J.sh ${t#*:} ${t%%:*} 2>&1 | sed "s/^/[J ${t%%:*}] /"; done
bash $U/tools/CR.sh > $U/logs/CR-rows.tsv 2>$U/logs/CR-rows.err; echo "CR rc=$? rows=$(wc -l < $U/logs/CR-rows.tsv)"
cd $W; if [ "$(wc -l < $U/logs/CR-rows.tsv)" = 4 ] && ! grep -q '^10435_' bin/refusal-witness-census.tsv; then cat $U/logs/CR-rows.tsv >> bin/refusal-witness-census.tsv; echo "census rows appended"; fi
bash $U/tools/GATES.sh $U/logs/GATES 2>&1
