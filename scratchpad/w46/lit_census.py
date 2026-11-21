"""Every Module 6 function whose FALL-THROUGH is a bare Why3 CONSTANT.

The fall-through is what a not-recognized shape gets.  A constant fall-through is
decidable in a guard (routes #24-#27, #29-#31) or a whole dropped statement (#37,
#38).  We report, per function: the constant, whether it is the LAST statement of
the body (a true fall-through) or only an `else`/branch return, and the enclosing
file:line.
"""
import ast, os, sys

CONSTS = {"true", "false", "0", "()", "", "1", "unit", "0.0"}
ROOT = "src/pycsl/module6_whyml"

def literal_of(node):
    if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant) \
            and isinstance(node.value.value, str):
        v = node.value.value.strip()
        if v in CONSTS:
            return v
    return None

rows = []
for dp, dn, fn in os.walk(ROOT):
    for f in sorted(fn):
        if not f.endswith(".py"):
            continue
        p = os.path.join(dp, f)
        t = ast.parse(open(p, encoding="utf-8").read())
        for fu in ast.walk(t):
            if not isinstance(fu, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            body = [s for s in fu.body if not (isinstance(s, ast.Expr)
                                               and isinstance(s.value, ast.Constant))]
            if not body:
                continue
            last = body[-1]
            lit = literal_of(last)
            if lit is not None:
                rows.append((p, last.lineno, fu.name, lit, "TAIL"))
                continue
            # a trailing `if ...: ... else: return "<const>"` is a fall-through too
            if isinstance(last, ast.If) and last.orelse:
                ol = [s for s in last.orelse if not (isinstance(s, ast.Expr)
                                                     and isinstance(s.value, ast.Constant))]
                if ol:
                    lit2 = literal_of(ol[-1])
                    if lit2 is not None:
                        rows.append((p, ol[-1].lineno, fu.name, lit2, "ELSE"))

print("%d fall-through-constant function(s)" % len(rows))
for lit in sorted({r[3] for r in rows}):
    sub = [r for r in rows if r[3] == lit]
    print("\n--- literal %r : %d ---" % (lit, len(sub)))
    for p, ln, nm, _l, kind in sub:
        print("  %-6s %s:%d  %s" % (kind, p, ln, nm))
