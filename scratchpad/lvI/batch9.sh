#!/bin/bash
L=/home/fabrice/git/pycsl-lvI/scratchpad/lvI
for n in nd8 nd9; do $L/pr.sh $L/st2 $L/nd/$n.py ${n}_st2; $L/pr.sh /home/fabrice/git/pycsl-lvI-base $L/nd/$n.py ${n}_base; done
echo done > $L/b9.done
