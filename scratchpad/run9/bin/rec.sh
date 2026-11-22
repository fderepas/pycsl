#!/bin/bash
# rec.sh <pid> <tag> <mirror-rel> <log> : wait for an orphaned proof's heavy.sh to exit, then append its proveq-style line
while kill -0 $1 2>/dev/null; do sleep 30; done
L=$4; echo "$3 rc=? valid=$(grep -c 'Prover result is: Valid' $L) total=$(grep -c 'Prover result is:' $L) $(grep -oE 'Verification (SUCCESS|FAILED)' $L | tail -1) (recorded by the driver after the loop stop)" >> /home/fabrice/git/pycsl/scratchpad/run9/$2-proofs.txt
