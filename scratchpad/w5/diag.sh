#!/bin/bash
# diag.sh <mirror-relpath> <Class:name|:name> [context-lines]
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
cd /home/fabrice/git/pycsl
REL="$1"; SPEC="$2"; CTX="${3:-14}"
python3 scratchpad/w4/port_sig.py "$REL" "$SPEC" >/dev/null || exit 1
M="src/self-annotate/src/${REL%.py}.mlw"
PYTHONHASHSEED=0 timeout 900 python3 src/pycsl/pycsl.py "src/self-annotate/src/$REL" --import-path src/pycsl --no-proof --keep-mlw > /tmp/diag_out.txt 2>&1
grep -A3 '^File "' /tmp/diag_out.txt | head -5
grep -E '^\[!\] PIPELINE ERROR' -A2 /tmp/diag_out.txt | head -3
LN=$(grep -m1 '^File "' /tmp/diag_out.txt | sed 's/.*line \([0-9]*\),.*/\1/')
if [ -n "$LN" ] && [ -f "$M" ]; then
  echo "--- $M around $LN ---"
  sed -n "$((LN>CTX ? LN-CTX : 1)),$((LN+3))p" "$M" | cat -n | sed "s/^/  /"
fi
rm -f "$M"
git checkout "src/self-annotate/src/$REL" >/dev/null 2>&1
