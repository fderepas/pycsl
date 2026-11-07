"""Which functions does the `-> str` + `return None` refusal break?"""
import ast, os, sys
for root in sys.argv[1:]:
    hits = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('__pycache__', '.git', '.venv')]
        for f in sorted(fn):
            if not f.endswith('.py'):
                continue
            p = os.path.join(dp, f)
            try:
                t = ast.parse(open(p, encoding='utf-8').read())
            except Exception:
                continue
            for n in ast.walk(t):
                if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                r = n.returns
                if not (isinstance(r, ast.Name) and r.id == 'str'):
                    if not (isinstance(r, ast.Constant) and r.value == 'str'):
                        continue
                inner = {d for sub in ast.walk(n)
                         if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub is not n
                         for d in ast.walk(sub)}
                for x in ast.walk(n):
                    if x in inner:
                        continue
                    if isinstance(x, ast.Return) and (
                            x.value is None
                            or (isinstance(x.value, ast.Constant) and x.value.value is None)):
                        hits.append(f"{os.path.relpath(p, root)}::{n.name}:{x.lineno}")
                        break
    print(f"== {root}: {len(hits)}")
    for h in hits:
        print("   " + h)
