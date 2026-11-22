#!/bin/bash
# log.sh <num> <commit-subject> : append "<ts> | <num> | <stdin text>" to the run log and commit it. Feed text via a QUOTED heredoc.
cd /home/fabrice/git/pycsl || exit 1
T=$(cat | tr '\n' ' ' | sed 's/  */ /g; s/ $//')
echo "$(date -u +%FT%H:%MZ) | $1 | $T |" >> getting-better/driver-run-log.md
git add getting-better/driver-run-log.md && git commit -q -m "log $1: $2

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo "logged $1"
