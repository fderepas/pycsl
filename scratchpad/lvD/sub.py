#!/usr/bin/env python3
# sub.py <file> : apply replacements from $SUBS (a python file defining SUBS=[(old,new),...]); each must hit exactly once
import sys, os
f = sys.argv[1]; s = open(f).read(); ns = {}
exec(open(os.environ["SUBS"]).read(), ns)
for o, n in ns["SUBS"]:
    c = s.count(o)
    print("sub", repr(o[:60]), "hits", c)
    if c != 1: sys.exit("BAD COUNT")
    s = s.replace(o, n)
open(f, "w").write(s)
