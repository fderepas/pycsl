"""Which emitted modules USE a Why3 theory symbol without importing its theory?

Pure text over an already-emitted .mlw set: for each module, collect the `use X` lines
and look for tokens that need a theory that is not imported. This is the
missing-`use` family, enumerated rather than met one instance at a time.
"""
import os, re, sys, collections

NEEDS = [
    (r"(?<![\w.])map\s+\S", "map.Map"),
    (r"(?<![\w.])Map\.", "map.Map"),
    (r"(?<![\w.])const\s*\(", "map.Const"),
    (r"(?<![\w.])Some\b|(?<![\w.])None\b|(?<![\w.])option\s+\S", "option.Option"),
    (r"(?<![\w.])Seq\.", "seq.Seq"),
    (r"(?<![\w.])seq\s+\S", "seq.Seq"),
    (r"(?<![\w.])Array\.|\barray\s+\S", "array.Array"),
    (r"(?<![\w.])String\.", "string.String"),
    (r"(?<![\w.])matrix\b", "matrix.Matrix"),
    (r"(?<![\w.])List\.|(?<![\w.])list\s+\S", "list.List"),
    (r"(?<![\w.])real\b|(?<![\w.])Real\.", "real.Real"),
    (r"(?<![\w.])Bool\.|(?<![\w.])orb\b|(?<![\w.])andb\b|(?<![\w.])notb\b", "bool.Bool"),
]
root = sys.argv[1]
miss = collections.Counter(); examples = collections.defaultdict(list); files = 0
for f in sorted(os.listdir(root)):
    if not f.endswith(".mlw"):
        continue
    files += 1
    txt = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
    uses = set(re.findall(r"^\s*use\s+([\w.]+)", txt, re.M))
    # a module body without its `use` lines
    body = "\n".join(l for l in txt.split("\n") if not l.strip().startswith("use "))
    for pat, theory in NEEDS:
        if theory in uses:
            continue
        if re.search(pat, body):
            miss[theory] += 1
            if len(examples[theory]) < 6:
                examples[theory].append(f)
print("scanned %d emitted module(s)" % files)
for th, c in miss.most_common():
    print("  %-16s missing in %4d file(s)   e.g. %s" % (th, c, ", ".join(examples[th][:4])))
