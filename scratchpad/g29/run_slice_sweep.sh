#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
/home/fabrice/git/pycsl/.venv/bin/python3 /home/fabrice/git/pycsl/scratchpad/g29/slice_sweep.py "$1" "$2"
