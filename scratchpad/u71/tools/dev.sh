#!/bin/bash
# dev.sh <tag> : --no-proof dev probes on the u71 working tree + witnesses (q). QUICK job.
U=/home/fabrice/git/pycsl-u71/scratchpad/u71
bash $U/tools/r.sh q /home/fabrice/git/pycsl-u71 $U/logs/$1 $U/tools/dev.lst
bash $U/tools/wit.sh q /home/fabrice/git/pycsl-u71 $U/logs/$1/w
