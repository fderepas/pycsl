#!/bin/bash
# qtab.sh <dir-prefix> <tags...> : one line per probe: name | verdict per tag (S = Verification SUCCESS, R = PIPELINE ERROR, T = tc fail, ? other)
P=$1; shift
for t in "$@"; do sed -E 's/^\[([dpw])\] ([^ ]+) .*/\2 \0/' $P-$t.txt | grep -v '^##' | awk -v t=$t '{v="?"; if ($0 ~ /Verification SUCCESS/) v="S"; else if ($0 ~ /PIPELINE ERROR/) v="R"; else if ($0 ~ /NOT type-check/) v="T"; else if ($0 ~ /Verification FAIL|NOT a success/) v="F"; print $1, t, v}'; done |
awk '{k[$1]=1; v[$1,$2]=$3} END {for (n in k) {printf "%s", n; for (i=2;i<=ARGC;i++); print ""}}' > /dev/null
for t in "$@"; do sed -E 's/^\[([dpw])\] ([^ ]+) .*/\2/' $P-$t.txt | grep -v '^##' > /tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/n.$t; done
python3 - "$P" "$@" <<'PY'
import sys,re
P=sys.argv[1]; tags=sys.argv[2:]; rows={}; order=[]
for t in tags:
    for l in open(f"{P}-{t}.txt"):
        m=re.match(r"^\[([dpw])\] (\S+) ",l)
        if not m: continue
        n=m.group(2)
        v="S" if "Verification SUCCESS" in l else "R" if "PIPELINE ERROR" in l else "T" if "NOT type-check" in l else "F" if ("Verification FAIL" in l or "NOT a success" in l) else "?"
        if n not in rows: rows[n]={}; order.append(n)
        rows[n][t]=v
for n in order:
    print(n, "|", " ".join(f"{t}={rows[n].get(t,'-')}" for t in tags))
PY
