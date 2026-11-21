"""Exact ROUTE #13 victim list: every `self.<field>.<mutator>(...)` call inside a mirror
method that is NOT `\trusted`. Trust is decided by the CONTIGUOUS `#@` block directly above
the def (decorators included), not by a fixed window."""
import ast, os, warnings
warnings.filterwarnings("ignore")
MUT = {"append", "extend", "insert", "remove", "pop", "clear", "sort", "reverse",
       "update", "popitem", "setdefault", "add", "discard",
       "intersection_update", "difference_update", "symmetric_difference_update"}
ROOT = 'src/self-annotate/src'

def is_trusted(lines, first_line):
    i = first_line - 2          # 0-based line just above the def/decorator
    seen = False
    while i >= 0:
        st = lines[i].strip()
        if st.startswith("#@"):
            seen = True
            if st.startswith("#@ \\trusted"):
                return True
        elif st.startswith("#") or st == "":
            if seen:
                break
        else:
            break
        i -= 1
    return False

out = []
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d != '__pycache__']
    for f in sorted(fn):
        if not f.endswith('.py'):
            continue
        p = os.path.join(dp, f)
        src = open(p, encoding='utf-8').read()
        lines = src.splitlines()
        try:
            t = ast.parse(src)
        except SyntaxError:
            continue
        for n in ast.walk(t):
            if not isinstance(n, ast.FunctionDef):
                continue
            first = min([d.lineno for d in n.decorator_list] + [n.lineno])
            tr = is_trusted(lines, first)
            for c in ast.walk(n):
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) \
                        and c.func.attr in MUT:
                    r = c.func.value
                    if isinstance(r, ast.Attribute) and isinstance(r.value, ast.Name) \
                            and r.value.id == "self":
                        out.append((os.path.relpath(p, ROOT), n.name, n.lineno,
                                    r.attr, c.func.attr, tr))
conv = [o for o in out if not o[5]]
print("sites: %d  (CONVERTED %d / trusted %d)" % (len(out), len(conv), len(out) - len(conv)))
for o in conv:
    print("   CONVERTED  %-28s %-34s :%d  self.%s.%s()" % (o[0], o[1], o[2], o[3], o[4]))
