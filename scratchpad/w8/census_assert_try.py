"""ROUTE #16 census: a Python `assert` inside a `try` whose handlers can catch
AssertionError (named, bare `except`, or `except Exception`/`BaseException`)."""
import ast, os, warnings
warnings.filterwarnings("ignore")
ROOTS = ['test-suite/corpus/pycsl-reference', 'test-suite/corpus/python-reference',
         'src/self-annotate/src', 'src/pycsl_lib', 'src/pycsl', 'tests']
CATCHERS = {"AssertionError", "Exception", "BaseException"}

def handler_catches(h):
    if h.type is None:
        return True                       # bare `except:`
    names = []
    t = h.type
    if isinstance(t, ast.Tuple):
        names = [n.id for n in t.elts if isinstance(n, ast.Name)]
    elif isinstance(t, ast.Name):
        names = [t.id]
    elif isinstance(t, ast.Attribute):
        names = [t.attr]
    return any(n in CATCHERS for n in names)

tot_assert = 0
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
                tree = ast.parse(open(p, encoding='utf-8').read())
            except Exception:
                continue
            asserts = [n for n in ast.walk(tree) if isinstance(n, ast.Assert)]
            tot_assert += len(asserts)
            if not asserts:
                continue
            for t in [n for n in ast.walk(tree) if isinstance(n, (ast.Try,))]:
                if not any(handler_catches(h) for h in t.handlers):
                    continue
                for stmt in t.body:
                    for n in ast.walk(stmt):
                        if isinstance(n, ast.Assert):
                            hits.append((p, n.lineno))
print("Python `assert` statements in scope:", tot_assert)
print("ROUTE #16 EXPLOITABLE SHAPE (assert inside a catching try):", len(hits))
for h in hits[:30]:
    print("   ", h)
