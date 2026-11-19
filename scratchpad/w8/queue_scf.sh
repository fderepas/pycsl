#!/bin/bash
cd /home/fabrice/git/pycsl
P=scratchpad/w7/proofs
while [ ! -f $P/FINAL_DONE ]; do sleep 120; done
./scratchpad/w7/pr2.sh src/self-annotate/src/module6_whyml/stmt_control_flow.py o_scf 28800
echo "SCF RE-PROOF COMPLETE rc=$(cat $P/o_scf.rc)" > $P/SCF_DONE
