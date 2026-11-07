#!/bin/bash
# batch.sh <file-with "relpath Class:name" lines>
while read rel spec; do
  [ -z "$rel" ] && continue
  echo "########## $rel $spec"
  timeout 300 python3 /home/fabrice/git/pycsl/scratchpad/w4/diag_any.py "$rel" "$spec" 2>&1 | grep -v "^  " | head -3
  timeout 300 python3 /home/fabrice/git/pycsl/scratchpad/w4/diag_any.py "$rel" "$spec" 2>&1 | grep "^>>" | head -4
done < "$1"
