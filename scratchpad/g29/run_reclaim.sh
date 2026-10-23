#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
G=/home/fabrice/git/pycsl/scratchpad/g29
/home/fabrice/git/pycsl/.venv/bin/python3 $G/reclaim_sweep.py /home/fabrice/git/pycsl "$@"
