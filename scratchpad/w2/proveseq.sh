#!/bin/bash
# Prove the given mirrors SEQUENTIALLY (never stacked, lesson (ai)); log a line per file.
set -u
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
LOGDIR="$1"; shift
for f in "$@"; do
  key=$(echo "$f" | tr '/' '_')
  echo "[START $(date -u +%H:%M:%S)] $f" >> "$LOGDIR/seq.status"
  PYTHONHASHSEED=0 python3 -u src/pycsl/pycsl.py "$f" --import-path src/pycsl \
      --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' > "$LOGDIR/$key.log" 2>&1
  v=$(grep -c "Prover result is: Valid" "$LOGDIR/$key.log")
  t=$(grep -c "Prover result is:" "$LOGDIR/$key.log")
  s=$(grep -c "Verification SUCCESS" "$LOGDIR/$key.log")
  echo "[DONE  $(date -u +%H:%M:%S)] $f valid=$v total=$t success=$s" >> "$LOGDIR/seq.status"
done
echo "[ALLDONE $(date -u +%H:%M:%S)]" >> "$LOGDIR/seq.status"
