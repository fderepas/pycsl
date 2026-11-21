#!/bin/bash
# Cumulative per-method `#@ sibling_concrete` triage on the 1-second emit oracle.
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
CUR=$1   # current shadowed site count
shift
for spec in "$@"; do
  m=${spec%%:*}; files=${spec#*:}
  python3 scratchpad/w3/mark.py add "$m" $files >/dev/null
  bash scratchpad/w2/sweep.sh /home/fabrice/git/pycsl /home/fabrice/git/pycsl/scratchpad/w3/tri >/dev/null 2>&1
  tcf=$(grep -c TC_FAIL scratchpad/w3/tri/manifest.md5)
  sites=$(TMPDIR=/home/fabrice/git/pycsl/scratchpad python3 bin/check-shadowed-selfcalls.py 2>&1 | grep -oE '[0-9]+ bypassing call site' | grep -oE '^[0-9]+')
  if [ "$tcf" != "0" ] || [ -z "$sites" ] || [ "$sites" -ge "$CUR" ]; then
    python3 scratchpad/w3/mark.py del "$m" $files >/dev/null
    echo "REVERT $m  (TC_FAIL=$tcf sites=$sites, was $CUR)"
  else
    echo "KEEP   $m  ($CUR -> $sites)"
    CUR=$sites
  fi
done
echo "FINAL sites=$CUR"
