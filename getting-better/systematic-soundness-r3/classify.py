#!/usr/bin/env python3
"""Classify every confirmed red-team false proof (scratchpad/rt6..rt30) by root-cause family.

Sources (read-only):  /home/fabrice/git/pycsl/scratchpad/rtN/
  rt25..rt30 : FINDINGS.txt sections '#NNN TITLE' list the confirmed probes -> exact route -> family (routes.tsv)
  rt11..rt24 : progress.txt '<<<<< FALSE PROOF' lines (probe names that exist as rtN/<name>.py);
               route assigned by a per-round probe-name-prefix map (the red team's own grouping, see PREFIX)
  rt6..rt10  : prose progress only -> route-level counts from README 'OPENED (red team N ...)' (routes.tsv), no probe list
Families: a construct ignored / partially modelled   b stdlib/builtin semantics assumed
          c erased value treated as known            d class machinery partly modelled
          e aliasing / effects / frames              f contract plumbing   g name resolution / shadowing
Usage: classify.py [--probes out.tsv]
"""
import os, re, sys, collections
RT = "/home/fabrice/git/pycsl/scratchpad"
HERE = os.path.dirname(os.path.abspath(__file__))
routes = {}
for ln in open(os.path.join(HERE, "routes.tsv")):
    if ln.startswith("#") or not ln.strip(): continue
    r, rnd, fam, sub, title = ln.rstrip("\n").split("\t")
    routes[int(r)] = (int(rnd), fam, sub, title)

# per-round prefix -> route (first match wins; '' = default)
PREFIX = {
 11: [("", 303)], 12: [("", 304)],
 13: [("r", 305), ("", 306)],
 14: [("l1", 309), ("o05", 308), ("q02", 308), ("q03", 308), ("q10", 308), ("q11", 308), ("o15", 308), ("r04", 308), ("", 307)],
 15: [("a05", 311), ("j", 315), ("b04", 315), ("m07", 314), ("n07", 314), ("o08", 314),
      ("r0", 313), ("s0", 313), ("t0", 313), ("u0", 313), ("", 312)],
 16: [("o0", 317), ("", 316)],
 17: [("l4", 318), ("l5", 318), ("p1", 319), ("p0", 319), ("", 320)],
 18: [("d", 321), ("j", 321), ("n0", 321), ("k", 323), ("g", 322), ("h01", 322), ("s0", 322),
      ("p", 324), ("q", 324), ("", 321)],
 19: [("k", 326), ("p03", 326), ("p04", 326), ("x0", 326), ("z0", 326), ("", 325)],
 20: [("n", 327), ("t", 328), ("b", 329), ("", 330)],
 21: [("c01", 333), ("c21", 333), ("", 334)],
 22: [("", 335)],
 23: [("F4", 338), ("F5", 338), ("", 336)],
 24: [("d", 339), ("e", 339), ("c", 340), ("g", 340), ("o", 341), ("i", 342), ("x", 342), ("b", 323), ("", 339)],
}
# rt24 b* = sorted/list.index/count residuals -> builtin family; route 323 used as a builtin-family carrier
NAME = re.compile(r"\b([A-Za-z]\d{2,3}[a-z]?_[A-Za-z0-9_]+?)(?:\.py)?\b")

def exists(r, n): return os.path.exists(f"{RT}/rt{r}/{n}.py")

def probes_progress(r):
    out = []
    for ln in open(f"{RT}/rt{r}/progress.txt"):
        if "FALSE PROOF" not in ln: continue
        for tok in ln.split():
            tok = tok.rstrip(",:")
            if exists(r, tok) and tok not in out: out.append(tok)
    return out

