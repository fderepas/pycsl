#!/usr/bin/env python3
"""plan37.py <first.jsonl> : ch32 first-blocker census -> population, per-family totals, TCOK0 + facade, unlock table.
Families = g36 classify.py rules, PREFIXED by the refusal codes landed since 2026-10-17 (#277-#303 etc.).
PH does not apply (nothing is neutralised before the first blocker)."""
import json, re, sys, collections
sys.path.insert(0, __import__("os").path.dirname(__file__))
import classify
from classify import ev

NEW = [
    ("APPENDLEN `.append` to a list whose length the lowering cannot track (non-growable local: field/call-result bound)", lambda e: "appends to a list whose length this lowering cannot track" in e["m"]),
    ("COMPRECV mutator/call on a COMPUTED receiver (subscript / tuple elt / call result / attribute of one)", lambda e: "on a COMPUTED receiver" in e["m"]),
    ("ERASED erased (Any/object/unannotated) value flows into a builtin-typed parameter slot", lambda e: "an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot" in e["m"]),
    ("MCYCLE recursion through a METHOD/constructor call (bodyless stub would assume termination)", lambda e: "call one another in a cycle" in e["m"] or re.search(r"\[ir-semantic\] \S+: the functions \[", e["m"]) is not None),
    ("TUPALIAS mutating a collection aliased by a tuple-unpacking assignment", lambda e: "TUPLE-UNPACKING assignment aliases" in e["m"]),
    ("R301 dropped unpacking / loop target of tuple-with-tuple/attribute shape (route #301)", lambda e: "route #301" in e["m"]),
    ("ELEMSTORE element store through a value not modelled as a list (abstract subscript_set)", lambda e: "element store through a value the model does not represent as a list" in e["m"]),
    ("DEFASSIGN local read that is not definitely assigned on every path", lambda e: "not definitely assigned" in e["m"]),
    ("OPAQUEWRITE a WRITING call inside an opaquely-lowered comprehension/generator/lambda", lambda e: "which WRITES" in e["m"]),
    ("KWARG builtin keyword argument discarded by its lowering (sorted key= / open encoding=)", lambda e: "keyword arguments are DISCARDED" in e["m"]),
    ("WITH-AS context manager", lambda e: "proven inert" in e["m"]),
    ("ALIAS dict/set value observed through two names / mutated dict aliased or stored", lambda e: "in-place mutation reached through another name" in e["m"]),
    ("NOWHY3 why3 not on PATH (census artifact)", lambda e: "not found on PATH" in e["m"]),
]
COST = dict(classify_cost := {
    "MUTRECV": "M", "MUTPARAM": "L", "ALIAS": "M", "DICT": "L", "PYVAL": "M", "GETATTR": "M", "LISTSTR": "M",
    "INTSTR": "M", "RECORD": "M", "OPTREC": "M", "TUPLE": "M", "SET": "M", "STRM": "S", "GENEXP": "M",
    "NESTED": "M", "UNBOUND": "S", "EXT": "M", "FSTR": "S", "EXC": "M", "REBIND": "L", "UNIT": "S",
    "CALLABLE": "L", "WITH-AS": "M", "EFFECT": "M", "ARRAY-REASSIGN": "M", "MEMB": "M", "SYNTAX": "S",
    "OBJSTATE": "L", "ISBOOL": "S", "REF": "M", "FLOAT": "M", "HETERO": "L", "OTHER": "L", "SIG": "S",
    "STRPLUS": "S", "BOOL": "S",
    "APPENDLEN": "M", "COMPRECV": "M", "ERASED": "M", "MCYCLE": "L", "TUPALIAS": "M", "R301": "S",
    "ELEMSTORE": "L", "DEFASSIGN": "M", "OPAQUEWRITE": "M", "KWARG": "M", "UNKNOWN-LTC": "M",
})
W = {"S": 1, "M": 3, "L": 8}
FAMNAME = dict(classify.FAMNAME)
for n, _ in NEW: FAMNAME.setdefault(n.split(" ")[0], n)
FAMNAME["UNKNOWN-LTC"] = "UNKNOWN-LTC L3-tc failed but no located diagnostic in the output (unparsed)"


def fam1(c):
    e = ev(c)
    for name, p in NEW + classify.RULES:
        try:
            if p(e): return name.split(" ")[0].replace("MUTRECV2", "MUTRECV")
        except Exception: pass
    if c.get("kind") == "unknown": return "UNKNOWN-LTC"
    return "OTHER"


rows = [json.loads(l) for l in open(sys.argv[1])]
out = []
P = collections.Counter(); F = collections.Counter(); byfam = collections.defaultdict(list)
for j in rows:
    st = j["status"]
    if st.startswith("SKIP") or st == "TCOK0":
        P[st] += 1; continue
    P["BLOCKED"] += 1
    f = fam1(j["chain"][0]); j["fam"] = f; F[f] += 1; byfam[f].append(j)
print("## Population\n\n```")
for k, v in P.most_common(): print(f"  {v:5d}  {k}")
print(f"  {len(rows):5d}  TOTAL rows (trusted-reasons.tsv)\n```\n")
print("## Per-family totals (FIRST blocker)\n\n```")
for f, n in F.most_common(): print(f"  {n:4d}  {COST.get(f,'?')}  {FAMNAME.get(f, f)}")
print("```\n")
print("## Cheaper-first unlock table\n")
print("Rank = cost class (S=1 emitter arm, M=3 model extension + spike, L=8 new value model / certificate),")
print("then markers whose FIRST blocker is this family (desc). Unlocking the first blocker does NOT make a")
print("marker landable: most g36 chains had further blockers behind the first.\n")
print("| # | family | cost | markers (first blocker) | example markers |")
print("|---|---|---|---|---|")
for i, (f, n) in enumerate(sorted(F.items(), key=lambda x: (W[COST.get(x[0], 'L')], -x[1])), 1):
    ex = ", ".join(sorted("`%s`" % j["qual"].split(".")[-1] for j in byfam[f])[:4])
    print(f"| {i} | {f} | {COST.get(f,'?')} | {n} | {ex} |")
print("\n## TCOK0 (L3-tc clean at HEAD, zero neutralisation) + facade check\n\n```")
for j in rows:
    if j["status"] == "TCOK0":
        fc = j.get("facade") or {}
        print(f"  {j['file']}::{j['qual']}  facade={fc.get('facade')} used={fc.get('params_used')} marks={fc.get('marks')} reason={j['reason']}")
print("```\n")
if "--rows" in sys.argv:
    print("## Appendix — per-marker first blocker\n\n```")
    for j in rows:
        if "fam" in j:
            c = j["chain"][0]; e = ev(c)
            print(f"  {j['fam']:<11} {j['file']}::{j['qual']} | {(c.get('stmt') or '')[:70]} | {e['m'][:110]}")
        else:
            print(f"  {j['status']:<11} {j['file']}::{j['qual']}")
    print("```")
