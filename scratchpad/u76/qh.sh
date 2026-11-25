#!/bin/bash
# qh.sh <names>: QUICK --no-proof emissions at head only
for n in "$@"; do /home/fabrice/git/pycsl-u76/scratchpad/u76/run.sh h $n --no-proof; done