def probes_findings(r):
    conf = None
    cf = f"{RT}/rt{r}/confirmed.txt"
    if os.path.exists(cf):
        conf = set()
        for ln in open(cf):
            if ln.startswith("#") or not ln.strip(): continue
            conf.add(ln.split()[0].replace(".py", ""))
    cur, got = None, {}
    for ln in open(f"{RT}/rt{r}/FINDINGS.txt"):
        m = re.match(r"^(?:ROUTE )?#(\d{3})\b", ln)
        if m: cur = int(m.group(1)); continue
        if cur is None or cur not in routes: continue
        if re.match(r"^\s*\(", ln) or "Refused/failed for contrast" in ln or "contrast" in ln.lower(): continue
        for n in NAME.findall(ln):
            if not exists(r, n): continue
            if conf is not None and n not in conf: continue
            got.setdefault(n, cur)
    if conf:
        # second pass: short ids ('n07', 'b47') cited inside a section
        cur = None
        for ln in open(f"{RT}/rt{r}/FINDINGS.txt"):
            m = re.match(r"^(?:ROUTE )?#(\d{3})\b", ln)
            if m: cur = int(m.group(1)); continue
            if cur is None or cur not in routes: continue
            if "contrast" in ln.lower() or "fail correctly" in ln.lower() or "FAILS correctly" in ln: continue
            for sid in re.findall(r"\b([a-z]\d{2,3}[a-z]?)\b", ln):
                for n in conf:
                    if n not in got and n.startswith(sid + "_"): got[n] = cur
        for n in conf:
            if n not in got: got[n] = None
    return got

rows = []
for r in range(11, 31):
    if r >= 25:
        for n, rt in probes_findings(r).items(): rows.append((r, n, rt, "exact" if rt else "unmapped"))
    else:
        for n in probes_progress(r):
            nm = n.replace(f"rt{r}_", "")
            for pre, rt in PREFIX[r]:
                if nm.startswith(pre): break
            rows.append((r, n, rt, "prefix"))

fams = "abcdefg"
FN = dict(a="construct ignored/partial", b="stdlib/builtin assumed", c="erased value as known",
          d="class machinery", e="alias/effect/frame", f="contract plumbing", g="names/shadowing")
def fam(rt): return routes[rt][1] if rt in routes else "?"
def sub(rt): return routes[rt][2] if rt in routes else "?"

print("== ROUTE level (root causes opened per red-team round, rt6..rt30) ==")
cnt = collections.Counter(); per = collections.defaultdict(collections.Counter)
for rt, (rnd, f, s, t) in routes.items():
    if 6 <= rnd <= 30 and rt != 226: cnt[f] += 1; per[rnd][f] += 1
print("round " + " ".join(f"{x:>3}" for x in fams) + "  tot")
for rnd in sorted(per): print(f"rt{rnd:<3} " + " ".join(f"{per[rnd][x]:>3}" for x in fams) + f"  {sum(per[rnd].values()):>3}")
print("TOTAL " + " ".join(f"{cnt[x]:>3}" for x in fams) + f"  {sum(cnt.values()):>3}")
print()
print("== PROBE level (confirmed false proofs rt11..rt30; rt25+ exact route, rt11-24 prefix-mapped) ==")
pc = collections.Counter(); pr = collections.defaultdict(collections.Counter); ps = collections.Counter()
for r, n, rt, how in rows:
    pc[fam(rt)] += 1; pr[r][fam(rt)] += 1
    if fam(rt) == "d": ps[sub(rt)] += 1
print("round " + " ".join(f"{x:>3}" for x in fams) + "   ?  tot")
for r in sorted(pr): print(f"rt{r:<3} " + " ".join(f"{pr[r][x]:>3}" for x in fams) + f" {pr[r]['?']:>3}  {sum(pr[r].values()):>3}")
print("TOTAL " + " ".join(f"{pc[x]:>3}" for x in fams) + f" {pc['?']:>3}  {sum(pc.values()):>3}")
print("last-8 rounds (rt23..rt30) by family:", {x: sum(pr[r][x] for r in range(23, 31)) for x in fams + "?"})
print("class-machinery (d) subfamilies:", dict(ps.most_common()))
for x in fams: print(f"  {x} = {FN[x]}")
if "--probes" in sys.argv:
    with open(sys.argv[sys.argv.index("--probes") + 1], "w") as fo:
        for r, n, rt, how in rows: fo.write(f"rt{r}\t{n}\t{rt}\t{fam(rt)}\t{sub(rt)}\t{how}\n")
