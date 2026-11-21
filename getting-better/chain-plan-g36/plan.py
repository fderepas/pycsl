#!/usr/bin/env python3
"""plan.py <chain.jsonl> : per-marker family chains -> per-family totals, cheaper-first unlock table, greedy plan."""
import json, re, sys, collections
sys.path.insert(0, __import__("os").path.dirname(__file__))
from classify import fam, FAMNAME, ev

COST = {  # S = one emitter arm, M = model extension + hand spike, L = new value model / certificate
    "MUTRECV": "M", "MUTPARAM": "L", "ALIAS": "M", "DICT": "L", "PYVAL": "M", "GETATTR": "M", "LISTSTR": "M",
    "INTSTR": "M", "RECORD": "M", "OPTREC": "M", "TUPLE": "M", "SET": "M", "STRM": "S", "GENEXP": "M",
    "NESTED": "M", "UNBOUND": "S", "EXT": "M", "FSTR": "S", "EXC": "M", "REBIND": "L", "UNIT": "S",
    "CALLABLE": "L", "WITH-AS": "M", "EFFECT": "M", "ARRAY-REASSIGN": "M", "MEMB": "M", "SYNTAX": "S",
    "OBJSTATE": "L", "ISBOOL": "S", "REF": "M", "FLOAT": "M", "HETERO": "L", "OTHER": "L", "SIG": "S",
    "STRPLUS": "S", "BOOL": "S", "RIPPLE": "S",
}
W = {"S": 1, "M": 3, "L": 8}
DNC_VACUOUS = {("frontend/pure_ast.py", "_Parser.error"), ("frontend/pure_ast.py", "_Parser.unsupported")}

rows = [json.loads(l) for l in open(sys.argv[1])]
R2 = {}
if len(sys.argv) > 2:
    for l in open(sys.argv[2]):
        j = json.loads(l); R2[(j["file"], j["qual"])] = j
rows = [R2.get((j["file"], j["qual"]), j) for j in rows]
M = []
for j in rows:
    st = j["status"]
    purged = any((c.get("act") or "").startswith("purge") for c in j.get("chain", []))
    ripple = None
    if st == "STUCK-LOCATE" and j.get("chain"):
        lc = j["chain"][-1]
        if lc.get("anc") == "error-outside-anchors":
            b = lc.get("block") or ""
            if b.startswith("type "): ripple = "RIPPLE-TYPE"
            elif re.match(r"_(any|all)_fold_\d+", b): ripple = "GENEXP-FOLD"
            else: ripple = "RIPPLE"
    key = (j["file"], j["qual"])
    fams = []; mutk = []
    for c in j.get("chain", []):
        f = fam(c)
        if f == "MUTRECV":
            mm = re.search(r"`([^`]*)\.(\w+)\(\.\.\.\)`", c.get("msg", ""))
            if mm:
                r = mm.group(1); kind = "self-field" if r.startswith("self.") else "local/param"
                mutk.append(f"{mm.group(2)}@{kind}")
        if f not in fams: fams.append(f)
    ph = "PH" in fams
    fams_real = [f for f in fams if f != "PH"]
    if ripple:
        # the terminal event is outside the ported body: re-label it
        last_f = fam(j["chain"][-1])
        if last_f in fams_real and sum(1 for c in j["chain"] if fam(c) == last_f) == 1: fams_real.remove(last_f)
        tag = {"RIPPLE": "RIPPLE", "RIPPLE-TYPE": "RIPPLE", "GENEXP-FOLD": "GENEXP"}[ripple]
        if tag not in fams_real: fams_real.append(tag)
    fc = j.get("facade") or {}
    neut_ret = any((c.get("act") or "").startswith("return->") for c in j.get("chain", []))
    cat = None
    if st.startswith("SKIP"): cat = st
    elif key in DNC_VACUOUS: cat = "SKIP-DNC-RAISEONLY(vacuous)"
    elif st == "CRASH": cat = "UNMEASURED(port crash)"
    elif ripple == "RIPPLE":
        cat = "COMPLETE"
    elif st in ("TCOK", "TCOK0"):
        if fc.get("facade") == "FACADE" and purged:
            cat = "COMPLETE"
        elif fc.get("facade") == "FACADE":
            cat = "FACADE" if (st == "TCOK0" or not neut_ret) else "FACADE?(return neutralised)"
        else:
            cat = "COMPLETE"
    else:
        cat = "INCOMPLETE"
    marks = fc.get("marks") or {}
    risk = bool(marks.get("anyval") or marks.get("zeroary") or marks.get("getattr")) or (purged and st.startswith("TCOK"))
    M.append(dict(purged=purged, ripple=ripple, file=j["file"], qual=j["qual"], status=st, cat=cat, fams=fams_real, ph=ph, mutk=mutk, risk=risk,
                  marks=marks, reason=j.get("reason"), nst=j.get("nstmts"), last=(j.get("chain") or [{}])[-1].get("msg", "")[:160] if j.get("chain") else ""))

out = []
P = out.append
cats = collections.Counter(m["cat"] for m in M)
P("## Population\n")
for k, v in sorted(cats.items(), key=lambda x: -x[1]): P(f"    {v:4d}  {k}")
P(f"    {len(M):4d}  TOTAL rows (trusted-reasons.tsv, line-prefix markers)\n")

