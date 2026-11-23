#!/bin/bash
# P3.sh <tag> <listfile> [trees...] : full pycsl proofs (p.sh: cwd = tree root, PYTHON_CPU_COUNT=2, cap 3600 s,
# oom_kill before/after each file) of every file in <listfile> on each tree (default b0 u70 h1).
U=/home/fabrice/git/pycsl-u72/scratchpad/u72; TAG=$1; LST=$2; shift 2; TR=${@:-b0 u70 h1}
for t in $TR; do
  case $t in b0) T=/home/fabrice/git/pycsl-u72-b0;; u70) T=/home/fabrice/git/pycsl-u72-u70;; h1) T=/home/fabrice/git/pycsl-u72-h1;; esac
  echo "## $t $(git -C $T rev-parse --short HEAD) $(date -u)"
  bash $U/tools/p.sh $T $U/logs/$TAG-$t -- $(cat $LST)
done
echo "## end $(date -u)"
