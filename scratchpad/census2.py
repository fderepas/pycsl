import ast, os, re

MIRROR = "src/self-annotate/src"
LIVE = "src/pycsl"

def trusted_funcs(path):
    out = []
    try:
        lines = open(path).read().splitlines()
    except Exception:
        return out
    for i, ln in enumerate(lines):
        if "\\trusted" in ln and ln.strip().startswith("#@"):
            for j in range(i, min(i+12, len(lines))):
                m = re.match(r"\s*def\s+(\w+)", lines[j])
                if m:
                    out.append(m.group(1)); break
    return out

def live_node(live_path, fname):
    try:
        src = open(live_path).read(); tree = ast.parse(src)
    except Exception:
        return None, None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == fname:
            return node, src
    return None, None

def ret_ann(node):
    if node.returns is None:
        return "?"
    try:
        return ast.unparse(node.returns)
    except Exception:
        return "?"

def has_nested_def(node):
    for c in ast.walk(node):
        if c is node: continue
        if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            return True
    return False

rows = []
for root, _, files in os.walk(MIRROR):
    for f in files:
        if not f.endswith(".py"): continue
        mpath = os.path.join(root, f)
        rel = os.path.relpath(mpath, MIRROR)
        lpath = os.path.join(LIVE, rel)
        for fn in trusted_funcs(mpath):
            node, src = live_node(lpath, fn)
            if node is None: continue
            ret = ret_ann(node)
            # classify return: bool/set/int good; str/list-of-str construction bad
            good_ret = bool(re.search(r'\b(bool|Set|FrozenSet|frozenset|int)\b', ret)) or ret in ("bool","int")
            seg = ast.get_source_segment(src, node) or ""
            body = seg
            memberships = len(re.findall(r'\bin\s+[A-Za-z_][\w.]*(_SET|_set|_NAMES|_KINDS|set\b)', body))
            in_tuple = len(re.findall(r'\bin\s*\(', body))
            nested = has_nested_def(node)
            nlines = seg.count("\n")+1
            # detect string transform feeding comparison/membership (not returned)
            constructs = bool(re.search(r'(\.lower\(\)|\.upper\(\)|\+\s*["\']|["\']\s*\+|\.startswith|\.endswith)', body))
            rows.append((rel, fn, ret, good_ret, nested, nlines, memberships+in_tuple, constructs))

# rank: good_ret and not nested and small
def score(r):
    rel,fn,ret,good,nested,nl,mem,con = r
    s = 0
    if good: s += 100
    if not nested: s += 50
    s += mem*10
    if con: s += 20
    s -= nl
    return s
rows.sort(key=score, reverse=True)
print(f"{'ret':18s} {'nest':4s} {'L':4s} {'mem':3s} con  file :: fn")
for rel,fn,ret,good,nested,nl,mem,con in rows[:45]:
    if not good: continue
    print(f"{ret[:18]:18s} {'Y' if nested else '-':4s} {nl:4d} {mem:3d}  {'C' if con else '-'}   {rel} :: {fn}")
