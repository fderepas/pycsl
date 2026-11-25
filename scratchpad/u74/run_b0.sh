#!/bin/bash
P=/home/fabrice/git/pycsl-u74/scratchpad/u74/probe.sh; V=/home/fabrice/git/pycsl-u74/scratchpad/u74/v
$P $V/b0.py exception_model.py b0
$P $V/c0.py audit_proof_reverify.py c0
$P $V/p0.py module6_whyml/struct_format.py p0
