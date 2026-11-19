#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
for seed in $(seq "$1" "$2"); do
  timeout 1500 /home/fabrice/git/pycsl/.venv/bin/python3 \
    /home/fabrice/git/pycsl/scratchpad/g29/fuzz/gen4.py "$S/fz4_$seed" 20 "$seed"
done
echo BATCH4-DONE $(date -u +%H:%M:%SZ)
