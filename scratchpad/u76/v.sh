#!/bin/bash
# v.sh <log...>: one-line verdict per pycsl log
for f in "$@"; do
 if grep -q "All contracts formally proven" $f; then v=PROVED
 elif grep -q "PIPELINE ERROR" $f; then v="REFUSED $(grep -m1 -oE 'PYCSL-[A-Z0-9-]+' $f)"
 elif grep -q "goal(s) remain unproven" $f; then v="NOT-PROVED($(grep -m1 -oE '[0-9]+ goal\(s\) remain' $f | cut -d' ' -f1) unproven)"
 elif grep -qE "This expression has type|unbound|Type error|is expected to have type" $f; then v="FAIL-CLOSED(L3-tc)"
 else v="OTHER"; fi
 q=$(grep -cE "EDQUOT|Disk quota exceeded|No space left" $f)
 echo "$(basename ${f%.log}) $v $(tail -1 $f | grep -oE 'rc=[0-9]+|oom0=\[[^]]*\] oom1=\[[^]]*\]' | tr '\n' ' ') quota=$q"
done
