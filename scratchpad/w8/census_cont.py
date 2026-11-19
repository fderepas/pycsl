import ast, io, os, sys, tokenize, warnings
warnings.filterwarnings("ignore")

ROOTS = ["src", "test-suite", "bin", "tests"]
hits = []; scanned = 0; parsefail = 0

def leaf_spans(tree):
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.stmt):
            kids = []
            for f in ("body", "orelse", "finalbody", "handlers", "cases"):
                v = getattr(n, f, None)
                if isinstance(v, list):
                    kids.extend(x for x in v if isinstance(x, (ast.stmt, ast.excepthandler, ast.match_case)))
            out.append((n.lineno, getattr(n, "end_lineno", n.lineno), not kids, type(n).__name__))
    return out

for root in ROOTS:
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ("__pycache__", ".venv", "attic")]
        for f in fn:
            if not f.endswith(".py"): continue
            p = os.path.join(dp, f)
            try: src = open(p, encoding="utf-8").read()
            except Exception: continue
            if "#@" not in src: continue
            scanned += 1
            try:
                tree = ast.parse(src)
                toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
            except (SyntaxError, tokenize.TokenError, IndentationError):
                parsefail += 1; continue
            spans = leaf_spans(tree)
            for t in toks:
                if t.type != tokenize.COMMENT: continue
                if not t.string.startswith("#@"): continue
                i = t.start[0]
                for lo, hi, is_leaf, kind in spans:
                    if is_leaf and lo < i <= hi:
                        hits.append((p, i, kind, t.string.strip()[:70])); break

print("scanned files with #@:", scanned, " parse-failed:", parsefail)
print("REAL-COMMENT HITS:", len(hits))
for h in hits: print("   ", h)
