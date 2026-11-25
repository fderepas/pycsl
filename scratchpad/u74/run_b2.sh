#!/bin/bash
P=/home/fabrice/git/pycsl-u74/scratchpad/u74/probe.sh; V=/home/fabrice/git/pycsl-u74/scratchpad/u74/v
$P $V/b1.py exception_model.py b1
for t in p2 p3 p4; do $P $V/$t.py module6_whyml/struct_format.py $t; done
