#!/bin/bash
while read rel spec; do
  [ -z "$rel" ] && continue
  out=$(timeout 300 python3 /home/fabrice/git/pycsl/scratchpad/w4/diag_any.py "$rel" "$spec" 2>&1)
  echo "##### $rel $spec"
  echo "$out" | grep '^>>' | head -2
done < "$1"
