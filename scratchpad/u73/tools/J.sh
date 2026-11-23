#!/bin/bash
# J.sh <tree> <tag> : full proofs (p) with <tree>'s pycsl of every probe whose --no-proof run (logs/Q-<tag>, Q.sh)
# reached "Verification SUCCESS" (a refusal / type-check failure at q is final and is reported from the q log),
# plus every u73 witness / helper. One NORMAL job.
U=/home/fabrice/git/pycsl-u73/scratchpad/u73; L=$U/logs/J-$2; mkdir -p $L; T=$1; Q=$U/logs/Q-$2
echo "## $2 $T $(git -C $T rev-parse --short HEAD) $(date -u)"
D=(); for k in $(cat $U/tools/u73.lst $U/tools/rt81.lst); do grep -q "Verification SUCCESS" "$Q/d/${k//\//_}.log" 2>/dev/null && D+=("$k"); done
echo "## d-list ${#D[@]}: ${D[*]}"
[ ${#D[@]} -gt 0 ] && bash $U/tools/D.sh p $T $L/d "${D[@]}" | sed 's/^/[d] /'
: > $L/p.lst; while IFS='|' read -r n rest; do [ -z "$n" ] && continue; case "$n" in \#*) continue;; esac
  grep -q "Verification SUCCESS" "$Q/p/$n.log" 2>/dev/null && echo "$n|$rest" >> $L/p.lst; done < $U/tools/u71all.lst
echo "## p-list $(wc -l < $L/p.lst)"
bash $U/tools/r.sh p $T $L/p $L/p.lst | sed 's/^/[p] /'
bash $U/tools/wit.sh p $T $L/w | sed 's/^/[w] /'
echo "## end $(date -u)"
