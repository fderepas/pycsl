"""(o4) APPLIED TO THE WHOLE POPULATION: rank every `\trusted` marker by its live body's CALLEE
CLOSURE against the constructs the campaign has MEASURED as blocked, instead of by line count.

Blocked constructs are the measured ones: the in-place mutators behind one refusal
(pop/extend/update/insert/sort/remove/reverse/setdefault — 104 markers per the gen-#31 census),
`str.join`, dict `.items()`/`.keys()` iteration, and `re` (findall/match/sub/search/compile).
"""
import ast, builtins, collections, os, re, sys

MIRROR, LIVE = "src/self-annotate/src", "src/pycsl"
BLOCKED_METHODS = {
    "pop": "in-place-mutator", "extend": "in-place-mutator", "update": "in-place-mutator",
    "insert": "in-place-mutator", "sort": "in-place-mutator", "remove": "in-place-mutator",
    "reverse": "in-place-mutator", "setdefault": "setdefault-refusal",
    "join": "str.join", "items": "dict-items-iteration", "values": "dict-values-iteration",
    "findall": "regex", "match": "regex", "sub": "regex", "search": "regex", "compile": "regex",
}

def marked(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    tree = ast.parse("\n".join(lines))
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        i = n.lineno - 2
        while i >= 0:
            s = lines[i].strip()
            if not (s.startswith("#") or s.startswith("@") or not s):
                break
            if s.startswith(r"#@ \trusted"):
                out.append(n.name); break
            i -= 1
    return out

# index live defs by (file, name) and by bare name
live_defs = {}
for dp, dn, fns in os.walk(LIVE):
    dn[:] = [d for d in dn if d != "__pycache__"]
    for fn in sorted(fns):
        if not fn.endswith(".py"): continue
        p = os.path.join(dp, fn)
        try: t = ast.parse(open(p, encoding="utf-8").read())
        except Exception: continue
        for n in ast.walk(t):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                live_defs.setdefault(n.name, []).append((p, n))

rows = []
for dp, dn, fns in os.walk(MIRROR):
    dn[:] = [d for d in dn if d != "__pycache__"]
    for fn in sorted(fns):
        if not fn.endswith(".py"): continue
        mp = os.path.join(dp, fn)
        lp = mp.replace(MIRROR, LIVE, 1)
        for name in marked(mp):
            cands = live_defs.get(name, [])
            pick = next((c for c in cands if c[0] == lp), cands[0] if cands else None)
            if pick is None:
                rows.append((mp, name, None, ["NO-LIVE-DEF"], 0)); continue
            p, node = pick
            blockers, size = set(), node.end_lineno - node.lineno + 1
            for x in ast.walk(node):
                if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute):
                    b = BLOCKED_METHODS.get(x.func.attr)
                    if b: blockers.add(b)
            rows.append((mp, name, p, sorted(blockers), size))

clear = [r for r in rows if r[3] == [] and r[2]]
blocked = [r for r in rows if r[3] and r[2]]
nolive = [r for r in rows if not r[2]]
print(f"markers scanned: {len(rows)}")
print(f"  BLOCKED by a measured wall in the live body : {len(blocked)}")
print(f"  NO live def found                           : {len(nolive)}")
print(f"  CLEAR of every measured wall                : **{len(clear)}**")
c = collections.Counter(b for r in blocked for b in r[3])
print("\nblockers by frequency:")
for b, k in c.most_common(): print(f"   {k:4d}  {b}")
print(f"\nthe CLEAR list, smallest live body first (top 30 of {len(clear)}):")
for mp, name, p, _, size in sorted(clear, key=lambda r: r[4])[:30]:
    print(f"   {size:5d} lines  {mp.replace(MIRROR+'/','')}::{name}")
