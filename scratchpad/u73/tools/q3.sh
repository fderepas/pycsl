#!/bin/bash
# q3.sh <tag> <probe>... : --no-proof on head (u73 worktree), bh (08e65645c), b0 (L19), sequential
tag=$1; shift; U=/home/fabrice/git/pycsl-u73/scratchpad/u73
for t in h:/home/fabrice/git/pycsl-u73 bh:/home/fabrice/git/pycsl-u73-bh b0:/home/fabrice/git/pycsl-u73-b0; do
  bash $U/tools/D.sh q ${t#*:} $U/logs/$tag-${t%%:*} "$@" | sed "s/^/[${t%%:*}] /"; done
