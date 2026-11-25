#!/bin/bash
P=/home/fabrice/git/pycsl-u74/scratchpad/u74/probe.sh; V=/home/fabrice/git/pycsl-u74/scratchpad/u74/v
$P $V/m5.py frontend/Module5_IREmitter.py m5
$P $V/ap.py audit_proof.py ap
