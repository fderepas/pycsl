#!/bin/bash
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
O=/home/fabrice/git/pycsl-lvI/scratchpad/lvI/fun/$3.log; : > $O
timeout 600 why3 prove -P "Z3,4.13.3," --timelimit 10 "$1" -T PyCSL_Program -G "$2" >> $O 2>&1; echo "rc=$?" >> $O
