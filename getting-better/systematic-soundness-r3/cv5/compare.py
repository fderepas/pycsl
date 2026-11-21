import sys, os, json, glob, collections
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)
from classify_lib import classify_log, key_of
new = {}
for p in sorted(glob.glob(os.path.join(S, "logs", "*.log"))):
    if not os.path.exists(p[:-4] + ".done"): continue
    rel, qn, reason, v, msg = classify_log(p)
    new["%s::%s" % (rel, qn)] = dict(v=v, msg=msg, key=key_of(msg, v), fam=reason, id=os.path.basename(p)[:3])
old = json.load(open(os.path.join(S, "../cv4census/new.json")))
json.dump(new, open(os.path.join(S, "cv5.json"), "w"), indent=1)
print("cv5", len(new), "cv4", len(old))
print("cv5 totals", collections.Counter(d["v"] for d in new.values()))
print("cv4 totals", collections.Counter(d["v"] for d in old.values()))
print("only cv5:", [k for k in new if k not in old]); print("only cv4:", [k for k in old if k not in new and k.split('::')[0]])
tr = collections.Counter((old[k]["v"], new[k]["v"]) for k in new if k in old)
for (a, b), c in sorted(tr.items()): print("  %s -> %s : %d" % (a, b, c))
print("== verdict flips")
for k in new:
    if k in old and old[k]["v"] != new[k]["v"]:
        print("FLIP", new[k]["id"], k, old[k]["v"], "->", new[k]["v"], "|", old[k]["key"], "->", new[k]["key"]); print("   now:", new[k]["msg"][:300]); print("   was:", old[k]["msg"][:300])
print("== first-blocker key changes (same verdict)")
for k in new:
    if k in old and old[k]["v"] == new[k]["v"] and old[k]["key"] != new[k]["key"]:
        print("KEY", new[k]["id"], k, new[k]["v"], "|", old[k]["key"], "->", new[k]["key"]); print("   now:", new[k]["msg"][:300]); print("   was:", old[k]["msg"][:300])
print("== msg changes (same key)")
n=0
for k in new:
    if k in old and old[k]["key"] == new[k]["key"] and old[k]["msg"] != new[k]["msg"]:
        n+=1; print("MSG", new[k]["id"], k, new[k]["key"]); print("   now:", new[k]["msg"][:250]); print("   was:", old[k]["msg"][:250])
print("msg-only changes", n)
