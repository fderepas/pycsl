"""Blast-radius census for ROUTE #13, over the CORPUS (emitted .mlw already on disk) and
over source trees. A site is ERASED when the emitted module declares a nullary/self-less
abstract `val self_<field>_<mutator>_<n>`."""
import ast, os, re, warnings
warnings.filterwarnings("ignore")
MUT = {"append", "extend", "insert", "remove", "pop", "clear", "sort", "reverse",
       "update", "popitem", "setdefault", "add", "discard",
       "intersection_update", "difference_update", "symmetric_difference_update"}

def src_sites(path):
    try:
        src = open(path, encoding='utf-8').read()
        t = ast.parse(src)
    except Exception:
        return []
    out = []
    for c in ast.walk(t):
        if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) \
                and c.func.attr in MUT:
            r = c.func.value
            if isinstance(r, ast.Attribute) and isinstance(r.value, ast.Name) \
                    and r.value.id == "self":
                out.append((r.attr, c.func.attr))
    return out

# --- corpus: emitted .mlw are in scratchpad/w8/emit_head3 ---
CORP = 'test-suite/corpus/pycsl-reference'
EMIT = 'scratchpad/w8/emit_head3'
tot = era = 0
erased_files = []
for f in sorted(os.listdir(CORP)):
    if not f.endswith('.py'):
        continue
    sites = src_sites(os.path.join(CORP, f))
    if not sites:
        continue
    mlw = os.path.join(EMIT, f[:-3] + '.mlw')
    if not os.path.exists(mlw):
        continue
    text = open(mlw, encoding='utf-8').read()
    for field, mut in set(sites):
        tot += 1
        if re.search(r"^\s*val self_%s_%s_\d+ " % (re.escape(field), re.escape(mut)),
                     text, re.M):
            era += 1
            erased_files.append((f, field, mut))
print("CORPUS  self.<f>.<mut>() distinct sites: %d ; ERASED: %d" % (tot, era))
for e in erased_files:
    print("   ", e)

# --- pycsl_lib + live emitter: source-side count only (no .mlw on disk here) ---
for root in ('src/pycsl_lib', 'src/pycsl'):
    n = 0
    files = set()
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != '__pycache__']
        for f in fn:
            if f.endswith('.py'):
                s = src_sites(os.path.join(dp, f))
                if s:
                    n += len(s); files.add(os.path.join(dp, f))
    print("%-16s source-side self.<f>.<mut>() sites: %d in %d files" % (root, n, len(files)))
