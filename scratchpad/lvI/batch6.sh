#!/bin/bash
L=/home/fabrice/git/pycsl-lvI/scratchpad/lvI
$L/vc2.sh $L/tc/c5.Module6_WhyMLTranspiler.mlw module6_whymltranspiler___e_refines_statementemissionmixin tr_e2
cd /home/fabrice/git/pycsl-lvI && bin/run-soundness-planes.sh > $L/sw/planes2.txt 2>&1; echo "rc=$?" >> $L/sw/planes2.txt
echo done > $L/b6.done
