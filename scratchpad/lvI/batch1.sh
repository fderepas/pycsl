#!/bin/bash
L=/home/fabrice/git/pycsl-lvI/scratchpad/lvI
$L/pr.sh $L/st2 $L/nd/nd4.py nd4_st2
$L/pr.sh /home/fabrice/git/pycsl-lvI-base $L/nd/nd4.py nd4_base
$L/wit.sh /home/fabrice/git/pycsl-lvI-base base 9100 9101 9102
$L/wit.sh $L/st st 9100 9101 9102
echo done > $L/batch1.done
