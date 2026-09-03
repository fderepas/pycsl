#!/bin/bash
cd /home/fabrice/git/pycsl
P=scratchpad/w7/proofs
while [ ! -f $P/SCF_DONE ]; do sleep 120; done
./scratchpad/w7/pr2.sh src/self-annotate/src/module6_whyml/ir_scanner.py o_irs 28800
echo "IR_SCANNER RE-PROOF COMPLETE rc=$(cat $P/o_irs.rc)" > $P/IRS_DONE
