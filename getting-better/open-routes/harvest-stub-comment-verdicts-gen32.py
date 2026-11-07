"""#72 step 1, done properly: HARVEST the verdicts the `\trusted` stubs' OWN COMMENTS already record.

Wall-lesson (r4): "a `\trusted` shim's comment is the cheapest available account of why it is
trusted, and it is written by someone who already tried." `_parse_assigns`'s comment says
"Stays `\trusted` (builds an assigns target list — family-B list boundary)" — a recorded verdict my
call-shaped instrument called CLEAR.
"""
import ast, collections, os, re

MIRROR = "src/self-annotate/src"
VERDICT = re.compile(r"stays?\s+`?\\?trusted|must stay|remains?\s+`?\\?trusted|not convertible"
                     r"|cannot be converted|do not convert|left\s+`?\\?trusted|keeps?\s+its\s+marker"
                     r"|boundary\b|family-[AB]\b|RE-TRUSTED|by design", re.I)

rows = []
for dp, dn, fns in os.walk(MIRROR):
    dn[:] = [d for d in dn if d != "__pycache__"]
    for fn in sorted(fns):
        if not fn.endswith(".py"): continue
        p = os.path.join(dp, fn); rel = p.replace(MIRROR + "/", "")
        lines = open(p, encoding="utf-8").read().splitlines()
        for i, ln in enumerate(lines):
            if not ln.strip().startswith(r"#@ \trusted"): continue
            # the contiguous plain-comment block ABOVE the `#@` block
            ctx, j = [], i - 1
            while j >= 0:
                t = lines[j].strip()
                if t.startswith("#@") or not t: j -= 1; continue
                if t.startswith("#"): ctx.insert(0, t.lstrip("# ")); j -= 1; continue
                break
            # and any plain comments INSIDE the `#@` block below the marker, before the def
            k = i + 1; name = None
            while k < len(lines):
                t = lines[k].strip()
                m = re.match(r"def\s+(\w+)", t)
                if m: name = m.group(1); break
                if t.startswith("#") and not t.startswith("#@"): ctx.append(t.lstrip("# "))
                k += 1
            blob = " ".join(ctx)
            if name and blob and VERDICT.search(blob):
                rows.append((rel, name, blob))
print(f"markers whose OWN COMMENT records a stay-trusted / boundary verdict: **{len(rows)}**")
byfile = collections.Counter(r[0] for r in rows)
print("\nby file:")
for f, k in byfile.most_common(12): print(f"   {k:4d}  {f}")
print("\nsample verdicts (first 12):")
for rel, name, blob in rows[:12]:
    print(f"   {rel}::{name}")
    print(f"       {blob[:210]}")
