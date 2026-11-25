#!/usr/bin/env python3
"""merge_census.py <census.tsv> <rows.tsv> : replace the row of every witness named in rows.tsv (append if absent)."""
import sys
cen, rows = sys.argv[1], sys.argv[2]
new = {}
order = []
for line in open(rows):
    k = line.split("\t", 1)[0]
    new[k] = line if line.endswith("\n") else line + "\n"
    order.append(k)
out, seen = [], set()
for line in open(cen):
    k = line.split("\t", 1)[0]
    if k in new:
        if k not in seen:
            out.append(new[k]); seen.add(k)
        continue
    out.append(line)
for k in order:
    if k not in seen:
        out.append(new[k]); seen.add(k)
open(cen, "w").write("".join(out))
print("replaced/added", len(seen))
