import ast, os, re, sys

MIRROR = "src/self-annotate/src"
LIVE = "src/pycsl"

STROP = [
    (".lower(", "lower"), (".upper(", "upper"), (".startswith(", "startswith"),
    (".endswith(", "endswith"), (".split(", "split"), (".replace(", "replace"),
    (".strip(", "strip"), (".join(", "join"), ('f"', "fstr"), ("f'", "fstr"),
    (".rsplit(", "rsplit"), (".lstrip(", "lstrip"), (".rstrip(", "rstrip"),
]

def trusted_funcs(path):
    """Return list of function names marked #@ \\trusted in this mirror file."""
    out = []
    try:
        lines = open(path).read().splitlines()
    except Exception:
        return out
    for i, ln in enumerate(lines):
        if "\\trusted" in ln and ln.strip().startswith("#@"):
            # find next def
            for j in range(i, min(i+12, len(lines))):
                m = re.match(r"\s*def\s+(\w+)", lines[j])
                if m:
                    out.append(m.group(1))
                    break
    return out

def live_body_src(live_path, fname):
    try:
        src = open(live_path).read()
    except Exception:
        return None
    try:
        tree = ast.parse(src)
    except Exception:
        return None
    lines = src.splitlines()
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == fname:
            seg = ast.get_source_segment(src, node)
            found.append(seg)
    return found[0] if found else None

results = []
for root, _, files in os.walk(MIRROR):
    for f in files:
        if not f.endswith(".py"):
            continue
        mpath = os.path.join(root, f)
        rel = os.path.relpath(mpath, MIRROR)
        lpath = os.path.join(LIVE, rel)
        for fn in trusted_funcs(mpath):
            body = live_body_src(lpath, fn)
            if body is None:
                continue
            hits = set()
            # only look at body, strip signature/docstring roughly
            for tok, name in STROP:
                if tok in body:
                    hits.add(name)
            has_concat = bool(re.search(r'"\s*\+|\+\s*"|\'\s*\+|\+\s*\'', body))
            if has_concat:
                hits.add("concat")
            if hits:
                nlines = body.count("\n") + 1
                results.append((len(hits), nlines, rel, fn, sorted(hits)))

results.sort(key=lambda r: (-r[0], r[1]))
for nh, nl, rel, fn, hits in results:
    print(f"{nl:4d}L  {rel:40s} {fn:35s} {hits}")
print(f"\nTOTAL string-op trusted candidates: {len(results)}")
