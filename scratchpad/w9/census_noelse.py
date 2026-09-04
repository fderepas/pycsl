"""Census: Module-5 statement/expression handlers whose top-level dispatch is an
if/elif chain with NO else — the route-#23 shape, where an unmatched target shape
produces no IR at all and the statement SILENTLY VANISHES."""
import ast, os, sys

TARGETS = ["src/pycsl/frontend/Module5_IREmitter.py"]

def top_chain_has_else(fn):
    """True if every top-level if/elif chain in the function body ends in an else,
    or the function has a trailing unconditional statement (return/raise/append)."""
    body = fn.body
    # skip the docstring
    stmts = [s for s in body if not (isinstance(s, ast.Expr)
                                     and isinstance(s.value, ast.Constant)
                                     and isinstance(s.value.value, str))]
    if not stmts:
        return True, "empty"
    last = stmts[-1]
    if not isinstance(last, ast.If):
        return True, "ends with " + type(last).__name__
    # walk the elif chain
    node = last
    while True:
        if not node.orelse:
            return False, "if/elif chain with NO else"
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            node = node.orelse[0]
            continue
        return True, "chain ends in else"

rows = []
for t in TARGETS:
    tree = ast.parse(open(t).read())
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not (fn.name.startswith("_py_stmt_") or fn.name.startswith("_py_expr_")
                or fn.name.startswith("_process_")):
            continue
        ok, why = top_chain_has_else(fn)
        rows.append((ok, fn.name, fn.lineno, why))

bad = [r for r in rows if not r[0]]
print(f"{len(rows)} Module-5 handler(s) scanned; {len(bad)} end in an if/elif chain "
      f"with NO else (an unmatched shape produces NO IR):")
for _ok, name, ln, why in sorted(bad, key=lambda r: r[1]):
    print(f"    Module5_IREmitter.py:{ln}  {name}")
