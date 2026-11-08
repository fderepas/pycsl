"""How many `__init__` methods carry a `#@ requires` / `#@ ensures`, and how many of their
classes have a module-global singleton (the ONLY place `init_ensures` is re-checked)?"""
import ast, io, os, tokenize, warnings
warnings.filterwarnings("ignore")
ROOTS = ['test-suite/corpus/pycsl-reference', 'src/self-annotate/src', 'src/pycsl_lib',
         'src/pycsl', 'test-suite/corpus/python-reference']
tot = 0
hits = []
for root in ROOTS:
    if not os.path.isdir(root):
        continue
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != '__pycache__']
        for f in sorted(fn):
            if not f.endswith('.py'):
                continue
            p = os.path.join(dp, f)
            try:
                src = open(p, encoding='utf-8').read()
                tree = ast.parse(src)
                toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
            except Exception:
                continue
            cmts = {t.start[0]: t.string.strip() for t in toks
                    if t.type == tokenize.COMMENT and t.string.strip().startswith("#@")}
            if not cmts:
                continue
            for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
                for m in cls.body:
                    if not (isinstance(m, ast.FunctionDef) and m.name == '__init__'):
                        continue
                    first = min([d.lineno for d in m.decorator_list] + [m.lineno])
                    kinds = []
                    i = first - 1
                    while i in cmts or (i > 0 and i not in cmts and False):
                        st = cmts[i]
                        if st.startswith("#@ requires") or st.startswith("#@ ensures"):
                            kinds.append(st.split()[1])
                        i -= 1
                    if kinds:
                        tot += 1
                        hits.append((p, cls.name, sorted(set(kinds))))
print("__init__ methods carrying a requires/ensures:", tot)
seen = {}
for p, c, k in hits:
    seen.setdefault(p, []).append((c, k))
for p, v in sorted(seen.items()):
    print("   %-58s %s" % (p, v))
