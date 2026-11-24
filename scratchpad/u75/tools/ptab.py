# ptab.py : probe table  probe | CPython | L21 (b2) | u73 (b1) | head (h2)   from PB-*/q.txt + PB-*.txt full proofs
import re, sys, os
L = "/home/fabrice/git/pycsl-u75/scratchpad/u75/logs"
sys.path.insert(0, os.path.dirname(__file__))
def cls(l):
    if "Verification SUCCESS" in l: return "SUCCESS"
    if "does NOT type-check" in l: return "TC-FAIL"
    if "PIPELINE ERROR" in l:
        for k, v in (("uses `", "MODULE-VALUE"), ("module-level hook", "MODULE-HOOK"),
                     ("manipulates the import system", "STATE-MANIP"), ("imports the standard li", "STATE-MANIP"),
                     ("stores (line", "SUBMODULE-REBOUND"), ("has at import time", "SUBMODULE-REBOUND"),
                     ("wildcard import", "WILDCARD"), ("rebound after its definition", "rebound-name"),
                     ("runtime value is not", "runtime-value"), ("[ir-semantic]", "#483"), ("absolutely", "SEARCH-ORDER")):
            if k in l: return "REF " + v
        return "REF"
    if "FAIL" in l: return "FAIL"
    return "?"
def key(l):
    m = re.match(r"^\[[pq]:[a-z0-9]+\] (\S+) ", l)
    return m.group(1) if m else None
def load(tag):
    q, p = {}, {}
    for l in open(f"{L}/PB-{tag}.txt"):
        k = key(l)
        if not k: continue
        (q if l.startswith("[q:") else p)[k] = cls(l)
    return {k: (p.get(k, v) if v == "SUCCESS" else v) for k, v in q.items()}
cp = {}
for f in ("cpy-rt83.txt", "cpy-u75.txt", "cpy-rt81-u73.txt", "cpy-wit.txt"):
    for l in open(f"{L}/{f}"):
        k = l.split()[0]
        cp.setdefault(k, l.split("] ", 1)[1].strip()[-40:] if "] " in l else "?")
T = {t: load(t) for t in ("b2", "b1", "h2")}
only = "-d" in sys.argv
for k in sorted(set().union(*[set(v) for v in T.values()])):
    r = [T[t].get(k, "-") for t in ("b2", "b1", "h2")]
    c = cp.get(k, cp.get(k.replace(".py", ""), ""))
    if only and r[1] == r[2] and r[0] == r[2]: continue
    print(f"| {k} | {c} | {r[0]} | {r[1]} | {r[2]} |")
