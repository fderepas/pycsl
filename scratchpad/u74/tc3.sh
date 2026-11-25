#!/bin/bash
P=/home/fabrice/git/pycsl-u74/scratchpad/u74/probe.sh; V=/home/fabrice/git/pycsl-u74/scratchpad/u74/v
$P $V/m5b.py frontend/Module5_IREmitter.py m5b
$P $V/c3.py audit_proof_reverify.py c3
