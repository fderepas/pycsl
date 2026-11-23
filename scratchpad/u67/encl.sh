#!/bin/bash
# encl.sh <live file> <line> : enclosing def name and mirror twin status
f=$1; n=$2
name=$(awk -v n=$n 'NR<=n && /^ *def /{l=$0} NR==n{print l; exit}' $f | sed -E 's/^ *def ([A-Za-z0-9_]+).*/\1/')
m=/home/fabrice/git/pycsl-u67/src/self-annotate/src/${f#*/src/pycsl/}
echo "$f:$n -> $name"
if [ -f "$m" ]; then
  ln=$(grep -n "def $name(" $m | head -1 | cut -d: -f1)
  if [ -z "$ln" ]; then echo "  twin: ABSENT in $m"; else
  s=$((ln>12?ln-12:1)); if sed -n "${s},${ln}p" $m | grep -q '#@ \\trusted'; then echo "  twin: TRUSTED ($m:$ln)"; else echo "  twin: VERIFIED? ($m:$ln)"; fi; fi
else echo "  no mirror file"; fi
