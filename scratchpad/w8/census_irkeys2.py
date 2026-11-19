"""Sharper cross-module IR-key census. For each IR node tag Module 5 emits, restrict the
Module-6 side to the FUNCTIONS that actually mention that tag literal, plus their
same-file callee closure (depth 2). A key emitted by Module 5 but never mentioned inside
that closure is a field the node's own lowering does not read."""
import ast, os, collections, warnings
warnings.filterwarnings("ignore")

M5 = 'src/pycsl/frontend/Module5_IREmitter.py'
M6_ROOTS = ['src/pycsl/module6_whyml', 'src/pycsl/Module6_WhyMLTranspiler.py',
            'src/pycsl/core_ir_semantic.py', 'src/pycsl/ir_schema.py',
            'src/pycsl/frontend/ir_resolve.py', 'src/pycsl/frontend/desugar.py',
            'src/pycsl/frontend/ir_inline.py', 'src/pycsl/frontend/monomorphize.py']

emitted = collections.defaultdict(set)
for n in ast.walk(ast.parse(open(M5, encoding='utf-8').read())):
    if not isinstance(n, ast.Dict):
        continue
    keys, tag = [], None
    for k, v in zip(n.keys, n.values):
        if not (isinstance(k, ast.Constant) and isinstance(k.value, str)):
            continue
        keys.append(k.value)
        if k.value in ("type", "stmt") and isinstance(v, ast.Constant) \
                and isinstance(v.value, str):
            tag = v.value
    if tag is not None:
        emitted[tag].update(x for x in keys if x not in ("type", "stmt"))

files = []
for r in M6_ROOTS:
    if os.path.isfile(r):
        files.append(r)
    else:
        for dp, dn, fn in os.walk(r):
            dn[:] = [d for d in dn if d != '__pycache__']
            files += [os.path.join(dp, f) for f in fn if f.endswith('.py')]

funcs = {}                     # (file, name) -> [FunctionDef]
names_in = {}                  # (file, name) -> set of names mentioned
calls_in = {}                  # (file, name) -> set of callee names
for f in files:
    try:
        t = ast.parse(open(f, encoding='utf-8').read())
    except SyntaxError:
        continue
    for n in ast.walk(t):
        if isinstance(n, ast.FunctionDef):
            key = (f, n.name)
            funcs.setdefault(key, []).append(n)
            nm, cl = set(), set()
            for c in ast.walk(n):
                if isinstance(c, ast.Constant) and isinstance(c.value, str):
                    nm.add(c.value)
                elif isinstance(c, ast.Attribute):
                    nm.add(c.attr)
                if isinstance(c, ast.Call):
                    fn2 = c.func
                    if isinstance(fn2, ast.Attribute):
                        cl.add(fn2.attr)
                    elif isinstance(fn2, ast.Name):
                        cl.add(fn2.id)
            names_in.setdefault(key, set()).update(nm)
            calls_in.setdefault(key, set()).update(cl)

by_name = collections.defaultdict(list)
for (f, nme) in funcs:
    by_name[nme].append((f, nme))

def closure_names(seeds, depth=2):
    seen, frontier, out = set(), [(s, 0) for s in seeds], set()
    while frontier:
        k, d = frontier.pop()
        if k in seen or d > depth:
            continue
        seen.add(k)
        out |= names_in.get(k, set())
        if d < depth:
            for c in calls_in.get(k, set()):
                for k2 in by_name.get(c, []):
                    frontier.append((k2, d + 1))
    return out

hits = 0
for tag, keys in sorted(emitted.items()):
    seeds = [k for k in funcs if tag in names_in.get(k, set())]
    if not seeds:
        print("  %-28s NO MODULE-6 FUNCTION MENTIONS THIS TAG (keys=%s)" % (tag, sorted(keys)))
        hits += 1
        continue
    have = closure_names(seeds)
    missing = sorted(k for k in keys if k not in have)
    if missing:
        hits += 1
        print("  %-28s (%d handler fn) UNREAD KEYS: %s" % (tag, len(seeds), missing))
print("--- tags:", len(emitted), " flagged:", hits)
