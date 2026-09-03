#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/w7/tmp
mine=0; other=0
while read n; do
  f=""
  for d in test-suite/corpus/pycsl-reference test-suite/corpus/python-reference; do
     [ -f "$d/$n.py" ] && f="$d/$n.py"
     [ -z "$f" ] && [ -f "$d/stdlib/$n.py" ] && f="$d/stdlib/$n.py"
  done
  [ -z "$f" ] && f=$(find test-suite/corpus -name "$n.py" | head -1)
  [ -z "$f" ] && { echo "NOTFOUND $n"; continue; }
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  out=$(PYTHONHASHSEED=0 timeout 200 python3 src/pycsl/pycsl.py $flags "$f" 2>&1)
  if echo "$out" | grep -qE "except\*|async def. is NOT MODELLED|does not consume it|nonlocal. declaration|nothing after it to attach"; then
     echo "MINE $n"; mine=$((mine+1))
  else other=$((other+1)); fi
done < /home/fabrice/git/pycsl/scratchpad/w7/fail_list.txt
echo "caused by a #34 refusal: $mine ; other: $other"
