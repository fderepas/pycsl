#!/bin/bash
P=/home/fabrice/git/pycsl-u74/scratchpad/u74/probe.sh; V=/home/fabrice/git/pycsl-u74/scratchpad/u74/v
for t in "$@"; do $P $V/$t.py audit_proof_reverify.py $t; done
