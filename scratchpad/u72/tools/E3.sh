#!/bin/bash
# E3.sh <tag> : --no-proof emission of every probe + witness on the three trees (b0 = L20, u70, h1)
U=/home/fabrice/git/pycsl-u72/scratchpad/u72
for t in b0 u70 h1; do
  case $t in b0) T=/home/fabrice/git/pycsl-u72-b0;; u70) T=/home/fabrice/git/pycsl-u72-u70;; h1) T=/home/fabrice/git/pycsl-u72-h1;; esac
  echo "## $t $(git -C $T rev-parse --short HEAD) $(date -u)"
  bash $U/tools/q.sh $T $U/logs/$1-$t -- $(cat $U/tools/probes.lst)
done
