#!/bin/bash
# q2.sh <tag> : --no-proof of every probe, base then head
U=/home/fabrice/git/pycsl-u70/scratchpad/u70
bash $U/tools/run.sh q /home/fabrice/git/pycsl-u70-b0 $U/logs/$1-base
bash $U/tools/run.sh q /home/fabrice/git/pycsl-u70 $U/logs/$1-head
