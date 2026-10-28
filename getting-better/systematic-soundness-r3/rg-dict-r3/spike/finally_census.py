# Census for open route #431: `return` / `break` / `continue` lexically inside a `finally:` block
# (excluding nested defs / classes, and loops nested inside the finally for break/continue).
# Pure AST; usage: finally_census.py <list-file>...
import ast, sys


def jumps(stmts):
    out = []
    stack = [(s, False) for s in stmts]
    while stack:
        n, inloop = stack.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        if isinstance(n, ast.Return):
            out.append(("return", n.lineno))
        elif isinstance(n, (ast.Break, ast.Continue)) and not inloop:
            out.append((type(n).__name__.lower(), n.lineno))
        loop = isinstance(n, (ast.For, ast.While, ast.AsyncFor))
        for c in ast.iter_child_nodes(n):
            stack.append((c, inloop or loop))
    return out


for lst in sys.argv[1:]:
    files = [l.strip() for l in open(lst) if l.strip()]
    hits = 0
    for f in files:
        try:
            t = ast.parse(open(f, encoding="utf-8", errors="replace").read())
        except SyntaxError:
            continue
        for n in ast.walk(t):
            if isinstance(n, (ast.Try, getattr(ast, "TryStar", ast.Try))) and n.finalbody:
                for k, ln in jumps(n.finalbody):
                    hits += 1
                    print(f"{lst.rsplit('/', 1)[-1]}\t{f}\t{ln}\t{k}")
    print(f"# {lst.rsplit('/', 1)[-1]}: {len(files)} files, {hits} jump(s) in finally", file=sys.stderr)
