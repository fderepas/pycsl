"""The 24 `\trusted` cross-mixin MRO-boundary stubs: mirror-only defs that ARE trusted.
`check-sibling-concrete-fidelity.py` counts them "(by design)" and never names them.
For each: does a LIVE def of that bare name exist elsewhere (so `#@ sibling_concrete` applies),
and how big is the destination mirror (the re-proof bill)?"""
import importlib.util, os, sys, collections
spec = importlib.util.spec_from_file_location("sync", "bin/check-self-annotate-mirror-sync.py")
_sync = importlib.util.module_from_spec(spec); spec.loader.exec_module(_sync)

MIRROR, LIVE = "src/self-annotate/src", "src/pycsl"
# index every live def by bare name
live_idx = collections.defaultdict(list)
for dp, dn, fns in os.walk(LIVE):
    dn[:] = [d for d in dn if d != "__pycache__"]
    for fn in sorted(fns):
        if fn.endswith(".py"):
            p = os.path.join(dp, fn)
            try:
                for qn in _sync.methods(p):
                    live_idx[qn.rsplit(".", 1)[-1]].append(p)
            except Exception:
                pass

rows = []
for dp, dn, fns in os.walk(MIRROR):
    dn[:] = [d for d in dn if d != "__pycache__"]
    for fn in sorted(fns):
        if not fn.endswith(".py"):
            continue
        mp = os.path.join(dp, fn)
        lp = mp.replace(MIRROR, LIVE, 1)
        if not os.path.exists(lp):
            continue
        try:
            md, ld = _sync.methods(mp), _sync.methods(lp)
        except Exception:
            continue
        for qn in sorted(md):
            body, trusted = md[qn]
            if qn in ld or not trusted:
                continue
            bare = qn.rsplit(".", 1)[-1]
            rows.append((mp, qn, sorted(set(live_idx.get(bare, [])))))
print(f"`\\trusted` cross-mixin mirror-only stubs: {len(rows)}\n")
sizes = {}
by_file = collections.Counter()
for mp, qn, lives in rows:
    by_file[mp] += 1
    if mp not in sizes:
        sizes[mp] = sum(1 for _ in open(mp, encoding="utf-8"))
    tag = "LIVE FOUND" if lives else "NO LIVE DEF"
    print(f"  {mp} ({sizes[mp]} lines)")
    print(f"      {qn:52s} {tag}  {[os.path.basename(x) for x in lives][:3]}")
print("\nby destination file (the re-proof unit):")
for f, c in by_file.most_common():
    print(f"  {c:3d}  {f}  ({sizes[f]} lines)")
