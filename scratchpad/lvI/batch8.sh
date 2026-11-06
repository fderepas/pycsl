#!/bin/bash
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
L=/home/fabrice/git/pycsl-lvI/scratchpad/lvI
cd /home/fabrice/git/pycsl-lvI && bin/run-soundness-planes.sh > $L/sw/planes3.txt 2>&1; echo "rc=$?" >> $L/sw/planes3.txt
echo done > $L/b8.done
