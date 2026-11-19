"""Cross-module IR-key census: every key Module 5 EMITS into an IR node literal, checked
against every string constant / attribute name Module 6 MENTIONS. A key emitted but never
mentioned anywhere in Module 6 is a field the lowering cannot be reading."""
import ast, os, sys, collections, warnings
warnings.filterwarnings("ignore")

M5 = 'src/pycsl/frontend/Module5_IREmitter.py'
M6_ROOTS = ['src/pycsl/module6_whyml', 'src/pycsl/Module6_WhyMLTranspiler.py',
            'src/pycsl/core_ir_semantic.py', 'src/pycsl/ir_schema.py',
            'src/pycsl/frontend/ir_resolve.py', 'src/pycsl/frontend/desugar.py',
            'src/pycsl/frontend/ir_inline.py', 'src/pycsl/frontend/monomorphize.py']

# ---- what Module 5 emits -------------------------------------------------
emitted = collections.defaultdict(set)     # node tag -> {key, ...}
src = open(M5, encoding='utf-8').read()
for n in ast.walk(ast.parse(src)):
    if not isinstance(n, ast.Dict):
        continue
    keys = []
    tag = None
    for k, v in zip(n.keys, n.values):
        if not (isinstance(k, ast.Constant) and isinstance(k.value, str)):
            continue
        keys.append(k.value)
        if k.value in ("type", "stmt") and isinstance(v, ast.Constant) \
                and isinstance(v.value, str):
            tag = (k.value, v.value)
    if tag is not None:
        emitted[tag].update(x for x in keys if x not in ("type", "stmt"))

# ---- what Module 6 (and the IR-resolution passes) mention ----------------
mentioned = set()
files = []
for r in M6_ROOTS:
    if os.path.isfile(r):
        files.append(r)
    else:
        for dp, dn, fn in os.walk(r):
            dn[:] = [d for d in dn if d != '__pycache__']
            files += [os.path.join(dp, f) for f in fn if f.endswith('.py')]
for f in files:
    try:
        t = ast.parse(open(f, encoding='utf-8').read())
    except SyntaxError:
        continue
    for n in ast.walk(t):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            mentioned.add(n.value)
        elif isinstance(n, ast.Attribute):
            mentioned.add(n.attr)
        elif isinstance(n, (ast.arg,)):
            mentioned.add(n.arg)

print("Module 6 side scanned:", len(files), "files;", len(mentioned), "distinct names")
hits = 0
for (kind, tag), keys in sorted(emitted.items()):
    missing = sorted(k for k in keys if k not in mentioned)
    if missing:
        hits += 1
        print("  %-6s %-28s NEVER MENTIONED IN MODULE 6: %s" % (kind, tag, missing))
print("--- node tags emitted:", len(emitted), " with an unmentioned key:", hits)
