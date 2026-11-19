"""Census of ROUTE #13: a MUTATING METHOD CALL on a `self.<field>` collection.
Source side: find `self.<f>.<mut>(...)` in each mirror method, and whether that method is
`\trusted`. Model side: look for an abstract `val self_<f>_<mut>_<n>` in the emitted .mlw,
which is the ERASED lowering (nullary, no `self`, no `writes`)."""
import ast, os, re, sys, warnings
warnings.filterwarnings("ignore")

MUT = {"append", "extend", "insert", "remove", "pop", "clear", "sort", "reverse",
       "update", "popitem", "setdefault", "add", "discard",
       "intersection_update", "difference_update", "symmetric_difference_update"}
ROOT = 'src/self-annotate/src'

def trusted_lines(src):
    return {i + 1 for i, l in enumerate(src.splitlines()) if "#@ \\trusted" in l}

sites = []      # (relpath, method, field, mut, trusted?)
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d != '__pycache__']
    for f in sorted(fn):
        if not f.endswith('.py'):
            continue
        p = os.path.join(dp, f)
        src = open(p, encoding='utf-8').read()
        try:
            t = ast.parse(src)
        except SyntaxError:
            continue
        tl = trusted_lines(src)
        for fn_node in [n for n in ast.walk(t) if isinstance(n, ast.FunctionDef)]:
            # trusted if a \trusted marker sits in the 8 lines above the def / decorators
            first = min([d.lineno for d in fn_node.decorator_list] + [fn_node.lineno])
            is_tr = any(l in tl for l in range(first - 10, first))
            for c in ast.walk(fn_node):
                if not (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)):
                    continue
                if c.func.attr not in MUT:
                    continue
                recv = c.func.value
                if isinstance(recv, ast.Attribute) and isinstance(recv.value, ast.Name) \
                        and recv.value.id == "self":
                    sites.append((os.path.relpath(p, ROOT), fn_node.name,
                                  recv.attr, c.func.attr, is_tr))

conv = [s for s in sites if not s[4]]
trus = [s for s in sites if s[4]]
print("self.<field>.<mutator>() call sites in the mirror: %d  (CONVERTED %d / trusted %d)"
      % (len(sites), len(conv), len(trus)))

# model side: which of the CONVERTED ones are erased to a nullary abstract val?
erased = []
for rel, meth, field, mut, _ in conv:
    mlw = os.path.join(ROOT, rel[:-3] + '.mlw')
    if not os.path.exists(mlw):
        continue
    text = open(mlw, encoding='utf-8').read()
    pat = re.compile(r"^\s*val self_%s_%s_\d+ \(([^)]*)\)" % (re.escape(field), re.escape(mut)),
                     re.M)
    m = pat.search(text)
    if m:
        erased.append((rel, meth, field, mut, m.group(1)))
print("\nCONVERTED sites whose model is an ERASED abstract `self_<f>_<m>_N`:", len(erased))
seen = set()
for e in erased:
    k = (e[0], e[2], e[3])
    if k in seen:
        continue
    seen.add(k)
    print("   %-40s %-34s self.%s.%s(...)   val args=(%s)" % (e[0], e[1][:34], e[2], e[3], e[4]))
