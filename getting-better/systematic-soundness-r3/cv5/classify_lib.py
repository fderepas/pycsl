import re, sys, glob, os, json, collections
S = os.path.dirname(os.path.abspath(__file__))
CEN = "/home/fabrice/git/pycsl-cv4/getting-better/conversion-census-r3.md"

def key_of(msg, verdict):
    if verdict == "TC-OK": return "TC-OK"
    if verdict == "ABORT": return "ABORT"
    m = re.search(r"(PYCSL-[A-Z0-9-]+?)(?=[^A-Z0-9-]|$)", msg)
    if m: return m.group(1)
    if "MUTATES its receiver" in msg: return "in-place-mutator"
    m = re.search(r"[Rr][Oo][Uu][Tt][Ee] #(\d+)", msg)
    if m: return "route#" + m.group(1)
    m = re.search(r"This expression has type (.+?), but is expected to have type (.+?)(?:$| VERDICT|\s*$)", msg)
    if m:
        nt = lambda t: t.split()[0].rstrip(",").split(".")[-1] or t.split()[0]
        a = nt(m.group(1)); b = nt(m.group(2))
        return "tc:%s->%s" % (a, b)
    if verdict == "L3-TC": return "tc-other:" + re.sub(r"'[^']*'", "X", msg)[:60]
    msg = re.sub(r"^\S+\.py( \(func\S*\)| line \d+)?:? *", "", msg)
    return "other:" + re.sub(r"`[^`]*`|'[^']*'|\d+|\[[^]]*\]?", "X", msg)[:40]

def classify_log(path):
    L = open(path, encoding="utf-8", errors="replace").read().split("\n")
    stub = L[0].split("\t"); port = L[1][5:] if len(L) > 1 else ""
    rel, qn, reason = stub[1], stub[2], stub[3]
    rc = [l for l in L if l.startswith("RC\t")]
    if port.startswith("ABORT"):
        return rel, qn, reason, "ABORT", port[7:]
    txt = "\n".join(L)
    if "Verification SUCCESS" in txt:
        return rel, qn, reason, "TC-OK", ""
    for i, l in enumerate(L):
        if l.startswith("[!] PIPELINE ERROR"):
            msg = next((x for x in L[i+1:] if x.strip()), "")
            msg = re.sub(r"^\[[a-z0-9-]+\]( src/\S+:)?:?\s*", "", msg.strip())
            return rel, qn, reason, "REFUSED", msg
    # why3 type error: after File "...", line N, characters ..:
    for i, l in enumerate(L):
        if re.match(r'^File ".*", line \d+', l):
            ms = []
            for x in L[i+1:]:
                if not x.strip() or x.startswith(("File ", "[", "RC")):
                    if ms: break
                    continue
                ms.append(x.strip())
            return rel, qn, reason, "L3-TC", " ".join(ms)
    if "maximum recursion depth exceeded" in txt:
        return rel, qn, reason, "REFUSED", "maximum recursion depth exceeded"
    if rc and rc[0].split("\t")[1] in ("124", "137", "143"):
        return rel, qn, reason, "KILLED", rc[0]
    tail = [x for x in L if x.strip() and not x.startswith("RC")][-1:]
    return rel, qn, reason, "UNKNOWN", tail[0] if tail else ""

def old_table():
    rows = {}
    for l in open(CEN, encoding="utf-8"):
        if not re.match(r"^\| \d+ \| ", l): continue
        c = [x.strip() for x in l.rstrip("\n").split(" | ")]
        rel, qn, fam, va, fb, msg = c[1], c[2].strip("`"), c[3], c[4], c[5], c[6].rstrip(" |")
        v = ("TC-OK" if va == "TC-OK" else "ABORT" if va == "no-live-counterpart"
             else "L3-TC" if va.startswith("tc:") else "REFUSED")
        msg = re.sub(r"^\[[a-z0-9-]+\]( src/\S+:)?:?\s*", "", msg)
        rows[(rel, qn)] = dict(v=v, va=va, fb=fb, msg=msg, key=key_of(msg, v), fam=fam)
        k = rows[(rel, qn)]
        if k["key"].startswith(("other:", "tc-other:This expression has type")) and re.match(r"route#|PYCSL-|in-place|tc:", fb):
            k["key"] = fb if not fb.startswith("tc:") else "tc:" + "->".join(t.split(".")[-1] for t in fb[3:].split("->"))
    return rows

if __name__ == "__main__":
    new = {}
    for p in sorted(glob.glob(os.path.join(S, "logs", "*.log"))):
        if not os.path.exists(p[:-4] + ".done"): continue
        rel, qn, reason, v, msg = classify_log(p)
        new[(rel, qn)] = dict(v=v, msg=msg, key=key_of(msg, v), fam=reason, id=os.path.basename(p)[:3])
    old = old_table()
    json.dump({"%s::%s" % k: d for k, d in new.items()}, open(os.path.join(S, "new.json"), "w"), indent=1)
    json.dump({"%s::%s" % k: d for k, d in old.items()}, open(os.path.join(S, "old.json"), "w"), indent=1)
    print("new", len(new), "old", len(old))
    print(collections.Counter(d["v"] for d in new.values()))
