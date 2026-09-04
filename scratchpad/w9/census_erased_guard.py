"""Census: locals assigned a value the model erases to the literal 0, then used as a
BOOLEAN (if/while/and/or/not/ternary-test/comprehension-if). Read-only AST scan."""
import ast, os, sys

ERASED_RHS = (ast.Set, ast.Tuple, ast.GeneratorExp)   # the DEMONSTRATED-erased kinds

ROOTS = ["src/pycsl", "src/self-annotate/src", "src/pycsl_lib",
         "test-suite/corpus/pycsl-reference", "test-suite/corpus/python-reference",
         "tests"]

class Fn(ast.NodeVisitor):
    def __init__(self, path):
        self.path = path; self.hits = []
    def visit_FunctionDef(self, node):
        erased = {}
        for n in ast.walk(node):
            if isinstance(n, ast.Assign) and isinstance(n.value, ERASED_RHS):
                if isinstance(n.value, (ast.Set, ast.Tuple)) and not n.value.elts:
                    continue
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        erased[t.id] = (type(n.value).__name__, n.lineno)
        if not erased:
            return self.generic_visit(node)
        tests = []
        for n in ast.walk(node):
            if isinstance(n, (ast.If, ast.While)):
                tests.append(n.test)
            elif isinstance(n, ast.IfExp):
                tests.append(n.test)
            elif isinstance(n, ast.BoolOp):
                tests.extend(n.values)
            elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not):
                tests.append(n.operand)
            elif isinstance(n, ast.comprehension):
                tests.extend(n.ifs)
        for t in tests:
            if isinstance(t, ast.Name) and t.id in erased:
                k, ln = erased[t.id]
                self.hits.append(f"{self.path}:{t.lineno}  `{t.id}` ({k} assigned at line {ln}) used as a BOOLEAN")
        self.generic_visit(node)
    visit_AsyncFunctionDef = visit_FunctionDef

total = 0
for r in ROOTS:
    if not os.path.isdir(r):
        continue
    for root, _d, files in os.walk(r):
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            p = os.path.join(root, fn)
            try:
                tree = ast.parse(open(p, errors="replace").read())
            except Exception:
                continue
            v = Fn(p); v.visit(tree)
            for h in v.hits:
                print(h); total += 1
print("TOTAL:", total)
