#!/bin/bash
# chain1.sh : sweep snapshot h1 (pre-narrowing, e580aae79) and compare against base b1 (73f47db9d). One NORMAL job.
U=/home/fabrice/git/pycsl-u71/scratchpad/u71
bash $U/tools/S.sh /home/fabrice/git/pycsl-u71-h1 $U/logs/G/h1
bash $U/tools/CMP.sh h1
