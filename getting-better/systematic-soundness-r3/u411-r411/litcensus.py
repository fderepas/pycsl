#!/usr/bin/env python3
"""litcensus.py <dir>... : list .mlw files holding a WhyML string literal (outside comments /
attributes) whose decoded bytes are not all printable-ASCII-other-than-quote/backslash.
Independent re-implementation of the route-#411 lexer, for cross-checking the byte-diff."""
import sys, os, re

def unsafe_literals(t):
    i, n, dep, out = 0, len(t), 0, []
    while i < n:
        if dep:
            if t.startswith("(*)", i): i += 3
            elif t.startswith("*)", i): i += 2; dep -= 1
            elif t.startswith("(*", i): i += 2; dep += 1
            else: i += 1
            continue
        if t.startswith("(*)", i): i += 1; continue
        if t.startswith("(*", i): i += 2; dep = 1; continue
        if t.startswith(("[@", "[#"), i):
            j = t.find("]", i); i = n if j < 0 else j + 1; continue
        if t[i] != '"': i += 1; continue
        j = i + 1
        while j < n and t[j] != '"':
            j += 2 if t[j] == "\\" else 1
        tok = t[i:j + 1]; i = j + 1
        body = tok[1:-1]
        if "\\" in body or any(not (32 <= ord(c) <= 126) for c in body):
            # an escape that decodes to a safe byte (\x41, \') is rare; report all escapes
            out.append(tok)
    return out

for d in sys.argv[1:]:
    for f in sorted(os.listdir(d)):
        if f.endswith(".mlw"):
            lits = unsafe_literals(open(os.path.join(d, f), encoding="utf-8", errors="replace").read())
            if lits:
                print(f"{f}\t{len(lits)}\t{' '.join(sorted(set(lits)))[:200]}")
