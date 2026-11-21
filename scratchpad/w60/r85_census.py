"""Blast radius for ROUTE #85: a NON-EMPTY dict/set literal stored to a field in __init__."""
import ast, os
from collections import Counter
ROOTS = ["test-suite/corpus", "src/self-annotate", "src/pycsl", "src/pycsl_lib"]
rows = []
for root in ROOTS:
    for dp, dn, fns in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "__pycache__", ".venv")]
        for fn in fns:
            if not fn.endswith(".py"): continue
            p = os.path.join(dp, fn)
            try: tree = ast.parse(open(p, encoding="utf-8", errors="replace").read())
            except Exception: continue
            for cls in ast.walk(tree):
                if not isinstance(cls, ast.ClassDef): continue
                for ch in cls.body:
                    if not (isinstance(ch, ast.FunctionDef) and ch.name == "__init__"): continue
                    for st in ast.walk(ch):
                        t = r = None
                        if isinstance(st, ast.Assign) and len(st.targets) == 1: t, r = st.targets[0], st.value
                        elif isinstance(st, ast.AnnAssign): t, r = st.target, st.value
                        if not (isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                                and t.value.id == "self" and r is not None): continue
                        kind = None
                        if isinstance(r, ast.Dict) and len(r.keys) > 0: kind = "dict-literal"
                        elif isinstance(r, ast.Set) and len(r.elts) > 0: kind = "set-literal"
                        if kind:
                            rows.append((root, p, cls.name + "." + t.attr, kind))
print("ROUTE #85 sites (NON-EMPTY dict/set literal -> field, in __init__):", len(rows))
print("by root:", dict(Counter(r[0] for r in rows)))
print("by kind:", dict(Counter(r[3] for r in rows)))
print()
print("--- IN THE VERIFIED CORPUS (byte-diff / suite risk) ---")
for r in rows:
    if r[0] == "test-suite/corpus": print("   ", r[1], r[2], r[3])
print("--- IN THE MIRROR ---")
for r in rows:
    if r[0] == "src/self-annotate": print("   ", r[1], r[2], r[3])
