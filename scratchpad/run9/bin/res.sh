#!/bin/bash
# res.sh <log> : proveq-style result line for a pycsl.py proof log
L=$1; echo "$(basename $L) valid=$(grep -c 'Prover result is: Valid' $L) total=$(grep -c 'Prover result is:' $L) $(grep -oE 'Verification (SUCCESS|FAILED)' $L | tail -1)"
