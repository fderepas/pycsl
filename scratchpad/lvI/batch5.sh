#!/bin/bash
L=/home/fabrice/git/pycsl-lvI/scratchpad/lvI
$L/wit.sh /home/fabrice/git/pycsl-lvI-base base 9100 9101 9102
$L/wit.sh $L/st st 9100 9101 9102
$L/pr.sh $L/st2 $L/nd/nd5.py nd5_st2
$L/pr.sh $L/st2 $L/nd/nd6.py nd6_st2
$L/pr.sh /home/fabrice/git/pycsl-lvI-base $L/nd/nd5.py nd5_base
$L/pr.sh /home/fabrice/git/pycsl-lvI-base $L/nd/nd6.py nd6_base
echo done > $L/b5.done
