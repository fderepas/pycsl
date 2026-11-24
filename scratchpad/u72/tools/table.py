#!/usr/bin/env python3
"""table.py : probe table, CPython + full-proof verdict on b0 (L20) / u70 / h1, from logs/f1-*/<probe>.log."""
import os, re, glob
U = "/home/fabrice/git/pycsl-u72/scratchpad/u72/logs"
cpy = {}
for f in glob.glob(f"{U}/cpython-*.txt"):
    for line in open(f):
        if " :: " in line:
            k, v = line.rstrip("\n").split(" :: ", 1)
            cpy[k.strip()] = v.strip() or "(assert ok)"
def verdict(t, n):
    p = f"{U}/f1-{t}/{n}.log"
    if not os.path.exists(p):
        return "-"
    s = open(p, errors="replace").read()
    if re.search(r"quota|No space left|EDQUOT", s, re.I):
        return "VOID"
    if "Verification SUCCESS" in s:
        return "SUCCESS"
    m = re.search(r"(PYCSL-[A-Z0-9-]+)", s)
    if "PIPELINE ERROR" in s:
        return "REFUSED " + (m.group(1) if m else "")
    if "FAILED" in s or "NOT a success" in s:
        return "FAILED"
    m2 = re.search(r"unbound [^\n]*|raises unlisted[^\n]*|already defined[^\n]*", s)
    return "TC-ERROR " + (m2.group(0)[:40] if m2 else "")
names = sorted({os.path.basename(p)[:-4] for p in glob.glob(f"{U}/f1-h1/*.log")})
print("| probe | CPython | L20 b0 | u70 | head |\n|---|---|---|---|---|")
for n in names:
    print(f"| {n} | {cpy.get(n, '?')[:40]} | {verdict('b0', n)} | {verdict('u70', n)} | {verdict('h1', n)} |")
