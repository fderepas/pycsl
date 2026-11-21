"""Blast-radius predictor for route #51: `X is None` where X is a PARAM or FIELD whose
DECLARED annotation is a string type, inside a class carrying @mutable_state."""
import ast, sys, os

STR = {'str', 'Optional[str]', 'Text'}

def strann(a):
    if a is None:
        return False
    s = ast.unparse(a)
    return 'str' in s

for root in sys.argv[1:]:
    hits = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('__pycache__', '.git')]
        for f in sorted(fn):
            if not f.endswith('.py'):
                continue
            p = os.path.join(dp, f)
            try:
                tree = ast.parse(open(p, encoding='utf-8').read())
            except Exception:
                continue
            for cls in ast.walk(tree):
                if not isinstance(cls, ast.ClassDef):
                    continue
                decs = {ast.unparse(d) for d in cls.decorator_list}
                if 'mutable_state' not in ' '.join(decs):
                    continue
                fields = {}
                for st in cls.body:
                    if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                        fields[st.target.id] = st.annotation
                for m in cls.body:
                    if not isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    pann = {a.arg: a.annotation for a in m.args.args + m.args.kwonlyargs}
                    assigned = set()
                    for n in ast.walk(m):
                        if isinstance(n, ast.Assign):
                            for t in n.targets:
                                if isinstance(t, ast.Name):
                                    assigned.add(t.id)
                        elif isinstance(n, (ast.AnnAssign, ast.AugAssign)) and isinstance(n.target, ast.Name):
                            assigned.add(n.target.id)
                    for n in ast.walk(m):
                        if not (isinstance(n, ast.Compare) and len(n.ops) == 1
                                and isinstance(n.ops[0], (ast.Is, ast.IsNot))):
                            continue
                        c = n.comparators[0]
                        if not (isinstance(c, ast.Constant) and c.value is None):
                            continue
                        L = n.left
                        if isinstance(L, ast.Name) and L.id in pann and L.id not in assigned:
                            if strann(pann[L.id]):
                                hits.append(f"PARAM {os.path.relpath(p,root)}::{cls.name}.{m.name}:{n.lineno}  {L.id}: {ast.unparse(pann[L.id])}")
                        elif (isinstance(L, ast.Attribute) and isinstance(L.value, ast.Name)
                              and L.value.id == 'self'):
                            a = fields.get(L.attr)
                            if a is not None and strann(a):
                                hits.append(f"FIELD {os.path.relpath(p,root)}::{cls.name}.{m.name}:{n.lineno}  self.{L.attr}: {ast.unparse(a)}")
    print(f"== {root}: {len(hits)} string-typed PARAM/FIELD `is None` sites in @mutable_state classes")
    for h in hits:
        print("   " + h)