meas = [m for m in M if m["cat"] in ("COMPLETE", "INCOMPLETE", "FACADE", "FACADE?(return neutralised)")]
# per-family totals
P("## Per-family totals (measured rows only)\n")
P("    fam            cost  in-chain  first  only-blocker(complete)  complete-chains-containing")
fc_ = collections.Counter(); ff = collections.Counter(); fo = collections.Counter(); fcc = collections.Counter()
for m in meas:
    for f in m["fams"]: fc_[f] += 1
    if m["fams"]: ff[m["fams"][0]] += 1
    if m["cat"] == "COMPLETE":
        for f in m["fams"]: fcc[f] += 1
        if len(m["fams"]) == 1: fo[m["fams"][0]] += 1
for f, n in fc_.most_common():
    P(f"    {f:<14} {COST.get(f,'?'):>4}  {n:8d}  {ff[f]:5d}  {fo[f]:22d}  {fcc[f]:26d}   {FAMNAME.get(f,f).split(' ',1)[1][:90]}")
P("")

comp = [m for m in M if m["cat"] == "COMPLETE"]
inc = [m for m in M if m["cat"] == "INCOMPLETE"]


def unlocked(fixed, pop):
    return [m for m in pop if set(m["fams"]) <= fixed]


# cheaper-first table
P("## Cheaper-first: markers type-check-clean if family F and every family of cost <= cost(F) ranked above it are fixed\n")
order = sorted(fc_, key=lambda f: (W[COST.get(f, "L")], -fcc[f], -fc_[f]))
fixed = set(); prev = len(unlocked(set(), comp))
P(f"    (no fix: {prev} complete chains already clean = TCOK0)")
for f in order:
    fixed.add(f)
    u = unlocked(fixed, comp); ui = unlocked(fixed, inc)
    P(f"    +{f:<14} [{COST.get(f,'?')}]  complete-unlocked {len(u):4d} (+{len(u)-prev})   incomplete-whose-known-chain-is-covered {len(ui):4d}")
    prev = len(u)
P("")

# greedy plan with fractional credit
P("## Greedy plan (complete chains; score = sum over chains of 1/#unfixed-families-in-chain, divided by cost weight)\n")
fixed = set(); steps = []
base = unlocked(fixed, comp)
cum = len(base)
remaining = set(fc_)
while remaining:
    best = None
    for f in remaining:
        sc = 0.0; newly = 0
        for m in comp:
            unf = set(m["fams"]) - fixed
            if f in unf:
                sc += 1.0 / len(unf)
                if len(unf) == 1: newly += 1
        sc_w = sc / W[COST.get(f, "L")]
        k = (newly / W[COST.get(f, "L")], sc_w)
        if best is None or k > best[0]: best = (k, f, newly, sc)
    (k, f, newly, sc) = best
    if sc == 0: break
    before = set((m["file"], m["qual"]) for m in unlocked(fixed, comp))
    fixed.add(f); remaining.discard(f)
    now = unlocked(fixed, comp)
    new = [m for m in now if (m["file"], m["qual"]) not in before]
    newi = [m for m in unlocked(fixed, inc) if set(m["fams"]) and f in m["fams"]]
    steps.append((f, new, len(now), newi))
for i, (f, new, c, newi) in enumerate(steps, 1):
    P(f"{i:2d}. {f} [{COST.get(f,'?')}] — {FAMNAME.get(f,f).split(' ',1)[1]}")
    P(f"    unlocks {len(new)} (cumulative {c} incl. {len(base)} TCOK0){'  — ' + ', '.join(sorted(set(m['file'].split('/')[-1] + '::' + m['qual'] + ('*' if m['risk'] else '') for m in new))) if new else ''}")
    if newi:
        P(f"    + {len(newi)} INCOMPLETE chains whose known prefix is now covered (tail unmeasured): " + ", ".join(sorted(m['qual'] for m in newi))[:900])
P("")
P("(* = final emitted body carries erasure marks: any-valued / 0-ary vals / getattr — FACADE RISK, inspect before landing)\n")

P("## TCOK0 (type-check clean with ZERO neutralisation)\n")
for m in M:
    if m["status"] == "TCOK0":
        P(f"    {m['cat']:<28} {m['file']}::{m['qual']}  marks={m['marks']}")
P("")
P("## FACADE flags\n")
for m in M:
    if m["cat"].startswith("FACADE"):
        P(f"    {m['cat']:<28} {m['file']}::{m['qual']}  chain={m['fams']}")
P("")
P("## MUTRECV kind x receiver (markers)\n")
mk = collections.Counter()
for m in meas:
    for k in set(m["mutk"]): mk[k] += 1
for k, v in mk.most_common(): P(f"    {v:4d}  {k}")
P("")
P("## Per-marker chains\n")
P("    cat | file::qual | status | families (ordered) | PH? | last msg")
for m in sorted(M, key=lambda m: (m["cat"], m["file"], m["qual"])):
    P(f"    {m['cat']} | {m['file']}::{m['qual']} | {m['status']} | {' > '.join(m['fams'])} | {'PH' if m['ph'] else ''}{' risk' if m['risk'] else ''} | {' '.join(m['last'].split())[:110]}")
print("\n".join(out))
json.dump(M, open(sys.argv[1].replace(".jsonl", ".markers.json"), "w"), indent=0)
