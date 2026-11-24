#!/usr/bin/env python3
"""cmp3.py <tag> : per probe, the --no-proof verdict on b0 / u70 / h1 and whether the h1 .mlw equals b0's / u70's."""
import os, re, sys, filecmp
U = "/home/fabrice/git/pycsl-u72/scratchpad/u72/logs"
tag = sys.argv[1]
def verdicts(t):
    d = {}
    for line in open(f"{U}/E3-{tag}.txt"):
        pass
    return d
rows = {}
cur = None
for line in open(f"{U}/E3-{tag}.txt"):
    if line.startswith("## "):
        cur = line.split()[1]; continue
    m = re.match(r"(\S+) rc=(\d+) (\S+) :: (.*)", line)
    if m and cur:
        n, rc, code, msg = m.groups()
        v = "OK" if rc == "0" else ("REF:" + (code if code != "no-code" else re.sub(r"^\[!\] PIPELINE ERROR: ", "", msg)[:50]))
        rows.setdefault(n, {})[cur] = v
for n in sorted(rows):
    r = rows[n]
    def same(a, b):
        fa, fb = f"{U}/{tag}-{a}/{n}.mlw", f"{U}/{tag}-{b}/{n}.mlw"
        if not (os.path.exists(fa) and os.path.exists(fb)):
            return "-"
        return "=" if filecmp.cmp(fa, fb, shallow=False) else "DIFF"
    print(f"{n[:52]:52} b0={r.get('b0','?')[:40]:40} u70={r.get('u70','?')[:40]:40} h1={r.get('h1','?')[:40]:40} mlw(b0,h1)={same('b0','h1')} mlw(u70,h1)={same('u70','h1')}")
