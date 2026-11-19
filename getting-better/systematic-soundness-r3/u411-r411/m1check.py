#!/usr/bin/env python3
"""m1check.py <basedir> <canddir> <name.mlw>... : M1 inspection for route #411.
Normalises BOTH texts to the same canonical form and requires equality:
  * candidate: drop the `module PyCSL_StrLit .. end` block (+ its blank line) and every
    `  use PyCSL_StrLit` line; fold every `(pystr_cat A B)` / `(pystr_chr N)` / plain literal
    back to one canonical literal token;
  * base: canonicalise every literal token (decode escapes -> bytes -> canonical spelling).
So the ONLY permitted difference is the literal re-encoding + the module/use lines."""
import re, sys, os

def decode(tok):
    b, j, s = [], 0, tok[1:-1]
    while j < len(s):
        c = s[j]
        if c != "\\":
            b.append(ord(c)); j += 1; continue
        n = s[j + 1]
        if s[j+1:j+4].isdigit() and len(s[j+1:j+4]) == 3:
            b.append(int(s[j+1:j+4])); j += 4
        elif n == "x":
            b.append(int(s[j+2:j+4], 16)); j += 4
        elif n == "o":
            b.append(int(s[j+2:j+5], 8)); j += 5
        else:
            b.append(ord({"n": "\n", "r": "\r", "t": "\t", "b": "\b"}.get(n, n))); j += 2
    return b

def canon(bs):
    return "<<" + ",".join(map(str, bs)) + ">>"

LIT = r'"(?:[^"\\]|\\.)*"'
def canon_base(t):
    return re.sub(LIT, lambda m: canon(decode(m.group(0))), t)

def canon_cand(t):
    t = re.sub(r"module PyCSL_StrLit\n.*?\nend\n\n", "", t, count=1, flags=re.S)
    t = t.replace("\n  use PyCSL_StrLit", "")
    t = re.sub(LIT, lambda m: canon(decode(m.group(0))), t)
    t = re.sub(r"\(pystr_chr (\d+)\)", lambda m: canon([int(m.group(1))]), t)
    pat = re.compile(r"\(pystr_cat <<([\d,]*)>> <<([\d,]*)>>\)")
    while True:
        t2 = pat.sub(lambda m: "<<" + ",".join(x for x in (m.group(1), m.group(2)) if x) + ">>", t)
        if t2 == t:
            return t
        t = t2

bad = 0
for n in sys.argv[3:]:
    a = canon_base(open(os.path.join(sys.argv[1], n)).read())
    b = canon_cand(open(os.path.join(sys.argv[2], n)).read())
    ok = a == b
    bad += not ok
    print(("OK   " if ok else "DIFF ") + n)
sys.exit(1 if bad else 0)
