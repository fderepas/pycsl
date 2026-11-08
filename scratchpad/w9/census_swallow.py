"""Census: broad exception handlers in the LIVE emitter that SWALLOW and continue.

An `except Exception: pass` (or `-> return None/0/""` ) inside the lowering turns an
INTERNAL ERROR into a silent fallback, which is the same defect class this campaign has
found 28 times: the model quietly stops meaning what the body says. A top-level handler
that exits 1 is fail-closed; a mid-pipeline one that continues is not."""
import ast, os, sys

ROOTS = ["src/pycsl"]
rows = []
for r in ROOTS:
    for root, _d, files in os.walk(r):
        if "__pycache__" in root:
            continue
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            p = os.path.join(root, fn)
            try:
                tree = ast.parse(open(p, errors="replace").read())
            except Exception:
                continue
            for h in ast.walk(tree):
                if not isinstance(h, ast.ExceptHandler):
                    continue
                # broad = bare `except:` or `except Exception`
                t = h.type
                broad = (t is None
                         or (isinstance(t, ast.Name) and t.id in ("Exception", "BaseException"))
                         or (isinstance(t, ast.Tuple) and any(
                             isinstance(e, ast.Name) and e.id in ("Exception", "BaseException")
                             for e in t.elts)))
                if not broad:
                    continue
                body = h.body
                # SWALLOWING shapes: pass / continue / a bare return / return of a constant
                kind = None
                if len(body) == 1:
                    b = body[0]
                    if isinstance(b, ast.Pass):
                        kind = "pass"
                    elif isinstance(b, ast.Continue):
                        kind = "continue"
                    elif isinstance(b, ast.Return):
                        if b.value is None:
                            kind = "return None"
                        elif isinstance(b.value, ast.Constant):
                            kind = f"return {b.value.value!r}"
                if any(isinstance(x, ast.Raise) for x in ast.walk(h)):
                    kind = None          # re-raises: not a swallow
                if kind:
                    rows.append((os.path.relpath(p), h.lineno, kind))

print(f"{len(rows)} broad exception handler(s) in the LIVE emitter that SWALLOW and continue:")
by_kind = {}
for p, ln, k in rows:
    by_kind.setdefault(k, []).append(f"{p}:{ln}")
for k in sorted(by_kind, key=lambda k: -len(by_kind[k])):
    print(f"  {len(by_kind[k]):4d}  {k}")
    for e in by_kind[k][:6]:
        print(f"          {e}")
