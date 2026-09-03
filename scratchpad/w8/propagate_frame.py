"""ROUTE #13 follow-through: give every `_Unparser` method in the MIRROR the frame its
LIVE body actually has. The transitive write set is computed from the live class; the new
`#@ assigns` is the UNION of what is declared today and what is measured, so this can only
WIDEN a frame, never narrow one."""
import ast, collections, re, sys, warnings
warnings.filterwarnings("ignore")

LIVE = 'src/pycsl/frontend/pure_ast.py'
MIRROR = 'src/self-annotate/src/frontend/pure_ast.py'
MUT = ("append", "extend", "insert", "remove", "pop", "clear", "sort", "reverse",
       "update", "add", "discard", "setdefault", "popitem")

src = open(LIVE, encoding='utf-8').read()
cls = [n for n in ast.walk(ast.parse(src))
       if isinstance(n, ast.ClassDef) and n.name == '_Unparser'][0]
methods = {m.name: m for m in cls.body if isinstance(m, ast.FunctionDef)}
direct = collections.defaultdict(set)
calls = collections.defaultdict(set)
for nm, m in methods.items():
    for c in ast.walk(m):
        if isinstance(c, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            tg = c.targets if isinstance(c, ast.Assign) else [c.target]
            for x in tg:
                if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name) \
                        and x.value.id == 'self':
                    direct[nm].add(x.attr)
        if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute):
            r = c.func.value
            if isinstance(r, ast.Attribute) and isinstance(getattr(r, 'value', None), ast.Name) \
                    and r.value.id == 'self' and c.func.attr in MUT:
                direct[nm].add(r.attr)
            if isinstance(r, ast.Name) and r.id == 'self' and c.func.attr in methods:
                calls[nm].add(c.func.attr)
writes = {k: set(direct.get(k, set())) for k in methods}
changed = True
while changed:
    changed = False
    for nm in methods:
        for cal in calls.get(nm, ()):
            new = writes[nm] | writes.get(cal, set())
            if new != writes[nm]:
                writes[nm] = new
                changed = True

# ---- rewrite the mirror's `#@ assigns` lines inside class _Unparser -------
mtext = open(MIRROR, encoding='utf-8').read()
mlines = mtext.splitlines(keepends=True)
mtree = ast.parse(mtext)
mcls = [n for n in ast.walk(mtree)
        if isinstance(n, ast.ClassDef) and n.name == '_Unparser'][0]
edits = []          # (line_index, new_text)
for m in mcls.body:
    if not isinstance(m, ast.FunctionDef):
        continue
    want = writes.get(m.name, set())
    first = min([d.lineno for d in m.decorator_list] + [m.lineno])
    # locate the `#@ assigns` line in the contiguous `#@` block above `first`
    i = first - 2
    aidx = None
    while i >= 0:
        st = mlines[i].strip()
        if st.startswith("#@"):
            if st.startswith("#@ assigns"):
                aidx = i
        elif st.startswith("#") or st == "":
            if aidx is not None:
                break
        else:
            break
        i -= 1
    if aidx is None:
        continue
    cur = mlines[aidx].strip()[len("#@ assigns"):].strip()
    have = set() if cur == r"\nothing" else {x.strip()[len("self."):]
                                            for x in cur.split(",") if x.strip().startswith("self.")}
    new = sorted(have | want)
    if not new or set(new) == have:
        continue
    indent = mlines[aidx][:len(mlines[aidx]) - len(mlines[aidx].lstrip())]
    edits.append((aidx, indent + "#@ assigns " + ", ".join("self." + f for f in new) + "\n"))

for idx, text in edits:
    mlines[idx] = text
open(MIRROR, 'w', encoding='utf-8').write("".join(mlines))
print("methods whose mirror frame was WIDENED:", len(edits))
